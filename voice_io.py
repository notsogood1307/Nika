import os
import time
import tempfile
import keyboard
import sounddevice as sd
import soundfile as sf
import pyttsx3
from faster_whisper import WhisperModel
import config
import numpy as np

# Initialize pyttsx3 per-call inside speak() due to a known Windows event loop bug.
# (Removed global init to prevent the engine from freezing after the first run)

# Initialize Whisper Model
whisper_model = WhisperModel(
    config.WHISPER_MODEL_SIZE, 
    device=config.WHISPER_DEVICE, 
    compute_type="default"
)

def record_audio() -> str:
    print("Listening...", flush=True)
    
    # Audio settings
    sample_rate = 16000
    channels = 1
    
    # Start recording
    recorded_data = []
    
    def callback(indata, frames, time, status):
        recorded_data.append(indata.copy())

    stream = sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback)
    with stream:
        while keyboard.is_pressed('space'):
            time.sleep(0.01)
            
    print("Got it, thinking...", flush=True)
    
    if not recorded_data:
        return ""
        
    audio_data = np.concatenate(recorded_data, axis=0)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    
    sf.write(temp_file.name, audio_data, sample_rate)
    return temp_file.name

def transcribe(audio_path: str) -> str:
    if not audio_path or not os.path.exists(audio_path):
        return ""
        
    try:
        segments, info = whisper_model.transcribe(audio_path, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
        return text
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass

def speak(text: str) -> None:
    # We must initialize per-call because pyttsx3's event loop often hangs 
    # after the first runAndWait() in interactive terminal loops on Windows.
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    # Delete instance to ensure it properly clears from memory/COM
    del engine

import pyttsx3
import keyboard
import time

def speak(text: str) -> None:
    engine = pyttsx3.init()
    
    def onWord(name, location, length):
        if keyboard.is_pressed('space') or keyboard.is_pressed('esc'):
            print("Speech cancelled!")
            engine.stop()
            
    engine.connect('started-word', onWord)
    engine.say(text)
    engine.runAndWait()
    del engine

if __name__ == '__main__':
    print("Will say a long sentence. Hold 'space' or 'esc' to cancel.")
    speak("This is a very very long sentence that you should try to cancel by pressing space or escape right now before I finish speaking.")
    print("Finished speaking or was cancelled.")

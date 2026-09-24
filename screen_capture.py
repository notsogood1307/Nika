import mss
import tempfile
import base64
import os
from PIL import Image

def capture_screen() -> str:
    with mss.mss() as sct:
        # Grab the primary monitor (monitor 1)
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Resize if width > 1920
        if img.width > 1920:
            ratio = 1920 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
            
        # Save to temp file
        fd, temp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        
        try:
            img.save(temp_path, format="PNG")
            
            with open(temp_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            return encoded_string
        finally:
            # Delete temp file
            try:
                os.remove(temp_path)
            except OSError:
                pass

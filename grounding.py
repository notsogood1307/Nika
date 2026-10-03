import moondream as md
from PIL import Image
import logging

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

print("Loading Moondream Vision model (this happens once and may take a moment)...")
model = md.photon("moondream2")
print("Moondream Vision model loaded.")
logging.info("Moondream Vision model loaded via Photon.")

def find_click_target(image: Image.Image, description: str) -> tuple | None:
    try:
        orig_width, orig_height = image.size
        # Resize image to prevent token limit errors
        if max(image.width, image.height) > 960:
            image.thumbnail((960, 960))
            
        result = model.point(image, description)
        logging.debug(f"Raw point result for '{description}': {result}")
        
        if result and "points" in result and len(result["points"]) > 0:
            point = result["points"][0]
            # convert the normalized [0,1] coordinate to pixel coordinates using the ORIGINAL width/height
            pixel_x = int(point["x"] * orig_width)
            pixel_y = int(point["y"] * orig_height)
            return (pixel_x, pixel_y)
            
        return None
    except Exception as e:
        logging.exception(f"Error in find_click_target: {e}")
        return None

def describe_screen(image: Image.Image, question: str) -> str:
    try:
        if max(image.width, image.height) > 960:
            image.thumbnail((960, 960))
        result = model.query(image, question)
        if isinstance(result, dict) and "answer" in result:
            return result["answer"]
        elif isinstance(result, str):
            return result
        return str(result)
    except Exception as e:
        logging.exception(f"Error in describe_screen: {e}")
        return f"Error analyzing screen: {e}"

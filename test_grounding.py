import grounding
from PIL import Image, ImageDraw, ImageFont

# Create a dummy image representing a screen
img = Image.new('RGB', (1920, 1080), color=(255, 255, 255))
d = ImageDraw.Draw(img)
# Draw "File" menu text at a specific coordinate
d.text((50, 20), "File", fill=(0,0,0))
img.save("dummy_screen.png")

target = grounding.find_click_target(img, "the File menu")
print("Computed coordinates on dummy screen:", target)

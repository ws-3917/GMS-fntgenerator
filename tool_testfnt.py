# textfnt - Quick test for drawing effects of specific characters,
# useful for fine-tuning font height, size, and verifying support for specific characters
from PIL import Image, ImageFont, ImageDraw
import numpy as np

# Font path, character to display, font size, and drawing type
# '1' for binary image (black and white), 'L' for grayscale
fontfile = "fnt_en/determination-mono.woff"
ch = "æ"
size = 16
glyphtype = 'L'
threshold = 160  # Binarization threshold

font = ImageFont.truetype(fontfile, size)

# startpoint is the upper left drawing start point, endpoint is the lower right drawing endpoint (block size)
# Can be calculated using getbbox or manually specified

startpoint = (0, -1)
#startpoint = font.getbbox(ch)[:2]
#endpoint = (18, 18)
endpoint = font.getbbox(ch)[2:]

# Drawing
newimg = Image.new(glyphtype, endpoint)
drawtool = ImageDraw.Draw(newimg)
drawtool.text(startpoint, ch, font=font, fill=255)

# Convert binary image to a transparent grayscale image for output
arr = np.array(newimg)
# Create a new array for storing grayscale and transparency
new_arr = np.empty((arr.shape[0], arr.shape[1], 2), dtype=np.uint8)
new_arr[..., 0] = (arr > threshold) * 255  # Set grayscale and transparency

new_arr[..., 1] = 255  # Black background
#new_arr[..., 1] = new_arr[..., 0]  # Transparent background

newimg = Image.fromarray(new_arr, "LA")
#newimg.save("test.png")
newimg.show()

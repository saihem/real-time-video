import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def send_image(image_bytes):
    img = Image.open(image_bytes)
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype("arial.ttf", 14)
    # draw.text((0, 220), "This is a test11", (255, 255, 0), font=font)
    # draw = ImageDraw.Draw(img)
    img.save(f"frame_{elapsed}.jpeg")
    print("in image")
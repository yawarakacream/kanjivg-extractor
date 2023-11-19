import os
from typing import Union

from PIL import Image, ImageDraw, ImageFont


def pathstr(*s: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.join(*s)))


def char2code(char):
    return format(ord(char), "#07x")[len("0x"):]


def create_vertical_stack_image(data_list: list[Union[str, list[Image.Image]]], gap, font: ImageFont.FreeTypeFont):
    functions = []
    width = 0
    height = 0
    y = gap
    for data in data_list:
        x = gap
        if isinstance(data, str):
            dx, dy = font.getsize(data) # type: ignore
            functions.append((lambda image, draw, x=x, y=y, data=data, font=font: draw.text((x, y), text=data, font=font, fill=0)))
            x += dx + gap
            y += dy + gap
        elif isinstance(data, list):
            m_dy = 0
            for data0 in data:
                dx = data0.width
                dy = data0.height
                functions.append((lambda image, draw, x=x, y=y, data0=data0: image.paste(data0, (x, y))))
                x += dx + gap
                m_dy = max(m_dy, dy)
            y += m_dy + gap
        width = max(width, x)
    height = y

    image = Image.new("RGB", size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    for f in functions:
        f(image, draw)

    return image

import os
import subprocess
from typing import NamedTuple, Sequence, Union

import numpy as np

from PIL import Image, ImageDraw, ImageFont, ImageMath


def pathstr(*s: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.join(*s)))


def char2code(char):
    return format(ord(char), "#07x")[len("0x"):]


def generate_image_from_svg(svg: str, png_size: tuple[int, int], background: str):
    from uuid import uuid4

    tmp_filename = f"tmp_{uuid4()}"

    svg_filename = f"{tmp_filename}.svg"
    with open(svg_filename, "w") as f:
        print(svg, file=f)

    png_filename = f"{tmp_filename}.png"
    subprocess.run([
        "convert",
        "-background", background,
        "-resize", f"{png_size[0]}x{png_size[1]}",
        svg_filename, png_filename,
    ], check=True)
    
    with Image.open(png_filename) as png:
        png = png.copy()
    
    os.remove(svg_filename)
    os.remove(png_filename)

    assert png.size == png_size

    return png


class LImageCompositionResult(NamedTuple):
    image: Image.Image # 合成結果
    n_blended: int # 被ったピクセルの数


def composite_L_images(images: Sequence[Image.Image]) -> LImageCompositionResult:
    if len(images) == 0:
        raise Exception()
    
    image_size = images[0].size
    
    image = Image.new("L", image_size)
    sum_of_images = np.zeros(image_size, np.int32)
    for i in range(len(images)):
        if images[i].mode != "L":
            raise Exception(f"images[{i}] is not L")
        if images[i].size != image_size:
            raise Exception(f"invalid image size: {images[i].size} at {i}, {image_size} at 0")
        
        image = ImageMath.eval("image | image_i", image=image, image_i=images[i]).convert("L")
        assert isinstance(image, Image.Image)
        sum_of_images += np.array(images[i]) > 0 # 適当

    n_blended = np.count_nonzero(sum_of_images > 1)

    return LImageCompositionResult(image=image, n_blended=n_blended)


# I から L への変換がうまく動かない
# https://github.com/python-pillow/Pillow/issues/3011
def convert_to_L(image: Image.Image):
    if image.mode == "L":
        pass
    elif image.mode == "RGB" or image.mode == "RGBA":
        image = image.convert("L")
    elif image.mode == "I":
        image = ImageMath.eval("image >> 8", image=image).convert("L")
        assert isinstance(image, Image.Image)
    else:
        raise Exception(f"unknown mode: {image.mode}")
    assert image.mode == "L"
    return image


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

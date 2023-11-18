from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Final, Optional
from uuid import uuid4

import bs4
from PIL import Image, ImageMath

import config


@dataclass
class Kvg:
    kvgid: Final[str]
    name: Final[Optional[str]]
    part: Final[Optional[str]]
    position: Final[Optional[str]]
    svg: Final[list[str]]
    children: Final[list[Kvg]]

    @staticmethod
    def parse(char, *, log=False):
        charcode = format(ord(char), "#07x")[len("0x"):]
        if log: print(f"code: {charcode}")

        with open(config.input_kvg_path(charcode), encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, features="xml")

        soup = soup.select(f"g[id='kvg:{charcode}']")[0]

        if log: print(soup)

        def parse(soup, level=0):
            nonlocal log

            kvgid = soup.get("id")[len("kvg:"):]
            name = soup.get("kvg:element")
            part = soup.get("kvg:part")
            position = soup.get("kvg:position")
            svg = [path.attrs["d"] for path in soup.find_all("path", recursive=False)]
            children = [parse(c, level + 1) for c in soup.find_all("g", recursive=False)]

            if log: print("  " * level + (f"{name}" if part is None else f"{name} ({part})"))
            
            return Kvg(kvgid=kvgid, name=name, part=part, position=position, svg=svg, children=children)

        return parse(soup)
    
    @staticmethod
    def from_dict(dct):
        children = [Kvg.from_dict(c) for c in dct.pop("children")]
        return Kvg(children=children, **dct)
    
    def to_dict(self):
        from dataclasses import asdict
        return asdict(self)
    
    @property
    def charcode(self):
        return self.kvgid.split("-")[0]

    def draw(self, image_size: int, padding: int, stroke_width: float) -> list[tuple[Kvg, Image.Image]]:
        image = Image.new("L", (image_size, image_size), 0)
        
        if len(self.svg):
            tmp_filename = f"tmp_{uuid4()}"

            svg_paths = [f'<path stroke="white" stroke-width="{stroke_width * 109 / (image_size - padding * 2)}" fill="none" stroke-linecap="round" stroke-linejoin="round" d="{path}"/>' for path in self.svg]
            svg = f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">{"".join(svg_paths)}</svg>'

            svg_filename = f"{tmp_filename}.svg"
            with open(svg_filename, "w") as f:
                print(svg, file=f)

            png_filename = f"{tmp_filename}.png"
            subprocess.run([
                "convert",
                "-background", "black",
                "-resize", f"{image_size - padding * 2}x{image_size - padding * 2}",
                svg_filename, png_filename,
            ])
            
            png = Image.open(png_filename)
            if png.mode == "L":
                pass
            elif png.mode == "RGB" or png.mode == "RGBA":
                png = png.convert("L")
            elif png.mode == "I":
                png = ImageMath.eval("image >> 8", image=png).convert("L")
            else:
                raise Exception(f"unknown mode: {png.mode} in {self.kvgid}")
            assert png.mode == "L"
            
            image.paste(png, (padding, padding))
            
            os.remove(svg_filename)
            os.remove(png_filename)

        images: list[tuple[Kvg, Image.Image]] = []
        for child in self.children:
            child_images = child.draw(image_size=image_size, padding=padding, stroke_width=stroke_width)
            images += child_images
            image = ImageMath.eval("image | child", image=image, child=child_images[0][1]).convert("L")
        
        images.insert(0, (self, image))
        
        return images
    
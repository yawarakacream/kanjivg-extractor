from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Optional

import bs4
from PIL import Image

import config
from utility import generate_image_from_svg, compose_L_images, convert_to_L


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

    def generate_image(self, image_size: int, padding: int, stroke_width: float) -> list[tuple[Kvg, Image.Image]]:
        image = Image.new("L", (image_size, image_size), 0)
        
        if len(self.svg):
            svg_paths = [f'<path stroke="white" stroke-width="{stroke_width * 109 / (image_size - padding * 2)}" fill="none" stroke-linecap="round" stroke-linejoin="round" d="{path}"/>' for path in self.svg]
            svg = f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="109" height="109" viewBox="0 0 109 109">{"".join(svg_paths)}</svg>'

            image0 = generate_image_from_svg(
                svg,
                png_size=(image_size - padding * 2, image_size - padding * 2),
                background="black"
            )
            image0 = convert_to_L(image0)
            
            image.paste(image0, (padding, padding))

        images: list[tuple[Kvg, Image.Image]] = []
        for child in self.children:
            child_images = child.generate_image(image_size=image_size, padding=padding, stroke_width=stroke_width)
            images += child_images
            image = compose_L_images((image, child_images[0][1])).image
        
        images.insert(0, (self, image))
        
        return images

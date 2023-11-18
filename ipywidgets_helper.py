import io

import IPython
import ipywidgets

import numpy as np

import PIL


def render_images(images, columns=None, scroll=False):
    if not isinstance(images, list):
        raise Exception()
    
    columns = columns or len(images)
    
    children = []
    for image in images:
        if isinstance(image, tuple):
            image, title = image
        else:
            title = None
        
        # path
        if isinstance(image, str):
            image = IPython.display.Image(image)
            if isinstance(image.data, str):
                raise Exception(f"image not found: {image.data}")
            image = ipywidgets.Image(value=image.data, layout=ipywidgets.Layout(margin="0", width="100%", object_fit="contain"))
        
        # ndarray
        elif isinstance(image, np.ndarray):
            image = PIL.Image.fromarray(image).convert("RGB")
            bytesio = io.BytesIO()
            image.save(bytesio, format="png")
            image = ipywidgets.Image(value=bytesio.getvalue(), layout=ipywidgets.Layout(margin="0", width="100%", object_fit="contain"))
        
        # ndarray
        elif isinstance(image, PIL.Image.Image):
            image = image.convert("RGB")
            bytesio = io.BytesIO()
            image.save(bytesio, format="png")
            image = ipywidgets.Image(value=bytesio.getvalue(), layout=ipywidgets.Layout(margin="0", width="100%", object_fit="contain"))
        
        else:
            raise Exception(f"unsupported image: {image}")
        
        if title is None:
            children.append(image)
        else:
            children.append(ipywidgets.VBox(
                [ipywidgets.Label(title), image],
                layout=ipywidgets.Layout(align_items="center"),
            ))
        
    grid = ipywidgets.GridBox(
        children=children,
        layout=ipywidgets.Layout(
            width="100%",
            height="fit-content",
            grid_template_columns=f"repeat({columns}, 1fr)",
            align_items="flex-end",
            grid_gap="8px",
        )
    )
    
    return grid

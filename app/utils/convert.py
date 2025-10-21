from io import BytesIO

import requests
from PIL.Image import Image


def load_image_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return img
    except Exception as e:
        return None
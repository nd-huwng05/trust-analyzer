from io import BytesIO

import requests
from PIL import Image

from backend.utils.logger import get_logger


def load_images_from_urls(urls):
    images = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            images.append(img)
        except Exception as e:
            get_logger().error(e)
    return images
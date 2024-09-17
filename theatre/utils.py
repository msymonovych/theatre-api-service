import os
import uuid

from django.utils.text import slugify


def play_image_path(instance: "Play", filename: str):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/plays/", filename)

import glob
import os
from pathlib import Path

from PIL import Image

from models import User
from repositories import ImageNotFoundException, ImageRepository


class ImageRepo(ImageRepository):

    def set_image(self, user_id: str, img: Image):
        img.save(os.path.join(os.getcwd(), "user_images", user_id + "." + img.format.lower()))

    def get_image(self, user_id: str) -> Image:
        image_path = glob.glob(os.path.join("user_images", user_id + "*"))
        if image_path:
            with open(image_path[0], "rb") as f:
                return Image.open(f)
        else:
            raise ImageNotFoundException("Could not locate image form user_id")

    def get_image_path(self, user: User) -> Path:
        image_path = glob.glob(os.path.join("user_images", user.id + "*"))
        if image_path:
            return Path(image_path[0])
        else:
            raise ImageNotFoundException("Could not locate image form user_id")
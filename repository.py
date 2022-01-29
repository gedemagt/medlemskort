import glob
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

import qrcode
from PIL import Image
from flask import request

from models import Token, User

tokens = {

}


USERS = {"erik": User(**{
    "id": "erik",
    "name": "Erik Eriksen",
    "valid_to": datetime(2022, 10, 10),
    "s1": True,
    "s2": True,
    "s3": False
})}


def login(username: str, password: str) -> User:
    return USERS["erik"]


def get_user(user_id: str) -> User:
    return USERS["erik"]


def set_image(user_id: str, img: Image):
    img.save(os.path.join(os.getcwd(), "user_images", user_id + "." + img.format.lower()))


def get_image_path(user_id: str) -> Path:
    image_path = glob.glob(os.path.join("user_images", user_id + "*"))
    if image_path:
        return Path(image_path[0])
    else:
        raise ValueError("Could not locate image form user_id")


def renew_token(user_id: str) -> Token:
    user = get_user(user_id)
    token = secrets.token_urlsafe(50)

    tokens[token] = Token(
        generated=datetime.now(),
        user=user_id,
        valid_to=user.valid_to,
        token_valid_to=datetime.now() + timedelta(minutes=30),
        token=token
    )

    return tokens[token]


def get_qr_image(user_id: str) -> Image:

    token = renew_token(user_id)
    img = qrcode.make(f"{request.url_root}token/{token.token}")

    return img


def get_token(token: str) -> Token:
    return tokens.get(token, None)

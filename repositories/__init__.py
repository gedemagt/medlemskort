import secrets
from datetime import datetime, timedelta
from pathlib import Path

import qrcode
from PIL import Image
from flask import request, Flask

from models import Token, User


class TokenNotFoundException(Exception):
    pass


class InvalidTokenException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class LoginFailedException(Exception):
    pass


class ImageNotFoundException(Exception):
    pass


class Repository:

    def init(self, app: Flask):
        pass

    def delete_user(self, user: User):
        raise NotImplementedError

    def update_user(self, user: User):
        raise NotImplementedError

    def add_user(self, user: User):
        raise NotImplementedError

    def login(self, username: str, password: str) -> User:
        raise NotImplementedError

    def get_user(self, user_id: str) -> User:
        raise NotImplementedError

    def set_image(self, user_id: str, img: Image):
        raise NotImplementedError

    def get_image(self, user_id: str) -> Image:
        raise NotImplementedError

    def get_image_path(self, user_id: str) -> Path:
        raise NotImplementedError

    def renew_token(self, user: User) -> Token:
        token = secrets.token_urlsafe(50)

        token = Token(
            generated=datetime.now(),
            user=user,
            token_valid_to=datetime.now() + timedelta(minutes=30),
            token=token
        )
        self.set_token(token)

        return token

    def set_token(self, token: Token):
        raise NotImplementedError

    def get_qr_image(self, user: User) -> Image:

        token = self.renew_token(user)
        img = qrcode.make(f"{request.url_root}token/{token.token}")

        return img

    def get_token(self, token: str) -> Token:
        raise NotImplementedError

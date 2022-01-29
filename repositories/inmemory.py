from datetime import datetime
from models import Token, User
from repositories import TokenNotFoundException
from repositories.image import ImageRepo


class InMemoryRepo(ImageRepo):

    def __init__(self):
        super().__init__()

        self._tokens = {}

        self._users = {"erik": User(**{
            "id": "erik",
            "name": "Erik Eriksen",
            "valid_to": datetime(2022, 10, 10),
            "s1": True,
            "s2": True,
            "s3": False
        })}

    def login(self, username: str, password: str) -> User:
        return self._users["erik"]

    def get_user(self, user_id: str) -> User:
        return self._users["erik"]

    def set_token(self, token: Token):
        self._tokens[token.token] = token

    def get_token(self, token: str) -> Token:
        if token not in self._tokens:
            raise TokenNotFoundException()
        return self._tokens.get(token)

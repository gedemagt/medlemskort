from models import Token, User
from repositories import TokenNotFoundException, LoginFailedException, UserNotFoundException
from repositories import ImageRepository, TokenRepository, Repository


class InMemoryRepo(TokenRepository, Repository):

    def delete_user(self, user: User):
        if user.id in self._users:
            self._users.pop(user.id)

    def update_user(self, user: User):
        self._users[user.id] = user

    def add_user(self, user: User):
        self._users[user.id] = user

    def __init__(self):
        super().__init__()
        self._tokens = {}
        self._users = {}

    def login(self, user_id: str, password: str) -> User:
        if user_id in self._users and self._users[user_id].password == password:
            return self._users[user_id]
        raise LoginFailedException()

    def get_user(self, user_id: str) -> User:
        try:
            return self._users[user_id]
        except KeyError:
            raise UserNotFoundException()

    def set_token(self, token: Token):
        self._tokens[token.token] = token

    def get_token(self, token: str) -> Token:
        if token not in self._tokens:
            raise TokenNotFoundException()
        return self._tokens.get(token)

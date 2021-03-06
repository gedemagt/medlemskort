from dataclasses import dataclass
from datetime import datetime

from flask_login import UserMixin


@dataclass
class User(UserMixin):

    id: str
    name: str
    valid_to: datetime
    s1: bool
    s2: bool
    s3: bool
    source: str = "local"
    password: str = None


@dataclass
class Token:
    generated: datetime
    user: User
    token_valid_to: datetime
    token: str

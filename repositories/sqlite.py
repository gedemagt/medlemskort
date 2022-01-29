from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from models import User, Token
from repositories import LoginFailedException, UserNotFoundException, TokenNotFoundException
from repositories.image import ImageRepo

db = SQLAlchemy()


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    password = db.Column(db.String)
    source = db.Column(db.String)
    valid_to = db.Column(db.DateTime)
    s1 = db.Column(db.Boolean, nullable=False, default=False)
    s2 = db.Column(db.Boolean, nullable=False, default=False)
    s3 = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<User %r>' % self.name


class TokenModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(), nullable=False)
    token = db.Column(db.String(), nullable=False)
    generated = db.Column(db.DateTime)
    valid_to = db.Column(db.DateTime)
    token_valid_to = db.Column(db.DateTime)

    def __repr__(self):
        return '<Token %r>' %self.name


class DBRepository(ImageRepo):

    def init(self, app: Flask):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.init_app(app)
        with app.app_context():
            db.create_all()

            if UserModel.query.filter_by(username="erik").first() is None:
                db.session.add(
                    UserModel(username="erik", name="Erik Eriksen", password="pass", source="local", valid_to=datetime(2022, 2, 1)))
                db.session.commit()

    def login(self, username: str, password: str) -> User:
        um = UserModel.query.filter_by(username=username, password=password).first()
        if um is None:
            raise LoginFailedException()
        return User(
            id=um.username,
            name=um.name,
            valid_to=um.valid_to,
            s1=um.s1,
            s2=um.s2,
            s3=um.s3
        )

    def get_user(self, user_id: str) -> User:
        um = UserModel.query.filter_by(username=user_id).first()
        if um is None:
            raise UserNotFoundException()
        return User(
            id=um.username,
            name=um.name,
            valid_to=um.valid_to,
            s1=um.s1,
            s2=um.s2,
            s3=um.s3
        )

    def set_token(self, token: Token):
        db.session.add(
            TokenModel(
                user=token.user.id,
                token=token.token,
                generated=token.generated,
                valid_to=token.valid_to,
                token_valid_to=token.token_valid_to
            )
        )

        # TODO: Delete old token for this user

    def get_token(self, token: str) -> Token:
        tm = TokenModel.query.filter_by(token=token).first()
        if tm is None:
            raise TokenNotFoundException()
        return Token(
            user=self.get_user(tm.user),
            token=tm.token,
            generated=tm.generated,
            valid_to=tm.valid_to,
            token_valid_to=tm.token_valid_to
        )

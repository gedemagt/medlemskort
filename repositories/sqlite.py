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
    active = db.Column(db.Boolean)
    s1 = db.Column(db.Boolean, nullable=False, default=False)
    s2 = db.Column(db.Boolean, nullable=False, default=False)
    s3 = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<User {self.username}>'


class TokenModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(), nullable=False)
    token = db.Column(db.String(), nullable=False)
    generated = db.Column(db.DateTime)
    valid_to = db.Column(db.DateTime)
    token_valid_to = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Token {self.token}>'


class DBRepository(ImageRepo):

    def delete_user(self, user: User):
        user_model = UserModel.query.filter_by(username=user.id).first()
        if user is None:
            raise UserNotFoundException()
        db.session.delete(user_model)
        db.session.commit()

    def update_user(self, user: User):
        user_model = UserModel.query.filter_by(username=user.id).first()
        if user is None:
            raise UserNotFoundException()
        user_model.username = user.id
        user_model.name = user.name
        user_model.password = user.password
        user_model.source = user.source
        user_model.active = user.active
        user_model.s1 = user.s1
        user_model.s2 = user.s2
        user_model.s3 = user.s3
        db.session.commit()

    def add_user(self, user: User):
        db.session.add(
            UserModel(
                username=user.id,
                name=user.name,
                password=user.password,
                source=user.source,
                active=user.active,
                s1=user.s1,
                s2=user.s2,
                s3=user.s3
            )
        )
        db.session.commit()

    def init(self, app: Flask):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def login(self, username: str, password: str) -> User:
        um = UserModel.query.filter_by(username=username, password=password).first()
        if um is None:
            raise LoginFailedException()
        return User(
            id=um.username,
            name=um.name,
            active=um.active,
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
            active=um.active,
            s1=um.s1,
            s2=um.s2,
            s3=um.s3
        )

    def set_token(self, token: Token):

        TokenModel.query.filter_by(user=token.user.id).delete()

        db.session.add(
            TokenModel(
                user=token.user.id,
                token=token.token,
                generated=token.generated,
                token_valid_to=token.token_valid_to
            )
        )
        db.session.commit()

    def get_token(self, token: str, user_repo) -> Token:
        tm = TokenModel.query.filter_by(token=token).first()

        if tm is None:
            raise TokenNotFoundException()

        return Token(
            user=user_repo.get_user(tm.user),
            token=tm.token,
            generated=tm.generated,
            token_valid_to=tm.token_valid_to
        )

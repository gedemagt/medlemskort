import datetime
import os
from datetime import timedelta
from io import BytesIO

import qrcode
from PIL import Image, ImageOps
from flask import Flask, render_template, send_from_directory, send_file, redirect, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from api import ConventusAPI
from models import User
from repositories import LoginFailedException, TokenNotFoundException, UserNotFoundException, ImageNotFoundException
from repositories.sqlite import DBRepository

try:
    import dotenv
    dotenv.load_dotenv()
except ModuleNotFoundError:
    pass

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "logn_secret_kley"

login_manager.login_view = 'login'

repository = DBRepository()
repository.init(app)

api = ConventusAPI(os.getenv("APIKEY"), os.getenv("FORENINGSID"))

with app.app_context():
    try:
        repository.get_user("erik")
    except UserNotFoundException:
        repository.add_user(User(
            "erik", "Erik Eriksen", True, False, False, False, password="pass"
        ))


@login_manager.user_loader
def load_user(user_id):
    return api.get_user(user_id)


def serve_pil_image(pil_img: Image):
    img_io = BytesIO()
    pil_img.save(img_io)
    img_io.seek(0)
    return send_file(img_io, mimetype="png")


@app.get("/token/<token>")
def valid_toke(token):
    try:
        token = repository.get_token(token, api)
        return render_template("token.html", token=token, user=token.user, valid_to=token.user.active, generated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except TokenNotFoundException:
        return render_template("invalid_token.html", token=None)


@app.get("/image/qr")
@login_required
def qr():
    token = repository.renew_token(current_user)
    url = f"{request.url_root}token/{token.token}"
    print(url)
    img = qrcode.make(url)
    return serve_pil_image(img)


@app.get("/image/<image>")
def images(image):
    return send_from_directory("images", image)


@app.get("/css/<stylesheet>")
def stylesheet(stylesheet):
    return send_from_directory("css", stylesheet)


@app.get("/js/<script>")
def script(script):
    return send_from_directory("js", script)


@app.get("/image/user")
@login_required
def user_image():
    return send_file(repository.get_image_path(current_user))


@app.post("/image")
@login_required
def set_images():
    x = float(request.values["cropX"])
    y = float(request.values["cropY"])
    w = float(request.values["cropW"])
    h = float(request.values["cropH"])
    file = request.files['image']
    image = Image.open(file.stream)
    fmt = image.format
    image = ImageOps.exif_transpose(image)
    image = image.crop((x, y, x+w, y+h))
    aspect_ratio = image.width / image.height
    image.thumbnail((aspect_ratio * 512, 512), Image.ANTIALIAS)
    image.format = "jpeg"

    repository.set_image(current_user.id, image)

    return redirect("/")


@app.get("/qr")
@login_required
def with_qr():
    return do_render(True)


@app.post("/login")
def login():
    try:
        user = api.login(request.form["username"], request.form["password"])
        login_user(user, duration=timedelta(minutes=30))
    except LoginFailedException as e:
        print("Login failed")
    return redirect("/")


@app.get("/login")
def get_login():
    return render_template("login.html")


def do_render(show_qr: bool):
    has_img = True

    if show_qr:
        img = "qr"
    else:
        try:
            repository.get_image_path(current_user)
            img = "user"
        except (ValueError, ImageNotFoundException):
            has_img = False
            img = "no_image.jpg"

    return render_template(
        "index.html", img=f"image/{img}", has_img=has_img, show_qr=show_qr,
        user=current_user
    )


@app.get("/")
@login_required
def index():
    return do_render(False)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


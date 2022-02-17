import os
from datetime import timedelta
from io import BytesIO

import pendulum
import qrcode
from PIL import Image, ImageOps
from flask import Flask, render_template, send_from_directory, send_file, redirect, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from api import ConventusAPI
from repositories import LoginFailedException, TokenNotFoundException, ImageNotFoundException, \
    TokenRepository, ImageRepository
from repositories.image import ImageRepo
from repositories.sqlite import DBRepository, SQLiteTokenRepository

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

image_repo: ImageRepository = ImageRepo()

user_repo = ConventusAPI(os.getenv("APIKEY"), os.getenv("FORENINGSID"))

token_repo: TokenRepository = SQLiteTokenRepository(user_repo)
token_repo.init(app)


@login_manager.user_loader
def load_user(user_id):
    return user_repo.get_user(user_id)


def serve_pil_image(pil_img: Image):
    img_io = BytesIO()
    pil_img.save(img_io)
    img_io.seek(0)
    return send_file(img_io, mimetype="png")


@app.get("/token/<token>")
def valid_toke(token):
    try:
        token = token_repo.get_token(token)
        return render_template(
            "token.html", token=token, user=token.user, valid_to=token.user.active,
            generated_at=token.generated.astimezone(pendulum.timezone("Europe/Paris")).strftime("%Y-%m-%d %H:%M:%S")
        )
    except TokenNotFoundException:
        return render_template("invalid_token.html", token=None)


@app.get("/image/qr")
@login_required
def qr():
    token = token_repo.renew_token(current_user)
    url = f"{request.url_root}token/{token.token}"
    img = qrcode.make(url)
    return serve_pil_image(img)


@app.get("/image/<_image>")
def images(_image):
    return send_from_directory("images", _image)


@app.get("/css/<_stylesheet>")
def stylesheet(_stylesheet):
    return send_from_directory("css", _stylesheet)


@app.get("/js/<_script>")
def script(_script):
    return send_from_directory("js", _script)


@app.get("/image/user")
@login_required
def user_image():
    return send_file(image_repo.get_image_path(current_user))


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

    image_repo.set_image(current_user.id, image)

    return redirect("/")


@app.get("/qr")
@login_required
def with_qr():
    return do_render(True)


@app.post("/login")
def login():
    try:
        user = user_repo.login(request.form["username"], request.form["password"])
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
            image_repo.get_image_path(current_user)
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


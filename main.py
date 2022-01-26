import glob
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from flask import Flask, render_template, send_from_directory, send_file, redirect, request, render_template_string
from flask_login import LoginManager, UserMixin, login_required, logout_user, current_user, login_user
from werkzeug.utils import secure_filename

from api import do_login, tokens, USER

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "logn_secret_kley"

login_manager.login_view = 'login'


@dataclass
class User(UserMixin):

    id: str
    name: str
    valid_to: datetime
    s1: bool
    s2: bool
    s3: bool
    image: str = None


@login_manager.user_loader
def load_user(user_id):
    return User(**USER)


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io)
    img_io.seek(0)
    return send_file(img_io, mimetype="png")


@app.get("/token/<token>")
def valid_toke(token):
    try:
        return tokens[token]
    except KeyError:
        return "Invalid token"


@app.get("/image/qr")
@login_required
def qr():
    token = str(uuid.uuid4())
    img = qrcode.make(f"{request.url_root}token/{token}")
    tokens[token] = {
        "generated": datetime.now(),
        "user": current_user.name,
        "valid_to": current_user.valid_to,
        "token_valid_to": datetime.now() + timedelta(minutes=30)
    }

    return serve_pil_image(img)


@app.get("/image/<image>")
def images(image):
    return send_from_directory("images", image)


@app.get("/image/user/<image>")
@login_required
def user_images(image):
    return send_from_directory("user_images", image)


@app.post("/image")
@login_required
def set_images():
    file = request.files['image']
    filename = secure_filename(file.filename)
    file.save(os.path.join("user_images", current_user.id + "." + filename.split(".")[-1]))

    return redirect("/")


@app.get("/qr")
@login_required
def with_qr():
    return do_render(True)


@app.post("/login")
def login():
    login_user(User(
        **do_login(request.form["username"], request.form["password"])
    ), duration=timedelta(minutes=30))
    return redirect("/")


@app.get("/login")
def get_login():
    return render_template("login.html")


def do_render(show_qr: bool):

    image_path = glob.glob(os.path.join("user_images", current_user.id + "*"))
    has_img = True

    if show_qr:
        img = "qr"
    elif image_path:
        img = f"user/{image_path[0].split('/')[-1]}"
    else:
        has_img = False
        img = "no_image.jpg"

    return render_template(
        "index.html", img=f"image/{img}", has_img=has_img, show_qr=show_qr,
        s1=current_user.s1, s2=current_user.s2, s3=current_user.s3,
        image=current_user.image, username=current_user.name, valid_to=current_user.valid_to.strftime("%Y-%m-%d")
    )


@app.get("/")
@login_required
def index():
    return do_render(False)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run("localhost", 5000)


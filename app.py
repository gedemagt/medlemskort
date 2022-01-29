from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image
from flask import Flask, render_template, send_from_directory, send_file, redirect, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

import repository

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "logn_secret_kley"

login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return repository.get_user(user_id)


def serve_pil_image(pil_img: Image):
    img_io = BytesIO()
    pil_img.save(img_io)
    img_io.seek(0)
    return send_file(img_io, mimetype="png")


@app.get("/token/<token>")
def valid_toke(token):

    token = repository.get_token(token)

    if token:
        return render_template("token.html", is_valid=token.token_valid_to >= datetime.now())
    else:
        return render_template("token.html", is_valid=False)


@app.get("/image/qr")
@login_required
def qr():
    return serve_pil_image(repository.get_qr_image(current_user.id))


@app.get("/image/<image>")
def images(image):
    return send_from_directory("images", image)


@app.get("/image/user")
@login_required
def user_image():
    return send_file(repository.get_image_path(current_user.id))


@app.post("/image")
@login_required
def set_images():
    file = request.files['image']
    repository.set_image(current_user.id, Image.open(file.stream))

    return redirect("/")


@app.get("/qr")
@login_required
def with_qr():
    return do_render(True)


@app.post("/login")
def login():
    login_user(repository.login(request.form["username"], request.form["password"]), duration=timedelta(minutes=30))
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
            repository.get_image_path(current_user.id)
            img = "user"
        except ValueError:
            has_img = False
            img = "no_image.jpg"

    return render_template(
        "index.html", img=f"image/{img}", has_img=has_img, show_qr=show_qr,
        s1=current_user.s1, s2=current_user.s2, s3=current_user.s3, username=current_user.name,
        valid_to=current_user.valid_to.strftime("%Y-%m-%d")
    )


@app.get("/")
@login_required
def index():
    return do_render(False)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


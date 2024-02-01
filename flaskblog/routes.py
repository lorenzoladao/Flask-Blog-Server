import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, Response
from flaskblog import app, db, bcrypt
from flaskblog.recognition import FaceRecognition
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, FR_LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import cv2
import math
import numpy

posts = [
    {
        'author' : 'Corey Schaefer',
        'title' : 'Blog post 1',
        'content'   : 'First post content',
        'date_posted'   : '1/30/2024'
    }, 
    {
        'author' : 'Mr. Feeney',
        'title' : 'Blog post 2',
        'content'   : 'Second post content',
        'date_posted'   : '1/31/2024'
    }, 
]

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

def save_frimg(form_picture, username):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = username + f_ext
    picture_path = os.path.join(app.root_path, 'static/fr_images', picture_fn)
    
    img = Image.open(form_picture)
    img.save(picture_path)

    return picture_fn

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        picture_image = save_frimg(form.picture.data, form.username.data)
        user = User(username=form.username.data, email=form.email.data, fr_image=picture_image, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login Failed. Please check username and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)

    img.save(picture_path)
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    image_file = url_for('static', filename='flaskblog/profile_pics/' + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)


def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # fr = FaceRecognition()
            # name = fr.run_recognition()
            # name = name.split('.')[0]
            # print(name)
            # return redirect(url_for('home'))
            # if name:
            #     user = User.query.filter_by(username=name).first()
            #     if user:
            #         login_user(user, remember=False)
            #         next_page = request.args.get('next')
            #         return redirect(next_page) if next_page else redirect(url_for('home'))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/frlogin", methods=["GET", "POST"])
def frlogin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = FR_LoginForm()
    if form.validate_on_submit():
        print("submit")
        fr = FaceRecognition()
        name = fr.run_recognition()
        if name != None:
            name = name.split('.')[0]
            print(name)
            if name:
                user = User.query.filter_by(username=name).first()
                if user:
                    login_user(user, remember=False)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
                else:
                    print('User not found')
    return render_template("frlogin.html", title="Facial Recognition Login", form=form)
    
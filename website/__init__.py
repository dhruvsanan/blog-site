from flask_sqlalchemy import SQLAlchemy
import json
from os import path
from flask import Flask, render_template, request, flash, url_for,make_response, jsonify, send_file
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from sqlalchemy import update
from werkzeug.utils import secure_filename
from fpdf import FPDF
from flask_restful import Api, Resource, marshal_with,fields,reqparse
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from redis import Redis
from flask_caching import Cache
import time
from celery import Celery
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,
    create_refresh_token
)
import smtplib
from datetime import timedelta,datetime
import pytz
ist = pytz.timezone("Asia/Kolkata")
current_time_ist = datetime.now(ist)

DB_NAME = "database.db"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) 

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        CELERY_TIMEZONE='Asia/Kolkata',
        enable_utc = False,
        timezone = "Asia/Calcutta"
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs): 
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "asdfghjkuytrds!@#$z5677654"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['UPLOAD_FOLDER'] = 'static'
api= Api(app)
app.config['JWT_SECRET_KEY'] = 'secretshouldnotbeshared'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=120)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=2)
jwt = JWTManager(app)

app.config.update(
CELERY_BROKER_URL='redis://localhost:6379',
CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)
paath = path.join(app.root_path, 'static')
db = SQLAlchemy()
db.init_app(app)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

redis = Redis(host='localhost', port=6379, db=0)

SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "dhruvtestemail01@gmail.com"
SENDER_PASSWORD =""

def send_email(to_address, subject, message):
    msg = MIMEMultipart()
    msg ["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg ["Subject"] = subject
    msg.attach(MIMEText (message, "html"))
    s= smtplib.SMTP (host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()

    return True

# MODELS

class View(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
  author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
  date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Follow(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  followed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    url = db.Column(db.String)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    daily_hour= db.Column(db.Integer, default=9)
    daily_minute= db.Column(db.Integer, default=00)
    monthly_hour= db.Column(db.Integer, default=9)
    monthly_minute= db.Column(db.Integer, default=00)
    format = db.Column(db.String(150), default="HTML")
    posts = db.relationship('Post', backref='user_posts', lazy='subquery', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', lazy='subquery', passive_deletes=True)
    follows = db.relationship('Follow', foreign_keys=[Follow.user_id], backref='user', lazy='subquery')
    followed = db.relationship('Follow', foreign_keys=[Follow.followed_user_id], backref='followed_user', lazy='subquery')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.String)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy='subquery', passive_deletes=True)
    likes = db.relationship('Like', backref='post', lazy='subquery', passive_deletes=True)
    views = db.relationship('View', backref='post', lazy='subquery')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created database!")

create_database(app)

# VIEW

# app = Blueprint("app", __name__)
# app.register_blueprint(app, url_prefix="/")

@app.route('/follow/<username>', methods=['GET', 'POST'])
@jwt_required()
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user_id = get_jwt_identity()
    uuser = User.query.filter_by(id=current_user_id).first()
    if not user:
        return jsonify({"status": "error", "message": "No user with that username exists!"})
    elif user.id==current_user_id:
        return jsonify({"status": "error", "message": "you cannot follow yourself!"})
    elif Follow.query.filter_by(user_id=current_user_id, followed_user_id=user.id).first() is None:
        follow = Follow(user_id=current_user_id, followed_user_id=user.id)
        db.session.add(follow)
        db.session.commit()
        return jsonify({'message': f'{uuser.username} is following {user.username}', 'category': 'success',"status":"followed"})
    else:
        follow = Follow.query.filter_by(user_id=current_user_id, followed_user_id=user.id).first()
        db.session.delete(follow)
        db.session.commit()
    return jsonify({'message': f'{uuser.username} is no longer following {user.username}', 'category': 'success',"status":"unfollowed"})

@app.route('/search-user', methods=['GET', 'POST'])
@jwt_required()
def searchuser():
    username = request.args.get('name')
    current_user_id = get_jwt_identity()
    if username:
        userss = User.query.filter_by(id=current_user_id).first()
        users = User.query.filter(User.username.like(f"%{username}%")).all()
        if userss in users:
            users.remove(userss)
        return jsonify(users=[{'username': user.username} for user in users])
    return "user not found"

@app.route('/search-post', methods=['GET', 'POST'])
@jwt_required()
def searchpost():
    title = request.args.get('title')
    if title:
        posts = Post.query.filter(Post.title.like(f"%{title}%")).order_by(Post.id.desc()).all()
        posts_list = []
        for post in posts:
            user = User.query.filter_by(id=post.author).first()
            post_dict = {
                'id': post.id,
                'title': post.title,
                'text': post.text,
                'url': post.url,
                'username': user.username,
                'like': len(post.likes)
            }
            posts_list.append(post_dict)
        return jsonify(posts=posts_list)

    return "post not found"

@app.route('/followers/<username>', methods=['GET'])
@jwt_required()
def user_followers(username):
    users = User.query.filter_by(username=username).first()
    follows = Follow.query.filter_by(followed_user_id=users.id).all()
    usernames=[]
    for follow in follows:
        user_id=follow.user_id
        user = User.query.filter_by(id=user_id).first()
        usern=user.username
        usernames.append(usern)
    return jsonify({"usernames": usernames})


@app.route('/following/<username>', methods=['GET'])
@jwt_required()
def user_following(username):
    users = User.query.filter_by(username=username).first()
    follows = Follow.query.filter_by(user_id=users.id).all()
    usernames=[]
    for follow in follows:
        user = User.query.filter_by(id=follow.followed_user_id).first()
        usern=user.username
        usernames.append(usern)
    return jsonify({"usernames": usernames})

@app.route("/create-post", methods=['GET', 'POST'])
@jwt_required()
def create_post():
    current_user_id=get_jwt_identity()
    if request.method == "POST":
        text = request.form.get('text')
        title = request.form.get('title')
        image = request.files['image']
        if not title:
                return jsonify({"status": "error", "message": "title cannot be empty!"})
        elif not text:
            return jsonify({"status": "error", "message": "Post cannot be empty!"})
        elif image:
            filename = secure_filename(image.filename)
            url = url_for('static', filename=filename)
            if '.' in filename and filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                return jsonify({"status": "error", "message": "File type not supported!"})
            else:
                post = Post(text=text,title=title, author=current_user_id,url=url)
                image.save(path.join(paath, filename))
                db.session.add(post)
                db.session.commit()
                return jsonify({"status": "success", "message": "Post created!"})
        else:
            post = Post(text=text,title=title, author=current_user_id)
            db.session.add(post)
            db.session.commit()
            return jsonify({"status": "success", "message": "Post created!"})
    return render_template('create_post.html', user=current_user_id)

@app.route("/update-post/<post_id>", methods=['GET', 'POST', 'PUT'])
@jwt_required()
def update_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({"status": "error", "message": "Post does not exist!"})
    elif current_user_id != post.author:
        return jsonify({"status": "error", "message": "You do not have permission to Update this post!"})
    else:
        if request.method == "PUT":
            text = request.form.get('text')
            title = request.form.get('title')
            image = request.files.get('image')
            if not title:
                return jsonify({"status": "error", "message": "title cannot be empty!"})
            elif not text:
                return jsonify({"status": "error", "message": "Post cannot be empty!"})
            elif image:
                filename = secure_filename(image.filename)
                url = url_for('static', filename=filename)
                if '.' in filename and filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                    return jsonify({"status": "error", "message": "File type not supported!"})
                else:
                        image.save(path.join(paath, filename))
                        ex = update(Post.__table__).where(Post.id==post.id).values(text=text,title=title,url=url)
                        db.session.execute(ex)
                        db.session.commit()
                        return jsonify({"status": "success", "message": "Post Updated!"})
            else:
                ex = update(Post.__table__).where(Post.id==post.id).values(text=text,title=title)
                db.session.execute(ex)
                db.session.commit()
            return jsonify({"status": "success", "message": "Post Updated!"})
    return render_template('update_post.html', user=current_user_id,post=post,url=url,text=text,title=title)

@app.route("/delete-user", methods=['GET', 'POST'])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    if not user:
        return jsonify({"status": "error", "message": "User does not exist!"})
    else:
        delete_p = Post.__table__.delete().where(Post.author == user.id)
        delete_c = Comment.__table__.delete().where(Comment.author == user.id)
        delete_l= Like.__table__.delete().where(Like.author == user.id)
        delete_fs= Follow.__table__.delete().where(Follow.user_id == user.id)
        delete_fd= Follow.__table__.delete().where(Follow.followed_user_id == user.id)
        delete_v= View.__table__.delete().where(View.author == user.id)
        if user.posts:
            for post in user.posts:
                delete_pv= View.__table__.delete().where(View.post_id == post.id)
                db.session.execute(delete_pv)
                db.session.commit()
        db.session.delete(user)
        db.session.execute(delete_p)
        db.session.execute(delete_l)
        db.session.execute(delete_c)
        db.session.execute(delete_fs)
        db.session.execute(delete_fd)
        db.session.execute(delete_v)
        db.session.commit()
    return jsonify({"status": "success", "message": "User deleted!"})

@app.route("/dashboard/<username>")
@jwt_required()
def user_dashboard(username):
    current_user_id = get_jwt_identity()
    cache_key = f"{request.url}{current_user_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        app.logger.info(f"Cache hit for request {request.path}")
        uid,userfollowing,email,nfollowed,nfollows,ncomments,nposts,nposts,url,views = cached_data
        response_data = {
            "uid": uid,
            "views": views,
            "url": url,
            "nposts": nposts,
            "ncomments": ncomments,
            "nfollows": nfollows,
            "nfollowed": nfollowed,
            "email": email,
            "userfollowing": userfollowing
        }
        return make_response(jsonify(response_data), 200)
    else:
        user = User.query.filter_by(username=username).first()
        uid=user.id
        email=user.email
        following= Follow.query.filter_by(user_id=current_user_id,followed_user_id=user.id).first()
        userfollowing=False
        if following:
            userfollowing=True
        if not user:
            flash('No user with that username exists.', category='error')
            return jsonify({"status": "error", "message": "No user with that username exists."})
        posts = user.posts
        comments=user.comments
        url=user.url
        views=0
        for post in posts:
            view=len(post.views)
            views+=view
        nposts=len(posts)
        ncomments=len(comments)
        follows = Follow.query.filter_by(user_id=user.id).all()
        nfollowed=0
        for follow in follows:
            nfollowed+=1
        followers = Follow.query.filter_by(followed_user_id=user.id).all()
        nfollows=0
        for follow in followers:
            nfollows+=1
        cache.set(cache_key, (uid,userfollowing,email,nfollowed,nfollows,ncomments,nposts,nposts,url,views), timeout=300)
        app.logger.info(f"Cache miss for request {request.path}")
        # return render_template("user_dashboard.html", user=current_user,views=views,url=url,followings=followings,following=following, Follow=Follow, username=username,nposts=nposts,ncomments=ncomments,nfollows=nfollows,nfollowed=nfollowed)
        response_data = {
            "uid": uid,
            "views": views,
            "url": url,
            "nposts": nposts,
            "ncomments": ncomments,
            "nfollows": nfollows,
            "nfollowed": nfollowed,
            "email": email,
            "userfollowing": userfollowing
        }
        return make_response(jsonify(response_data), 200)


import json


@app.route("/engagement", methods=['GET', 'POST'])
@jwt_required()
def user_engagement():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    posts = user.posts
    comments = user.comments
    views = 0
    for post in posts:
        view = len(post.views)
        views += view
    nposts = len(posts)
    ncomments = len(comments)
    follows = Follow.query.filter_by(user_id=user.id).all()
    nfollowed = 0
    for follow in follows:
        nfollowed += 1
    followers = Follow.query.filter_by(followed_user_id=user.id).all()
    nfollows = 0
    for follow in followers:
        nfollows += 1
    return jsonify({
        "nposts": nposts,
        "ncomments": ncomments,
        "views": views,
        "nfollowed": nfollowed,
        "nfollows": nfollows,
    })





@app.route("/dashboard")
@jwt_required()
def dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    email=user.email
    posts = user.posts
    url=user.url
    comments=user.comments
    nposts=len(posts)
    ncomments=len(comments)
    follows = Follow.query.filter_by(user_id=current_user_id).all()
    nfollowed=0
    for follow in follows:
        nfollowed+=1
    followers = Follow.query.filter_by(followed_user_id=current_user_id).all()
    nfollows=0
    for follow in followers:
        nfollows+=1
    app=0
    for post in posts:
        view=post.views.count()
        app+=view
    return jsonify({"app": app, "url": url, "nposts": nposts,"ncomments": ncomments, "nfollows": nfollows, "nfollowed": nfollowed, "email": email})

@app.route("/create-comment/<post_id>", methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user_id = get_jwt_identity()
    text = request.form.get('newCommentText')
    if not text:
        return jsonify({"status": "error", "message": "Comment cannot be empty."})
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user_id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            return jsonify({"status": "success", "message": "Comment Posted."})
        else:
            return jsonify({"status": "error", "message": "Post does not exist."})

@app.route("/delete-comment/<comment_id>", methods=['POST'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return jsonify({"status": "error", "message": "Comment does not exist."})
    elif current_user_id != comment.author and current_user_id != comment.post.author:
        return jsonify({"status": "error", "message": "You do not have permission to delete this comment."})
    else:
        db.session.delete(comment)
        db.session.commit()
    return jsonify({"status": "success", "message": "comment deleted."})

@app.route("/update-comment/<comment_id>", methods=['GET', 'POST','PATCH'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.filter_by(id=comment_id).first()
    post_id=comment.post_id
    if not comment:
        return jsonify({"status": "error", "message": "Comment does not exist."})
    elif current_user_id != comment.author and current_user_id != comment.post.author:
        return jsonify({"status": "error", "message": "You do not have permission to update this comment."})
    else:
        if request.method == "PATCH":
            data = request.json
            text = data.get('text')
            if not text:
                return jsonify({"status": "error", "message": "Comment cannot be empty."})
            else:
                post = Post.query.filter_by(id=post_id)
                if post:
                    ex = update(Comment.__table__).where(Comment.id==comment.id).values(text=text)
                    db.session.execute(ex)
                    db.session.commit()
                    return jsonify({"status": "ersuccessror", "message": "Comment updated."})
                else:
                    return jsonify({"status": "error", "message": "Post does not exist."})
                    
@app.route("/like-post/<post_id>", methods=['GET'])
@jwt_required()
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    current_user_id=get_jwt_identity()
    like = Like.query.filter_by(author=current_user_id, post_id=post_id).first()
    likes = len(post.likes)
    if not post:
        return jsonify({"status": "error", "message": "Post does not exist."})
    elif like:
        db.session.delete(like)
        db.session.commit()
        likes -=1
        likeButtonClass='far fa-thumbs-up'
    else:
        like = Like(author=current_user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        likes+=1
        likeButtonClass='fas fa-thumbs-up'
    return jsonify({"likes": likes,"likeButtonClass":likeButtonClass})

@app.route("/update-user", methods=['GET', 'POST'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    username=user.username
    email=user.email
    useree = User.query.filter_by(email=user.email).first()
    usernn = User.query.filter_by(username=user.username).first()
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        usern = User.query.filter_by(username=request.form.get("username")).all()
        usere = User.query.filter_by(email=request.form.get("email")).all()
        if useree in usere:
                usere.remove(useree)
        if usernn in usern:
                usern.remove(usernn)
        if len(username) < 2:
            return jsonify({"status": "error", "message": "Username is too short."})
        elif len(email) < 4:
            return jsonify({"status": "error", "message": "Email is invalid."})
        elif usere:
            return jsonify({"status": "error", "message": "Duplicate email."})
        elif usern:
            return jsonify({"status": "error", "message": "Duplicate username."})
        else:
            ex = update(User.__table__).where(User.id==current_user_id).values(email=email, username=username)
            db.session.execute(ex)
            db.session.commit()
            flash('User updated!', category='success')
            return jsonify({"status": "success", "message": "User updated."})
    return jsonify({"username":username,"email":email})

@app.route("/update-picture", methods=['GET', 'POST'])
@jwt_required()
def update_picture():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    if not user:
        flash('User does not exist.', category='error')
    url=user.url
    username=user.username
    if request.method == 'POST':
        image = request.files.get('image')
        filename = secure_filename(image.filename)
        if image:
            if '.' in filename and filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash('File type not supported', category='error')
                return jsonify({"status": "error", "message": "File type not supported."})
            else:
                url = url_for('static', filename=filename)
                image.save(path.join(paath, filename))
                ex = update(User.__table__).where(User.id==user.id).values(url=url)
                db.session.execute(ex)
                db.session.commit()
                flash('Profile Picture updated!', category='success')
                return jsonify({"status": "success", "message": "Profile Picture updated."})
    return jsonify({"url": url,"username":username})


@app.route("/update-password", methods=['GET', 'POST'])
@jwt_required()
def update_password():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    username=user.username
    if not user:
        flash('User does not exist.', category='error')
        return jsonify({"status": "error", "message": "User does not exist."})
    if request.method == 'POST':
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            flash('Password don\'t match!', category='error')
            return jsonify({"status": "error", "message": "Password don\'t match!."})
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
            return jsonify({"status": "error", "message": "Password is too short."})
        elif check_password_hash(user.password, password1):
            flash('You cannot use previous password.', category='error')
            return jsonify({"status": "error", "message": "You cannot use previous password."})
        else:
            ex = update(User.__table__).where(User.id==current_user_id).values(password=generate_password_hash(password1, method='sha256'))
            db.session.execute(ex)
            db.session.commit()
            flash('Password updated!', category='success')
            # return redirect(url_for('app.dashboard'))
            return jsonify({"status": "success", "message": "Password updated."})
    return jsonify({"username":username})


# AUTH

# auth = Blueprint("auth", __name__)
# app.register_blueprint(auth, url_prefix="/")

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    response = make_response(jsonify({"access_token":access_token}))
    response.set_cookie('access_token', access_token, httponly=True)
    return response

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                response = make_response(jsonify({"status": "success", "message": "User Logged in!","access_token":access_token,"refresh_token":refresh_token}))
                response.set_cookie('access_token', access_token, httponly=True)
                response.set_cookie('refresh_token', refresh_token, httponly=True)
                return response
            else:
                flash('Password is incorrect.', category='error')
                return jsonify({"status": "error", "message": "Password is incorrect."})
        else:
            flash('Email does not exist.', category='error')
            return jsonify({"status": "error", "message": "Email does not exist."})
    return render_template("login.html")


@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        image = request.files['image']

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
            return jsonify({"status": "error", "message": "Email is already in use."})
        elif username_exists:
            flash('Username is already in use.', category='error')
            return jsonify({"status": "error", "message": "Username is already in use."})
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
            return jsonify({"status": "error", "message": "Password don\'t match."})
        elif len(username) < 2:
            flash('Username is too short.', category='error')
            return jsonify({"status": "error", "message": "Username is too short."})
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
            return jsonify({"status": "error", "message": "Password is too short."})
        else:
            if image:
                filename = secure_filename(image.filename)
                if '.' in filename and filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                    flash('File type not supported', category='error')
                    return jsonify({"status": "error", "message": "File type not supported."})
                else:
                    url = url_for('static', filename=filename)
                    image.save(path.join(paath, filename))
                    new_user = User(email=email, username=username,url=url, password=generate_password_hash(
                        password1, method='sha256'))
                    db.session.add(new_user)
                    db.session.commit()
                    access_token = create_access_token(identity=new_user.id)
                    refresh_token = create_refresh_token(identity=new_user.id)
                    response = make_response(jsonify({"status": "success", "message": "User created!","access_token":access_token,"refresh_token":refresh_token}))
                    response.set_cookie('access_token', access_token, httponly=True)
                    response.set_cookie('refresh_token', refresh_token, httponly=True)
                    return response
            else:
                new_user = User(email=email, username=username, password=generate_password_hash(
                    password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                access_token = create_access_token(identity=new_user.id)
                refresh_token = create_refresh_token(identity=new_user.id)
                response = make_response(jsonify({"status": "success", "message": "User created!","access_token":access_token,"refresh_token":refresh_token}))
                response.set_cookie('access_token', access_token, httponly=True)
                response.set_cookie('refresh_token', refresh_token, httponly=True)
                return response

@app.route("/reset-password", methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user = User.query.filter_by(username=username,email=email).first()
        if user:
            if password1 != password2:
                flash('Password don\'t match!', category='error')
                return jsonify({"status": "error", "message": "Password don\'t match!."})
            elif len(password1) < 6:
                flash('Password is too short.', category='error')
                return jsonify({"status": "error", "message": "Password is too short."})
            elif check_password_hash(user.password, password1):
                flash('You cannot use previous password.', category='error')
                return jsonify({"status": "error", "message": "You cannot use previous password."})
            else:
                ex = update(User.__table__).where(User.username==username).values(password=generate_password_hash(
                    password1, method='sha256'))
                db.session.execute(ex)
                db.session.commit()
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                response = make_response(jsonify({"status": "success", "message": "Password Resetted!","access_token":access_token,"refresh_token":refresh_token}))
                response.set_cookie('access_token', access_token, httponly=True)
                response.set_cookie('refresh_token', refresh_token, httponly=True)
                return response
        else:
            return jsonify({"status": "error", "message": "Wrong username and email entered."})
    return jsonify({"username":username})


@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"status": "success", "message": "User Logged out!"}))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


class BusinessValidationError(HTTPException):
    def __init__ (self, status_code,error_codes,error_messages):
        message = {"error_code": error_codes, "error_message": error_messages}
        self.response=make_response(json.dumps(message),status_code)

create_user_parser = reqparse.RequestParser ()
create_user_parser.add_argument ('username')
create_user_parser.add_argument ('email')
create_user_parser.add_argument ('password')

check_user_parser = reqparse.RequestParser ()
check_user_parser.add_argument ('email')
check_user_parser.add_argument ('password')

update_user_parser = reqparse.RequestParser ()
update_user_parser.add_argument ('new_username')
update_user_parser.add_argument ('new_email')
update_user_parser.add_argument ('password')

create_post_parser = reqparse.RequestParser ()
create_post_parser.add_argument ('title')
create_post_parser.add_argument ('text')
create_post_parser.add_argument ('author')

update_post_parser = reqparse.RequestParser ()
update_post_parser.add_argument ('title')
update_post_parser.add_argument ('text')
update_post_parser.add_argument ('author')

create_comment_parser = reqparse.RequestParser ()
create_comment_parser.add_argument ('text')
create_comment_parser.add_argument ('author')

update_comment_parser = reqparse.RequestParser ()
update_comment_parser.add_argument ('text')
update_comment_parser.add_argument ('author')

post_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "text": fields.String,
    "url":fields.String,
    "date_created": fields.DateTime,
    "author": fields.Integer,
    "like":fields.Integer,
    "username":fields.String,
    "likeButtonClass":fields.String,
    "view":fields.String
}
comment_fields = {
    "id": fields.Integer,
    "text": fields.String,
    "date_created": fields.DateTime,
    "author": fields.Integer,
    "username":fields.String
}
user_fields = {
    "username": fields.String,
    "url":fields.String,
}

class CommentResource(Resource):
    @jwt_required()
    @marshal_with(comment_fields)
    def get(self, post_id):
        current_user_id = get_jwt_identity()
        cache_key = f"{request.url}{current_user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            app.logger.info(f"Cache hit for request {request.path}")
            return cached_data
        else:
            comments = Comment.query.filter_by(post_id=post_id).all()
            for comment in comments:
                user= User.query.filter_by(id=comment.author).first()
                comment.username=user.username
            if comments:
                cache.set(cache_key, comments, timeout=300)
                app.logger.info(f"Cache miss for request {request.path}")
                return comments
                
    @jwt_required()
    @marshal_with(comment_fields)
    def post(self):
        args = create_post_parser.parse_args()
        text = args.get("text", None)
        author = args.get("author", None)
        author_exists = User.query.filter_by(id=author).first()
        if not text:
            raise BusinessValidationError(status_code=400, error_codes="BE2002",error_messages="Description is required")
        elif not author:
            raise BusinessValidationError(status_code=400, error_codes="BE2003",error_messages="User Id is required")
        elif not author_exists:
            raise BusinessValidationError(status_code=400, error_codes="BE2004",error_messages="Author does not exists")
        else:
            comment=Comment(text=text,author=author)
            db.session.add(comment)
            db.session.commit()
            return comment, 201
        
    @marshal_with(comment_fields)
    @jwt_required()
    def put(self, comment_id):
        comment = Comment.query.filter_by(id=comment_id).first()
        if not comment:
            raise BusinessValidationError(status_code=400, error_codes="BE2005",error_messages="Post does not exist")
        else:
            args = update_comment_parser.parse_args()
            text = args.get("text", None)
            author = args.get("author", None)
            author_exists = User.query.filter_by(id=author).first()
            if not text:
                raise BusinessValidationError(status_code=400, error_codes="BE2002",error_messages="Description is required")
            elif not author:
                raise BusinessValidationError(status_code=400, error_codes="BE2003",error_messages="User Id is required")
            elif not author_exists:
                raise BusinessValidationError(status_code=400, error_codes="BE2004",error_messages="Author does not exists")
            else:
                ex=update(Comment).where(Comment.id==comment_id).values(text=text,author=author)
                db.session.execute(ex)
                db.session.commit()
                return comment
    @jwt_required()
    def delete(self, comment_id):
        comment = Comment.query.filter_by(id=comment_id).first()
        if comment:
            db.session.delete(comment)
            db.session.commit()
            return {'success':'Comment Deleted'}, 201
        else:
            raise BusinessValidationError(status_code=400, error_codes="BE2005",error_messages="Post does not exist")

class PostResource(Resource):
    @jwt_required()
    @marshal_with(post_fields)
    def get(self, post_id):
            current_user_id = get_jwt_identity()
            cache_key = f"{request.url}{current_user_id}"
            cached_data = cache.get(cache_key)
            if cached_data:
                app.logger.info(f"Cache hit for request {request.path}")
                return cached_data
            else:
                post = Post.query.filter_by(id=post_id).first()
                post.like = len(post.likes)
                l=[]
                for like in post.likes:
                    l.append(like.author)
                    post.liked=l
                user= User.query.filter_by(id=post.author).first()
                post.username=user.username
                if post.likes:
                    if current_user_id in post.liked:
                        post.likeButtonClass='fas fa-thumbs-up'
                    else:
                        post.likeButtonClass='far fa-thumbs-up'
                else:
                    post.likeButtonClass='far fa-thumbs-up'
                if post.author!=current_user_id:
                    view = View(post_id=post.id,author=current_user_id)
                    db.session.add(view)
                    db.session.commit()
                post.view = len(post.views)
                if post:
                    cache.set(cache_key, post, timeout=300)
                    app.logger.info(f"Cache miss for request {request.path}")
                    return post
                else:
                    raise BusinessValidationError(status_code=400, error_codes="BE2005",error_messages="Post does not exist")
    @jwt_required()
    @marshal_with(post_fields)
    def post(self):
        args = create_post_parser.parse_args()
        title = args.get("title", None)
        text = args.get("text", None)
        author = args.get("author", None)
        author_exists = User.query.filter_by(id=author).first()
        if not title:
            raise BusinessValidationError(status_code=400, error_codes="BE2001",error_messages="title is required")
        elif not text:
            raise BusinessValidationError(status_code=400, error_codes="BE2002",error_messages="Description is required")
        elif not author:
            raise BusinessValidationError(status_code=400, error_codes="BE2003",error_messages="User Id is required")
        elif not author_exists:
            raise BusinessValidationError(status_code=400, error_codes="BE2004",error_messages="Author does not exists")
        else:
            post=Post(title=title,text=text,author=author)
            db.session.add(post)
            db.session.commit()
            return post, 201
    @marshal_with(post_fields)
    @jwt_required()
    def put(self, post_id):
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            raise BusinessValidationError(status_code=400, error_codes="BE2005",error_messages="Post does not exist")
        else:
            args = update_post_parser.parse_args()
            title = args.get("title", None)
            text = args.get("text", None)
            author = args.get("author", None)
            author_exists = User.query.filter_by(id=author).first()
            if not title:
                raise BusinessValidationError(status_code=400, error_codes="BE2001",error_messages="title is required")
            if not text:
                raise BusinessValidationError(status_code=400, error_codes="BE2002",error_messages="Description is required")
            if not author:
                raise BusinessValidationError(status_code=400, error_codes="BE2003",error_messages="User Id is required")
            if not author_exists:
                raise BusinessValidationError(status_code=400, error_codes="BE2004",error_messages="Author does not exists")
            else:
                ex=update(Post).where(Post.id==post_id).values(title=title,text=text,author=author)
                db.session.execute(ex)
                db.session.commit()
                return post
    @jwt_required()
    def delete(self, post_id):
        post = Post.query.filter_by(id=post_id).first()
        if post:
            delete_c = Comment.__table__.delete().where(Comment.post_id == post.id)
            delete_l= Like.__table__.delete().where(Like.post_id == post.id)
            delete_v= View.__table__.delete().where(View.post_id == post.id)
            db.session.execute(delete_c)
            db.session.execute(delete_l)
            db.session.execute(delete_v)
            db.session.delete(post)
            db.session.commit()
            return {'success':'Post Deleted'}, 201
        else:
            raise BusinessValidationError(status_code=400, error_codes="BE2005",error_messages="Post does not exist")

class FeedResource(Resource):
    @jwt_required()
    @marshal_with(post_fields)
    def get(self):
        current_user_id = get_jwt_identity()
        cache_key = f"{request.url}{current_user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            app.logger.info(f"Cache hit for request {request.path}")
            return cached_data
        else:
            user = User.query.filter_by(id=current_user_id).first()
            if user:
                posts = []
                sorted_posts = []
                postss = user.posts
                for post in postss:
                    post.like = len(post.likes)
                    l = []
                    for like in post.likes:
                        l.append(like.author)
                    post.liked = l
                    user = User.query.filter_by(id=post.author).first()
                    post.username = user.username
                    sorted_posts.append((post.id, post))
                    sorted_posts = sorted(sorted_posts, reverse=True)
                    posts = [post[1] for post in sorted_posts]
                follows = Follow.query.filter_by(user_id=user.id).all()
                if follows:
                    for follow in follows:
                        user = User.query.filter_by(id=follow.followed_user_id).first()
                        postss = user.posts
                        for post in postss:
                            post.like = len(post.likes)
                            l=[]
                            for like in post.likes:
                                l.append(like.author)
                                post.liked=l
                            user= User.query.filter_by(id=post.author).first()
                            post.username=user.username
                            sorted_posts.append((post.id, post))
                            sorted_posts = sorted(sorted_posts, reverse=True)
                            posts = [post[1] for post in sorted_posts]
                if posts:
                    cache.set(cache_key, posts, timeout=300)
                    app.logger.info(f"Cache miss for request {request.path}")
                    return posts
        
class UserPostResource(Resource):
    @jwt_required()
    @marshal_with(post_fields)
    def get(self,username):
        current_user_id = get_jwt_identity()
        cache_key = f"{request.url}{current_user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            app.logger.info(f"Cache hit for request {request.path}")
            return cached_data
        else:
            user= User.query.filter_by(username=username).first()
            if user:
                posts = []
                sorted_posts = []
                postss = user.posts
                for post in postss:
                    post.like = len(post.likes)
                    l=[]
                    for like in post.likes:
                        l.append(like.author)
                        post.liked=l
                    user= User.query.filter_by(id=post.author).first()
                    post.username=user.username
                    sorted_posts.append((post.id, post))
                    sorted_posts = sorted(sorted_posts, reverse=True)
                    posts = [post[1] for post in sorted_posts]
                if posts:
                    cache.set(cache_key, posts, timeout=300)
                    app.logger.info(f"Cache miss for request {request.path}")
                    return posts
                else:
                    raise BusinessValidationError(status_code=400, error_codes="BE2001",error_messages="You need to follow more users")
            else:
                raise BusinessValidationError(status_code=400, error_codes="BE1007",error_messages="User does not exist")

class UserResources(Resource):
    @jwt_required()
    @marshal_with(user_fields)
    def get(self):
        current_user_id = get_jwt_identity()
        cache_key = f"{request.url}{current_user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            app.logger.info(f"Cache hit for request {request.path}")
            return cached_data
        else:
            user = User.query.filter_by(id=current_user_id).first()
            if user:
                cache.set(cache_key, user, timeout=300)
                app.logger.info(f"Cache miss for request {request.path}")
                return user, 200
            else:
                return {'message': 'User not found'}, 404

    @marshal_with(user_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)
        password = args.get("password", None)
        if not username:
            raise BusinessValidationError(status_code=400, error_codes="BE1001",error_messages="Username is required")
        if not password:
            raise BusinessValidationError(status_code=400, error_codes="BE1002",error_messages="Password is required")
        if not email:
            raise BusinessValidationError(status_code=400, error_codes="BE1003",error_messages="Email is required")
        if "@" not in email:
            raise BusinessValidationError(status_code=400, error_codes="BE1004",error_messages="invalid email")   
        usern = User.query.filter_by(username=request.json['username']).first()
        usere = User.query.filter_by(email=request.json['email']).first()
        if usere or usern:
            if usern:
                    raise BusinessValidationError(status_code=400, error_codes="BE1005",error_messages="Duplicate username") 
            else:
                raise BusinessValidationError(status_code=400, error_codes="BE1006",error_messages="Duplicate email") 
        user=User(username=username,email=email,password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return user, 201
    @jwt_required()
    @marshal_with(user_fields)
    def put(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise BusinessValidationError(status_code=400, error_codes="BE1007",error_messages="User does not exist")
        else:
            args = update_user_parser.parse_args()
            new_username = args.get("new_username", None)
            new_email = args.get("new_email", None)
            password = args.get("password", None)
            if not new_username:
                raise BusinessValidationError(status_code=400, error_codes="BE1001",error_messages="Username is required")
            if not password:
                raise BusinessValidationError(status_code=400, error_codes="BE1002",error_messages="Password is required")
            if not new_email:
                raise BusinessValidationError(status_code=400, error_codes="BE1003",error_messages="Email is required")
            if "@" not in new_email:
                raise BusinessValidationError(status_code=400, error_codes="BE1004",error_messages="invalid email")   
            useree = User.query.filter_by(email=user.email).first()
            usernn = User.query.filter_by(username=user.username).first()
            usern = User.query.filter_by(username=request.form.get("username")).all()
            usere = User.query.filter_by(email=request.form.get("email")).all()
            if useree in usere:
                    usere.remove(useree)
            if usernn in usern:
                    usern.remove(usernn)
            if usere:
                raise BusinessValidationError(status_code=400, error_codes="BE1005",error_messages="Duplicate username") 
            elif usern:
                raise BusinessValidationError(status_code=400, error_codes="BE1006",error_messages="Duplicate email")
            else:
                ex=update(User).where(User.id==user.id).values(username=new_username,email=new_email,password=generate_password_hash(password, method='sha256'))
                db.session.execute(ex)
                db.session.commit()
                return user
    @jwt_required()
    def delete(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise BusinessValidationError(status_code=400, error_codes="BE1007",error_messages="User does not exist")
        else:
            if user.posts:
                for post in user.posts:
                    delete_pv= View.__table__.delete().where(View.post_id == post.id)
                    db.session.execute(delete_pv)
                    db.session.commit()
            delete_p = Post.__table__.delete().where(Post.author == user.id)
            delete_p = Post.__table__.delete().where(Post.author == user.id)
            delete_c = Comment.__table__.delete().where(Comment.author == user.id)
            delete_l= Like.__table__.delete().where(Like.author == user.id)
            delete_fs= Follow.__table__.delete().where(Follow.user_id == user.id)
            delete_fd= Follow.__table__.delete().where(Follow.followed_user_id == user.id)
            delete_v= View.__table__.delete().where(View.author == user.id)
            db.session.execute(delete_p)
            db.session.execute(delete_c)
            db.session.execute(delete_l)
            db.session.execute(delete_v)
            db.session.execute(delete_fs)
            db.session.execute(delete_fd)
            db.session.delete(user)
            db.session.commit()
            return {'success':'User Deleted'}, 201

api.add_resource(UserResources,'/api/user', '/api/user/<string:username>')
api.add_resource(PostResource,'/api/post', '/api/post/<int:post_id>')
api.add_resource(FeedResource, '/api/posts')
api.add_resource(CommentResource, '/api/comment/<int:post_id>', '/api/comment/<int:comment_id>', '/api/comment')
api.add_resource(UserPostResource,'/api/posts/<string:username>')



from celery.schedules import crontab
from flask import make_response

@celery.task()
def create_posts_from_csv(current_user_id, csv_file_path):
    import csv
    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            post_data = dict(zip(fields, row))
            post = Post(author=current_user_id, **post_data)
            db.session.add(post)
        db.session.commit()
    return 'Posts created from CSV'

@app.route('/create-posts-from-csv', methods=['POST'])
@jwt_required()
def create_posts_from_csv_route():
    current_user_id = get_jwt_identity()
    csv_file = request.files['csv_file']
    filename = secure_filename(csv_file.filename)
    csv_file_path = path.join(paath, filename)
    csv_file.save(csv_file_path)
    create_posts_from_csv.delay(current_user_id, csv_file_path)
    return 'Task triggered'


@celery.task()
def celery_export_data(current_user_id):
    import csv
    time.sleep(3)
    fields = ['id', 'title', 'description', 'comments', 'likes', 'views', 'url']
    posts = Post.query.filter_by(author=current_user_id).all()
    # data rows of csv file
    rows = [[post.id, post.title, post.text, post.comments, len(post.likes), len(post.views), post.url] for post in posts]
    filename = path.join(app.root_path, 'static', 'data.csv')
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(fields)
        
        # writing the data rows
        csvwriter.writerows(rows)
    return 'job started'

@celery.task()
def celery_import_data(current_user_id):
    import csv
    time.sleep(3)
    fields = ['title', 'text']
    posts = Post.query.filter_by(author=current_user_id).all()
    # data rows of csv file
    rows = [[post.title, post.text] for post in posts]
    filename = path.join(app.root_path, 'static', 'data.csv')
    
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(fields)
        
        # writing the data rows
        csvwriter.writerows(rows)
    return 'job started'
@app.route('/import-demo-csv')
@jwt_required()
def import_demo_csv():
    current_user_id = get_jwt_identity()
    task = celery_import_data.apply_async((current_user_id,))
    while True:
        if task.state == 'PENDING':
            time.sleep(1)  # Wait 1 second before checking again
        elif task.state == 'SUCCESS':
            # task completed successfull
            return {
        "Task_ID": task.id,
        "Task_State": task.state,
        "Task_Result": task.result
        }
        else:
            # task failed or was revoked
            return "task failed"

@app.route('/celery-job')
@jwt_required()
def celery_job():
    current_user_id = get_jwt_identity()
    task = celery_export_data.apply_async((current_user_id,))
    while True:
        if task.state == 'PENDING':
            time.sleep(1)  # Wait 1 second before checking again
        elif task.state == 'SUCCESS':
            # task completed successfull
            return {
        "Task_ID": task.id,
        "Task_State": task.state,
        "Task_Result": task.result
        }
        else:
            # task failed or was revoked
            return "task failed"

@app.route("/download-file")
def download_file():
    filename = path.join(app.static_folder, 'data.csv')
    return send_file(filename, as_attachment=True)

def get_user_comments(user_id,start_date, end_date):
    comments = db.session.query(Comment).filter(
        Comment.author == user_id,
        Comment.date_created >= start_date,
        Comment.date_created <= end_date
    ).all()
    if comments:
        return comments
    else:
        return None

def get_user_liked_blogs(user_id,start_date, end_date):
    liked_blogs = db.session.query(Like).filter(
        Like.author == user_id,
        Like.date_created >= start_date,
        Like.date_created <= end_date
    ).all()
    if liked_blogs:
        likes=len(liked_blogs)
        return likes
    else:
        return None

def get_user_created_blogs(user_id,start_date, end_date):
    created_blogs = db.session.query(Post).filter(
        Post.author == user_id,
        Post.date_created >= start_date,
        Post.date_created <= end_date
    ).all()
    if created_blogs:
        return created_blogs
    else:
        return None

def generate_report_data(user_id):
    end_date = current_time_ist
    start_date = end_date.replace(day=1)
    user = User.query.filter_by(id=user_id).first()
    username=user.username
    comments = get_user_comments(user_id, start_date, end_date)
    likes = get_user_liked_blogs(user_id, start_date, end_date)
    created_blogs = get_user_created_blogs(user_id, start_date, end_date)
    return {
        'comments': comments,
        'likes': likes,
        'created_blogs': created_blogs,
        'username':username
    }

@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.format == 'pdf':
                sender.add_periodic_task(
                    crontab(minute=user.monthly_minute, hour=user.monthly_hour, day_of_month=1),
                    send_monthly_report_pdf.s(user.email),
                )
            else:
                sender.add_periodic_task(
                    crontab(minute=user.monthly_minute, hour=user.monthly_hour, day_of_month=1),
                    send_monthly_report_html.s(user.email),
                )

@celery.task
def send_monthly_report_html(user_email):
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if user:
            user_id = user.id
            template_path=path.join(app.root_path, 'templates', 'monthly_report.html')
            with open(template_path) as file :
                template = Template(file.read())
                report_data = generate_report_data(user_id)
                message = template.render(data=report_data)
            send_email (user.email, subject="Monthly Report", message=message)

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
app.config.update(
    MAIL_SERVER='localhost',
    MAIL_PORT=1025,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='dhruvtestemail01@gmail.com',
    MAIL_PASSWORD=''
)

@celery.task
def send_monthly_report_pdf(user_email):
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if user:
            posts = Post.query.filter_by(author=user.id).all()
            pdf = FPDF()
            pdf.set_font('Arial', 'B', 16)
            if posts:
                for post in posts:
                    pdf.add_page()
                    pdf.cell(0, 10, f'Id: {post.id}')
                    pdf.ln()
                    pdf.cell(0, 10, f'Title: {post.title}')
                    pdf.ln()
                    pdf.cell(0, 10, f'Text: {post.text}')
                    pdf.ln()
                    if post.url:
                        pdf.image(f'website/{post.url}', w=100)
                        pdf.ln()
                    pdf.cell(0, 10, f'Likes: {len(post.likes)}')
                    pdf.ln()
                    if post.comments:
                        for comment in post.comments:
                            pdf.cell(0, 10, f'Comment: {comment.text}')
                            pdf.ln()
                    else:
                        pdf.cell(0, 10, 'No comments found', 0, 1)
                    pdf.cell(0, 10, f'views: {len(post.views)}')
                    pdf.ln()
            else:
                pdf.add_page()
                pdf.cell(0, 10, 'No posts found')
                pdf.ln()

            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = app.config['MAIL_USERNAME']
            msg['To'] = COMMASPACE.join([user.email])
            msg['Subject'] = "Your blog engagement report"
            msg.attach(MIMEText("Please find your blog engagement report attached."))

            # Attach the PDF file to the email message
            part = MIMEBase('application', "octet-stream")
            part.set_payload(pdf.output(dest='S').encode('latin1'))
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename="blog_engagement.pdf")
            msg.attach(part)
            SMTP_SERVER_HOST = "localhost"
            SMTP_SERVER_PORT = 1025
            # Send the email using SMTP
            smtp = smtplib.SMTP(SMTP_SERVER_HOST, SMTP_SERVER_PORT)
            smtp.login(SENDER_ADDRESS, SENDER_PASSWORD)
            smtp.sendmail(app.config['MAIL_USERNAME'], [user.email], msg.as_string())
            smtp.close()

@app.route('/send-report')
@jwt_required()
def trigger_send_report():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    send_monthly_report_html.apply_async((user.email,))
    return 'Monthly report email task triggered!'

@app.route('/set-month-time',  methods=['GET', 'POST'])
@jwt_required()
def set_monthly_time():
    current_user_id = get_jwt_identity()
    monthly_minute= request.args.get('minute')
    monthly_hour = request.args.get('hour')
    user = User.query.filter_by(id=current_user_id).first()
    if user:
        ex = update(User.__table__).where(User.id==current_user_id).values(monthly_minute=monthly_minute,monthly_hour=monthly_hour)
        db.session.execute(ex)
        db.session.commit()
        return "Time frame set"    
    else:
        return "you need to login in"    

@app.route('/set-daily-time',  methods=['GET', 'POST'])
@jwt_required()
def set_daily_time():
    current_user_id = get_jwt_identity()
    daily_minute= request.args.get('minute')
    daily_hour = request.args.get('hour')
    user = User.query.filter_by(id=current_user_id).first()
    if user:
        ex = update(User.__table__).where(User.id==current_user_id).values(daily_minute=daily_minute,daily_hour=daily_hour)
        db.session.execute(ex)
        db.session.commit()
        return "Time frame set"    
    else:
        return "you need to login in" 

@app.route('/set-monthly-format',  methods=['GET', 'POST'])
@jwt_required()
def set_monthly_format():
    current_user_id = get_jwt_identity()
    Format= request.args.get('selectedFormat')
    user = User.query.filter_by(id=current_user_id).first()
    if user:
        ex = update(User.__table__).where(User.id==current_user_id).values(url=Format)
        db.session.execute(ex)
        db.session.commit()
        return "Time frame set"    
    else:
        return "you need to login in" 
    
def check_user_viewed_blog(user_id,start_date, end_date):
    viewed_blogs = db.session.query(View).filter(
        View.author == user_id,
        View.date_created >= start_date,
        View.date_created <= end_date
    ).all()
    if viewed_blogs:
        return True
    else:
        return False

def check_user_created_blog(user_id,start_date, end_date):
    created_blogs = db.session.query(Post).filter(
        Post.author == user_id,
        Post.date_created >= start_date,
        Post.date_created <= end_date
    ).all()
    if created_blogs:
        return True
    else:
        return False
    
def user_activity(user_id):
    end_date = current_time_ist
    start_date = current_time_ist - timedelta(days=1)
    user_id=user_id
    viewed_blogs = check_user_viewed_blog(user_id, start_date, end_date)
    created_blogs = check_user_created_blog(user_id, start_date, end_date)
    if viewed_blogs or created_blogs:
        return True
    else:
        return False

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"Adding periodic task for user {user.email}")
            sender.add_periodic_task(
                crontab(minute=user.daily_minute, hour=user.daily_hour),
                check_user_activity.s(user.email),
            )

@celery.task
def check_user_activity(user_email):
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if user:
            user_id = user.id
            template_path=path.join(app.root_path, 'templates', 'daily_reminder.html')
            report_data = user_activity(user_id)
            if not report_data:
                with open(template_path) as file :
                    template = Template(file.read())
                    message = template.render()
                    send_email (user.email, subject="Daily Reminder", message=message)
            else:
                pass
@app.route('/daily-reminder')
@jwt_required()
def trigger_daily_reminder():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    check_user_activity.apply_async((user.email,))
    return 'daily reminder email task triggered!'


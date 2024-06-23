from flask import Flask, request, session, url_for
from scripts.index import index
from scripts.register import register, verify
from scripts.login import login
from scripts.search import fresh, top, posts_by_user
from scripts.upload import upload
from scripts.vote import upvote, downvote
import os

app = Flask(__name__)
app.secret_key = os.environ['SESSION_KEY']

@app.route("/", methods=['GET'])
def index_endpoint():
    return index()

@app.route("/login", methods=['POST'])
def login_endpoint():
    return login(request.headers.get('Authorization'), app=app)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return 'Logged out', 200

@app.route("/register", methods=['POST'])
def register_endpoint():
    return register(request.json['username'], request.json['password'], request.json['email'], app=app)

@app.route("/verify/<uuid>", methods=['GET'])
def verify_endpoint(uuid):
    return verify(uuid, app)

@app.route("/<page>", methods=['GET'])
def fresh_endpoint(page):
    return fresh(page, app=app)

@app.route("/top/<page>", methods=['GET'])
def top_endpoint(page):
    return top(page, app=app)

@app.route("/users/<page>", methods=['GET'])
def users_endpoint(page):
    return posts_by_user(request.args.get('name', ''), page, app=app)

@app.route("/upload", methods=['POST'])
def upload_endpoint():
    if 'username' in session:
        return upload(request.files['image'], request.form['title'], request.form['tags'], session['username'], app=app)
    else:
        return 'Login required', 401

@app.route("/upvote/<postID>", methods=['POST'])
def upvote_endpoint(postID):
    if 'username' in session:
        return upvote(postID, session['username'], app=app)
    else:
        return 'Login required', 401

@app.route("/downvote/<postID>", methods=['POST'])
def downvote_endpoint(postID):
    if 'username' in session:
        return downvote(postID, session['username'], app=app)
    else:
        return 'Login required', 401

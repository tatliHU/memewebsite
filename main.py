from flask import Flask, request, url_for
from scripts.index import index
from scripts.register import register
from scripts.login import login
from scripts.search import fresh, top, posts_by_user
from scripts.upload import upload
from scripts.vote import upvote, downvote

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index_endpoint():
    return index()

@app.route("/login", methods=['POST'])
def login_endpoint():
    return login(request.headers.get('Authorization'), app=app)

@app.route("/register", methods=['POST'])
def register_endpoint():
    return register(request.json['username'], request.json['password'], app=app)

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
    return upload(request.files['image'], request.form['title'], request.form['tags'], request.form['username'], app=app)

@app.route("/upvote/<postID>", methods=['POST'])
def upvote_endpoint(postID):
    return upvote(postID, request.json['username'], app=app)

@app.route("/downvote/<postID>", methods=['POST'])
def downvote_endpoint(postID):
    return downvote(postID, request.json['username'], app=app)

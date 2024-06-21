from flask import Flask, request, url_for
from scripts.index import index
from scripts.register import register
from scripts.login import login
from scripts.search import search
from scripts.upload import upload

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
    return search('Published', page, app=app)

@app.route("/upload", methods=['POST'])
def upload_endpoint():
    return upload(request.files['image'], request.form['title'], request.form['tags'], request.form['username'], app=app)

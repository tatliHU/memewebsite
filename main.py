from flask import Flask, request, send_from_directory, session, render_template, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scripts.register import register, verify
from scripts.login import login
from scripts.change_password import change_password
from scripts.search import fresh, top, posts_by_user
from scripts.upload import upload
from scripts.vote import upvote, downvote
import os

app = Flask(__name__)
app.secret_key = os.environ['SESSION_KEY']
limiter = Limiter(get_remote_address, app=app, strategy="moving-window",
                  default_limits=["100 per minute", "5 per second"])

@app.route("/")
def index():
    return redirect("/fresh")

@app.route("/fresh", methods=['GET'])
def fresh_endpoint():
    return render_template('index.html', func="fresh", page=1)

@app.route("/top", methods=['GET'])
def top_endpoint():
    return render_template('index.html', func="top", page=1)

@app.route("/upload", methods=['GET'])
def upload_endpoint():
    return render_template('upload.html')

@app.route("/debug", methods=['GET'])
def debug_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'debug.html')

# static files
@app.route("/favicon.ico", methods=['GET'])
def favicon_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/script.js", methods=['GET'])
def js_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'script.js')

@app.route("/style.css", methods=['GET'])
def css_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'style.css')

@app.route("/robots.txt", methods=['GET'])
def robots_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

# api
@app.route("/api/login", methods=['POST'])
@limiter.limit("10 per minute")
def login_api_endpoint():
    return login(request.headers.get('Authorization'), app=app)

@app.route('/api/logout')
def logout_api_endpoint():
    session.pop('username', None)
    return 'Logged out', 200

@app.route("/api/register", methods=['POST'])
@limiter.limit("3 per minute")
def register_api_endpoint():
    return register(request.json['username'], request.json['password'], request.json['email'], app=app)

@app.route("/api/change_password", methods=['POST'])
@limiter.limit("3 per minute")
def change_password_api_endpoint():
    if 'username' in session:
        app.logger.debug(request.json)
        return change_password(session['username'], request.json['password'], app=app)
    else:
        return 'Login required', 401

@app.route("/api/verify/<uuid>", methods=['GET'])
def verify_api_endpoint(uuid):
    return verify(uuid, app)

@app.route("/api/fresh/<page>", methods=['GET'])
def fresh_api_endpoint(page):
    return fresh(page, app=app)

@app.route("/api/top/<page>", methods=['GET'])
def top_api_endpoint(page):
    return top(page, app=app)

@app.route("/api/users/<page>", methods=['GET'])
def users_api_endpoint(page):
    return posts_by_user(request.args.get('name', ''), page, app=app)

@app.route("/api/upload", methods=['POST'])
@limiter.limit("3 per minute")
def upload_api_endpoint():
    if 'username' in session:
        return upload(request.files['image'], request.form['title'], request.form['tags'], session['username'], app=app)
    else:
        return 'Login required', 401

@app.route("/api/vote", methods=['POST'])
def vote_api_endpoint():
    #session['username'] = 'atka' left here for testing until UI login implemented
    if 'username' in session:
        if int(request.json['delta']) == 1:
            return upvote(request.json['postID'], session['username'], app=app)
        elif int(request.json['delta']) == -1:
            return downvote(request.json['postID'], session['username'], app=app)
        else:
            return 'Invalid vote', 400
    else:
        return 'Login required', 401

from flask import Flask, request, send_from_directory, session, render_template, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scripts.register import register, verify
from scripts.login import login
from scripts.change_password import change_password
from scripts.search import fresh, top, trash, random, posts_by_user, posts_by_title, approve
from scripts.upload import upload
from scripts.vote import upvote, downvote
from scripts.approve import accept, deny
import os

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_KEY', 'QXEs3ZChrduSxkHT48WweK')
app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024
limiter = Limiter(get_remote_address, app=app, strategy="moving-window",
                  default_limits=["100 per minute", "5 per second"])

app.config['AWS_REGION']    = os.getenv('AWS_REGION', 'eu-north-1')
app.config['S3_BUCKET']     = os.getenv('S3_BUCKET', 'bmeme-images')
app.config['SENDER_EMAIL']  = os.getenv('SENDER_EMAIL', 'sender@example.com')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST', 'localhost')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT', '5432')
app.config['POSTGRES_DB']   = os.getenv('POSTGRES_DB', 'meme')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER', 'atka')
app.config['POSTGRES_PASS'] = os.getenv('POSTGRES_PASS', 'atka')
app.config['WEBSITE_URL']   = os.getenv('WEBSITE_URL', 'http://localhost:5000')
app.confog['DEBUG']         = os.getenv('DEBUG', False)

@app.route("/")
def index():
    return redirect("/fresh")

@app.route("/fresh", methods=['GET'])
def fresh_endpoint():
    return render_template('index.html', func="fresh", page=request.args.get('page', 1), voteEndpoint="vote")

@app.route("/top", methods=['GET'])
def top_endpoint():
    return render_template('index.html', func="top", page=request.args.get('page', 1), voteEndpoint="vote")

@app.route("/trash", methods=['GET'])
def trash_endpoint():
    return render_template('index.html', func="trash", page=request.args.get('page', 1), voteEndpoint="vote")

@app.route("/random", methods=['GET'])
def random_endpoint():
    return render_template('index.html', func="random", page=request.args.get('page', 1), voteEndpoint="vote")

@app.route("/search", methods=['GET'])
def search_endpoint():
    return render_template(
        'index.html',
        func="search",
        page=request.args.get('page', 1),
        query="title="+request.args.get('title'),
        voteEndpoint="vote"
    )

@app.route("/upload", methods=['GET'])
def upload_endpoint():
    return render_template('upload.html')

@app.route("/debug", methods=['GET'])
def debug_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'debug.html')

@app.route("/admin", methods=['GET'])
def admin_endpoint():
    return render_template('index.html', func="admin", page=request.args.get('page', 1), voteEndpoint="approve")

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

@app.route("/api/fresh", methods=['GET'])
def fresh_api_endpoint():
    return fresh(request.args.get('page', ''), app=app)

@app.route("/api/top", methods=['GET'])
def top_api_endpoint():
    return top(request.args.get('page', ''), app=app)

@app.route("/api/trash", methods=['GET'])
def trash_api_endpoint():
    return trash(request.args.get('page', ''), app=app)

@app.route("/api/random", methods=['GET'])
def random_api_endpoint():
    return random(request.args.get('page', ''), app=app)

@app.route("/api/search", methods=['GET'])
def search_api_endpoint():
    return posts_by_title(request.args.get('title'), request.args.get('page', ''), app=app)

@app.route("/api/users", methods=['GET'])
def users_api_endpoint():
    return posts_by_user(request.args.get('name', ''), request.args.get('page', ''), app=app)

@app.route("/api/upload", methods=['POST'])
@limiter.limit("3 per minute")
def upload_api_endpoint():
    if 'username' in session:
        return upload(request.files['image'], request.form['title'], request.form.getlist('tags[]'), session['username'], app=app)
    else:
        return 'Login required', 401

@app.route("/api/vote", methods=['POST'])
def vote_api_endpoint():
    if 'username' in session:
        if int(request.json['delta']) == 1:
            return upvote(request.json['postID'], session['username'], app=app)
        elif int(request.json['delta']) == -1:
            return downvote(request.json['postID'], session['username'], app=app)
        else:
            return 'Invalid vote', 400
    else:
        return 'Login required', 401

@app.route("/api/admin", methods=['GET'])
def admin_api_endpoint():
    return approve(request.args.get('page', ''), app=app)

@app.route("/api/approve", methods=['POST'])
def approve_api_endpoint():
    if 'username' in session:
        if int(request.json['delta']) == 1:
            return accept(request.json['postID'], session['username'], app=app)
        elif int(request.json['delta']) == -1:
            return deny(request.json['postID'], session['username'], app=app)
        else:
            return 'Invalid vote', 400
    else:
        return 'Login required', 401
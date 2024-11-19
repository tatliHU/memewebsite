from flask import Flask, request, send_from_directory, session, render_template, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scripts.register import register, verify
from scripts.login import login
from scripts.change_password import change_password, forgot_password, reset_password
from scripts.search import fresh, top, trash, random, posts_by_user, posts_by_title, posts_by_tag, posts_by_id, approve
from scripts.upload import upload
from scripts.vote import upvote, downvote
from scripts.approve import accept, deny
from scripts.helpers import is_admin
import os

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_KEY', 'QXEs3ZChrduSxkHT48WweK')
app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024
limiter = Limiter(get_remote_address, app=app, strategy="moving-window",
                  default_limits=["100 per minute", "5 per second"])

app.config['AWS_REGION']    = os.getenv('AWS_REGION', 'eu-north-1')
app.config['S3_BUCKET']     = os.getenv('S3_BUCKET', 'bmeme-images')
app.config['POSTGRES_HOST'] = os.getenv('POSTGRES_HOST', 'localhost')
app.config['POSTGRES_PORT'] = os.getenv('POSTGRES_PORT', '5432')
app.config['POSTGRES_DB']   = os.getenv('POSTGRES_DB', 'meme')
app.config['POSTGRES_USER'] = os.getenv('POSTGRES_USER', 'atka')
app.config['POSTGRES_PASS'] = os.getenv('POSTGRES_PASS', 'atka')
app.config['DOMAIN']        = os.getenv('DOMAIN', 'bme.lol')
app.config['WEBSITE_URL']   = os.getenv('WEBSITE_URL', 'http://localhost:5000')
app.config['DEBUG']         = os.getenv('DEBUG', False)
app.config['NOTIFY_ADMINS'] = os.getenv('NOTIFY_ADMINS', False)

@app.route("/")
def index():
    return redirect("/fresh")

@app.route("/fresh", methods=['GET'])
def fresh_endpoint():
    return render_template(
        'index.html',
        func="fresh",
        page=request.args.get('page', 1),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/top", methods=['GET'])
def top_endpoint():
    return render_template(
        'index.html',
        func="top",
        page=request.args.get('page', 1),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/trash", methods=['GET'])
def trash_endpoint():
    return render_template(
        'index.html',
        func="trash",
        page=request.args.get('page', 1),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/random", methods=['GET'])
def random_endpoint():
    return render_template(
        'index.html',
        func="random",
        page=request.args.get('page', 1),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/search", methods=['GET'])
def search_endpoint():
    return render_template(
        'index.html',
        func="search",
        page=request.args.get('page', 1),
        query="title="+request.args.get('title'),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/user", methods=['GET'])
def user_endpoint():
    return render_template(
        'index.html',
        func="user",
        page=request.args.get('page', 1),
        query="name="+request.args.get('name'),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/tag", methods=['GET'])
def tag_endpoint():
    return render_template(
        'index.html',
        func="tag",
        page=request.args.get('page', 1),
        query="name="+request.args.get('name'),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/post", methods=['GET'])
def post_endpoint():
    return render_template(
        'index.html',
        func="post",
        page=1,
        query="id="+request.args.get('id'),
        voteEndpoint="vote",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/upload", methods=['GET'])
def upload_endpoint():
    return render_template('upload.html', username=session['username'] if 'username' in session else '')

@app.route("/change-password", methods=['GET'])
def change_password_endpoint():
    return render_template('change_password.html', username=session['username'] if 'username' in session else '')

@app.route("/forgot-password", methods=['GET'])
def forgot_password_endpoint():
    return render_template('forgot_password.html', username=session['username'] if 'username' in session else '')

@app.route("/admin", methods=['GET'])
def admin_endpoint():
    if not 'username' in session or not is_admin(session['username'], app):
        return {'message': 'You must be an admin to view this page'}, 403
    return render_template(
        'index.html',
        func="admin",
        page=request.args.get('page', 1),
        voteEndpoint="approve",
        username=session['username'] if 'username' in session else ''
    )

@app.route("/verify/<uuid>", methods=['GET'])
def verify_endpoint(uuid):
    return render_template(
        'message.html',
        message=verify(uuid, app)[0]['message'],
        username=session['username'] if 'username' in session else ''
    )

@app.route("/forgot-password/<uuid>", methods=['GET'])
def reset_password_endpoint(uuid):
    return render_template(
        'message.html',
        message=reset_password(uuid, app)[0]['message'],
        username=session['username'] if 'username' in session else ''
    )

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

@app.route("/gdpr.pdf", methods=['GET'])
def gdpr_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'gdpr.pdf')

@app.route("/profile.png", methods=['GET'])
def profile_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'profile.png')

@app.route("/logo.png", methods=['GET'])
def logo_endpoint():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'logo.png')

# api
@app.route("/api/login", methods=['POST'])
@limiter.limit("10 per minute")
def login_api_endpoint():
    return login(request.headers.get('Authorization'), app=app)

@app.route('/api/logout', methods=['GET', 'POST'])
def logout_api_endpoint():
    session.pop('username', None)
    return redirect("/")

@app.route("/api/register", methods=['POST'])
@limiter.limit("3 per minute")
def register_api_endpoint():
    return register(request.json, app=app)

@app.route("/api/change-password", methods=['POST'])
@limiter.limit("3 per minute")
def change_password_api_endpoint():
    if 'username' in session:
        return change_password(session['username'], request.json['currentPassword'], request.json['newPassword'], app=app)
    else:
        return {'message': 'Login required'}, 401

@app.route("/api/forgot-password", methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password_api_endpoint():
    return forgot_password(request.json['email'], app=app)

@app.route("/api/forgot-password/<uuid>", methods=['GET'])
def reset_password_api_endpoint(uuid):
    return reset_password(uuid, app=app)

@app.route("/api/verify/<uuid>", methods=['GET'])
def verify_api_endpoint(uuid):
    return verify(uuid, app)

@app.route("/api/fresh", methods=['GET'])
def fresh_api_endpoint():
    return fresh(request.args.get('page', ''),
                 username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/top", methods=['GET'])
def top_api_endpoint():
    return top(request.args.get('page', ''),
               username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/trash", methods=['GET'])
def trash_api_endpoint():
    return trash(request.args.get('page', ''),
                 username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/random", methods=['GET'])
def random_api_endpoint():
    return random(request.args.get('page', ''),
                  username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/search", methods=['GET'])
def search_api_endpoint():
    return posts_by_title(request.args.get('title'), request.args.get('page', ''),
                          username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/user", methods=['GET'])
def user_api_endpoint():
    return posts_by_user(request.args.get('name', ''), request.args.get('page', ''),
                         username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/tag", methods=['GET'])
def tag_api_endpoint():
    return posts_by_tag(request.args.get('name', ''), request.args.get('page', ''),
                        username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/post", methods=['GET'])
def post_api_endpoint():
    return posts_by_id(request.args.get('id', ''),
                       username=session['username'] if 'username' in session else '', app=app)

@app.route("/api/upload", methods=['POST'])
@limiter.limit("3 per minute")
def upload_api_endpoint():
    if 'username' in session:
        return upload(request.files['image'], request.form['title'], request.form.getlist('tags[]'), session['username'], app=app)
    else:
        return {'message': 'Login required'}, 401

@app.route("/api/vote", methods=['POST'])
def vote_api_endpoint():
    if 'username' in session:
        if int(request.json['delta']) == 1:
            return upvote(request.json['postID'], session['username'], app=app)
        elif int(request.json['delta']) == -1:
            return downvote(request.json['postID'], session['username'], app=app)
        else:
            return {'message': 'Invalid vote'}, 400
    else:
        return {'message': 'Login required'}, 401

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
            return {'message': 'Invalid vote'}, 400
    else:
        return {'message': 'Login required'}, 401
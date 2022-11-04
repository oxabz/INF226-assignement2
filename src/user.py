import base64
import re
import sys
from urllib.parse import urljoin, urlparse
from app import app, conn
import bcrypt
from apsw import Error
import flask
from flask import abort, redirect, request, render_template, url_for
from werkzeug.datastructures import WWWAuthenticate
from src.forms.signup_form import SignupForm
from src.forms.login_form import LoginForm
from http import HTTPStatus
from base64 import b64decode

import flask_login
from flask_login import login_required, login_user, logout_user

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(flask_login.UserMixin):
    
    username: str = ""
    password: str = ""

    @staticmethod
    def get(username):
        if username is None :
            return None
        c = conn[0].cursor()
        stmt = "SELECT * FROM users WHERE username = ?;"
        try:
            c.execute(stmt, (username,))
            rows = c.fetchall()
            if len(rows) != 1 :
                return None
            user = User()
            user.id = username
            user.username = username
            user.password = str(rows[0][1])
            return user
        except Error as e:
            print(e, file=sys.stderr)
            return None

    @staticmethod
    def new(username, password): 
        # Adding the salt to password
        salt = bcrypt.gensalt()
        # Hashing the password
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        hashed = base64.b64encode(hashed)
        
        c = conn[0].cursor()
        stmt = """
            INSERT INTO users(username, password) VALUES (?, ?);
        """
        c.execute(stmt, (username, hashed.decode("utf-8")))

    @staticmethod
    def check(username, password):
        user = User.get(username)
        if user is None:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), b64decode(user.password))


@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.path.startswith('/api/'):
        return 'Unauthorized', HTTPStatus.UNAUTHORIZED
    return redirect('/login?next=' + request.path)

# This method is called whenever the login manager needs to get
# the User object for a given user id
@login_manager.user_loader
def user_loader(user_id):
    return User.get(user_id)
    

# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@login_manager.request_loader
def request_loader(request):
    # Even though this HTTP header is primarily used for *authentication*
    # rather than *authorization*, it's still called "Authorization".
    auth = request.headers.get('Authorization')

    # If there is not Authorization header, do nothing, and the login
    # manager will deal with it (i.e., by redirecting to a login page)
    if not auth:
        return

    (auth_scheme, auth_params) = auth.split(maxsplit=1)
    auth_scheme = auth_scheme.casefold()
    if auth_scheme == 'basic':  # Basic auth has username:password in base64
        (username,passwd) = b64decode(auth_params.encode(errors='ignore')).decode(errors='ignore').split(':', maxsplit=1)
        if User.check(username,passwd):
            return user_loader(username)
    # If we failed to find a valid Authorized header or valid credentials, fail
    # with "401 Unauthorized" and a list of valid authentication schemes
    # (The presence of the Authorized header probably means we're talking to
    # a program and not a user in a browser, so we should send a proper
    # error message rather than redirect to the login page.)
    # (If an authenticated user doesn't have authorization to view a page,
    # Flask will send a "403 Forbidden" response, so think of
    # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
    abort(HTTPStatus.UNAUTHORIZED, www_authenticate = WWWAuthenticate('Basic realm=inf226, Bearer'))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.check(username,password):
            user = user_loader(username)
            
            # automatically sets logged in session cookie
            login_user(user)

            flask.flash('Logged in successfully.')

            next = flask.request.args.get('next')
    
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return flask.redirect(next or flask.url_for('index_html'))
    return render_template('./login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if re.match("^[a-zA-Z0-9]+$", username) is None:
            form.username.errors.append("Username can only contain letters and numbers")
            print(f'Received form: invalid ')
            return render_template('./signup.html', form=form)
        if User.get(username) is not None:
            form.username.errors.append("Username already taken")
            print(f'Received form: invalid ')
            return render_template('./signup.html', form=form)
        User.new(username,password)
        return redirect(url_for('login'))
    return render_template('./signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index_html'))
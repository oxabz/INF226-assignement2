from app import app
from flask import render_template, send_from_directory, make_response
from flask_login import login_required

@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory(app.root_path, 'static/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(app.root_path, 'static/favicon.png', mimetype='image/png')


@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    return send_from_directory(app.root_path,
                        'static/index.html', mimetype='text/html')


@app.get('/index.js')
def index_js():
    return send_from_directory(app.root_path,
                        'static/index.js', mimetype='text/javascript')

@app.get('/new')
@app.get('/new.html')
def new_html():
    return send_from_directory(app.root_path,
                        'static/new.html', mimetype='text/html')

@app.get('/new.js')
def new_js():
    return send_from_directory(app.root_path,
                        'static/new.js', mimetype='text/javascript')

@app.get('/message.js')
def message_js():
    return send_from_directory(app.root_path,
                        'static/message.js', mimetype='text/javascript')

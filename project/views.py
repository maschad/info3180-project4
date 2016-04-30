import smtplib
import urlparse

import BeautifulSoup
import requests
from flask import request, jsonify, session, g
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.datastructures import MultiDict

from project import app, db
from project.models import User, Item

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

# routes
@app.route('/api/user/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/user/register', methods=['POST'])
def register():
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    if User.query.filter_by(email=email).first() is not None:
        status = 'user already registered'
    else:
        user = User(email=email,name=name)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        status = 'success'
        db.session.close()

    return jsonify({'result':status})


@app.route('/api/user/login', methods=['GET', 'POST'])
def login():
    json_data = request.json
    user = User.query.filter_by(email=json_data['email']).first()
    if user.verify_password(json_data['password']):
        session['logged_in'] = True
        status = True
    else:
        status = False
    toRet = user.__repr__()
    toRet['status'] = status
    toRet['token'] = user.generate_auth_token()
    return jsonify(toRet)


@app.route('/api/user/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in',None)
    return jsonify({'result':'success'})


@app.route('/api/user/<user_id>/wishlist', methods=['POST'])
def add_item(user_id):
    data = MultiDict(mapping=request.json)
    name = data['name']
    description = data['description']
    url = data['url']
    image_url = data['image_url']
    item = Item(name, description, user_id, url, image_url)
    db.session.add(item)
    db.session.commit()
    return jsonify({'name': name, 'description': description, 'url': url})


@app.route('/api/user/<user_id>/wishlist', methods=['GET'])
@auth.login_required
def view(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    items = []
    for item in user.items:
        items.append(item.__repr__())
    return jsonify({'items': items})


@app.route('/api/user/<item_id>/wishlist', methods=['DELETE'])
@auth.login_required
def delete(item_id):
    db.session.query(Item).filter_by(id=item_id).delete()
    db.session.commit()
    return jsonify({'status': True})


@app.route('/api/user/<user_id>/wishlist/<item_id>', methods=['GET'])
@auth.login_required
def view_item(user_id, item_id):
    return jsonify()


@app.route('/api/user/<user_id>/share')
@auth.login_required
def share(user_id):
    data = request.get_json()
    item = data['url']
    title = data['name']
    email = data['email']
    itemUrl = data['url']
    fromaddr = 'chad.nehemiah@gmail.com'
    user = db.session.query(User).filter_by(id=user_id).first()
    subject = 'Please buy this for %s' % (user.name)

    message = """From: {} <{}>
    To: {} <{}>
    Subject: {}

    <a href={}></a>
    """

    messagetosend = message.format(
        user.name,
        fromaddr,
        subject,
        email,
        subject,
        message,
        item,
        title,
        itemUrl)

    username = 'chad.nehemiah@gmail.com'
    password = 'pass'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(username, email, messagetosend)
    server.quit()
    return jsonify({'message': 'Shared'})


@app.route('/api/thumbnail/process', methods=['POST'])
@auth.login_required
def getImage():
    images = []

    json_data = request.get_json()
    url = json_data['url']
    result = requests.get(url).text
    soup = BeautifulSoup.BeautifulSoup(result)
    for img in soup.findAll("img", src=True):
        if not 'gif' in img['src'] and not 'png' in img['src'] and not 'sprite' in img['src']:
            images.append(urlparse.urljoin(url, img["src"]))
    return jsonify({'images': images})

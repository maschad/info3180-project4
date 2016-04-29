import urlparse

import BeautifulSoup
import requests
from flask import request, jsonify, session, g
from flask.ext.httpauth import HTTPBasicAuth

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
@app.route('/api/user/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


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
    return jsonify({'result':status})


@app.route('/api/user/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in',None)
    return jsonify({'result':'success'})


@app.route('/api/user/<user_id>/wishlist', methods=['POST'])
def add_item(user_id):
    data = request.get_json()
    name = data['name']
    description = data['description']
    url = data['url']
    item = Item(name, description, url, user_id)
    db.session.add(item)
    db.session.commit()
    response = jsonify({'name': item.name, 'description': item.description, 'url': url})
    return response


@app.route('/api/user/<user_id>/wishlist', methods=['GET'])
@auth.login_required
def view(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    items = user.items
    result = {'items': items, 'firstname': user.firstname, 'lastname': user.lastname}
    return jsonify(result)


@app.route('/api/thumbnail/process', methods=['POST'])
@auth.login_required
def getImage():
    images = []

    json_data = request.get_json()
    url = json_data['url']
    result = requests.get(url).text
    soup = BeautifulSoup.BeautifulSoup(result)
    for img in soup.findAll("img", src=True):
        if not 'gif' in img.get('src') and not 'png' in img.get('src') and not 'sprite' in img.get('src'):
            images.append(urlparse.urljoin(url, img["src"]))

    print images[0]
    return jsonify({'images': images})

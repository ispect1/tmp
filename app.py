#! /usr/bin/env python
"""Flask Login Example and instagram fallowing find"""
from crypto import generate_hash
from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from instagram import getfollowedby, getname
from datetime import date
from flask import jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            username = getname(request.form['username'])
            return render_template('index.html', data=getfollowedby(username))
        return render_template('index.html')


# @app.route('/api/sync_key', methods=['GET', 'POST'])
# def sync_key():
#     return json.dumps(None)




# @app.route('/api/subscribe')
# def subscribe():
#     data = request.json
#     hash = data['hash']
#     place_uid =
# @app.route('/api/unsubscribe')
# @app.route('/api/checking')
@app.route('/api/get_places', methods=['GET', 'POST'])
def get_places():
    data = request.json
    print(data)
    return jsonify(places)

# @app.route('/api/get_place_info')
# @app.route('/api/get_place_photos')
# @app.route('/api/get_user_places')


@app.route('/api/sign_in', methods=['GET', 'POST'])
def login():
    data = request.json or {}
    try:
        tab_num = register_users[data['tab_num']]['tab_num']
    except KeyError:
        return jsonify({'text': 'Пользователь не зарегистрирован', 'code': -2})

    if data['password'] != register_users[data['password']] and data['tab_num'] != tab_num:
        return jsonify({'text': 'Неправильный табельный/пароль', 'code': -1})
    _hash = generate_hash()
    register_users[tab_num]['hash'] = _hash
    return jsonify({'code': 1, 'text': 'Успешно', 'data': {'access_token': _hash}})


@app.route('/api/sign_up', methods=['GET', 'POST'])
def register():
    data = request.json or {}
    if set(data) != {"tab_num", 'password', 'identifier'}:
        return jsonify({'text': 'Неверный формат данных', 'code': -2})
    elif data['tab_num'] in register_users:
        return jsonify({'text': 'Уже зарегистрирован', 'code': -1})
    elif data['tab_num'] in all_users:
        _hash = generate_hash()
        data['hash'] = generate_hash()
        register_users[data['tab_num']] = data
        return jsonify({'code': 1, 'text': 'Успешно', 'data': {'access_token': _hash}})
    else:
        return jsonify({'text': 'Такого табельного нет в базе', 'code': -3})
    # try:
    #     data = User.query.filter_by(username=name, password=passw).first()
    #     if data is not None:
    #         session['logged_in'] = True
    #         return redirect(url_for('home'))
    #     else:
    #         return 'Dont Login'
    # except:
    #     return "Dont Login"


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """Register Form"""
#     if request.method == 'POST':
#         new_user = User(
#             username=request.form['username'],
#             password=request.form['password'])
#         db.session.add(new_user)
#         db.session.commit()
#         return render_template('login.html')
#     return render_template('register.html')


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    all_users = {"123", "456", "admin"}
    register_users = dict()
    places = [{'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
              "year": 2021, 'city': "Москва", 'free_seats': 1},
              {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
               "year": 2021, 'city': "Сочи", 'free_seats': 30},
              {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
               "year": 2021, 'city': "Москва", 'free_seats': 0},
              {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 1,
               "year": 2021, 'city': "Москва", 'free_seats': 30},
              {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 2,
               "year": 2021, 'city': "Москва", 'free_seats': 30},
              {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 2,
               "year": 2021, 'city': "Москва", 'free_seats': 30}
              ]

    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run(host='0.0.0.0')

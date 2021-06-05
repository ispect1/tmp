#! /usr/bin/env python
"""Flask Login Example and instagram fallowing find"""
from crypto import generate_hash
from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from instagram import getfollowedby, getname
from datetime import date
from flask import jsonify
from datetime import date
from utils import from_base64


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


@app.route('/api/subscribe')
def subscribe():
    data = request.json
    access_token = data['hash']
    place_uid = data['uuid']
    if place_uid not in places:
        return jsonify(code=-1, text='Такого объекта не существует')
    for tab_num, user_data in register_users.items():
        if user_data['accessToken'] != access_token:
            continue
        if place_uid is user_data['places']:
            return jsonify(code=-3, text='Пользователь уже зарегистрирован')
        user_data['places'][place_uid] = places[place_uid]
        user_data['places'][place_uid]['isVisit'] = False
        return jsonify(code=1, text='Успешно')

    return jsonify(code=-2, text='Токен неверный')



@app.route('/api/unsubscribe')
def unsubscribe():
    data = request.json
    access_token = data['hash']
    place_uid = data['uuid']
    if place_uid not in places:
        return jsonify(code=-1, text='Такого объекта не существует')
    for tab_num, user_data in register_users.items():
        if user_data['accessToken'] != access_token:
            continue
        if place_uid not in user_data['places']:
            return jsonify(code=-3, text='Пользователь уже зарегистрирован')
        user_data['places'][place_uid] = places[place_uid]
        user_data['places'][place_uid]['isVisit'] = False
        return jsonify(code=1, text='Успешно')

    return jsonify(code=-2, text='Токен неверный')

@app.route('/api/сheckVisit')
def check_visit():
    data = from_base64(request.json) or {}
    access_token = data['accessToken']

    for tab_num, user_data in register_users.items():
        if access_token != user_data['accessToken']:
            continue
    # for tab_num

    return jsonify(code=-3, text='Invalid token')


@app.route('/api/getCities')
def get_cities():
    return jsonify(code=1, text='Успешно', data=['Москва', 'Казань', 'Санкт-Петербург'])


@app.route('/api/getPlaces', methods=['GET', 'POST'])
def get_places():
    data = from_base64(request.json) or {}
    print(data)
    city = data['city']
    count = data['count']
    page = data['page']
    sorted_places = [place for place in list(places.values()) if place['city'] == city]
    if set(data) == {'city'}:
        sorted_places = [place for place in sorted_places if date(day=place['day'], month=place['month'],
                                                                  year=place['year']) >= date.today()]
    sorted_places = sorted(sorted_places, key=lambda x: (x['day'], x['month'], x['year']))
    if 'day' in data:
        sorted_places = [place for place in sorted_places if place['day'] == data['day']]
    if 'month' in data:
        sorted_places = [place for place in sorted_places if place['month'] == data['month']]
    if 'year' in data:
        sorted_places = [place for place in sorted_places if place['year'] == data['year']]
    return jsonify(code=1, text='Успешно', data=sorted_places[page*count:(page+1)*count])


@app.route('/api/isSignIn', methods=["GET", "POST"])
def is_sign_in():
    data = from_base64(request.json) or {}
    print(data)
    print(register_users)
    for tab_num, user_data in register_users.items():
        if data['accessToken'] == user_data['accessToken']:
            return jsonify({'code': 1, 'text': 'Успешно'})
    return jsonify({'code': -1, 'text': 'Сессия не найдена'})


@app.route('/api/signIn', methods=['GET', 'POST'])
def login():
    data = from_base64(request.json) or {}
    print(data)
    if 'tabNum' not in data or 'password' not in data:
        return jsonify({'text': 'Неверный формат данных', 'code': -2})
    tab_num = data['tabNum']
    if tab_num not in all_users:
        return jsonify({'text': 'Такого табельного нет в базе', 'code': -3})
    if tab_num not in register_users:
        _hash = generate_hash()
        data['accessToken'] = _hash
        data['places'] = {}
        register_users[tab_num] = data
        return jsonify({'code': 1, 'text': 'Успешно', 'data': {'accessToken': _hash}})
    if data['password'] != register_users[tab_num]['password'] and data['tabNum'] != tab_num:
        return jsonify({'text': 'Неправильный табельный/пароль', 'code': -1})
    _hash = generate_hash()
    data['accessToken'] = _hash
    register_users[tab_num] = data
    isAdmin = False if tab_num != 'admin' else True
    return jsonify({'code': 1, 'text': 'Успешно', 'data': {'accessToken': _hash, isAdmin: isAdmin}})


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
    places = {"1": {'uuid': "1", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
                    "year": 2021, 'city': "Москва", 'freeSeats': 1},
              "2": {'uuid': "2", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
                    "year": 2021, 'city': "Москва", 'freeSeats': 30},
              "3": {'uuid': "3", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 12, "month": 1,
                    "year": 2021, 'city': "Москва", 'freeSeats': 0},
              "4": {'uuid': "4", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 1,
                    "year": 2021, 'city': "Москва", 'freeSeats': 30},
              "5": {'uuid': "5", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 2,
                    "year": 2021, 'city': "Казань", 'freeSeats': 30},
              "6": {'uuid': "6", "title": "Дворец спорта", "description": "Заебись. " * 20, "day": 13, "month": 2,
                    "year": 2021, 'city': "Санкт-Петербург", 'freeSeats': 30}
              }

    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run(host='0.0.0.0')

#! /usr/bin/env python
# coding=utf-8
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


@app.route('/api/subscribe', methods=['GET', 'POST'])
def subscribe():
    data = request.json
    access_token = data['accessToken']
    place_uid = data['placeUuid']
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


@app.route('/api/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    data = request.json
    access_token = data['accessToken']
    place_uid = data['placeUuid']
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


@app.route('/api/checkVisit', methods=['GET', 'POST'])
def check_visit():
    data = from_base64(request.json) or {}
    access_token = data['accessToken']
    place_uid = data['placeUuid']

    for tab_num, user_data in register_users.items():
        if access_token != user_data['accessToken']:
            continue

        if place_uid not in user_data['places']:
            return jsonify(code=-2, text='Пользователь не зарегистрирован')

        return jsonify(code=1, text='Успешно')
    return jsonify(code=-1, text='Invalid token')


@app.route('/api/getCities')
def get_cities():
    return jsonify(code=1, text='Успешно', data=['Москва', 'Казань', 'Санкт-Петербург'])


@app.route('/api/getPlaces', methods=['GET', 'POST'])
def get_places():
    data = from_base64(request.json) or {}
    print('getPlace', register_users)
    city = data['city']
    count = data['count']
    page = data['page']
    token = data['accessToken']
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
    sorted_places = sorted_places[page*count:(page+1)*count]
    curr_user_info = None
    for user_info in register_users.values():
        if user_info['accessToken'] == token:
            curr_user_info = user_info
    if curr_user_info is None:
        return jsonify(code=-1, text='Неправильный токен')
    # print('info', curr_user_info)
    for place in sorted_places:
        place['isSubscribe'] = place['placeUuid'] in curr_user_info['places']
    return jsonify(code=1, text='Успешно', data=sorted_places[page*count:(page+1)*count])


@app.route('/api/isSignIn', methods=["GET", "POST"])
def is_sign_in():
    data = from_base64(request.json) or {}
    # print(data)
    # print(register_users)
    for tab_num, user_data in register_users.items():
        if data['accessToken'] == user_data['accessToken']:
            return jsonify({'code': 1, 'text': 'Успешно'})
    return jsonify({'code': -1, 'text': 'Сессия не найдена'})


@app.route('/api/signIn', methods=['GET', 'POST'])
def login():
    data = from_base64(request.json) or {}
    # print(data)
    if 'tabNum' not in data or 'password' not in data:
        return jsonify({'text': 'Неверный формат данных', 'code': -2})
    tab_num = data['tabNum']
    if tab_num not in all_users:
        return jsonify({'text': 'Такого табельного нет в базе', 'code': -3})
    is_admin = False if tab_num != 'admin' else True
    if tab_num not in register_users:
        _hash = generate_hash()
        data['accessToken'] = _hash
        data['places'] = {}
        data['isAdmin'] = is_admin
        register_users[tab_num] = data
        return jsonify({'code': 1, 'text': 'Успешно', 'data': {'accessToken': _hash}})
    if data['password'] != register_users[tab_num]['password'] or data['tabNum'] != tab_num:
        return jsonify({'text': 'Неправильный табельный/пароль', 'code': -1})
    _hash = generate_hash()
    data['accessToken'] = _hash
    data['places'] = {}
    data['isAdmin'] = is_admin
    register_users[tab_num] = data
    print('users', register_users)
    data = {'code': 1, 'text': 'Успешно', 'data': {'accessToken': _hash, 'isAdmin': is_admin}}
    return jsonify(data)


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
    description = """Спорт – это специфический вид интеллектуальной и физической активности, который совершается человеком в соревновательных целях. Главной мотивацией занятия спортом является желание человека улучшить свое физическое здоровье, получить чувство морального удовлетворения.

Благодаря спорту происходит улучшение физико-психологических характеристик. Спорт – это основная и неотъемлемая часть физической культуры. Именно спорт полностью раскрывает и мобилизирует нравственные и психические качества человека."""

    hok_photo = 'https://i.ibb.co/104hLHJ/photo-2021-06-05-20-10-09.jpg'
    foot_photo = 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2100&q=80'
    basket_photo = 'https://image.freepik.com/free-photo/soccer-football-stadium-with-spotlights_163782-3549.jpg'
    plavanie_photo = 'https://image.freepik.com/free-photo/stadium-lights-flashes-football-field_99433-1401.jpg'
    beg_photo = 'https://marathonec.ru/wp-content/uploads/2020/05/cross-country-beg.jpg'

    places = {
        "1": {'placeUuid': "1", "title": "Футбол", "description": description, "day": 6, "month": 6,
              "year": 2021, 'city': "Москва", 'freeSeats': 1, 'photoUrl': foot_photo, 'datetime': '25 июля'},
        "2": {'placeUuid': "2", "title": "Хоккей", "description": description, "day": 6, "month": 6,
              "year": 2021, 'city': "Москва", 'freeSeats': 1, 'photoUrl': hok_photo, 'datetime': '25 июля'},
        "3": {'placeUuid': "3", "title": "Баскетбол", "description": description, "day": 6, "month": 6,
              "year": 2021, 'city': "Москва", 'freeSeats': 30, 'photoUrl': basket_photo, 'datetime': '25 июля'},
        "4": {'placeUuid': "4", "title": "Бег", "description": description, "day": 7, "month": 6,
              "year": 2021, 'city': "Москва", 'freeSeats': 30, 'photoUrl': beg_photo, 'datetime': '25 июля'},
        "5": {'placeUuid': "4", "title": "Плавание", "description": description, "day": 8, "month": 6,
              "year": 2021, 'city': "Москва", 'freeSeats': 30, 'photoUrl': plavanie_photo, 'datetime': '25 июля'},
        "6": {'placeUuid': "5", "title": "Футбол", "description": description, "day": 6, "month": 6,
              "year": 2021, 'city': "Казань", 'freeSeats': 30, 'photoUrl': foot_photo, 'datetime': '25 июля'},
        "7": {'placeUuid': "6", "title": "Хоккей", "description": description, "day": 6, "month": 6,
              "year": 2021, 'city': "Санкт-Петербург", 'freeSeats': 30, 'photoUrl': hok_photo, 'datetime': '25 июля'}
              }

    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run(host='0.0.0.0')

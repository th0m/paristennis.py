#!/usr/bin/env python2

from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from flask import url_for
from pymongo import MongoClient
import uuid

app = Flask(__name__)

@app.route('/api/alerts', methods=['GET'])
def getAlerts():
    key = request.headers.get('key')
    if key is None:
        abort(400)
    return jsonify({'key': key})

@app.route('/api/alerts', methods=['POST'])
def postAlerts():
    key = request.headers.get('key')

    alertName = request.json.get('alertName')
    allArrdts = request.json.get('allArrdts')
    coveredCourt = request.json.get('coveredCourt')
    arrdt1 = request.json.get('arrdt1')
    arrdt2 = request.json.get('arrdt2')
    arrdt3 = request.json.get('arrdt3')
    startHour = request.json.get('startHour')
    endHour = request.json.get('endHour')

    alert = {}

    if key is None or not db.users.find_one({'key': key}):
        abort(400)
    else:
        alert['key'] = key

    if coveredCourt is None:
        abort(400)
    else:
        alert['coveredCourt'] = coveredCourt

    if alertName is None:
        abort(400)
    else:
        alert['alertName'] = alertName

    if allArrdts is None:
        if arrdt1 is None and arrdt2 is None and arrdt3 is None:
            abort(400)
        else:
            alert['arrdt1'] = arrdt1
            alert['arrdt2'] = arrdt2
            alert['arrdt3'] = arrdt3
    else:
        alert['allArrdt'] = True

    if startHour is None or endHour is None:
        abort(400)
    else:
        alert['startHour'] = startHour
        alert['endHour'] = endHour
    
    db.alerts.insert(alert) 
    return jsonify({'alertName': alertName}), 201
    
@app.route('/api/users', methods=['POST'])
def new_user():
    login = request.json.get('login')
    password = request.json.get('password')
    if login is None or password is None:
        abort(400)

    key = str(uuid.uuid4())

    user = {
        'key': key,
        'login': login,
        'password': password
    }
    db.users.insert(user)
    return jsonify({ 'key': key }), 201

@app.route('/api/users', methods=['GET'])
def get_user():
    key = request.headers.get('key')
    if key is None:
        abort(400)
    user = db.users.find_one({'key': key}, {'login': 1, '_id': 0})
    return jsonify(user)

if __name__ == '__main__':
    db = MongoClient().tennis
    app.run(host='0.0.0.0',debug=True)

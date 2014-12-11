#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

@app.route('/api/alerts', methods=['GET']
def getAlerts():
    if id is None:
        abort(400)

@app.route('/api/alerts', methods=['POST']
def postAlerts():
    if id is None:
        abort(400)
    if allArrdt is None and arrdt1 is None and arrdt2 is None and arrdt3 is None:
        abort(400)
    if startHour is None or endHour is None:
        abort(400)
    
@app.route('/api/users', methods=['POST'])
def register():
    login = request.json.get('login')
    password = request.json.get('password')
    if login is None or password is None:
        abort(400)

    return jsonify

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, render_template, request, redirect, url_for
import json
from joblib import load
from flask import Flask,redirect,url_for, request, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
from google.cloud import firestore, storage
import time
from datetime import datetime, timedelta

app = Flask(__name__)

db = 'progettoseul'
db = firestore.Client.from_service_account_json('credentials.json', database=db)
filestorage = storage.Client.from_service_account_json('credentials.json')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dati/<name>', methods=['POST'])
def dati(name):
    data = request.get_json()
    if name == 'station':
        code = data['code']
        namedist = data['namedist']
        address = data['address']
        latitude = data['latitude']
        longitude = data['longitude']
        doc_ref = db.collection('station').document(str(code))
        doc_ref.set({
            'code': code,
            'namedist': namedist,
            'address': address,
            'latitude': latitude,
            'longitude': longitude
        })
    return '', 200


@app.route('/dati/<name>', methods=['GET'])
def get_dati(name):
    if name == 'station':
        stations = []
        docs = db.collection('station').stream()
        for doc in docs:
            stations.append(doc.to_dict())
        return json.dumps(stations), 200
    return '', 404







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
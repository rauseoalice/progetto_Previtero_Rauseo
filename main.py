
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



@app.route('/dati/<dato>',methods=['GET'])
def read(dato):
    entity = db.collection('dati').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        return json.dumps(d['readings']), 200
    else:
        return 'not found', 404



@app.route('/dati/<dato>', methods=['POST'])
def new_data(dato):
    code = request.values['code']
    namedist = request.values['namedist']
    address = request.values['address']
    latitude = request.values['latitude']
    longitude = request.values['longitude']

    entity = db.collection('dati').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        d['readings'].append({'code': code, 'namedist': namedist, 'address': address, 'latitude': latitude, 'longitude': longitude})
        db.collection('dati').document(dato).set(d)
    else:
        db.collection('dati').document(dato).set({'readings':[{'code': code, 'namedist': namedist, 'address': address, 'latitude': latitude, 'longitude': longitude}]})
    return 'ok', 200





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
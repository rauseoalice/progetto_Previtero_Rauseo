
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
    if dato == 'station':
        entity = db.collection('dati').document(dato).get()
        if entity.exists:
            d = entity.to_dict()
            return json.dumps(d['readings']), 200
        else:
            return 'not found', 404
    elif dato == 'item':
        entity = db.collection('dati').document(dato).get()
        if entity.exists:
            d = entity.to_dict()
            return json.dumps(d['readings']), 200
        else:
            return 'not found', 404
    else:
        return 'not found', 404


@app.route('/dati/<dato>', methods=['POST'])
def new_data(dato):
    if dato == 'station':
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
    elif dato == 'item':
        item_code = request.values['item_code']
        item_name = request.values['item_name']
        unit = request.values['unit']
        good = request.values['good']
        normal = request.values['normal']
        bad = request.values['bad']
        very_bad = request.values['very_bad']

        entity = db.collection('dati').document(dato).get()
        if entity.exists:
            d = entity.to_dict()
            d['readings'].append({'item_code': item_code, 'item_name': item_name, 'unit': unit, 'good': good, 'normal': normal, 'bad': bad, 'very_bad': very_bad})
            db.collection('dati').document(dato).set(d)
        else:
            db.collection('dati').document(dato).set({'readings':[{'item_code': item_code, 'item_name': item_name, 'unit': unit, 'good': good, 'normal': normal, 'bad': bad, 'very_bad': very_bad}]})
        return 'ok', 200
    else:
        return 'not found', 404



@app.route('/valori/<dato>', methods=['GET'])
def read_values(dato):
    entity = db.collection('dati').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        return json.dumps(d['readings']), 200
    else:
        return 'not found', 404



@app.route('/valori/<dato>', methods=['POST'])
def new_values(dato):
    data = request.values['data']
    code = request.values['code']
    address = request.values['address']
    latitude = request.values['latitude']
    longitude = request.values['longitude']
    SO2 = request.values['SO2']
    NO2 = request.values['NO2']
    O3 = request.values['O3']
    CO = request.values['CO']
    PM10 = request.values['PM10']
    PM25 = request.values['PM25']

    entity = db.collection('dati').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        d['readings'].append({'data': data, 'code': code, 'address': address, 'latitude': latitude, 'longitude': longitude,
                                  'SO2': SO2, 'NO2': NO2, 'O3': O3, 'CO': CO, 'PM10': PM10, 'PM25': PM25})
        db.collection('dati').document(dato).set(d)
    else:
        db.collection('dati').document(dato).set({'readings':[{'data': data, 'code': code, 'address': address, 
                                                                   'latitude': latitude, 'longitude': longitude,
                                                                   'SO2': SO2, 'NO2': NO2, 'O3': O3, 
                                                                   'CO': CO, 'PM10': PM10, 'PM25': PM25}]})
    return 'ok', 200





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
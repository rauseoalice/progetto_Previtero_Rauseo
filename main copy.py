#DA ELIMINARE ALLA FINE

from flask import Flask, render_template, request, redirect, url_for
import json
from joblib import load
from flask import Flask,redirect,url_for, request, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
from google.cloud import firestore, storage
import time
from datetime import datetime, timedelta
from google.cloud.firestore import SERVER_TIMESTAMP
from datetime import datetime

app = Flask(__name__)

db = 'progettoseul'
db = firestore.Client.from_service_account_json('credentials.json', database=db)
filestorage = storage.Client.from_service_account_json('credentials.json')


@app.route('/')
def index():
    return render_template('index.html')

'''
@app.route('/grafici')
def grafici():
    return render_template('grafici.html')
'''

@app.route('/previsioni')
def previsione():
    return render_template('previsioni.html')


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
        code = int(request.values['code'])
        namedist = request.values['namedist']
        address = request.values['address']
        latitude = float(request.values['latitude'])
        longitude = float(request.values['longitude'])

        entity = db.collection('dati').document(dato).get()
        if entity.exists:
            d = entity.to_dict()
            d['readings'].append({'code': code, 'namedist': namedist, 'address': address, 'latitude': latitude, 'longitude': longitude})
            db.collection('dati').document(dato).set(d)
        else:
            db.collection('dati').document(dato).set({'readings':[{'code': code, 'namedist': namedist, 'address': address, 'latitude': latitude, 'longitude': longitude}]})
        return 'ok', 200
    elif dato == 'item':
        item_code = int(request.values['item_code'])
        item_name = request.values['item_name']
        unit = request.values['unit']
        good = float(request.values['good'])
        normal = float(request.values['normal'])
        bad = float(request.values['bad'])
        very_bad = float(request.values['very_bad'])

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
    entity = db.collection('valori').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        readings = d['readings']
        for r in readings:
            if isinstance(r.get('data'), datetime):
                r['data'] = r['data'].strftime('%Y-%m-%d %H:%M:%S')
        return json.dumps(readings), 200
    else:
        return 'not found', 404



@app.route('/valori/<dato>', methods=['POST'])
def new_values(dato):
    
    data = datetime.strptime((request.values['data']), '%Y-%m-%d %H:%M:%S')
    
    code = int(request.values['code'])
    address = request.values['address']
    latitude = float(request.values['latitude'])
    longitude = float(request.values['longitude'])
    SO2 = float(request.values['SO2'])
    NO2 = float(request.values['NO2'])
    O3 = float(request.values['O3'])
    CO = float(request.values['CO'])
    PM10 = float(request.values['PM10'])
    PM25 = float(request.values['PM25'])

    entity = db.collection('valori').document(dato).get()
    if entity.exists:
        d = entity.to_dict()
        d['readings'].append({'data': data, 'code': code, 'address': address, 'latitude': latitude, 'longitude': longitude,'SO2': SO2, 'NO2': NO2, 'O3': O3, 'CO': CO, 'PM10': PM10, 'PM25': PM25})
        db.collection('valori').document(dato).set(d)
    else:
        db.collection('valori').document(dato).set({'readings':[{'data': data, 'code': code, 'address': address, 'latitude': latitude, 'longitude': longitude,'SO2': SO2, 'NO2': NO2, 'O3': O3, 'CO': CO, 'PM10': PM10, 'PM25': PM25}]})
    return 'ok', 200


@app.route('/grafici')
def grafici():
    docs = db.collection('valori').stream()
    so2, no2, o3, co, pm10, pm25 = [], [], [], [], [], []

    station_doc = db.collection('dati').document('station').get()
    stations = []
    if station_doc.exists:
        stations = station_doc.to_dict().get('readings', [])

    # Funzione per trovare il nome della stazione
    def get_station_name(lat, lon, stations):
        for s in stations:
            if abs(float(s['latitude']) - float(lat)) < 1e-6 and abs(float(s['longitude']) - float(lon)) < 1e-6:
                return s['namedist']
        return "Stazione sconosciuta"

    # Lista per il nuovo grafico (senza duplicati)
    station_coords = []

    for doc in docs:
        d = doc.to_dict()
        if 'readings' in d:
            for r in d['readings']:
                data_str = r['data'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(r['data'], datetime) else str(r['data'])
                so2.append([data_str, r.get('SO2')])
                no2.append([data_str, r.get('NO2')])
                o3.append([data_str, r.get('O3')])
                co.append([data_str, r.get('CO')])
                pm10.append([data_str, r.get('PM10')])
                pm25.append([data_str, r.get('PM25')])
                lat = r.get('latitude')
                lon = r.get('longitude')
                if lat is not None and lon is not None:
                    nome = get_station_name(lat, lon, stations)
                    # Salva solo se non già presente
                    if [lat, lon, nome] not in station_coords:
                        station_coords.append([lat, lon, nome])
    



    return render_template(
        'grafici.html',
        data_so2=json.dumps(so2),
        data_no2=json.dumps(no2),
        data_o3=json.dumps(o3),
        data_co=json.dumps(co),
        data_pm10=json.dumps(pm10),
        data_pm25=json.dumps(pm25),
        station_coords=json.dumps(station_coords)
    )








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
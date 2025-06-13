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
from collections import defaultdict


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


@app.route('/previsioni')
def previsione():
    return render_template('previsioni.html')

'''

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
    all_readings = []

    station_doc = db.collection('dati').document('station').get()
    stations = []
    if station_doc.exists:
        stations = station_doc.to_dict().get('readings', [])

    def get_station_name(lat, lon, stations):
        for s in stations:
            if abs(float(s['latitude']) - float(lat)) < 1e-6 and abs(float(s['longitude']) - float(lon)) < 1e-6:
                return s['namedist']
        return "Stazione sconosciuta"

    station_coords = []

    

    # Raccogli tutti i readings in una lista unica
    for doc in docs:
        d = doc.to_dict()
        if 'readings' in d:
            for r in d['readings']:
                data = r['data']
                if isinstance(data, str):
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                r['data'] = data
                all_readings.append(r)
                lat = r.get('latitude')
                lon = r.get('longitude')
                if lat is not None and lon is not None:
                    nome = get_station_name(lat, lon, stations)
                    if [lat, lon, nome] not in station_coords:
                        station_coords.append([lat, lon, nome])

    # Ordina tutti i readings per data
    all_readings.sort(key=lambda x: x['data'])

    # Trova la data più recente
    if all_readings:
        last_time = all_readings[-1]['data']
        first_time = last_time - timedelta(hours=24)
        # Filtra solo le ultime 24 ore
        filtered = [r for r in all_readings if first_time <= r['data'] <= last_time]
    else:
        filtered = []

    # Recupera i range degli item
    item_doc = db.collection('dati').document('item').get()
    item_ranges = {}
    if item_doc.exists:
        for item in item_doc.to_dict().get('readings', []):
            name = item['item_name']  # es: 'SO2'
            item_ranges[name] = {
                'good': float(item['good']),
                'normal': float(item['normal']),
                'bad': float(item['bad']),
                'very_bad': float(item['very_bad'])
            }

    def get_index(val, ranges):
        if val <= ranges['good']:
            return 'good'
        elif val <= ranges['normal']:
            return 'normal'
        elif val <= ranges['bad']:
            return 'bad'
        else:
            return 'very_bad'

    def hourly_avg(filtered, key, ranges):
        by_hour = defaultdict(list)
        for r in filtered:
            hour = r['data'].replace(minute=0, second=0, microsecond=0)
            value = r.get(key)
            if value is not None:
                by_hour[hour].append(value)
        result = []
        for hour in sorted(by_hour):
            avg = sum(by_hour[hour]) / len(by_hour[hour])
            idx = get_index(avg, ranges)
            result.append([hour.strftime('%Y-%m-%d %H:%M:%S'), avg, idx])
        return result

    so2 = hourly_avg(filtered, 'SO2', item_ranges['SO2'])
    no2 = hourly_avg(filtered, 'NO2', item_ranges['NO2'])
    o3 = hourly_avg(filtered, 'O3', item_ranges['O3'])
    co = hourly_avg(filtered, 'CO', item_ranges['CO'])
    pm10 = hourly_avg(filtered, 'PM10', item_ranges['PM10'])
    pm25 = hourly_avg(filtered, 'PM25', item_ranges['PM2.5'])

    def index_score(idx):
        if idx == 'good':
            return 1
        elif idx == 'normal':
            return 2
        elif idx == 'bad':
            return 6
        elif idx == 'very_bad':
            return 10
        return 0


    # Calcola la qualità generale per ogni ora
    general_quality = []
    ore = set([x[0] for x in so2]) & set([x[0] for x in no2]) & set([x[0] for x in o3]) & set([x[0] for x in co]) & set([x[0] for x in pm10]) & set([x[0] for x in pm25])
    for hour in sorted(ore):
        idxs = []
        for serie in [so2, no2, o3, co, pm10, pm25]:
            for x in serie:
                if x[0] == hour:
                    idxs.append(index_score(x[2]))
                    break
        if idxs:
            avg_score = sum(idxs) / len(idxs)
            if avg_score <= 1.5:
                idx = 'good'
            elif avg_score <= 2.5:
                idx = 'normal'
            elif avg_score <= 3.5:
                idx = 'bad'
            else:
                idx = 'very_bad'
            general_quality.append([hour, avg_score, idx])

    # Salva general_quality su Firestore
    general_quality_dicts = [
        {'data': hour, 'avg_score': avg_score, 'index': idx}
        for hour, avg_score, idx in general_quality
    ]
    db.collection('valori').document('media').set({'readings': general_quality_dicts})


    return render_template(
        'grafici.html',
        data_so2=json.dumps(so2),
        data_no2=json.dumps(no2),
        data_o3=json.dumps(o3),
        data_co=json.dumps(co),
        data_pm10=json.dumps(pm10),
        data_pm25=json.dumps(pm25),
        station_coords=json.dumps(station_coords),
        item_ranges=json.dumps(item_ranges),
        general_quality=json.dumps(general_quality)
    )

def f_next_date(last_hour):
    # Calcolo del giorno successivo
    next_hour = last_hour + timedelta(hours=1)
    # Conversione di nuovo in stringa
    return next_hour.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/previsioni')
def previsione():
    #time.sleep(10)


    '''
    entity = db.collection('valori').document('media').get()
    if entity.exists:
        x = entity.to_dict()['readings']
        x2 = []
        for d in x:
            x2.append([d['data'], d['avg_score']])
        
        model = load('progetto_Previtero_Rauseo/model.joblib') 
        y = []

        next_date1 = f_next_date(x2[-1][0])
        history = [x2[-1][1],x2[-2][1],x2[-3][1]]
        predictions =[model.predict([history])]
        y.append([next_date1,float(predictions[0][0])])

        next_date2 = f_next_date(next_date1)
        history = [y[-1][1],x2[-1][1],x2[-2][1]]
        predictions =[model.predict([history])]
        y.append([next_date2,float(predictions[0][0])])


        x2 = x2 + y
        x = str(x2)
        return render_template('previsioni.html', data=x, sensor=sensor)    
    else:
        return 'not found', 404'''



    # Recupera la serie storica della qualità dell'aria generale
    entity = db.collection('valori').document('media').get()
    if entity.exists:
        readings = entity.to_dict()['readings']
        # Ordina per data
        readings.sort(key=lambda x: x['data'])
        # Prendi solo avg_score (o index se vuoi classificazione)
        history = [r['avg_score'] for r in readings]
        last_date = readings[-1]['data']

        model = load('progetto_Previtero_Rauseo/models/model.joblib')  # Usa il tuo modello, o uno addestrato per questo scopo
        predictions = []
        dates = []

        # Previsione per le prossime 24 ore (1 ora alla volta)
        for i in range(24):
            # Usa le ultime 3 osservazioni come input (adatta se il modello è autoregressivo)
            input_history = history[-3:]
            pred = model.predict([input_history])[0]
            # Calcola la prossima data
            next_date = f_next_date(last_date)
            predictions.append({'data': next_date, 'avg_score': float(pred)})
            dates.append(next_date)
            # Aggiorna history e last_date per la prossima iterazione
            history.append(pred)
            last_date = next_date

        # Puoi passare predictions al template o restituirle come JSON
        return render_template('previsioni.html', previsioni_qualita=json.dumps(predictions))
    else:
        return 'not found', 404








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
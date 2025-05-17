
from requests import get, post
import time

server = 'http://127.0.0.1:8080'
name = 'station'

with open('Measurement_station_info.csv') as f:
    next(f)
    for line in f:
        #problema nella lettura del file csv, tra le virgolette ci sono delle virgole
        parts = line.strip().split(',')
        
        code, namedist, address, latitude, longitude = line.strip().split(',')
        code =int(code)
        latitude = float(latitude)
        longitude = float(longitude)
        post(f'{server}/dati/{name}', code={'code': code, 'namedist': namedist, 'address': address, 'latitude': latitude, 'longitude': longitude})
        #time.sleep(3)
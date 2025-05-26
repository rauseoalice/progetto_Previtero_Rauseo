
from requests import get, post
import time

server = 'http://127.0.0.1:8080'
name = 'station'



with open('Measurement_station_info.csv') as f:
    next(f)
    for line in f:
        for line in f:
            line = line.strip()
        if line:
            parts = line.split('"')
            if len(parts) >= 5:
                first_part = parts[0].rstrip(',')
                second_part = parts[1]
                third_part = parts[3]
                
                code, namedist = first_part.strip.split(',', 1)
                address = second_part
                latitude, longitude = third_part.split(',', 1)
                
                post(f'{server}/dati/{name}', json={
                    'code': int(code), 'namedist': namedist, 'address': address,
                    'latitude': float(latitude), 'longitude': float(longitude)
                    })
                print(code, namedist, address, latitude, longitude)


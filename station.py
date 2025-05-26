
from requests import get, post
import time

server = 'http://127.0.0.1:8080'
name = 'station'



with open('Measurement_station_info.csv') as f:
    next(f)
    for line in f:
        line = line.strip()
        if line:
            parts = line.split('"')
            first_part = parts[0].rstrip(',')
            second_part = parts[1]
            third_part = parts[2]
            third_part_good = third_part.strip(',')
                    
            code, namedist = first_part.split(',', 1)
            address = second_part
            latitude, longitude = third_part_good.split(',',1)
                    
            post(f'{server}/dati/{name}', data={
                        'code': int(code), 'namedist': namedist, 'address': address,
                        'latitude': float(latitude), 'longitude': float(longitude)
                })
                    
            print(code, namedist, address, latitude, longitude)



name = 'item'

with open('Measurement_item_info.csv') as f:
    next(f)
    for line in f:
        line = line.strip()
        if line:
            parts = line.split(',')
            item_code = int(parts[0])
            item_name = parts[1]
            unit = parts[2]
            good = float(parts[3])
            normal = float(parts[4])
            bad = float(parts[5])
            very_bad = float(parts[6])
            
            post(f'{server}/dati/{name}', data={
                'item_code': item_code,
                'item_name': item_name,
                'unit': unit,
                'good': good,
                'normal': normal,
                'bad': bad,
                'very_bad': very_bad
            })
            
            print(item_code, item_name, unit, good, normal, bad, very_bad)
from requests import post, get
import time
from datetime import datetime

server = 'http://127.0.0.1:8080'
name = 'summary'

rows = []

with open('Measurement_summary.csv') as f:
    next(f)
    for line in f:
        line = line.strip()
        if line:
            parts = line.split('"')
            first_part = parts[0].rstrip(',')
            second_part = parts[1]
            third_part = parts[2]
            third_part_good = third_part.strip(',')

            date_str, code = first_part.split(',', 1)
            date = datetime.strptime(date_str + ':00', '%Y-%m-%d %H:%M:%S')
            address = second_part
            latitude, longitude, SO2, NO2, O3, CO, PM10, PM25 = third_part_good.split(',', 7)

            row = {
                'date': date,
                'code': int(code),
                'address': address,
                'latitude': float(latitude),
                'longitude': float(longitude),
                'SO2': float(SO2),
                'NO2': float(NO2),
                'O3': float(O3),
                'CO': float(CO),
                'PM10': float(PM10),
                'PM25': float(PM25)
            }
            rows.append(row)

# Ordina le righe per data
rows.sort(key=lambda x: x['date'])

# Invia i dati ordinati
for row in rows:
    post(f'{server}/valori/{name}', data={
        'data': row['date'],
        'code': row['code'],
        'address': row['address'],
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'SO2': row['SO2'],
        'NO2': row['NO2'],
        'O3': row['O3'],
        'CO': row['CO'],
        'PM10': row['PM10'],
        'PM25': row['PM25']
    })
    print(row['date'], row['code'], row['address'], row['latitude'], row['longitude'],
          row['SO2'], row['NO2'], row['O3'], row['CO'], row['PM10'], row['PM25'])
    time.sleep(1)





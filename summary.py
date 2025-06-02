from requests import get, post
import time
from datetime import datetime

server = 'http://127.0.0.1:8080'
name = 'summary'


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
                    
            date, code = first_part.split(',', 1)
            date = datetime.strptime(date + ':00', '%Y-%m-%d %H:%M:%S')
            #date = datetime.strptime(date, '%Y-%m-%d %H:%M')
            address = second_part
            latitude, longitude, SO2, NO2, O3, CO, PM10, PM25 = third_part_good.split(',', 7)

            code = int(code)
            latitude = float(latitude)
            longitude = float(longitude)
            SO2 = float(SO2)
            NO2 = float(NO2)
            O3 = float(O3)
            CO = float(CO)
            PM10 = float(PM10)
            PM25 = float(PM25)
                    
            post(f'{server}/valori/{name}', data={'data': date, 
                                                  'code': code, 
                                                  'address': address, 
                                                  'latitude': latitude, 
                                                  'longitude': longitude, 
                                                  'SO2': SO2, 
                                                  'NO2': NO2, 
                                                  'O3': O3, 
                                                  'CO': CO, 
                                                  'PM10': PM10, 
                                                  'PM25': PM25})
                    
            print(date, code, address, latitude, longitude, SO2, NO2, O3, CO, PM10, PM25)
            time.sleep(1)  # Sleep to avoid overwhelming the server




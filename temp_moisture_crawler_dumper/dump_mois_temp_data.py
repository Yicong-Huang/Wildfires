#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import os

import psycopg2
import rootpath

rootpath.append()
from configurations import REC_TEMP_MOIS_PATH
from extract_mois_temp_data import GRIBExtractor, TIFExtractor


class MoistureTemperatureDumper:
    def __init__(self, path, data_time, data_type='temperature'):
        self.conn = psycopg2.connect(dbname="testdb", user="tester", password="testpassword",
                                     host="cloudberry05.ics.uci.edu", port="5432")
        self.path = path  # path to data
        self.data_time = data_time  # recent or historical
        self.data_type = data_type  # moisture or temperature

    def extract_and_dump(self, dateCount=1):
        files = os.listdir(self.path)
        if self.data_time == 'recent':
            for count in range(1, dateCount + 1):
                curDate = datetime.datetime.today() - datetime.timedelta(days=count)
                formattedDate = curDate.strftime('%y%m%d')
                date = '20' + str(formattedDate)
                print(date)
                for file in files:
                    if not os.path.isdir(file) and 'txt' in file and date in file:
                        print(file)
                        file = self.path + '/' + file
                        if self.data_type == 'moisture':
                            grib_extractor = GRIBExtractor(file,
                                                           prop_name='Liquid volumetric soil moisture (non-frozen)',
                                                           prop_first=0, prop_second=10)
                            dictionary = grib_extractor.extractMoisture()
                        if self.data_type == 'temperature':
                            grib_extractor = GRIBExtractor(file, prop_name='Temperature', prop_typeOfLevel='surface')
                            dictionary = grib_extractor.extractTemperature()

                        start_hour = int(file[file.find('.t') + 2:file.find('z')])
                        end_hour = start_hour + int(file[file.find('grbf') + 4:file.find('.grib2')])

                        start_time = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), start_hour, 0, 0)
                        end_time = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), end_hour, 0, 0)

                        for key, value in dictionary.items():
                            lat = float(key[1:key.find(',')])
                            long = float(key[key.find(',') + 1:key.find(')')])
                            value = float(value)
                            if str(value) != 'nan':
                                if self.data_type == 'temperature':
                                    self.dump_data(p_lat=lat, p_long=long, p_value=value, p_start=start_time,
                                                   p_end=end_time, attri_name='rec_temp')
                                if self.data_type == 'moisture':
                                    self.dump_data(p_lat=lat, p_long=long, p_value=value, p_start=start_time,
                                                   p_end=end_time, attri_name='rec_mois')

        if self.data_time == 'historical':
            for file in files:
                if not os.path.isdir(file) and 'tif' in file:
                    full_file = self.path + '/' + file
                    tif_extractor = TIFExtractor(full_file)
                    xyzFile = open('output.xyz')
                    line = xyzFile.readline()
                    while line:
                        long = line.split()[0]
                        lat = line.split()[1]
                        value = line.split()[2]
                        if str(value) != '-999000000':
                            if self.data_type == 'temperature':
                                time = file[20:28]
                                self.dump_data(p_lat=lat, p_long=long, p_value=value, p_time=time,
                                               attri_name='his_temp')
                            if self.data_type == 'moisture':
                                time = file[7:15]
                                self.dump_data(p_lat=lat, p_long=long, p_value=value, p_time=time,
                                               attri_name='his_mois')
                        line = xyzFile.readline()
                    xyzFile.close()

    def dump_data(self, p_lat, p_long, p_value, p_time=0, p_start=0, p_end=0, attri_name=''):
        cur = self.conn.cursor()
        if attri_name == 'rec_temp':
            cur.execute(
                "INSERT INTO recent_temperature(lat,long,temperature,starttime,endtime) values (%s, %s, %s, %s, %s)",
                (p_lat, p_long, p_value, p_start, p_end))
        if attri_name == 'rec_mois':
            cur.execute("INSERT INTO recent_moisture(lat,long,moisture,starttime, endtime) values (%s, %s, %s, %s, %s)",
                        (p_lat, p_long, p_value, p_start, p_end))
        if attri_name == 'his_temp':
            cur.execute("INSERT INTO historical_temperature(lat,long,temperature,datetime) values (%s, %s, %s, %s)",
                        (p_lat, p_long, p_value, p_time))
        if attri_name == 'his_mois':
            cur.execute("INSERT INTO historical_moisture(lat,long,moisture,datetime) values (%s, %s, %s, %s)",
                        (p_lat, p_long, p_value, p_time))
        self.conn.commit()
        cur.close()


if __name__ == '__main__':
    # path to datafile, data_date = 'historical' or 'recent', data_type = 'temperature' or 'moisture'
    # dumper = MoistureTemperatureDumper(REC_TEMP_MOIS_PATH, 'recent', 'temperature')
    # dumper.extract_and_dump(1)
    dumper = MoistureTemperatureDumper(REC_TEMP_MOIS_PATH, 'recent', 'moisture')
    dumper.extract_and_dump(1)
    # dumper = MoistureTemperatureDumper(HIS_MOIS_PATH, 'historical', 'moisture')
    # dumper.extract_and_dump()
    # dumper = MoistureTemperatureDumper(HIS_TEMP_PATH, 'historical', 'temperature')
    # dumper.extract_and_dump()

    # conn = psycopg2.connect(dbname="testdb", user="tester", password="testpassword",
    #                         host="cloudberry05.ics.uci.edu", port="5432")
    # cur = conn.cursor()
    # cur.execute("delete from historical_moisture")
    # conn.commit()
    # cur.close()

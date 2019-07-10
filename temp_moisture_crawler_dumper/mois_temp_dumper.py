#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rootpath
rootpath.append()

from backend.data_preparation.dumper.dumperbase import DumperBase


class MoisTempDumper(DumperBase):
    HIS_TEMP_MODE = 0
    HIS_MOIS_MODE = 1
    REC_TEMP_MODE = 2
    REC_MOIS_MODE = 3

    def insert_one(self, data_type, conn, p_lat, p_long, p_value, p_time=0, p_start=0, p_end=0):
        # insert one record into database
        # recording insert count number to self.inserted_count

        # filter for geolocation in America
        if p_lat > 49 or p_lat < 25 or p_long < 230 or p_long > 290:
            return

        cur = conn.cursor()
        try:
            if data_type == MoisTempDumper.REC_TEMP_MODE:
                cur.execute(
                    "INSERT INTO recent_temperature(lat,long,temperature,starttime,endtime) values (%s, %s, %s, %s, %s)",
                    (p_lat, p_long, p_value, p_start, p_end))
            if data_type == MoisTempDumper.REC_MOIS_MODE:
                cur.execute("INSERT INTO recent_moisture(lat,long,moisture,starttime, endtime) values (%s, %s, %s, %s, %s)",
                            (p_lat, p_long, p_value, p_start, p_end))
            if data_type == MoisTempDumper.HIS_TEMP_MODE:
                cur.execute("INSERT INTO historical_temperature(lat,long,temperature,datetime) values (%s, %s, %s, %s)",
                            (p_lat, p_long, p_value, p_time))

            if data_type == MoisTempDumper.HIS_MOIS_MODE:
                cur.execute("INSERT INTO historical_moisture(lat,long,moisture,datetime) values (%s, %s, %s, %s)",
                            (p_lat, p_long, p_value, p_time))
        except Exception as err:
            print("error", err)

        conn.commit()
        cur.close()
        self.inserted_count += 1
        print('number of inserted records: ', self.inserted_count)


    def insert_batch(*args, **kwargs):
        # insert a batch of records into database
        # recording insert count number to self.inserted_count
        pass
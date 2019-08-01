from typing import List, Dict

import rootpath
rootpath.append()

from backend.data_preparation.dumper.dumperbase import DumperBase
from backend.data_preparation.connection import Connection

class FireDumper(DumperBase):
    """
    Table 1(fire_crawl_history): fireyear firename
    Table 2(fire_geoms): firename firetime firegeom
    """
    sql_check_if_history_table_exists = 'SELECT table_name FROM information_schema.TABLES WHERE table_name = \'fire_crawl_history\''
    sql_create_history_table = 'CREATE TABLE IF NOT EXISTS fire_crawl_history (year int4, name VARCHAR (40), PRIMARY KEY (year, name))'
    sql_retrieve_all_fires = 'SELECT * FROM fire_crawl_history'
    sql_check_if_fire_info_table_exists = 'SELECT table_name FROM information_schema.TABLES WHERE table_name = \'fire_info\''
    sql_create_fire_info_table = 'CREATE TABLE IF NOT EXISTS fire_info (name VARCHAR (40), if_sequence boolean, agency VARCHAR (20), time timestamp, geom geometry, PRIMARY KEY (name, time))'
    sql_insert_fire_into_history = 'INSERT INTO "fire_crawl_history" (year, name) VALUES (%(year)s, %(firename)s) ON CONFLICT DO NOTHING'
    sql_insert_fire_into_info = 'INSERT INTO "fire_info" (name, if_sequence, agency, time, geom) VALUES (%(firename)s,%(if_sequence)s,%(agency)s,%(datetime)s,%(geopolygon)s) ON CONFLICT DO NOTHING'
    sql_count_records = 'SELECT COUNT(*) FROM fire_info'

    def __init__(self):
        super().__init__()

    def insert(self) -> None:
        pass

    def check_history(self, conn):
        """
        create fire_crawl_history table if not exist
        """
        cur = conn.cursor()
        # if table not exist
        cur.execute(self.sql_check_if_history_table_exists)
        tables = cur.fetchall()
        if len(tables) == 0:
            print("No history table exists. Creating a new one.")
            cur.execute(FireDumper.sql_create_history_table)
            conn.commit()
        cur.close()

    def check_info(self, conn):
        """
        create fire_crawl_history table if not exist
        """
        cur = conn.cursor()
        # if table not exist
        cur.execute(self.sql_check_if_fire_info_table_exists)
        tables = cur.fetchall()
        if len(tables) == 0:
            print("No info table exists. Creating a new one.")
            cur.execute(FireDumper.sql_create_fire_info_table)
            conn.commit()
        cur.close()

    def retrieve_all_fires(self):
        """
        retrieve all fires in the database
        :return: set
        """
        with Connection() as connect:
            self.check_history(connect)
            cur = connect.cursor()
            cur.execute(self.sql_retrieve_all_fires)
            result = cur.fetchall()
        return result

    def insert(self, info: dict):
        print("Inserting fire:",info["firename"],info["datetime"])
        # s = "("
        # for t in info["geopolygon"]:
        #     s += "({},{}),".format(t[0], t[1])
        # info["geopolygon"] = s[:-1] + ")"
        with Connection() as connect:
            self.check_info(connect)
            cur = connect.cursor()
            cur.execute(self.sql_insert_fire_into_info, info)
            connect.commit()
            cur.execute(self.sql_count_records)
            self.inserted_count = cur.fetchone()[0]
            cur.close()
        print("Finished inserting file:",info["firename"],info["datetime"])
        print("record count:",self.inserted_count)
        return info["datetime"].year, info["firename"]

    def insert_history(self,year,name):
        with Connection() as connect:
            info = {"year":year,"firename":name}
            cur = connect.cursor()
            cur.execute(self.sql_insert_fire_into_history, info)
            connect.commit()
            cur.close


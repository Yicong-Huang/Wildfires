import datetime
import logging

import numpy as np
import psycopg2.errors
import psycopg2.extras
import rootpath

rootpath.append()
from backend.data_preparation.connection import Connection
from backend.data_preparation.dumper.dumperbase import DumperBase

logger = logging.getLogger('TaskManager')


class PRISMDumper(DumperBase):
    INSERT_SQL = '''
                insert into prism_master (date, gid, ppt, tmax, vpdmax) values %s
            '''
    INSERT_INFO = 'insert into prism_info_master (date, ppt, tmax, vpdmax) values (%s, 1, 1, 1) ' \
                  'on conflict(date) do update set vpdmax=EXCLUDED.vpdmax',

    def insert(self, date: datetime.date, ppt: np.ndarray, tmax: np.ndarray, vpdmax: np.ndarray):
        ppt = ppt.flatten()
        tmax = tmax.flatten()
        vpdmax = vpdmax.flatten()
        with Connection() as conn:
            cur = conn.cursor()
            psycopg2.extras.execute_values(cur, PRISMDumper.INSERT_SQL,
                                           PRISMDumper.record_generator(date, ppt, tmax, vpdmax),
                                           template=None, page_size=10000)
            cur.execute(PRISMDumper.INSERT_INFO, (date,))
            conn.commit()
            cur.close()

    @staticmethod
    def record_generator(date: datetime.date, ppt, tmax, vpdmax):
        tmax = tmax.tolist()
        vpdmax = vpdmax.tolist()
        for gid, val in enumerate(ppt.tolist()):
            yield (date, gid, val, tmax[gid], vpdmax[gid])

            # for test purpose
            # if gid > 5:
            #     break

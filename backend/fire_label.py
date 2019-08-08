import os

import numpy as np
import rootpath

rootpath.append()
from backend.data_preparation.connection import Connection
from paths import FIRE_LABEL_PATH


# fire existed on these days
def get_fire_dates():
    sql_get_fire_dates = 'SELECT date(fire_info."time") FROM "fire_info" GROUP BY date(fire_info."time")' \
                         'ORDER BY date(fire_info."time") DESC'
    with Connection() as conn:
        cur = conn.cursor()
        cur.execute(sql_get_fire_dates)
        return [_ for _, in cur.fetchall()]


def do_query(date_str: str):
    query = '''
    SELECT gid
    from mesh_all4all,
    (
        SELECT date(fire_info."time"), st_astext(st_union(ST_MakeValid(geom_1e2))) as unioned FROM "fire_info"
        where date(fire_info."time")=%s
        GROUP BY date(fire_info."time")
    ) as polygons
    where st_within(geom, polygons.unioned)
    '''

    with Connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (date_str,))
        return [_ for _, in cur.fetchall()]


if __name__ == '__main__':
    for date in get_fire_dates():
        # mkdir if not exist
        if not os.path.exists(FIRE_LABEL_PATH):
            os.mkdir(FIRE_LABEL_PATH)

        # skip existing dates
        if os.path.exists(os.path.join(FIRE_LABEL_PATH, f'{date}.npy')):
            print(f'[skipped] {date}.npy exists')
            continue

        mat = np.zeros((228, 248), dtype=np.float32)
        print(f'[query] date={date}')
        # mark pixel within fire range as 1.0
        for point in do_query(str(date)):
            mat[point // 248][point % 248] = 1.0
        np.save(os.path.join(FIRE_LABEL_PATH, f'{date}'), mat)
        print(f'[saved] {date}.npy')

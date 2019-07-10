import os

# root path of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# path of the config file for connection to postgresql
DATABASE_CONFIG_PATH = os.path.join(ROOT_DIR, 'configs/database.ini')

NLTK_MODEL_PATH = os.path.join(ROOT_DIR, 'backend/models/nltk_model.pickle')

TEST_DATA_PATH = os.path.join(ROOT_DIR, 'data/test')

GRIB2_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'grib-data')

WIND_DATA_DIR = os.path.join(ROOT_DIR, 'backend', 'data')

GRIB2JSON_PATH = os.path.join('converter', 'bin', 'grib2json')

HIS_TEMP_PATH = os.path.join(ROOT_DIR, 'data/historical_temp')

HIS_MOIS_PATH = os.path.join(ROOT_DIR, 'data/historical_mois')

REC_TEMP_MOIS_PATH = os.path.join(ROOT_DIR, 'data/recent_temp_mois')

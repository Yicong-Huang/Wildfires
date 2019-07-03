from typing import Dict
import pygrib
import json
import os

class GRIBExtractor:
    def __init__(self, open_file_name, prop_name, prop_typeOfLevel):
        self.file_handler = pygrib.open(open_file_name)
        self.data: Dict = self.extract(prop_name, prop_typeOfLevel)

    def extract(self, prop_name: str, prop_typeOfLevel: str) -> dict:
        prop_msg = self.file_handler.select(name=prop_name, typeOfLevel=prop_typeOfLevel)[0]
        prop_dict = dict()  # creates a new dictionary to store data
        prop_vals = prop_msg.values  # values under the started property
        lats, lons = prop_msg.latlons()
        for row_cnt in range(0, len(prop_vals)):
            for col_cnt in range(0, len(prop_vals[row_cnt])):
                prop_dict[str((lats[row_cnt][col_cnt], lons[row_cnt][col_cnt]))] = prop_vals[row_cnt][col_cnt]
        return prop_dict  # the location coordinates are different, don't need to worry about duplicated keys

    def export(self, file_type: str, file_name) -> None:  # json
        if file_type == 'json':
            json.dump(self.data, open(file_name, 'w'))

    def __getitem__(self, lat_lng_pair: tuple) -> float:
        value = self.data.get(str(lat_lng_pair))
        return value

if __name__ == '__main__':

    path = "./temperature_data"  # file directory
    files = os.listdir(path)  # gets all the file names


    for file in files:
        print(file)
        grib_extractor = GRIBExtractor('./temperature_data/'+file, 'Temperature', 'surface')
        dictionary = grib_extractor.extract('Temperature', 'surface')
        print(len(dictionary))

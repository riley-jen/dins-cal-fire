'''
this program is to clean the already filtered .geojson
it writes a new .geojson that cleans the errors from the data
includes duplicate inputs and same incident names

not to be confused with filter_data.py
'''

import json
import geopandas as gpd

filtered_filename = "POSTFIRE_FILTERED_DATA.geojson"
gdf = gpd.read_file(filtered_filename)

def get_data_timestamps(gdf):
  timestamps = []

  for i, data in gdf.iterrows():
    fire_name = data['INCIDENTNAME']
    time = data['INCIDENTSTARTDATE']

    ts = (fire_name, time)

    if ts not in timestamps:
      timestamps.append(ts)

  return timestamps

print(get_data_timestamps(gdf))

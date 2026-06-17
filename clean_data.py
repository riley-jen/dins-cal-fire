'''
this program is to clean the already filtered .geojson
it writes a new .geojson that cleans the errors from the data
includes duplicate inputs and same incident names

not to be confused with filter_data.py
'''

import json
import geopandas as gpd

filename = "POSTFIRE_FILTERED_DATA.geojson"
gdf = gpd.read_file(filename)


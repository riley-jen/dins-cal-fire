import json
import ijson
import geopandas as gpd
from decimal import Decimal

fires_list = ["palisades", "mountain", "eaton", "franklin", "line", "bridge", "unspecified"]
fires_perimeter_count = dict.fromkeys(fires_list, 0)

'''
function that takes in a .geojson file and returns a list of filtered features given a dictionary
also updates the counts
'''
def read_file(raw_file, filter_dict):
  new_features = []
  with open(raw_file, 'rb') as f:
    features = ijson.items(f,'features.item')

    for feature in features:
      properties = feature.get('properties',{})
      incident = properties.get("INCIDENTNAME",'').lower()

      if incident == None:
        filter_dict["unspecified"] += 1
      if incident in filter_dict.keys():
        filter_dict[incident] += 1
        new_features.append(feature)

  return new_features

raw_filename = "../POSTFIRE_MASTER_DATA.geojson"
select_features = read_file(raw_filename, select_incidents)

assert (select_incidents["unspecified"] == 0), "unspecified incidents present!"

'''
handles json not being able to serialize decmials... hopefully
'''
def decimal_encoder(obj):
  if isinstance(obj, Decimal):
    return float(obj)
  return obj

'''
writes new .geojson file given a list of features
'''
def write_file(new_file, features):
  new_geojson = {
    "type": "FeatureCollection",
    "features": features
  }

  with open(new_file, "w") as f:
    json.dump(new_geojson, f, indent = 2, default=decimal_encoder)

clean_filename = "./POSTFIRE_FILTERED_DATA.geojson"
write_file(clean_filename, select_features)
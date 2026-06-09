import json
import ijson
import geopandas as gpd

'''
helper function that creates a dictionary from a list
'''
def create_dict(list):
  new_dict = {}
  for item in list:
    new_dict[item] = 0
  return new_dict

select_incidents_list = ["palisades", "mountain", "eaton", "franklin", "line", "bridge"]
select_incidents = create_dict(select_incidents_list)

def read_file(raw_file, filter_dict):
  new_features = []
  with open(raw_file, 'rb') as f:
    features = ijson.items(f,'features.item')

    for feature in features:
      properties = feature.get('properties',{})
      incident = properties.get("INCIDENTNAME",'').lower()

      if incident in filter_dict.keys():
        filter_dict[incident] += 1
        new_features.append(feature)

filename = "../POSTFIRE_MASTER_DATA.geojson"
select_features = read_file(filename, select_incidents)

print(select_incidents)


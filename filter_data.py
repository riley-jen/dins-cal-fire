import json
import ijson
import geopandas as gpd

# helper functions
def create_dict(list):
  new_dict = {}
  for item in list:
    new_dict[item] = 0
  return new_dict

select_incidents_list = ["palisades", "mountain", "eaton", "franklin", "line", "bridge"]
select_incidents = create_dict(select_incidents_list)


select_features = []

raw_file = "../POSTFIRE_MASTER_DATA.geojson"

print("checkpoint 1")

with open(raw_file, 'rb') as f:
  features = ijson.items(f,'features.item')
  done = False

  for feature in features:
    properties = feature.get('properties',{})
    incident = properties.get("INCIDENTNAME",'').lower()

    if incident in select_incidents.keys():
      select_features.append(feature)
      select_incidents[incident] += 1

print("checkpoint 2")
print(select_incidents)

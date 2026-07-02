'''
this program is to filter the raw, cal fire sourced .geojson 
it writes a new .geojson that contains only the features from the selected fires

not to be confused with clean_structure.py
'''

import json
import ijson
import geopandas as gpd
from decimal import Decimal
from pathlib import Path

'''
helper function that returns a dictionary from a list
'''
def create_dict(list):
  new_dict = {}
  for item in list:
    new_dict[item] = 0
  return new_dict

select_incidents_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge', 'unspecified']
select_incidents = create_dict(select_incidents_list)
raw_filename = Path(__file__).resolve().parents[2] / 'POSTFIRE_MASTER_DATA.geojson'
clean_filename = Path(__file__).resolve().parent.parent / 'files' / 'POSTFIRE_FILTERED_DATA.geojson'

'''
function that takes in a .geojson file and returns a list of filtered features given a dictionary
also updates the counts
'''
def read_file(raw_file, filter_dict):
  new_features = []
  before_count = 0
  with open(raw_file, 'rb') as f:
    features = ijson.items(f,'features.item')

    for feature in features:
      before_count += 1
      properties = feature.get('properties',{})
      incident = properties.get('INCIDENTNAME','').lower()

      if incident == '':
        filter_dict['unspecified'] += 1
      if incident in filter_dict.keys():
        filter_dict[incident] += 1
        new_features.append(feature)

  return new_features, (before_count, len(new_features))

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
    'type': 'FeatureCollection',
    'features': features
  }

  with open(new_file, 'w') as f:
    json.dump(new_geojson, f, indent = 2, default=decimal_encoder)

def get_count():
  filter_counts = create_dict(select_incidents_list)
  select_features, count = read_file(raw_filename, filter_counts)
  assert (filter_counts['unspecified'] == 0), 'unspecified incidents present!'
  return count


def write_main():
  count = get_count()
  filter_counts = create_dict(select_incidents_list)
  select_features, _ = read_file(raw_filename, filter_counts)
  assert (filter_counts['unspecified'] == 0), 'unspecified incidents present!'
  write_file(clean_filename, select_features)
  return count


if __name__ == '__main__':
  write_main()

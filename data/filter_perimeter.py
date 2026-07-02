'''
this program is to filter the raw, wfigs sourced .geojson 
it writes a new .geojson that contains only the features from the selected fires

not to be confused with clean_perimeter.py
'''

import ijson
import geopandas as gpd
from pathlib import Path
from shapely.geometry import shape

fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge', 'unspecified']
fires_perimeter_count = dict.fromkeys(fires_list, 0)
raw_filename = Path(__file__).resolve().parents[2] / 'WFIGS_INTERAGENCY_PERIMETERS_MASTER_DATA.geojson'
clean_filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'

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
      incident = properties.get('poly_IncidentName','') or ''
      incident = incident.lower()
      geometry = feature.get('geometry')


      if incident == '':
        filter_dict['unspecified'] += 1
      if incident in filter_dict.keys():
        filter_dict[incident] += 1
        row_data = properties.copy()
        row_data['geometry'] = shape(geometry)

        new_features.append(row_data)

  return new_features, (before_count, len(new_features))

'''
writes new .geojson file given a list of features
'''
def write_file(new_file, features):
  gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
  gdf.to_file(new_file, 'GEOJSON')


def get_count():
  filter_counts = dict.fromkeys(fires_list, 0)
  select_features, count = read_file(raw_filename, filter_counts)
  return count


def write_main():
  count = get_count()
  filter_counts = dict.fromkeys(fires_list, 0)
  select_features, _ = read_file(raw_filename, filter_counts)
  write_file(clean_filename, select_features)
  return count

if __name__ == '__main__':
  write_main()

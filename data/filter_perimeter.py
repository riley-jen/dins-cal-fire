import json
import ijson
import geopandas as gpd
from shapely.geometry import shape

fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge', 'unspecified']
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

  return new_features

raw_filename = '../../WFIGS_INTERAGENCY_PERIMETERS_MASTER_DATA.geojson'
select_features = read_file(raw_filename, fires_perimeter_count)

# print(fires_perimeter_count)
# assert (fires_perimeter_count['unspecified'] == 0), 'unspecified incidents present!'

'''
writes new .geojson file given a list of features
'''
def write_file(new_file, features):
  gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
  gdf.to_file(clean_filename, 'GEOJSON')

clean_filename = '../files/WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'
write_file(clean_filename, select_features)
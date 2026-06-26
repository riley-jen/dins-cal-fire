import geopandas as gpd


# --- PREP ---
filename = '../files/WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:4326', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)


# --- PERIMETER DATA ---
perimeter_index = {
  'palisades': 4,
  'mountain': 5,
  'eaton': 1, 
  'franklin': 1,
  'line': 5, 
  'bridge': 10
}


def get_perimeter_gdf(fire_name):
  fire_gdf = gdf_base[(gdf_base['poly_IncidentName'].str.lower()) == fire_name]
  return fire_gdf.iloc[[perimeter_index[fire_name]]]


# --- META FUNCTION ---
def get_data(fire_name):
  return {
    'perimeter_gdf': get_perimeter_gdf(fire_name),
  }

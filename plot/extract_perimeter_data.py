import geopandas as gpd
from pathlib import Path


# --- PREP ---
filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:4326', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)


# --- PERIMETER DATA ---
def get_perimeter_gdf(fire_name):
  fire_gdf = gdf_base[(gdf_base['poly_IncidentName'].str.lower()) == fire_name]

  if len(fire_gdf) == 0:
    return fire_gdf

  return fire_gdf.iloc[[0]]


# --- META FUNCTION ---
def get_data(fire_name):
  perimeter_gdf = get_perimeter_gdf(fire_name)

  return {
    'perimeter_gdf': perimeter_gdf,
  }

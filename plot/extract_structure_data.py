import geopandas as gpd
import pandas as pd
from pathlib import Path


# --- PREP ---
filename = Path(__file__).resolve().parent.parent / 'files' / 'POSTFIRE_CLEAN_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:3310', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)


# --- DAMAGE DATA ---
damage_list = ['no damage', 'affected (>0-10%)', 'minor (10-25%)', 'major (25-50%)', 'destroyed (>50%)', 'inaccessible']
color_code = ['green', 'yellow', 'orange', 'red', 'black', 'gray']
color_dict = dict(zip(damage_list, color_code))


def get_fire_gdf(fire_name):
  return gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]


def get_damage_data(fire_gdf):
  damage_count = {}
  damage_gdfs = {}

  for damage in damage_list:
    damage_gdf = fire_gdf[(fire_gdf['DAMAGE'].str.lower()) == damage]
    damage_count[damage] = len(damage_gdf)
    damage_gdfs[damage] = damage_gdf

  return {
    'damage_count': damage_count,
    'damage_gdfs': damage_gdfs,
    'total': len(fire_gdf),
  }


# --- MATERIAL DATA ---
materials = ['asphalt', 'composite', 'masonry', 'metal', 'tile', 'vinyl', 'wood', 'n/a']
building_elements = ['ROOFCONSTRUCTION', 'EXTERIORSIDING', 'DECKPORCHONGRADE', 'DECKPORCHELEVATED']
building_elements_display = ['material', 'roof', 'side', 'ground deck', 'elevated deck']


def get_material(string):
  clean_string = string.strip().lower().replace('/', ' ')
  
  for material in materials:
    if clean_string == material:
      return material
          
  if clean_string in ['masonry concrete', 'stucco brick cement', 'concrete']:
    return 'masonry'
  
  if 'no ' in clean_string or 'other' in clean_string or 'unknown' in clean_string:
    return 'n/a'
  
  return 'n/a'


def get_material_table(fire_gdf):
  table_values = {element: {material: 0 for material in materials} for element in building_elements}

  for element in building_elements:
    converted_material = fire_gdf[element].astype(str).apply(get_material)

    for material in materials:
      material_gdf = fire_gdf[converted_material == material]
      table_values[element][material] = len(material_gdf)

  df = pd.DataFrame(table_values)
  df_clean = df.reset_index()
  df_clean = df_clean.rename(columns={'index': 'Elements'})
  df_clean.columns = building_elements_display

  return df_clean


# --- META FUNCTION ---
def get_data(fire_name):
  fire_gdf = get_fire_gdf(fire_name)
  damage_data = get_damage_data(fire_gdf)

  return {
    'fire_gdf': fire_gdf,
    'damage_count': damage_data['damage_count'],
    'damage_gdfs': damage_data['damage_gdfs'],
    'total': damage_data['total'],
    'material_table': get_material_table(fire_gdf),
    'damage_list': damage_list,
    'color_code': color_code,
    'color_dict': color_dict,
  }

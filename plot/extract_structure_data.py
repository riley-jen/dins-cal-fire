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
damage_display_list = ['no damage', 'affected', 'minor', 'major', 'destroyed', 'inaccessible']
damage_display_dict = dict(zip(damage_list, damage_display_list))
color_code = ['green', 'gold', 'orange', 'red', 'black', 'gray']
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


def get_gdf_for_damages(damage_gdfs, displayed_damages):
  selected_gdfs = []

  for damage in damage_list:
    if damage in displayed_damages:
      selected_gdfs.append(damage_gdfs[damage])

  if len(selected_gdfs) == 0:
    first_damage = damage_list[0]
    return damage_gdfs[first_damage].iloc[0:0]

  return gpd.GeoDataFrame(pd.concat(selected_gdfs), crs=selected_gdfs[0].crs)


# --- MATERIAL DATA ---
materials = ['asphalt', 'composite', 'masonry', 'metal', 'tile', 'vinyl', 'wood', 'n/a']
building_elements = ['ROOFCONSTRUCTION', 'EXTERIORSIDING', 'DECKPORCHONGRADE', 'DECKPORCHELEVATED']
building_elements_display = ['material', 'roof', 'side', 'ground deck', 'elevated deck']
combustible_materials = ['asphalt', 'composite', 'vinyl', 'wood']
non_combustible_materials = ['masonry', 'metal', 'tile']


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


def get_material_table_for_damages(damage_gdfs, displayed_damages):
  damage_gdf = get_gdf_for_damages(damage_gdfs, displayed_damages)
  return get_material_table(damage_gdf)


# --- STRUCTURE ELEMENT DATA ---
structure_element_table_configs = [
  {
    'key': 'eaves_table',
    'columns': ['build', 'eaves'],
    'properties': ['EAVES'],
    'rows': ['enclosed', 'unenclosed', 'n/a'],
    'row_map': {
      'enclosed': 'enclosed',
      'unenclosed': 'unenclosed',
      'no eaves': 'n/a',
      'unknown': 'n/a',
    },
  },
  {
    'key': 'ventscreen_table',
    'columns': ['build', 'mesh screen'],
    'properties': ['VENTSCREEN'],
    'rows': ['<= 1/8"', '> 1/8"', 'unscreened', 'n/a'],
    'row_map': {
      'mesh screen <= 1/8"': '<= 1/8"',
      'mesh screen > 1/8"': '> 1/8"',
      'unscreened': 'unscreened',
      'no vents': 'n/a',
      'unknown': 'n/a',
    },
  },
  {
    'key': 'windowpane_table',
    'columns': ['build', 'window pane'],
    'properties': ['WINDOWPANE'],
    'rows': ['single pane', 'multi pane', 'n/a'],
    'row_map': {
      'single pane': 'single pane',
      'multi pane': 'multi pane',
      'no windows': 'n/a',
      'unknown': 'n/a',
    },
  },
  {
    'key': 'patio_fence_table',
    'columns': ['build', 'patio cover', 'fence'],
    'properties': ['PATIOCOVERCARPORT', 'FENCEATTACHEDTOSTRUCTURE'],
    'rows': ['combustible', 'non-combustible', 'n/a'],
    'row_map': {
      'combustible': 'combustible',
      'non combustible': 'non-combustible',
      'non-combustible': 'non-combustible',
      'no patio cover carport': 'n/a',
      'no patio cover/carport': 'n/a',
      'no fence': 'n/a',
      'unknown': 'n/a',
    },
  },
]


def clean_structure_element_value(value):
  return str(value).strip().lower()


def get_structure_element_row(value, config):
  clean_value = clean_structure_element_value(value)

  if clean_value in config['row_map']:
    return config['row_map'][clean_value]

  clean_value_no_slash = clean_value.replace('/', ' ')
  if clean_value_no_slash in config['row_map']:
    return config['row_map'][clean_value_no_slash]

  return 'n/a'


def get_structure_element_table(fire_gdf, config):
  table_values = {}

  for property_name in config['properties']:
    rows = {row: 0 for row in config['rows']}
    converted_values = fire_gdf[property_name].apply(lambda value: get_structure_element_row(value, config))

    for row in config['rows']:
      rows[row] = len(fire_gdf[converted_values == row])

    table_values[property_name] = rows

  df = pd.DataFrame(table_values)
  df_clean = df.reset_index()
  df_clean.columns = config['columns']

  return df_clean


def get_material_combustibility_counts(fire_gdf, property_name):
  converted_material = fire_gdf[property_name].astype(str).apply(get_material)

  return {
    'combustible': len(fire_gdf[converted_material.isin(combustible_materials)]),
    'non-combustible': len(fire_gdf[converted_material.isin(non_combustible_materials)]),
    'n/a': len(fire_gdf[converted_material == 'n/a']),
  }


def get_combustibility_table(fire_gdf):
  table_values = {
    'ROOFCONSTRUCTION': get_material_combustibility_counts(fire_gdf, 'ROOFCONSTRUCTION'),
    'EXTERIORSIDING': get_material_combustibility_counts(fire_gdf, 'EXTERIORSIDING'),
    'DECKPORCHONGRADE': get_material_combustibility_counts(fire_gdf, 'DECKPORCHONGRADE'),
    'DECKPORCHELEVATED': get_material_combustibility_counts(fire_gdf, 'DECKPORCHELEVATED'),
  }

  patio_fence_config = next(
    config for config in structure_element_table_configs
    if config['key'] == 'patio_fence_table'
  )
  for property_name in patio_fence_config['properties']:
    rows = {row: 0 for row in patio_fence_config['rows']}
    converted_values = fire_gdf[property_name].apply(lambda value: get_structure_element_row(value, patio_fence_config))

    for row in patio_fence_config['rows']:
      rows[row] = len(fire_gdf[converted_values == row])

    table_values[property_name] = rows

  df = pd.DataFrame(table_values)
  df_clean = df.reset_index()
  df_clean.columns = ['combustibility', 'roof', 'side', 'ground deck', 'elevated deck', 'patio cover', 'fence']

  return df_clean


def get_structure_element_tables(fire_gdf):
  tables = {}

  for config in structure_element_table_configs:
    if config['key'] == 'patio_fence_table':
      tables[config['key']] = get_combustibility_table(fire_gdf)
    else:
      tables[config['key']] = get_structure_element_table(fire_gdf, config)

  return tables


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
    'structure_element_tables': get_structure_element_tables(fire_gdf),
    'damage_list': damage_list,
    'damage_display_list': damage_display_list,
    'damage_display_dict': damage_display_dict,
    'color_code': color_code,
    'color_dict': color_dict,
  }

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# prep
filename = '../files/POSTFIRE_CLEAN_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:3310', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)

# --- fire filtering ---
materials = ["asphalt", "composite", "masonry", "metal", "tile", "vinyl", "wood", "n/a"]
building_elements = ["ROOFCONSTRUCTION", "EXTERIORSIDING", "DECKPORCHONGRADE", "DECKPORCHELEVATED"]
building_elements_display = ["material", "roof", "side", "ground deck", "elevated deck"]

table_values = {element: {material: 0 for material in materials} for element in building_elements}

def show_fire_material(table_ax, fire_name):
  fire_gdf = gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]
  
  # plot each color of points separately
  for element in building_elements:
    for material in materials:
      converted_material = fire_gdf[element].astype(str).apply(get_material)
      material_gdf = fire_gdf[converted_material == material]

      table_values[element][material] = len(material_gdf)

  df = gpd.pd.DataFrame(table_values)
  df_clean = df.reset_index()
  df_clean = df_clean.rename(columns={'index': 'Elements'})

  df_clean.columns = building_elements_display

  t = table_ax.table(
      cellText=df_clean.values,
      colLabels=df_clean.columns,
      loc='center',
      cellLoc='center'
  )
  t.auto_set_font_size(False)
  t.set_fontsize(10)
  t.scale(1.1, 1.3)

def get_material(string):
  # Convert to lowercase and strip whitespace for consistent matching
  clean_string = string.strip().lower().replace("/", " ")
  
  for material in materials:
    if clean_string == material:
      return material
          
  if clean_string in ["masonry concrete", "stucco brick cement", "concrete"]:
    return "masonry"
  
  if "no " in clean_string or "other" in clean_string or "unknown" in clean_string:
    return "n/a"
  
  print(string)
  return "n/a"
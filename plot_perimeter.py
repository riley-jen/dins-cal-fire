import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import contextily as ctx

# prep
filename = './WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:4326', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)

# # set basic features for the window
# fig, ax = plt.subplots(figsize=(8, 8))
# plt.subplots_adjust(bottom=0.15)

# --- fire filtering ---
perimeter_index = {
  'palisades': 4,
  'mountain': 5,
  'eaton': 1, 
  'franklin': 1,
  'line': 5, 
  'bridge': 10
}

# draw plot
def show_fire_perimeter(ax, fire_name, index):
  fire_gdf = gdf_base[(gdf_base['poly_IncidentName'].str.lower()) == fire_name]
  # fire_gdf = fire_gdf.iloc[[index]]
  fire_gdf = fire_gdf.iloc[[perimeter_index[fire_name]]]
  
  fire_gdf.plot(ax=ax, categorical=True, markersize=2, color='blue', alpha=0.3, zorder=3)
  
  # plt.draw()

def make_perimeter_buttons(dict, buttons):
  
  up_button_space = plt.axes([0.1, 0.15, 0.3, 0.05]) # left, bottom, width, height
  up_button = Button(up_button_space, '^')
  up_button.on_clicked(lambda event: change_index('up', dict))


  down_button_space = plt.axes([0.6, 0.15, 0.3, 0.05]) # left, bottom, width, height
  down_button = Button(down_button_space, 'v')
  down_button.on_clicked(lambda event: change_index('down', dict))

  buttons.append(up_button)
  buttons.append(down_button)

def change_index(direction, dict):
  global index
  if direction == 'up':
    dict['index'] += 1
  else:
    dict['index'] -= 1
  print(dict['index'])

# ax.set_aspect('equal')
# plt.show()
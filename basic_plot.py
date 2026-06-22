import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import contextily as ctx
from plot_perimeter import show_fire_perimeter, make_perimeter_buttons

# prep
filename = './POSTFIRE_CLEAN_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:3310', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)

# set basic features for the window
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.15)

# draw default layers
# gdf_base.plot(ax=ax, markersize=15, color='crimson', alpha=0.8, zorder=2)
# ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)

values = {"index":0}

# --- fire filtering ---
damage_list = ['no damage', 'affected (>0-10%)', 'minor (10-25%)', 'major (25-50%)', 'destroyed (>50%)', 'inaccessible']
color_code = ['green', 'yellow', 'orange', 'red', 'black', 'gray']
color_dict = dict(zip(damage_list, color_code))

# draw plot
def show_specific_fire(fire_name):
  ax.clear()
  fire_gdf = gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]
  i = values["index"]

  show_fire_perimeter(ax, fire_name, i)
  
  # plot each color of points separately
  for damage, color in color_dict.items():
    damage_gdf = fire_gdf[(fire_gdf['DAMAGE'].str.lower()) == damage]

    if len(damage_gdf) > 0:
      damage_gdf.plot(ax=ax, categorical=True, markersize=2, label=damage, color=color, alpha=0.8, zorder=2)
  ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  
  make_legend()
  apply_base_features()
  plt.draw()

# make legend
def make_legend():
  handles, labels = ax.get_legend_handles_labels()
  legend_lookup = dict(zip([label.lower() for label in labels], handles))

  sorted_handles = []
  sorted_labels = []
  
  for damage in damage_list:
    if damage in labels:
      sorted_labels.append(damage)
      sorted_handles.append(legend_lookup[damage])
    
  ax.legend(sorted_handles, sorted_labels, markerscale=3, title='Damage Rating', loc='upper right', frameon=True, facecolor='white')

buttons = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
nf = len(fires_list) # number of fires

# make buttons
def make_button(fire_index):
  fire_name = fires_list[fire_index]
  
  space = 0.025
  width = (1-(0.2+space*(nf-1)))/nf
  button_space = plt.axes([0.1+(width+space)*fire_index, 0.05, width, 0.05]) # left, bottom, width, height
  fire_btn = Button(button_space, fire_name)
  fire_btn.on_clicked(lambda event: show_specific_fire(fire_name))

  buttons.append(fire_btn)

for i in range(len(fires_list)):
  make_button(i)

make_perimeter_buttons(values, buttons)
# ------

# set basic features for the plot
def apply_base_features():
  ax.set_title('california fire')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)

apply_base_features()
plt.show()
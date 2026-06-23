import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import contextily as ctx

from plot_structure import show_fire_structure
from plot_perimeter import show_fire_perimeter, make_perimeter_buttons


# set basic features for the window
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.15)

fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
map_position = [0.06, 0.50, 0.66, 0.44] # left, bottom, width, height

# --- helper funcs ---
# draw plot
def plot_fire(fire_name):
  ax.clear()
  set_map_position(ax)

  show_fire_structure(ax, fire_name) # zorder 3
  show_fire_perimeter(ax, fire_name) # zorder 2
  ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  
  apply_base_features(fire_name)
  add_scale_bar(ax)
  plt.draw()

# keep the map in the upper-left part of the fixed-size window
def set_map_position(ax):
  ax.set_position(map_position)
  ax.set_aspect('auto')

# draw a small scale bar for the current map extent
def add_scale_bar(ax):
  x_min, x_max = ax.get_xlim()
  y_min, y_max = ax.get_ylim()
  map_width = x_max - x_min
  map_height = y_max - y_min
  scale_length = max([length for length in 
    [30.48, 76.2, 152.4, 304.8, 804.672, 1609.344, 8046.72, 16093.44, 80467.2] 
    if length <= map_width / 4] or [30.48])
  x_start = x_min + map_width * 0.08
  y_start = y_min + map_height * 0.08
  x_end = x_start + scale_length
  label = str(int(scale_length / 1609.344)) + ' mi' if scale_length >= 1609.344 else str(int(scale_length / 0.3048)) + ' ft'

  ax.plot([x_start, x_end], [y_start, y_start], color='black', linewidth=3, zorder=4)
  ax.text((x_start + x_end) / 2, y_start + map_height * 0.02, label, ha='center', va='bottom', color='black', 
    fontsize=9, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2), zorder=4)

# make buttons
def make_fire_buttons(buttons, fires_list):
  nf = len(fires_list)

  for i in range(len(fires_list)):
    fire_name = fires_list[i]
    
    space = 0.025
    width = (1-(0.2+space*(nf-1)))/nf
    button_space = plt.axes([0.1+(width+space)*i, 0.05, width, 0.05]) # left, bottom, width, height
    fire_btn = Button(button_space, fire_name)
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire(name))

    buttons.append(fire_btn)
  
  return buttons

# set basic features for the plot
def apply_base_features(fire_name = ""):
  set_map_position(ax)
  if fire_name != "":
    ax.set_title('california fire: ' + fire_name)
  else:
    ax.set_title('california fire')
  ax.get_xaxis().set_visible(False)
  ax.get_yaxis().set_visible(False)
# ------
buttons = []
make_fire_buttons(buttons, fires_list)

apply_base_features()
plt.show()

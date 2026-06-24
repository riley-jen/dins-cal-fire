import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import contextily as ctx
import math

from plot_structure import show_fire_structure
from plot_perimeter import show_fire_perimeter, make_perimeter_buttons


# set basic features for the window
fig = plt.figure(figsize=(8, 8))
plt.subplots_adjust(bottom=0.15)

fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']

map_position = [0.06, 0.50, 0.66, 0.44] # left, bottom, width, height
map_ax = fig.add_axes(map_position)

pie_position = [0.06, 0.15, 0.44, 0.3]
pie_ax = fig.add_axes(pie_position)

# --- MAIN FUNCTIONS ---
# draw plots
def plot_fire(fire_name):
  map_ax.clear()
  pie_ax.clear()

  set_map_position(map_ax)
  show_fire_structure(map_ax, pie_ax, fire_name) # zorder 3
  show_fire_perimeter(map_ax, fire_name) # zorder 2
  fit_map_bounds(map_ax)
  ctx.add_basemap(map_ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  
  add_scale_bar(map_ax)
  apply_map_base_features(fire_name)
  apply_pie_base_features()
  plt.draw()

# make buttons for selecting fire
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

# --- HELPER FUNCTIONS ---

# set basic features for the plot
def apply_map_base_features(fire_name = ""):
  if fire_name != "":
    map_ax.set_title('california fire: ' + fire_name)
  else:
    map_ax.set_title('california fire')
  map_ax.get_xaxis().set_visible(False)
  map_ax.get_yaxis().set_visible(False)

def apply_pie_base_features(fire_name = ""):
  pie_ax.set_title('damaged structures distribution')
  pie_ax.get_xaxis().set_visible(False)
  pie_ax.get_yaxis().set_visible(False)

# keep the map in the upper-left part of the fixed-size window
def set_map_position(ax):
  ax.set_position(map_position)
  ax.set_aspect('equal', adjustable='box')

# expand the map bounds to fit the fixed rectangular map area without stretching
def fit_map_bounds(ax):
  x_min, x_max = ax.get_xlim()
  y_min, y_max = ax.get_ylim()
  x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
  width, height = x_max - x_min, y_max - y_min
  target_ratio = map_position[2] / map_position[3]

  if width / height < target_ratio:
    width = height * target_ratio
  else:
    height = width / target_ratio

  ax.set_xlim(x_center - width / 2, x_center + width / 2)
  ax.set_ylim(y_center - height / 2, y_center + height / 2)

# draw a small scale bar for the current map extent
def add_scale_bar(ax):
  x_min, x_max = ax.get_xlim()
  y_min, y_max = ax.get_ylim()
  map_width = x_max - x_min
  map_height = y_max - y_min
  center_lat = math.atan(math.sinh(((y_min + y_max) / 2) / 6378137))
  projection_scale = 1 / math.cos(center_lat)
  scale_length = max([length for length in
    [30.48, 76.2, 152.4, 304.8, 804.672, 1609.344, 8046.72, 16093.44, 80467.2] 
    if length * projection_scale <= map_width / 4] or [30.48])
  projected_length = scale_length * projection_scale
  x_start = x_min + map_width * 0.08
  y_start = y_min + map_height * 0.08
  x_end = x_start + projected_length
  label = str(int(scale_length / 1609.344)) + ' mi' if scale_length >= 1609.344 else str(int(scale_length / 0.3048)) + ' ft'

  ax.plot([x_start, x_end], [y_start, y_start], color='black', linewidth=3, zorder=4)
  ax.text((x_start + x_end) / 2, y_start + map_height * 0.02, label, ha='center', va='bottom', color='black', 
    fontsize=9, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2), zorder=4)
# ------

buttons = []
make_fire_buttons(buttons, fires_list)
fit_map_bounds(map_ax)

apply_map_base_features()
apply_pie_base_features()
plt.show()

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
map_position = [0.06, 0.50, 0.44, 0.44] # left, bottom, width, height

# --- helper funcs ---
# draw plot
def plot_fire(fire_name):
  ax.clear()

  show_fire_structure(ax, fire_name) # zorder 3
  show_fire_perimeter(ax, fire_name) # zorder 2
  set_square_map_extent(ax)
  ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  
  apply_base_features(fire_name)
  plt.draw()

# keep the map in a fixed square in the top left corner
def set_square_map_position(ax):
  ax.set_position(map_position)
  ax.set_aspect('equal', adjustable='box')

# keep the plotted map extent square, even if the data is wider or taller
def set_square_map_extent(ax):
  x_min, x_max = ax.get_xlim()
  y_min, y_max = ax.get_ylim()

  x_center = (x_min + x_max) / 2
  y_center = (y_min + y_max) / 2
  width = x_max - x_min
  height = y_max - y_min
  side_length = max(width, height)

  if side_length == 0:
    side_length = 1000

  side_length *= 1.1
  half_side = side_length / 2

  ax.set_xlim(x_center - half_side, x_center + half_side)
  ax.set_ylim(y_center - half_side, y_center + half_side)
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
  set_square_map_position(ax)
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

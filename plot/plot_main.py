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

# --- helper funcs ---
# draw plot
def plot_fire(fire_name):
  ax.clear()

  show_fire_structure(ax, fire_name) # zorder 3
  show_fire_perimeter(ax, fire_name) # zorder 2
  ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  
  apply_base_features(fire_name)
  plt.draw()

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
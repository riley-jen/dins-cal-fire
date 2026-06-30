import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import extract_structure_data
import extract_perimeter_data
from damage.plot_map import make_perimeter_buttons, show_fire_map
from damage.plot_pie import show_damage_pie

# --- VARIABLES ---
fig = None
buttons = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']

map_position = [0.06, 0.50, 0.66, 0.44] # left, bottom, width, height
map_ax = None

pie_position = [0.7, 0.1, 0.24, 0.38]
pie_ax = None

current_fire_name = ''
perimeter_state = {'index': 0, 'max_index': 0}


# --- MAIN FUNCTIONS ---
# draw plots
def plot_fire(fire_name, reset_perimeter=True):
  global current_fire_name

  current_fire_name = fire_name

  map_ax.clear()
  pie_ax.clear()

  structure_data = extract_structure_data.get_data(fire_name)
  perimeter_data = extract_perimeter_data.get_data(fire_name)
  perimeter_state['max_index'] = max(perimeter_data['total'] - 1, 0)

  if reset_perimeter:
    perimeter_state['index'] = 0
  else:
    perimeter_state['index'] = min(perimeter_state['index'], perimeter_state['max_index'])

  show_fire_map(map_ax, structure_data, perimeter_data, map_position, perimeter_state['index'])
  show_damage_pie(pie_ax, structure_data)
  
  apply_base_features(fire_name)
  plt.draw()

# make buttons for selecting fire
def make_fire_buttons(buttons, fires_list):
  nf = len(fires_list)

  for i in range(len(fires_list)):
    fire_name = fires_list[i]
    
    space = 0.025
    width = (1-(0.2+space*(nf-1)))/nf
    button_space = fig.add_axes([0.1+(width+space)*i, 0.05, width, 0.05]) # left, bottom, width, height
    fire_btn = Button(button_space, fire_name)
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire(name, reset_perimeter=True))

    buttons.append(fire_btn)
  
  return buttons


def replot_current_fire():
  if current_fire_name == '':
    return
  
  plot_fire(current_fire_name, reset_perimeter=False)


# --- HELPER FUNCTIONS ---

# set basic features for all plots
def apply_base_features(fire_name = ''):
  if fire_name != '':
    map_ax.set_title('california fire: ' + fire_name)
    pie_ax.set_title('damaged structures\ndistribution')
  else:
    map_ax.set_title('california fire')

  map_ax.get_xaxis().set_visible(False)
  map_ax.get_yaxis().set_visible(False)

  pie_ax.axis('off')

# --- SET UP ---

def make_damage_window(input_figure):
  global fig, map_ax, pie_ax, buttons
  fig = input_figure

  fig.canvas.manager.set_window_title('Damage Window')
  map_ax = fig.add_axes(map_position)
  pie_ax = fig.add_axes(pie_position)
  
  buttons = []
  make_fire_buttons(buttons, fires_list)
  make_perimeter_buttons(perimeter_state, buttons, replot_current_fire)

  apply_base_features()

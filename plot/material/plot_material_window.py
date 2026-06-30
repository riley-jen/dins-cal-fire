import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import extract_structure_data
from material.plot_material import show_fire_material


# --- VARIABLES ---
fig = None
material_ax = None
buttons = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
structure_data_by_fire = {}

table_position = [0.06, 0.1, 0.6, 0.38]


# --- MAIN FUNCTIONS ---
def preload_data():
  for fire_name in fires_list:
    structure_data_by_fire[fire_name] = extract_structure_data.get_data(fire_name)


def plot_fire_material(fire_name):
  material_ax.clear()

  structure_data = structure_data_by_fire[fire_name]
  show_fire_material(material_ax, structure_data)

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
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire_material(name))

    buttons.append(fire_btn)
  
  return buttons


# --- HELPER FUNCTIONS ---

def apply_base_features(fire_name = ''):
  if fire_name != '':
    material_ax.set_title('structural composition and material', y=0.85)

  material_ax.axis('off')


# --- SET UP ---

def make_material_window(input_figure):
  global fig, material_ax, buttons
  preload_data()

  fig = input_figure

  fig.canvas.manager.set_window_title('Material Window')
  material_ax = fig.add_axes(table_position)
  
  buttons = []
  make_fire_buttons(buttons, fires_list)

  apply_base_features()

import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import extract_structure_data
from material.plot_material import show_fire_material


# --- VARIABLES ---
fig = None
material_ax = None
buttons = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']

table_position = [0.06, 0.1, 0.6, 0.38]


# --- MAIN FUNCTIONS ---

def plot_fire_material(fire_name):
  material_ax.clear()

  structure_data = extract_structure_data.get_data(fire_name)
  show_fire_material(material_ax, structure_data)

  apply_base_features(fire_name)
  plt.draw()


# --- HELPER FUNCTIONS ---

def apply_base_features(fire_name = ''):
  if fire_name != '':
    material_ax.set_title('structural composition and material', y=0.85)

  material_ax.axis('off')


# --- SET UP ---

def make_material_window(input_figure):
  global fig, material_ax, buttons
  fig = input_figure

  fig.canvas.manager.set_window_title('Material Window')
  material_ax = fig.add_axes(table_position)
  
  buttons = []
  make_fire_buttons(buttons, fires_list)

  apply_base_features()

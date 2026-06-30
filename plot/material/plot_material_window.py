import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons

import extract_structure_data
from material.plot_material import show_fire_material


# --- VARIABLES ---
fig = None
material_ax = None
buttons = []
damage_boxes = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
structure_data_by_fire = {}
displayed_damages = extract_structure_data.damage_list.copy()
current_fire_name = None

table_position = [0.06, 0.1, 0.6, 0.38]


# --- MAIN FUNCTIONS ---
def preload_data():
  for fire_name in fires_list:
    structure_data_by_fire[fire_name] = extract_structure_data.get_data(fire_name)


def plot_fire_material(fire_name, displayed_damages):
  global current_fire_name
  current_fire_name = fire_name

  material_ax.clear()

  structure_data = structure_data_by_fire[fire_name]
  filtered_structure_data = structure_data.copy()
  filtered_structure_data['material_table'] = extract_structure_data.get_material_table_for_damages(
    structure_data['damage_gdfs'],
    displayed_damages
  )

  show_fire_material(material_ax, filtered_structure_data)

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
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire_material(name, displayed_damages))

    buttons.append(fire_btn)
  
  return buttons

def make_damage_boxes(boxes, damage_list):
  nd = len(damage_list)
    
  for i in range(len(damage_list)):
    damage = damage_list[i]

    space = 0.01
    width = (1-(0.2+space*(nd-1)))/nd
    box_space = fig.add_axes([0.1+(width+space)*i, 0.9, width, 0.05]) # left, bottom, width, height
    damage_box = CheckButtons(box_space, [damage], [damage in displayed_damages])
    damage_box.labels[0].set_color(extract_structure_data.color_dict[damage])
    damage_box.on_clicked(lambda label, name=damage: toggle_damage(name))

    boxes.append(damage_box)

  return boxes


def toggle_damage(damage):
  if damage in displayed_damages:
    displayed_damages.remove(damage)
  else:
    displayed_damages.append(damage)

  if current_fire_name is not None:
    plot_fire_material(current_fire_name, displayed_damages)


# --- HELPER FUNCTIONS ---

def apply_base_features(fire_name = ''):
  if fire_name != '':
    material_ax.set_title('structural composition and material', y=0.85)

  material_ax.axis('off')


# --- SET UP ---

def make_material_window(input_figure):
  global fig, material_ax, buttons, damage_boxes
  preload_data()

  fig = input_figure

  fig.canvas.manager.set_window_title('Material Window')
  material_ax = fig.add_axes(table_position)
  
  buttons = []
  damage_boxes = []
  make_damage_boxes(damage_boxes, extract_structure_data.damage_list)
  make_fire_buttons(buttons, fires_list)

  apply_base_features()

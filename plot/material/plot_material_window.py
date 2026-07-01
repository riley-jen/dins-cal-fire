'''
this program creates the interactive material window
it wires together fire buttons, damage checkboxes, and the material tables
'''

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons

import extract_structure_data
from material.plot_table import show_fire_material, show_structure_element_table


# --- VARIABLES ---
fig = None
material_ax = None
structure_element_axes = {}
total_text = None
buttons = []
damage_boxes = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
structure_data_by_fire = {}
displayed_damages = extract_structure_data.damage_list.copy()
current_fire_name = None

table_position = [0.1, 0.55, 0.8, 0.34]
structure_element_table_positions = {
  'patio_fence_table': [0.1, 0.465, 0.8, 0.080],
  'eaves_table': [0.64, 0.355, 0.30, 0.080],
  'ventscreen_table': [0.64, 0.240, 0.30, 0.095],
  'windowpane_table': [0.64, 0.140, 0.30, 0.080],
}


# --- MAIN FUNCTIONS ---
'''
loads structure data for all fires before any buttons are clicked
this keeps the window from rereading the geojson on every redraw
'''
def preload_data():
  for fire_name in fires_list:
    structure_data_by_fire[fire_name] = extract_structure_data.get_data(fire_name)


'''
redraws all material-window tables for one fire and selected damages
this is called when a fire button or damage checkbox changes
'''
def plot_fire_material(fire_name, displayed_damages):
  global current_fire_name
  current_fire_name = fire_name

  material_ax.clear()
  clear_structure_element_axes()

  structure_data = structure_data_by_fire[fire_name]
  displayed_gdf = extract_structure_data.get_gdf_for_damages(
    structure_data['damage_gdfs'],
    displayed_damages
  )
  filtered_structure_data = structure_data.copy()
  filtered_structure_data['material_table'] = extract_structure_data.get_material_table(displayed_gdf)
  filtered_structure_data['structure_element_tables'] = extract_structure_data.get_structure_element_tables(displayed_gdf)

  # both table groups use the same filtered structures
  show_fire_material(material_ax, filtered_structure_data)
  show_structure_element_tables(filtered_structure_data)

  update_total_count(len(displayed_gdf))
  apply_base_features(fire_name)
  plt.draw()

'''
makes buttons for selecting fire
each button redraws the window with the current damage filters
'''
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

'''
makes checkboxes for filtering by damage type
the checkbox label color matches the damage color
'''
def make_damage_boxes(boxes, damage_list):
  nd = len(damage_list)
    
  for i in range(len(damage_list)):
    damage = damage_list[i]

    space = 0.01
    width = (1-(0.2+space*(nd-1)))/nd
    box_space = fig.add_axes([0.1+(width+space)*i, 0.9, width, 0.05]) # left, bottom, width, height
    box_space.set_frame_on(False)
    box_space.set_xticks([])
    box_space.set_yticks([])

    display_name = extract_structure_data.damage_display_dict[damage]
    damage_box = CheckButtons(box_space, [display_name], [damage in displayed_damages])
    damage_box.labels[0].set_color(extract_structure_data.color_dict[damage])
    damage_box.on_clicked(lambda label, name=damage: toggle_damage(name))

    boxes.append(damage_box)

  return boxes


'''
turns one damage filter on or off
if a fire is already selected, the window redraws right away
'''
def toggle_damage(damage):
  if damage in displayed_damages:
    displayed_damages.remove(damage)
  else:
    displayed_damages.append(damage)

  if current_fire_name is not None:
    plot_fire_material(current_fire_name, displayed_damages)


# --- HELPER FUNCTIONS ---

'''
updates the total structure count shown at the top of the window
the count changes with fire and damage filters
'''
def update_total_count(total):
  total_text.set_text('total structures: ' + str(total))

'''
applies titles and turns axes off after drawing tables
matplotlib tables still need axes, even though the axes are hidden
'''
def apply_base_features(fire_name = ''):
  if fire_name != '':
    material_ax.set_title('structural composition and material', y=0.85)

  material_ax.axis('off')

  for table_ax in structure_element_axes.values():
    table_ax.axis('off')


'''
clears the smaller structure element table axes
this prevents old table text from staying behind on redraw
'''
def clear_structure_element_axes():
  for table_ax in structure_element_axes.values():
    table_ax.clear()


'''
draws the combustibility and structure element tables
the order follows the position dictionary at the top of the file
'''
def show_structure_element_tables(structure_data):
  for table_key in structure_element_table_positions:
    df_clean = structure_data['structure_element_tables'][table_key]
    show_structure_element_table(
      structure_element_axes[table_key],
      df_clean
    )


# --- SET UP ---

'''
sets up the material window on the given figure
this creates axes, buttons, checkboxes, and the initial empty layout
'''
def make_material_window(input_figure):
  global fig, material_ax, structure_element_axes, total_text, buttons, damage_boxes
  preload_data()

  fig = input_figure

  fig.canvas.manager.set_window_title('Material Window')
  total_text = fig.text(0.5, 0.985, 'total structures: 0', ha='center', va='top', fontsize=13)
  material_ax = fig.add_axes(table_position)
  structure_element_axes = {
    table_key: fig.add_axes(position)
    for table_key, position in structure_element_table_positions.items()
  }
  
  buttons = []
  damage_boxes = []
  make_damage_boxes(damage_boxes, extract_structure_data.damage_list)
  make_fire_buttons(buttons, fires_list)

  apply_base_features()

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons

import extract_structure_data
import extract_perimeter_data
from subplot.plot_bar import show_material_bar_chart
from subplot.plot_map import show_fire_map
from subplot.plot_pie import show_damage_pie
from subplot.plot_table import show_fire_material, show_structure_element_table


# --- VARIABLES ---
fig = None
buttons = []
damage_boxes = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
structure_data_by_fire = {}
perimeter_data_by_fire = {}
displayed_damages = extract_structure_data.damage_list.copy()
current_fire_name = None

map_ax = None
pie_ax = None
material_ax = None
bar_ax = None
structure_element_axes = {}
structural_elements_text = None

damage_map_position = [0.03, 0.50, 0.33, 0.44]
damage_pie_position = [0.35, 0.1, 0.12, 0.38]
pie_legend_anchor = [0.48, 0.5]
damage_button_left = 0.05
damage_button_bottom = 0.05
damage_button_space = 0.0125
damage_button_width = 0.05625
damage_box_left = 0.37
damage_box_top = 0.91
damage_box_width = 0.11
damage_box_height = 0.035
damage_box_space = 0.006

material_table_position = [0.55, 0.55, 0.4, 0.34]
material_bar_position = [0.575, 0.155, 0.23, 0.28]
material_structure_element_table_positions = {
  'patio_fence_table': [0.55, 0.465, 0.4, 0.080],
  'eaves_table': [0.82, 0.355, 0.15, 0.080],
  'ventscreen_table': [0.82, 0.240, 0.15, 0.095],
  'windowpane_table': [0.82, 0.140, 0.15, 0.080],
}
structural_elements_position = [0.75, 0.985]


# --- MAIN FUNCTIONS ---
def preload_data():
  for fire_name in fires_list:
    structure_data_by_fire[fire_name] = extract_structure_data.get_data(fire_name)
    perimeter_data_by_fire[fire_name] = extract_perimeter_data.get_data(fire_name)


def plot_fire(fire_name):
  global current_fire_name
  current_fire_name = fire_name

  plot_fire_damage(fire_name)
  plot_fire_material(fire_name)
  plt.draw()


def plot_fire_damage(fire_name):
  map_ax.clear()
  pie_ax.clear()

  structure_data = structure_data_by_fire[fire_name]
  perimeter_data = perimeter_data_by_fire[fire_name]

  show_fire_map(map_ax, structure_data, perimeter_data, damage_map_position)
  show_damage_pie(pie_ax, structure_data, pie_legend_anchor)
  apply_damage_features(fire_name)


def plot_fire_material(fire_name):
  material_ax.clear()
  bar_ax.clear()
  clear_structure_element_axes()

  structure_data = structure_data_by_fire[fire_name]
  displayed_gdf = extract_structure_data.get_gdf_for_damages(
    structure_data['damage_gdfs'],
    displayed_damages
  )
  filtered_structure_data = structure_data.copy()
  filtered_structure_data['material_table'] = extract_structure_data.get_material_table(displayed_gdf)
  filtered_structure_data['structure_element_tables'] = extract_structure_data.get_structure_element_tables(displayed_gdf)

  show_fire_material(material_ax, filtered_structure_data)
  show_material_bar_chart(bar_ax, filtered_structure_data)
  show_structure_element_tables(filtered_structure_data)

  apply_material_features(fire_name)


def make_fire_buttons(buttons, fires_list):
  for i in range(len(fires_list)):
    fire_name = fires_list[i]

    button_space = fig.add_axes([
      damage_button_left + (damage_button_width + damage_button_space) * i,
      damage_button_bottom,
      damage_button_width,
      0.05,
    ])
    fire_btn = Button(button_space, fire_name)
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire(name))

    buttons.append(fire_btn)

  return buttons


def make_damage_boxes(boxes, damage_list):
  for i in range(len(damage_list)):
    damage = damage_list[i]

    box_space = fig.add_axes([
      damage_box_left,
      damage_box_top - (damage_box_height + damage_box_space) * i,
      damage_box_width,
      damage_box_height,
    ])
    box_space.set_frame_on(False)
    box_space.set_xticks([])
    box_space.set_yticks([])

    display_name = extract_structure_data.damage_display_dict[damage]
    damage_box = CheckButtons(box_space, [display_name], [damage in displayed_damages])
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
    plot_fire_material(current_fire_name)
    plt.draw()


def apply_damage_features(fire_name = ''):
  if fire_name != '':
    map_ax.set_title('california fire: ' + fire_name)
    pie_ax.set_title('damaged structures\ndistribution')
  else:
    map_ax.set_title('california fire')

  map_ax.get_xaxis().set_visible(False)
  map_ax.get_yaxis().set_visible(False)

  pie_ax.axis('off')


def apply_material_features(fire_name = ''):
  if fire_name != '':
    material_ax.set_title('structural composition and material', y=0.85)

  material_ax.axis('off')

  for table_ax in structure_element_axes.values():
    table_ax.axis('off')


def clear_structure_element_axes():
  for table_ax in structure_element_axes.values():
    table_ax.clear()


def show_structure_element_tables(structure_data):
  for table_key in material_structure_element_table_positions:
    df_clean = structure_data['structure_element_tables'][table_key]
    show_structure_element_table(
      structure_element_axes[table_key],
      df_clean
    )


# --- SET UP ---
def make_main_window(input_figure):
  global fig, map_ax, pie_ax, material_ax, bar_ax, structure_element_axes
  global structural_elements_text, buttons, damage_boxes

  preload_data()

  fig = input_figure

  fig.canvas.manager.set_window_title('Damage Window')
  structural_elements_text = fig.text(
    structural_elements_position[0],
    structural_elements_position[1],
    'structural elements',
    ha='center',
    va='top',
    fontsize=13,
  )
  map_ax = fig.add_axes(damage_map_position)
  pie_ax = fig.add_axes(damage_pie_position)
  material_ax = fig.add_axes(material_table_position)
  bar_ax = fig.add_axes(material_bar_position)
  structure_element_axes = {
    table_key: fig.add_axes(position)
    for table_key, position in material_structure_element_table_positions.items()
  }

  buttons = []
  damage_boxes = []
  make_damage_boxes(damage_boxes, extract_structure_data.damage_list)
  make_fire_buttons(buttons, fires_list)

  apply_damage_features()
  apply_material_features()
  bar_ax.axis('off')


main_fig = plt.figure(figsize=(16, 8))
make_main_window(main_fig)

plt.show()

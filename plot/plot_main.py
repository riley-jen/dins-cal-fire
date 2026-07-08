import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons

import extract_structure_data
import extract_perimeter_data
from subplot.plot_bar import show_material_bar_chart
from subplot.plot_map import show_fire_map
from subplot.plot_pie import show_damage_pie
from subplot.plot_sampling import show_sampling_scatter
from subplot.plot_table import show_combustibility_table, show_table, show_structure_element_table


# --- VARIABLES ---
fig = None
buttons = []
display_buttons = []
damage_boxes = []
fires_list = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
structure_data_by_fire = {}
perimeter_data_by_fire = {}
displayed_damages = extract_structure_data.damage_list.copy()
current_fire_name = None
current_display = 'table'

map_ax = None
pie_ax = None
sampling_ax = None
table_ax = None
bar_ax = None
combustibility_ax = None
structure_element_axes = {}

damage_map_position = [0.03, 0.50, 0.33, 0.44]
damage_pie_position = [0.35, 0.1, 0.12, 0.38]
damage_sampling_position = [0.075, 0.15, 0.27, 0.28]
pie_legend_anchor = [0.37, 0.5]

table_position = [0.55, 0.465, 0.4, 0.34]
material_bar_position = [0.525, 0.2, 0.275, 0.28]
combustibility_table_position = [0.55, 0.83, 0.4, 0.080]
material_structure_element_table_positions = {
  'eaves_table': [0.82, 0.355, 0.15, 0.080],
  'ventscreen_table': [0.82, 0.240, 0.15, 0.095],
  'windowpane_table': [0.82, 0.140, 0.15, 0.080],
}
display_button_names = ['table', 'bar chart']


# --- MAIN FUNCTIONS ---
def preload_data():
  for fire_name in fires_list:
    structure_data_by_fire[fire_name] = extract_structure_data.get_data(fire_name)
    perimeter_data_by_fire[fire_name] = extract_perimeter_data.get_data(fire_name)


def plot_fire(fire_name):
  global current_fire_name
  current_fire_name = fire_name

  map_ax.clear()
  pie_ax.clear()
  sampling_ax.clear()
  table_ax.clear()
  bar_ax.clear()
  combustibility_ax.clear()
  clear_structure_element_axes()

  structure_data = structure_data_by_fire[fire_name]
  perimeter_data = perimeter_data_by_fire[fire_name]

  show_fire_map(map_ax, structure_data, perimeter_data, damage_map_position, displayed_damages)
  show_damage_pie(pie_ax, structure_data, pie_legend_anchor, displayed_damages)
  show_sampling_scatter(sampling_ax, fire_name)
  apply_damage_features(fire_name)
  displayed_gdf = extract_structure_data.get_gdf_for_damages(
    structure_data['damage_gdfs'],
    displayed_damages
  )
  filtered_structure_data = structure_data.copy()
  filtered_structure_data['material_table'] = extract_structure_data.get_material_table(displayed_gdf)
  filtered_structure_data['structure_element_tables'] = extract_structure_data.get_structure_element_tables(displayed_gdf)

  show_table(table_ax, filtered_structure_data)
  show_material_bar_chart(bar_ax, filtered_structure_data)
  show_combustibility_table(combustibility_ax, filtered_structure_data)
  show_structure_element_tables(filtered_structure_data)

  apply_material_features(fire_name)
  plt.draw()


def make_fire_buttons(buttons, fires_list):
  nf = len(fires_list)

  for i in range(len(fires_list)):
    fire_name = fires_list[i]

    space = 0.025
    width = (1-(0.5+space*(nf-1)))/nf
    button_space = fig.add_axes([0.25+(width+space)*i, 0.04, width, 0.05]) # left, bottom, width, height
    
    fire_btn = Button(button_space, fire_name)
    fire_btn.on_clicked(lambda event, name=fire_name: plot_fire(name))

    buttons.append(fire_btn)
  return buttons


def make_display_buttons(buttons):
  nf = len(fires_list)
  space = 0.025
  width = (1-(0.5+space*(nf-1)))/nf

  for i in range(len(display_button_names)):
    display_name = display_button_names[i]
    button_space = fig.add_axes([0.825+(width+space)*i, 0.93, width, 0.05])

    display_btn = Button(button_space, display_name)
    display_btn.label.set_fontsize(9)
    display_btn.on_clicked(lambda event, name=display_name: set_display_mode(name))

    buttons.append(display_btn)

  return buttons


def make_damage_boxes(boxes, damage_list):
  for i in range(len(damage_list)):
    damage = damage_list[i]
    box_space = fig.add_axes([0.37, 0.91 - (0.035 + 0.006)*i, 0.11, 0.035])
    box_space.set_frame_on(False)
    box_space.set_xticks([])
    box_space.set_yticks([])

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
    plot_fire(current_fire_name)


def apply_damage_features(fire_name = ''):
  if fire_name != '':
    map_ax.set_title(fire_name + ' fire structures map')
    pie_ax.set_title('damaged structures\ndistribution')
  else:
    map_ax.set_title('california fire')

  map_ax.get_xaxis().set_visible(False)
  map_ax.get_yaxis().set_visible(False)

  pie_ax.axis('off')

  if fire_name == '':
    sampling_ax.axis('off')


def apply_material_features(fire_name = ''):
  if fire_name != '':
    table_ax.set_title('structural composition and material', y=0.85)
    pass

  table_ax.axis('off')
  combustibility_ax.axis('off')

  for structure_element_ax in structure_element_axes.values():
    structure_element_ax.axis('off')

  update_display_button_features()


def update_display_button_features():
  for display_btn in display_buttons:
    if display_btn.label.get_text() == current_display:
      display_btn.ax.set_facecolor('0.85')
    else:
      display_btn.ax.set_facecolor('0.95')


def clear_structure_element_axes():
  for structure_element_ax in structure_element_axes.values():
    structure_element_ax.clear()


def show_structure_element_tables(structure_data):
  for table_key in material_structure_element_table_positions:
    df_clean = structure_data['structure_element_tables'][table_key]
    show_structure_element_table(
      structure_element_axes[table_key],
      df_clean
    )
    if table_key == 'eaves_table':
      structure_element_axes[table_key].set_title('building properties')


# --- SET UP ---
def make_main_window(input_figure):
  global fig, map_ax, pie_ax, sampling_ax, table_ax, combustibility_ax, structure_element_axes
  global buttons, display_buttons, damage_boxes

  preload_data()

  fig = input_figure

  fig.canvas.manager.set_window_title('cal fire structure data')

  map_ax = fig.add_axes(damage_map_position)
  pie_ax = fig.add_axes(damage_pie_position)
  sampling_ax = fig.add_axes(damage_sampling_position)
  table_ax = fig.add_axes(table_position)
  bar_ax = fig.add_axes(material_bar_position)
  combustibility_ax = fig.add_axes(combustibility_table_position)
  structure_element_axes = {
    table_key: fig.add_axes(position)
    for table_key, position in material_structure_element_table_positions.items()
  }

  buttons = []
  display_buttons = []
  damage_boxes = []
  make_damage_boxes(damage_boxes, extract_structure_data.damage_list)
  make_fire_buttons(buttons, fires_list)
  make_display_buttons(display_buttons)

  apply_damage_features()
  apply_material_features()
  bar_ax.axis('off')


main_fig = plt.figure(figsize=(16, 8))
make_main_window(main_fig)

plt.show()

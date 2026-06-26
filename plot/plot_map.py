import contextily as ctx
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


# --- MAIN FUNCTIONS ---
def show_fire_map(map_ax, structure_data, perimeter_data, map_position):
  set_map_position(map_ax, map_position)
  show_fire_structures(map_ax, structure_data)
  show_fire_perimeter(map_ax, perimeter_data)
  fit_map_bounds(map_ax, map_position)
  ctx.add_basemap(map_ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)
  add_scale_bar(map_ax)


# --- STRUCTURE LAYER ---
def show_fire_structures(map_ax, structure_data):
  damage_gdfs = structure_data['damage_gdfs']
  color_dict = structure_data['color_dict']

  for damage, color in color_dict.items():
    damage_gdf = damage_gdfs[damage]

    if len(damage_gdf) > 0:
      damage_gdf.plot(ax=map_ax, categorical=True, markersize=2, label=damage, color=color, alpha=0.8, zorder=2)

  make_map_legend(map_ax, structure_data['damage_list'])


def make_map_legend(ax, damage_list):
  handles, labels = ax.get_legend_handles_labels()
  legend_lookup = dict(zip([label.lower() for label in labels], handles))

  sorted_handles = []
  sorted_labels = []
  
  for damage in damage_list:
    if damage in labels:
      sorted_labels.append(damage)
      sorted_handles.append(legend_lookup[damage])
    
  ax.legend(sorted_handles, sorted_labels, markerscale=3, title='Damage Rating', loc='upper right', 
    bbox_to_anchor=(0.96, 0.95), bbox_transform=ax.figure.transFigure, frameon=True, facecolor='white')


# --- PERIMETER LAYER ---
def show_fire_perimeter(ax, perimeter_data):
  perimeter_gdf = perimeter_data['perimeter_gdf']
  perimeter_gdf.plot(ax=ax, categorical=True, markersize=2, color='blue', alpha=0.3, zorder=3)


# --- MAP HELPERS ---
def set_map_position(ax, map_position):
  ax.set_position(map_position)
  ax.set_aspect('equal', adjustable='box')


def fit_map_bounds(ax, map_position):
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


# ----- ARCHIVE -----
def make_perimeter_buttons(dict, buttons):
  up_button_space = plt.axes([0.1, 0.15, 0.3, 0.05]) # left, bottom, width, height
  up_button = Button(up_button_space, '^')
  up_button.on_clicked(lambda event: change_index('up', dict))

  down_button_space = plt.axes([0.6, 0.15, 0.3, 0.05]) # left, bottom, width, height
  down_button = Button(down_button_space, 'v')
  down_button.on_clicked(lambda event: change_index('down', dict))

  buttons.append(up_button)
  buttons.append(down_button)


def change_index(direction, dict):
  if direction == 'up':
    dict['index'] += 1
  else:
    dict['index'] -= 1
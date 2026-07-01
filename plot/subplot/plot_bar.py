'''
this program draws the stacked bar chart used in the material window
it uses the same formatted material table data that is shown in the table
'''

import re

from matplotlib.patches import Patch


material_colors = {
  'wood': '#8B4513',
  'asphalt': '#333333',
  'vinyl': '#F4E1A6',
  'composite': '#D2691E',
  'metal': '#708090',
  'masonry': '#B22222',
  'tile': '#4682B4',
  'n/a': '#D3D3D3',
}

bar_elements = ['roof', 'side', 'ground deck', 'elevated deck']


'''
pulls the displayed percentage out of one material table cell
material table cells are formatted like "12 (34%)"
'''
def get_cell_percent(cell_value):
  match = re.search(r'\((\d+)%\)', str(cell_value))

  if match is None:
    return 0

  return int(match.group(1)) / 100


'''
draws four equal-length stacked bars from the material table percentages
'''
def show_material_bar_chart(bar_ax, structure_data):
  df_clean = structure_data['material_table']
  material_column = df_clean.columns[0]
  materials = list(df_clean[material_column])

  bar_ax.clear()
  bar_ax.set_axis_on()

  for bar_index, element in enumerate(bar_elements):
    left = 0

    for material in materials:
      material_row = df_clean[df_clean[material_column] == material]
      width = get_cell_percent(material_row[element].iloc[0])

      if width > 0:
        bar_ax.barh(
          bar_index,
          width,
          left=left,
          color=material_colors[material],
          edgecolor='white',
          linewidth=0.8,
          label=material if bar_index == 0 else None,
        )

      left += width

  bar_ax.set_xlim(0, 1)
  bar_ax.set_xticks([])
  bar_ax.set_yticks(range(len(bar_elements)))
  bar_ax.set_yticklabels(bar_elements, fontsize=8)
  bar_ax.invert_yaxis()

  for spine in ['top', 'right', 'left', 'bottom']:
    bar_ax.spines[spine].set_visible(False)

  legend_handles = [
    Patch(facecolor=material_colors[material], edgecolor='white', label=material)
    for material in material_colors
  ]

  bar_ax.legend(
    handles=legend_handles,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.2),
    ncol=4,
    fontsize=7,
    frameon=False,
  )

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

combustibility_colors = {
  'combustible': '#8B4513',
  'non-combustible': '#4682B4',
  'n/a': '#D3D3D3',
}

structure_element_colors = {
  'enclosed': '#B22222',
  'unenclosed': '#4682B4',
  '<= 1/8"': '#4682B4',
  '> 1/8"': '#B22222',
  'unscreened': '#FFD700',
  'single pane': '#B22222',
  'multi pane': '#4682B4',
  'n/a': '#D3D3D3',
}

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
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=material_colors,
    legend_columns=4,
  )


'''
draws a combustibility stacked bar chart from the combustibility table
'''
def show_combustibility_bar_chart(bar_ax, structure_data):
  df_clean = structure_data['structure_element_tables']['combustibility_table']
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=combustibility_colors,
    legend_columns=3,
  )


'''
draws one small building element stacked bar chart
'''
def show_structure_element_bar_chart(bar_ax, df_clean):
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=structure_element_colors,
    legend_columns=2,
    label_fontsize=8,
    legend_fontsize=8,
  )


'''
draws equal-length horizontal stacked bars from a formatted count/percent table
'''
def show_stacked_bar_chart(
  bar_ax,
  df_clean,
  row_column,
  colors,
  legend_columns,
  label_fontsize=8,
  legend_fontsize=9,
):
  rows = list(df_clean[row_column])
  elements = list(df_clean.columns[1:])

  bar_ax.clear()
  bar_ax.set_axis_on()

  for bar_index, element in enumerate(elements):
    left = 0

    for row_name in rows:
      row_data = df_clean[df_clean[row_column] == row_name]
      width = get_cell_percent(row_data[element].iloc[0])

      if width > 0:
        bar_ax.barh(
          bar_index,
          width,
          left=left,
          color=colors[row_name],
          edgecolor='white',
          linewidth=0.8,
          label=row_name if bar_index == 0 else None,
        )

      left += width

  bar_ax.set_xlim(0, 1)
  bar_ax.set_xticks([])
  bar_ax.set_yticks(range(len(elements)))
  bar_ax.set_yticklabels(elements, fontsize=label_fontsize)
  bar_ax.invert_yaxis()

  for spine in ['top', 'right', 'left', 'bottom']:
    bar_ax.spines[spine].set_visible(False)

  legend_handles = [
    Patch(facecolor=colors[row_name], edgecolor='white', label=row_name)
    for row_name in rows
  ]

  bar_ax.legend(
    handles=legend_handles,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.25),
    ncol=legend_columns,
    fontsize=legend_fontsize,
    frameon=False,
  )

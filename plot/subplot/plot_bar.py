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
  'combustible': '#B22222',
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
def show_material_bar_chart(bar_ax, structure_data, show_na=True):
  df_clean = structure_data['material_table']
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=material_colors,
    legend_columns=4,
    title='structural composition and material',
    title_y=1.08,
    show_na=show_na,
  )


'''
draws a combustibility stacked bar chart from the combustibility table
'''
def show_combustibility_bar_chart(bar_ax, structure_data, show_na=True):
  df_clean = structure_data['structure_element_tables']['combustibility_table']
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=combustibility_colors,
    legend_columns=3,
    title='combustibility',
    title_y=1.10,
    show_na=show_na,
  )


'''
draws one small building element stacked bar chart
'''
def show_structure_element_bar_chart(bar_ax, df_clean, show_na=True):
  show_stacked_bar_chart(
    bar_ax,
    df_clean,
    row_column=df_clean.columns[0],
    colors=structure_element_colors,
    legend_columns=2,
    label_fontsize=8,
    legend_fontsize=8,
    chart_label=df_clean.columns[1],
    chart_label_y=1.02,
    legend_y=-0.45,
    show_y_labels=False,
    show_na=show_na,
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
  title=None,
  title_y=1.03,
  chart_label=None,
  chart_label_y=1.02,
  legend_y=-0.25,
  show_y_labels=True,
  show_na=True,
):
  rows = list(df_clean[row_column])
  elements = list(df_clean.columns[1:])

  bar_ax.clear()
  bar_ax.set_axis_on()

  if title is not None:
    bar_ax.set_title(title, y=title_y)

  if chart_label is not None:
    bar_ax.text(
      0.5,
      chart_label_y,
      chart_label,
      transform=bar_ax.transAxes,
      ha='center',
      va='bottom',
      fontsize=9,
    )

  for bar_index, element in enumerate(elements):
    left = 0
    widths = {}

    for row_name in rows:
      row_data = df_clean[df_clean[row_column] == row_name]
      widths[row_name] = get_cell_percent(row_data[element].iloc[0])

    if not show_na:
      visible_total = sum(
        width
        for row_name, width in widths.items()
        if row_name != 'n/a'
      )

      for row_name in widths:
        if row_name == 'n/a' or visible_total == 0:
          widths[row_name] = 0
        else:
          widths[row_name] = widths[row_name] / visible_total

    for row_name in rows:
      width = widths[row_name]

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
  if show_y_labels:
    bar_ax.set_yticklabels(elements, fontsize=label_fontsize)
  else:
    bar_ax.set_yticklabels([])
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
    bbox_to_anchor=(0.5, legend_y),
    ncol=legend_columns,
    fontsize=legend_fontsize,
    frameon=False,
  )

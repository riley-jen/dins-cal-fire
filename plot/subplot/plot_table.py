'''
this program draws the tables used in the material window
it handles the main material table and the smaller structure element tables
'''

'''
draws the main material composition table
this table uses the largest font and scale in the material window
'''
def show_fire_material(table_ax, structure_data):
  df_clean = structure_data['material_table']
 
  t = table_ax.table(
      cellText=df_clean.values,
      colLabels=df_clean.columns,
      loc='center',
      cellLoc='center'
  )
  t.auto_set_font_size(False)
  t.set_fontsize(10)
  t.scale(1.1, 1.3)


structure_element_fontsize = 8
structure_element_build_width = 0.45
structure_element_detail_width = (1 - structure_element_build_width) / 2
combustibility_table_width = 1.1
combustibility_build_width = combustibility_table_width / 5


'''
draws one of the structure element tables
the combustibility table gets special sizing because it has more columns
'''
def show_structure_element_table(table_ax, df_clean):
  t = table_ax.table(
      cellText=df_clean.values,
      colLabels=df_clean.columns,
      loc='center',
      cellLoc='center'
  )
  t.auto_set_font_size(False)

  # the combustibility table is meant to match the main material table
  if len(df_clean.columns) == 7:
    t.set_fontsize(10)
    t.scale(1, 1.3)
  else:
    t.set_fontsize(structure_element_fontsize)
    t.scale(1, 0.95)

  if len(df_clean.columns) == 7:
    detail_width = (combustibility_table_width - combustibility_build_width) / 6
    column_widths = [combustibility_build_width] + [detail_width] * 6
  elif len(df_clean.columns) == 3:
    column_widths = [
      structure_element_build_width,
      structure_element_detail_width,
      structure_element_detail_width,
    ]
  else:
    column_widths = [
      structure_element_build_width,
      structure_element_detail_width * 2,
    ]

  # apply widths after the table is made so all rows line up
  for (row_index, column_index), cell in t.get_celld().items():
    cell.set_width(column_widths[column_index])
    if len(df_clean.columns) == 7 and column_index > 0:
      cell.set_fontsize(9)

'''
this program draws the tables used in the material window
it handles the main material table and the smaller structure element tables
'''

'''
draws the main material composition table
this table uses the largest font and scale in the material window
'''
def show_table(table_ax, structure_data):
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

combustibility_table_width = 1.1
combustibility_build_width = combustibility_table_width / 5


'''
draws one of the structure element tables
'''
def show_structure_element_table(table_ax, df_clean):
  t = table_ax.table(
      cellText=df_clean.values,
      colLabels=df_clean.columns,
      loc='center',
      cellLoc='center'
  )
  t.auto_set_font_size(False)
  t.set_fontsize(8)
  t.scale(1.1, 1.3)

'''
draws the combustibility summary table
this table is larger than the building property tables
'''
def show_combustibility_table(table_ax, structure_data):
  df_clean = structure_data['structure_element_tables']['combustibility_table']

  t = table_ax.table(
      cellText=df_clean.values,
      colLabels=df_clean.columns,
      loc='center',
      cellLoc='center'
  )
  t.auto_set_font_size(False)
  t.set_fontsize(10)
  t.scale(1, 1.3)

  detail_width = (combustibility_table_width - combustibility_build_width) / 6
  column_widths = [combustibility_build_width] + [detail_width] * 6

  for (row_index, column_index), cell in t.get_celld().items():
    cell.set_width(column_widths[column_index])
    if column_index > 0:
      cell.set_fontsize(9)

  table_ax.set_title('combustibility', y=1.2)

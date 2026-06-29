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

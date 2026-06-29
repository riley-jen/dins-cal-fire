# --- MAIN FUNCTIONS ---
def show_damage_pie(pie_ax, structure_data):
  damage_count = structure_data['damage_count']
  color_code = structure_data['color_code']

  wedges, _, percentages = pie_ax.pie(list(damage_count.values()), labels=None, colors=color_code, autopct='%1.1f%%', startangle=90)
  
  for text in percentages:
    text.set_visible(False)
  
  make_pie_legend(pie_ax, wedges, percentages, structure_data)


# --- HELPER FUNCTIONS ---
def make_pie_legend(ax, wedges, percentages, structure_data):
  texts = []
  counts = list(structure_data['damage_count'].values())
  
  for i in range(len(counts)):
    texts.append(str(counts[i]) + ' (' + percentages[i].get_text() + ')')

  ax.legend(wedges, texts, markerscale=3, 
    title='Total structures: ' + str(structure_data['total']), loc='lower right', 
    bbox_to_anchor=(0.96, 0.5), bbox_transform=ax.figure.transFigure, frameon=True, facecolor='white')

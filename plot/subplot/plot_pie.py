# --- MAIN FUNCTIONS ---
def show_damage_pie(pie_ax, structure_data, legend_anchor, displayed_damages = None):
  damage_count = get_displayed_damage_counts(structure_data, displayed_damages)
  color_code = structure_data['color_code']
  total = sum(damage_count.values())

  if total > 0:
    wedges, _, percentages = pie_ax.pie(
      list(damage_count.values()),
      labels=None,
      colors=color_code,
      autopct='%1.1f%%',
      startangle=90
    )

    for text in percentages:
      text.set_visible(False)

    percentage_texts = [text.get_text() for text in percentages]
  else:
    wedges = []
    percentage_texts = ['0.0%' for damage in damage_count]

  make_pie_legend(pie_ax, wedges, percentage_texts, damage_count, structure_data, legend_anchor)


# --- HELPER FUNCTIONS ---
def get_displayed_damage_counts(structure_data, displayed_damages = None):
  if displayed_damages is None:
    displayed_damages = structure_data['damage_list']

  return {
    damage: structure_data['damage_count'][damage] if damage in displayed_damages else 0
    for damage in structure_data['damage_list']
  }


def make_pie_legend(ax, wedges, percentages, damage_count, structure_data, legend_anchor):
  texts = []
  counts = list(damage_count.values())
  displayed_total = sum(counts)
  fire_total = structure_data['total']
  displayed_percent = get_displayed_percent(displayed_total, fire_total)
  
  for i in range(len(counts)):
    damage = structure_data['damage_list'][i]
    texts.append(str(counts[i]) + ' (' + percentages[i] + ')')

  if len(wedges) == 0:
    from matplotlib.patches import Patch
    wedges = [
      Patch(facecolor=color, edgecolor='none')
      for color in structure_data['color_code']
    ]

  ax.legend(wedges, texts, markerscale=3,
    title='displayed: ' + str(displayed_total) + ' (' + displayed_percent + ')', loc='lower left',
    bbox_to_anchor=legend_anchor, bbox_transform=ax.figure.transFigure, frameon=True, facecolor='white')


def get_displayed_percent(displayed_total, fire_total):
  if fire_total == 0:
    return '0%'

  return str(round((displayed_total / fire_total) * 100)) + '%'

'''
this program draws the categorical sampling scatter plot used in the damage window
'''

sampling_types = ['Chips', 'Sorbent Tubes', 'Wipes', 'Wristbands']
sampling_colors = {
  'Chips': "#54d3a9",
  'Sorbent Tubes': '#F28E2B',
  'Wipes': '#2F80ED',
  'Wristbands': '#E85D9E',
}
sampling_data = {
  'bridge': [
    ('2024-09-10', ['Wipes']),
    ('2024-09-11', ['Chips', 'Sorbent Tubes', 'Wristbands']),
    ('2024-09-12', ['Sorbent Tubes', 'Wipes', 'Wristbands']),
    ('2024-09-13', ['Chips']),
    ('2024-09-14', ['Chips', 'Sorbent Tubes', 'Wipes', 'Wristbands']),
  ],
  'line': [
    ('2024-09-10', ['Chips', 'Sorbent Tubes', 'Wristbands']),
    ('2024-09-12', ['Wristbands']),
    ('2024-09-13', ['Chips']),
  ],
  'franklin': [
    ('2024-12-10', ['Chips', 'Wipes', 'Wristbands']),
  ],
  'eaton': [
    ('2025-01-08', ['Wristbands']),
  ],
  'mountain': [
    ('2024-11-07', ['Wipes']),
  ],
  'palisades': [
    ('2025-01-11', ['Wristbands']),
  ],
}


def show_sampling_scatter(sampling_ax, fire_name):
  fire_sampling_data = sampling_data.get(fire_name, [])
  dates = [date for date, _ in fire_sampling_data]
  date_positions = {date: index for index, date in enumerate(dates)}
  type_positions = {
    sample_type: len(sampling_types) - index - 1
    for index, sample_type in enumerate(sampling_types)
  }
  x_values = []
  y_values = []
  colors = []

  sampling_ax.clear()
  sampling_ax.set_axis_on()

  for date, sample_types in fire_sampling_data:
    for sample_type in sample_types:
      if sample_type in type_positions:
        x_values.append(date_positions[date])
        y_values.append(type_positions[sample_type])
        colors.append(sampling_colors[sample_type])

  sampling_ax.scatter(
    x_values,
    y_values,
    s=85,
    marker='o',
    c=colors,
    edgecolor='white',
    linewidth=1.1,
    zorder=3,
  )

  sampling_ax.set_title('sampling dates', pad=8)
  sampling_ax.set_xlim(-0.5, max(len(dates) - 0.5, 0.5))
  sampling_ax.set_ylim(-0.5, len(sampling_types) - 0.5)
  sampling_ax.set_xticks(range(len(dates)))
  sampling_ax.set_xticklabels(dates, ha='right', fontsize=8)
  sampling_ax.set_yticks(range(len(sampling_types)))
  sampling_ax.set_yticklabels(list(reversed(sampling_types)), fontsize=8)
  sampling_ax.grid(color='#D9D9D9', linewidth=0.7, zorder=1)

  for spine in ['top', 'right']:
    sampling_ax.spines[spine].set_visible(False)

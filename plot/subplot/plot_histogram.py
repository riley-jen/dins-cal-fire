'''
this program draws the stacked year-built histogram used in the damage window
'''


def show_year_built_histogram(histogram_ax, structure_data, displayed_damages):
  year_built_counts = structure_data['year_built_damage_counts']
  damage_list = structure_data['damage_list']
  color_dict = structure_data['color_dict']
  selected_damages = [
    damage for damage in damage_list
    if damage in displayed_damages
  ]
  years = [
    year for year in year_built_counts
    if 1900 <= year <= 2020
  ]
  unspecified_count = sum(
    year_built_counts.get(0, {}).get(damage, 0)
    for damage in selected_damages
  )

  histogram_ax.clear()
  histogram_ax.set_axis_on()

  if len(years) == 0 or len(selected_damages) == 0:
    histogram_ax.text(
      0.5,
      0.5,
      'no year built data',
      transform=histogram_ax.transAxes,
      ha='center',
      va='center',
      fontsize=9,
    )
    format_histogram_axes(histogram_ax, unspecified_count)
    return

  year_range = list(range(min(years), max(years) + 1))
  bottoms = [0 for _ in year_range]

  for damage in selected_damages:
    counts = [
      year_built_counts.get(year, {}).get(damage, 0)
      for year in year_range
    ]

    histogram_ax.bar(
      year_range,
      counts,
      bottom=bottoms,
      width=1.0,
      color=color_dict[damage],
      edgecolor='white',
      linewidth=0.2,
      label=damage,
    )

    bottoms = [
      bottom + count
      for bottom, count in zip(bottoms, counts)
    ]

  histogram_ax.set_xlim(min(year_range) - 0.5, max(year_range) + 0.5)
  histogram_ax.set_ylim(0, max(bottoms) * 1.1 if max(bottoms) > 0 else 1)
  format_histogram_axes(histogram_ax, unspecified_count)


def format_histogram_axes(histogram_ax, unspecified_count):
  histogram_ax.set_title('year built', fontsize=10)
  histogram_ax.set_xlabel('year built', fontsize=8, labelpad=2)
  histogram_ax.xaxis.set_label_coords(0.42, -0.18)
  histogram_ax.set_ylabel('number of buildings', fontsize=8, labelpad=2)
  histogram_ax.tick_params(axis='both', labelsize=7)
  histogram_ax.grid(axis='y', color='#D9D9D9', linewidth=0.7, zorder=1)
  histogram_ax.set_axisbelow(True)
  histogram_ax.text(
    1.02,
    0.5,
    'unspecified year built\n' + str(unspecified_count),
    transform=histogram_ax.transAxes,
    ha='left',
    va='center',
    fontsize=8,
  )

  for spine in ['top', 'right']:
    histogram_ax.spines[spine].set_visible(False)

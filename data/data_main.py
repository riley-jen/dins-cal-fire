'''
prints data counts before and after each filtering and cleaning step
'''

import clean_perimeter
import clean_structure
import filter_perimeter
import filter_structure


def format_counts():
  perimeter_filter_before, perimeter_filter_after = filter_perimeter.get_count()
  structure_filter_before, structure_filter_after = filter_structure.get_count()

  perimeter_clean_counts = clean_perimeter.get_count()
  structure_clean_counts = clean_structure.get_count()

  perimeter_time_after = perimeter_clean_counts['time'][1]
  perimeter_location_after = perimeter_clean_counts['location'][1]
  structure_time_after = structure_clean_counts['time'][1]

  return (
    'COUNTS:\n'
    '--- perimeter ---\n'
    f'original data: {perimeter_filter_before}\n'
    f'filtered data: {perimeter_filter_after}\n'
    f'clean data: {perimeter_time_after} (time), {perimeter_location_after} (location)\n'
    '--- structure ---\n'
    f'original data: {structure_filter_before}\n'
    f'filtered data: {structure_filter_after}\n'
    f'clean data: {structure_time_after} (time)'
  )


def main():
  print(format_counts())


if __name__ == '__main__':
  main()

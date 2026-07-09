"""
Query exported analysis tables from the command line.

Criteria are represented as a list of (column, value) pairs, for example:
[('fire', 'palisades'), ('roof_material', 'wood')]
"""

import csv
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
CONDITION_FILE = ROOT_DIR / 'analysis' / 'outputs' / 'condition_records.csv'

QUERY_COLUMNS = [
  'fire',
  'damage',
  'roof_material',
  'side_material',
  'ground_deck_material',
  'elevated_deck_material',
  'eaves',
  'vent_screen',
  'window_pane',
  'patio_cover',
  'fence',
]

PROMPTS = {
  'fire': 'choose fire',
  'damage': 'choose dmg',
  'roof_material': 'choose roof material',
  'side_material': 'choose side material',
  'ground_deck_material': 'choose ground deck material',
  'elevated_deck_material': 'choose elevated deck material',
  'eaves': 'choose eaves',
  'vent_screen': 'choose vent screen',
  'window_pane': 'choose window pane',
  'patio_cover': 'choose patio cover',
  'fence': 'choose fence',
}

FIRE_ORDER = ['palisades', 'mountain', 'eaton', 'franklin', 'line', 'bridge']
FIRE_LABELS = {'mountain': 'mtn'}
DAMAGE_ORDER = [
  'no damage',
  'affected (>0-10%)',
  'minor (10-25%)',
  'major (25-50%)',
  'destroyed (>50%)',
  'inaccessible',
]


def normalize_criteria(criteria):
  return [(column, str(value)) for column, value in criteria]


def get_count(criteria):
  total = 0
  criteria = normalize_criteria(criteria)

  with CONDITION_FILE.open(newline='') as file:
    reader = csv.DictReader(file)

    for row in reader:
      if all(row[column] == value for column, value in criteria):
        total += int(row['count'])

  return total


def get_percentage(numerator_criteria, denominator_criteria):
  numerator = get_count(numerator_criteria)
  denominator = get_count(denominator_criteria)

  if denominator == 0:
    return 0

  return (numerator / denominator) * 100


def get_available_values():
  values = {column: set() for column in QUERY_COLUMNS}

  with CONDITION_FILE.open(newline='') as file:
    reader = csv.DictReader(file)

    for row in reader:
      for column in QUERY_COLUMNS:
        values[column].add(row[column])

  return {
    column: sort_values(column, column_values)
    for column, column_values in values.items()
  }


def sort_values(column, values):
  if column == 'fire':
    return [value for value in FIRE_ORDER if value in values]

  if column == 'damage':
    return [value for value in DAMAGE_ORDER if value in values]

  return sorted(values)


def make_label(column, value):
  if column == 'fire':
    return FIRE_LABELS.get(value, value)

  return value


def ask_choice(question, options):
  option_text = ', '.join(
    f'{label} ({index})'
    for index, (label, _) in enumerate(options, start=1)
  )
  answer = input(f'{question}: {option_text}\n> ').strip()

  if answer.isdigit():
    index = int(answer)
    if 1 <= index <= len(options):
      return options[index - 1][1]

  print('Please enter one of the listed numbers.')
  return ask_choice(question, options)


def ask_test_type():
  return ask_choice('choose test', [
    ('count', 'count'),
    ('percentage', 'percentage'),
  ])


def ask_base_criteria(available_values):
  criteria = []

  for column in QUERY_COLUMNS:
    options = [
      (make_label(column, value), value)
      for value in available_values[column]
    ]
    options.append(('none', None))

    value = ask_choice(PROMPTS[column], options)
    if value is not None:
      criteria.append((column, value))

  return criteria


def ask_denominator_criteria(numerator_criteria):
  denominator_criteria = []
  remaining_criteria = numerator_criteria.copy()

  while remaining_criteria:
    options = [
      (f'{column} = {value}', (column, value))
      for column, value in remaining_criteria
    ]
    options.append(('none', None))

    chosen = ask_choice('choose criteria', options)
    if chosen is None:
      break

    denominator_criteria.append(chosen)
    remaining_criteria.remove(chosen)

  return denominator_criteria

def ask_again():
  return ask_choice('choose next', [
    ('again', 'again'),
    ('end', 'end'),
  ])


def run_query(available_values):
  test_type = ask_test_type()
  criteria = ask_base_criteria(available_values)

  if test_type == 'count':
    print(f'count: {get_count(criteria)}')
    return

  denominator_criteria = ask_denominator_criteria(criteria)
  percentage = get_percentage(criteria, denominator_criteria)
  print(f'percentage: {percentage:.2f}%')


def run_queries(available_values):
  run_query(available_values)

  if ask_again() == 'again':
    run_queries(available_values)


def main():
  available_values = get_available_values()
  run_queries(available_values)


if __name__ == '__main__':
  main()

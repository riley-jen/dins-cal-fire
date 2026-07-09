"""
Query exported analysis tables from the command line.

Criteria are represented as a list of (column, value) pairs, for example:
[('fire', 'palisades'), ('roof_material', 'wood')]

Repeated columns are treated as OR values:
[('fire', 'palisades'), ('fire', 'mountain')] matches either fire.
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
  normalized = {}

  for column, value in criteria:
    if column not in normalized:
      normalized[column] = set()

    if isinstance(value, (list, tuple, set)):
      normalized[column].update(str(item) for item in value)
    else:
      normalized[column].add(str(value))

  return normalized


def get_count(criteria):
  total = 0
  criteria = normalize_criteria(criteria)

  with CONDITION_FILE.open(newline='') as file:
    reader = csv.DictReader(file)

    for row in reader:
      if all(row[column] in values for column, values in criteria.items()):
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

  sorted_values = sorted(value for value in values if value != 'n/a')

  if 'n/a' in values:
    sorted_values.append('n/a')

  return sorted_values


def make_label(column, value):
  if column == 'fire':
    return FIRE_LABELS.get(value, value)

  return value


def make_option_text(options, has_none):
  option_labels = [
    f'{label} ({index})'
    for index, (label, _) in enumerate(options, start=1)
  ]

  if has_none:
    option_labels.append('none (0)')

  return ', '.join(option_labels)


def parse_choices(answer, option_count, has_none, allow_multiple):
  if answer == '0' and has_none:
    return []

  raw_choices = [choice.strip() for choice in answer.split(',')]

  if not allow_multiple and len(raw_choices) > 1:
    return None

  if any(not choice.isdigit() for choice in raw_choices):
    return None

  choices = [int(choice) for choice in raw_choices]

  if 0 in choices:
    return [] if has_none and len(choices) == 1 else None

  if any(choice < 1 or choice > option_count for choice in choices):
    return None

  if len(set(choices)) != len(choices):
    return None

  return choices


def ask_choice(question, options, allow_multiple=False, has_none=False):
  option_text = make_option_text(options, has_none)
  answer = input(f'{question}: {option_text}\n> ').strip()
  choices = parse_choices(answer, len(options), has_none, allow_multiple)

  if choices is not None:
    if not choices:
      return [] if allow_multiple else None

    values = [options[index - 1][1] for index in choices]
    return values if allow_multiple else values[0]

  if allow_multiple:
    print('Please enter listed numbers separated by commas, or 0 for none.')
  else:
    print('Please enter one of the listed numbers.')
  return ask_choice(question, options, allow_multiple, has_none)


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

    selected_values = ask_choice(PROMPTS[column], options, allow_multiple=True, has_none=True)
    for value in selected_values:
      criteria.append((column, value))

  return criteria


def get_selected_columns(criteria):
  return list(dict.fromkeys(column for column, _ in criteria))


def criteria_for_columns(criteria, selected_columns):
  return [
    (column, value)
    for column, value in criteria
    if column in selected_columns
  ]


def ask_denominator_criteria(numerator_criteria):
  selected_columns = get_selected_columns(numerator_criteria)
  options = [(column, column) for column in selected_columns]
  denominator_columns = ask_choice('choose criteria', options, allow_multiple=True, has_none=True)

  return criteria_for_columns(numerator_criteria, denominator_columns)


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

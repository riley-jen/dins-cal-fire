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


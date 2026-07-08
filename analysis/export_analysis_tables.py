"""
Export analysis-friendly CSV tables from the cleaned DINS structure GeoJSON.

Outputs:
- outputs/structure_records.csv: one row per inspected structure
- outputs/condition_records.csv: one row per observed condition combination
"""

import csv
import json
from collections import Counter
from pathlib import Path

try:
  import ijson
except ImportError:
  ijson = None


ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT_DIR / 'files' / 'POSTFIRE_CLEAN_DATA.geojson'
OUTPUT_DIR = ROOT_DIR / 'analysis' / 'outputs'
STRUCTURE_OUTPUT_FILE = OUTPUT_DIR / 'structure_records.csv'
CONDITION_OUTPUT_FILE = OUTPUT_DIR / 'condition_records.csv'

CONDITION_COLUMNS = [
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

STRUCTURE_COLUMNS = [
  'structure_id',
  *CONDITION_COLUMNS,
  'coordinate_x',
  'coordinate_y',
]

MATERIALS = ['asphalt', 'composite', 'masonry', 'metal', 'tile', 'vinyl', 'wood', 'n/a']

STRUCTURE_VALUE_MAPS = {
  'eaves': {
    'enclosed': 'enclosed',
    'unenclosed': 'unenclosed',
    'no eaves': 'n/a',
    'unknown': 'n/a',
  },
  'vent_screen': {
    'mesh screen <= 1/8"': '<= 1/8 in',
    'mesh screen > 1/8"': '> 1/8 in',
    'unscreened': 'unscreened',
    'no vents': 'n/a',
    'unknown': 'n/a',
  },
  'window_pane': {
    'single pane': 'single pane',
    'multi pane': 'multi pane',
    'no windows': 'n/a',
    'unknown': 'n/a',
  },
  'combustibility': {
    'combustible': 'combustible',
    'non combustible': 'non-combustible',
    'non-combustible': 'non-combustible',
    'no patio cover carport': 'n/a',
    'no patio cover/carport': 'n/a',
    'no fence': 'n/a',
    'unknown': 'n/a',
  },
}


def clean_value(value):
  return str(value or '').strip().lower()


def get_material(value):
  clean = clean_value(value).replace('/', ' ')

  if clean in MATERIALS:
    return clean

  if clean in ['masonry concrete', 'stucco brick cement', 'concrete']:
    return 'masonry'

  if 'no ' in clean or 'other' in clean or 'unknown' in clean:
    return 'n/a'

  return 'n/a'


def get_mapped_value(value, value_map):
  clean = clean_value(value)

  if clean in value_map:
    return value_map[clean]

  clean_no_slash = clean.replace('/', ' ')
  if clean_no_slash in value_map:
    return value_map[clean_no_slash]

  return 'n/a'


def iter_features(path):
  if ijson is not None:
    with path.open('rb') as file:
      yield from ijson.items(file, 'features.item')
    return

  with path.open() as file:
    data = json.load(file)
    yield from data['features']


def get_coordinates(feature):
  geometry = feature.get('geometry') or {}
  coordinates = geometry.get('coordinates') or []

  if len(coordinates) < 2:
    return '', ''

  return coordinates[0], coordinates[1]


def build_structure_record(structure_id, feature):
  properties = feature.get('properties') or {}
  coordinate_x, coordinate_y = get_coordinates(feature)

  return {
    'structure_id': structure_id,
    'fire': clean_value(properties.get('INCIDENTNAME')),
    'damage': clean_value(properties.get('DAMAGE')),
    'roof_material': get_material(properties.get('ROOFCONSTRUCTION')),
    'side_material': get_material(properties.get('EXTERIORSIDING')),
    'ground_deck_material': get_material(properties.get('DECKPORCHONGRADE')),
    'elevated_deck_material': get_material(properties.get('DECKPORCHELEVATED')),
    'eaves': get_mapped_value(properties.get('EAVES'), STRUCTURE_VALUE_MAPS['eaves']),
    'vent_screen': get_mapped_value(properties.get('VENTSCREEN'), STRUCTURE_VALUE_MAPS['vent_screen']),
    'window_pane': get_mapped_value(properties.get('WINDOWPANE'), STRUCTURE_VALUE_MAPS['window_pane']),
    'patio_cover': get_mapped_value(properties.get('PATIOCOVERCARPORT'), STRUCTURE_VALUE_MAPS['combustibility']),
    'fence': get_mapped_value(properties.get('FENCEATTACHEDTOSTRUCTURE'), STRUCTURE_VALUE_MAPS['combustibility']),
    'coordinate_x': coordinate_x,
    'coordinate_y': coordinate_y,
  }


def export_tables():
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  condition_counts = Counter()
  structure_count = 0

  with STRUCTURE_OUTPUT_FILE.open('w', newline='') as structure_file:
    structure_writer = csv.DictWriter(structure_file, fieldnames=STRUCTURE_COLUMNS)
    structure_writer.writeheader()

    for structure_id, feature in enumerate(iter_features(INPUT_FILE), start=1):
      record = build_structure_record(structure_id, feature)
      structure_writer.writerow(record)

      condition_key = tuple(record[column] for column in CONDITION_COLUMNS)
      condition_counts[condition_key] += 1
      structure_count += 1

  with CONDITION_OUTPUT_FILE.open('w', newline='') as condition_file:
    condition_writer = csv.writer(condition_file)
    condition_writer.writerow([*CONDITION_COLUMNS, 'count'])

    for condition_key, count in sorted(condition_counts.items()):
      condition_writer.writerow([*condition_key, count])

  print(f'Wrote {structure_count} structure records to {STRUCTURE_OUTPUT_FILE}')
  print(f'Wrote {len(condition_counts)} condition records to {CONDITION_OUTPUT_FILE}')


if __name__ == '__main__':
  export_tables()

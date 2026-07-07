'''
this program is to clean the already filtered structure .geojson
it writes a new .geojson that cleans the errors from the data by time
and keeps only the columns used by the plotting programs
it also writes a web copy reprojected to longitude/latitude for Leaflet

not to be confused with filter_structure.py
'''

from datetime import datetime
from pathlib import Path
import geopandas as gpd

# set up
filtered_filename = Path(__file__).resolve().parent.parent / 'files' / 'POSTFIRE_FILTERED_DATA.geojson'
clean_filename = Path(__file__).resolve().parent.parent / 'files' / 'POSTFIRE_CLEAN_DATA.geojson'
web_clean_filename = Path(__file__).resolve().parent.parent / 'docs' / 'data' / 'POSTFIRE_CLEAN_DATA.geojson'
plot_columns = [
  'INCIDENTNAME',
  'DAMAGE',
  'ROOFCONSTRUCTION',
  'EXTERIORSIDING',
  'DECKPORCHONGRADE',
  'DECKPORCHELEVATED',
  'EAVES',
  'VENTSCREEN',
  'WINDOWPANE',
  'PATIOCOVERCARPORT',
  'FENCEATTACHEDTOSTRUCTURE',
  'geometry',
]

incident_start_dates = [
  ('palisades', datetime(2025, 1, 7)),   # Palisades Fire (Ignited Jan 7, 2025)
  ('mountain', datetime(2024, 11, 6)),  # Mountain Fire (Ignited Nov 6, 2024)
  ('eaton', datetime(2025, 1, 7)),   # Eaton Fire (Ignited Jan 7, 2025)
  ('franklin', datetime(2024, 12, 9)),   # Franklin Fire (Ignited Dec 9, 2025)
  ('line', datetime(2024, 9, 5)),   # Line Fire (Ignited Sept 5, 2024)
  ('bridge', datetime(2024, 9, 8))    # Bridge Fire (Ignited Sept 8, 2024)
]

# --- helper functions ---

'''
turns string from cal fire incident start time data to datetime object
'''
def get_date(string):
  string = str(string)
  months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

  assert(string[5:7].isdigit()), f'the string {string} is not ok'
  day = int(string[5:7])
  month = months.index(string[8:11].lower()) + 1
  year = int(string[12:16])

  return datetime(year, month, day)

'''
checks if dates from a geopandas datetime series and another datetime are 
  within a week apart
'''
def is_close(series_date, date2):
  return abs((series_date - date2).dt.days) <= 7
# ------

'''
takes in a filtered gdf and returns a gdf cleaned by time
where cleaned by time means each structure included has INCIDENTSTARTDATE 
  within 7 days of the official start day for that fire
'''
def clean_by_time(gdf):
  before_count = len(gdf)
  gdf_list = []
  for incident, time in incident_start_dates:
    fire_gdf = gdf[gdf['INCIDENTNAME'].str.lower() == incident]

    converted_dates = fire_gdf['INCIDENTSTARTDATE'].astype(str).apply(get_date)
    time_gdf = fire_gdf[is_close(converted_dates, time)]

    gdf_list.append(time_gdf)
  
  clean_gdf = gpd.pd.concat(gdf_list, ignore_index=True)
  return clean_gdf, (before_count, len(clean_gdf))


'''
keeps only the properties and geometry used by extract_structure_data.py
so the clean GeoJSON is smaller but has the same record count
'''
def select_plot_columns(gdf):
  return gdf[plot_columns].copy()


'''
writes a GeoJSON file, replacing the old copy if it exists
'''
def write_geojson(gdf, filename):
  filename.parent.mkdir(parents=True, exist_ok=True)

  if filename.exists():
    filename.unlink()

  gdf.to_file(filename, 'GEOJSON')


'''
writes the web dashboard structure file in EPSG:4326
Leaflet expects longitude/latitude coordinates, while the Python plots use EPSG:3310
'''
def write_web_geojson(clean_gdf):
  web_gdf = clean_gdf.set_crs('EPSG:3310', allow_override=True).to_crs('EPSG:4326')
  write_geojson(web_gdf, web_clean_filename)


# --- file writing ---
def get_count():
  gdf = gpd.read_file(filtered_filename)
  clean_gdf, time_count = clean_by_time(gdf)
  return {
    'time': time_count
  }


def write_main():
  count = get_count()
  gdf = gpd.read_file(filtered_filename)
  clean_gdf, _ = clean_by_time(gdf)
  clean_gdf = select_plot_columns(clean_gdf)

  write_geojson(clean_gdf, clean_filename)
  write_web_geojson(clean_gdf)
  return count


if __name__ == '__main__':
  write_main()


# ----- ARCHIVE -----
'''
returns a list of all unique timestamps for each fire incident
'''
def get_data_timestamps(gdf):
  timestamps = []

  for i, data in gdf.iterrows():
    fire_name = data['INCIDENTNAME']
    time = data['INCIDENTSTARTDATE']

    ts = (fire_name, time)

    if ts not in timestamps:
      timestamps.append(ts)

  return timestamps

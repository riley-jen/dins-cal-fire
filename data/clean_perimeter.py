'''
this program is to clean the already filtered perimeter .geojson
it writes a new .geojson that cleans the errors from the data by time

not to be confused with filter_perimeter.py
'''

from datetime import datetime
from pathlib import Path
import geopandas as gpd


# set up
filtered_filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'
gdf = gpd.read_file(filtered_filename)

incident_start_dates = [
  ('palisades', datetime(2025, 1, 7)),   # Palisades Fire (Ignited Jan 7, 2025)
  ('mountain', datetime(2024, 11, 6)),  # Mountain Fire (Ignited Nov 6, 2024)
  ('eaton', datetime(2025, 1, 7)),   # Eaton Fire (Ignited Jan 7, 2025)
  ('franklin', datetime(2024, 12, 9)),   # Franklin Fire (Ignited Dec 9, 2025)
  ('line', datetime(2024, 9, 5)),   # Line Fire (Ignited Sept 5, 2024)
  ('bridge', datetime(2024, 9, 8))    # Bridge Fire (Ignited Sept 8, 2024)
]

perimeter_date_columns = ['poly_CreateDate', 'poly_DateCurrent', 'poly_PolygonDateTime']


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
checks if dates from a geopandas datetime series are after another datetime
'''
def is_after(series_date, date2):
  return series_date > date2


# ------

'''
takes in a filtered perimeter gdf and returns a gdf cleaned by time
where cleaned by time means every non-null perimeter date included is after the
  official start day for that fire. null perimeter dates are allowed
'''
def clean_by_time(gdf):
  gdf_list = []

  for incident, time in incident_start_dates:
    fire_gdf = gdf[gdf['poly_IncidentName'].str.lower() == incident]
    time_check = gpd.pd.Series(True, index=fire_gdf.index)

    for date_column in perimeter_date_columns:
      dates_present = fire_gdf[date_column].notna()
      converted_dates = fire_gdf.loc[dates_present, date_column].astype(str).apply(get_date)
      time_check.loc[dates_present] = time_check.loc[dates_present] & is_after(converted_dates, time)

    time_gdf = fire_gdf[time_check]
    gdf_list.append(time_gdf)
  
  return gpd.pd.concat(gdf_list, ignore_index=True)


# --- file writing ---
clean_filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson'
clean_gdf = clean_by_time(gdf)

if clean_filename.exists():
  clean_filename.unlink()

clean_gdf.to_file(clean_filename, 'GEOJSON')

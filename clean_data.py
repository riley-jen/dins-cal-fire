'''
this program is to clean the already filtered .geojson
it writes a new .geojson that cleans the errors from the data
includes duplicate inputs and same incident names

not to be confused with filter_data.py
'''

from datetime import datetime
import geopandas as gpd

# set up
filtered_filename = "POSTFIRE_FILTERED_DATA.geojson"
gdf = gpd.read_file(filtered_filename)

incident_start_dates = [
  ("palisades", datetime(2025, 1, 7)),   # Palisades Fire (Ignited Jan 7, 2025)
  ("mountain", datetime(2024, 11, 6)),  # Mountain Fire (Ignited Nov 6, 2024)
  ("eaton", datetime(2025, 1, 7)),   # Eaton Fire (Ignited Jan 7, 2025)
  ("franklin", datetime(2024, 12, 9)),   # Franklin Fire (Ignited Dec 9, 2025)
  ("line", datetime(2024, 9, 5)),   # Line Fire (Ignited Sept 5, 2024)
  ("bridge", datetime(2024, 9, 8))    # Bridge Fire (Ignited Sept 8, 2024)
]

# --- helper functions ---

'''
turns string from cal fire incident start time data to datetime object
'''
def get_date(string):
  string = str(string)
  months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

  assert(string[5:7].isdigit()), f"the string {string} is not ok"
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
  gdf_list = []
  for incident, time in incident_start_dates:
    fire_gdf = gdf[gdf['INCIDENTNAME'].str.lower() == incident]

    converted_dates = fire_gdf['INCIDENTSTARTDATE'].astype(str).apply(get_date)
    time_gdf = fire_gdf[is_close(converted_dates, time)]

    gdf_list.append(time_gdf)
  
  return gpd.pd.concat(gdf_list, ignore_index=True)


# --- file writing ---
clean_filename = "POSTFIRE_CLEAN_DATA.geojson"
clean_gdf = clean_by_time(gdf)

clean_gdf.to_file(clean_filename, "GEOJSON")


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
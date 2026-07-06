'''
this program is to clean the already filtered perimeter .geojson
it writes a new .geojson that cleans the errors from the data
and keeps only the columns used by the plotting program

not to be confused with filter_perimeter.py
'''

from datetime import datetime
import math
from pathlib import Path
import geopandas as gpd


# set up
filtered_filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson'
clean_filename = Path(__file__).resolve().parent.parent / 'files' / 'WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson'
plot_columns = [
  'poly_IncidentName',
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

perimeter_date_columns = ['poly_CreateDate', 'poly_DateCurrent', 'poly_PolygonDateTime']
los_angeles_coordinates = (34.05, -118.25)
max_distance_miles = 200


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


def get_distance_miles(point1, point2):
  lat1, lon1 = point1
  lat2, lon2 = point2
  earth_radius_miles = 3958.8

  lat1 = math.radians(lat1)
  lon1 = math.radians(lon1)
  lat2 = math.radians(lat2)
  lon2 = math.radians(lon2)

  lat_diff = lat2 - lat1
  lon_diff = lon2 - lon1
  a = math.sin(lat_diff / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(lon_diff / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

  return earth_radius_miles * c


def get_polygon_coordinates(geometry):
  if geometry.geom_type == 'Polygon':
    polygons = [geometry]
  elif geometry.geom_type == 'MultiPolygon':
    polygons = geometry.geoms
  else:
    return []

  coordinates = []
  for polygon in polygons:
    coordinates.extend(list(polygon.exterior.coords))

    for interior in polygon.interiors:
      coordinates.extend(list(interior.coords))

  return coordinates


def is_close_to_los_angeles(geometry):
  coordinates = get_polygon_coordinates(geometry)

  for lon, lat in coordinates:
    distance = get_distance_miles((lat, lon), los_angeles_coordinates)

    if distance > max_distance_miles:
      return False

  return True


# ------

'''
takes in a filtered perimeter gdf and returns a gdf cleaned by time
where cleaned by time means every non-null perimeter date included is after the
  official start day for that fire. null perimeter dates are allowed
'''
def clean_by_time(gdf):
  before_count = len(gdf)
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
  
  clean_gdf = gpd.pd.concat(gdf_list, ignore_index=True)
  return clean_gdf, (before_count, len(clean_gdf))


'''
takes in a filtered perimeter gdf and returns a gdf cleaned by distance
where cleaned by distance means every polygon point is less than 200 miles
  from Los Angeles
'''
def clean_by_distance(gdf):
  before_count = len(gdf)
  clean_gdf = gdf[gdf['geometry'].apply(is_close_to_los_angeles)].reset_index(drop=True)
  return clean_gdf, (before_count, len(clean_gdf))


'''
keeps only the incident name and geometry used by extract_perimeter_data.py
so the clean GeoJSON is smaller but has the same record count
'''
def select_plot_columns(gdf):
  return gdf[plot_columns].copy()


# --- file writing ---
def get_count():
  gdf = gpd.read_file(filtered_filename)
  clean_gdf, location_count = clean_by_distance(gdf)
  clean_gdf, time_count = clean_by_time(clean_gdf)
  return {
    'location': location_count,
    'time': time_count
  }


def write_main():
  count = get_count()
  gdf = gpd.read_file(filtered_filename)
  clean_gdf, _ = clean_by_distance(gdf)
  clean_gdf, _ = clean_by_time(clean_gdf)
  clean_gdf = select_plot_columns(clean_gdf)

  if clean_filename.exists():
    clean_filename.unlink()

  clean_gdf.to_file(clean_filename, 'GEOJSON')
  return count


if __name__ == '__main__':
  write_main()

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import contextily as ctx

# prep
filename = "./WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson"
gdf = gpd.read_file(filename)

gdf = gdf.set_crs("EPSG:4326", allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)

# set basic features for the window
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.15)

# --- fire filtering ---

# draw plot
def show_fire_perimeter(ax, fire_name):
  fire_gdf = gdf_base[(gdf_base['poly_IncidentName'].str.lower()) == fire_name]
  # fire_gdf = fire_gdf.head(1)
  
  fire_gdf.plot(ax=ax, categorical=True, markersize=2, color="blue", alpha=0.8, zorder=3)
  
  plt.draw()

# show_fire_perimeter(ax, "eaton")
# ax.set_aspect("equal")
# plt.show()
import geopandas as gpd
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import contextily as ctx

# prep
filename = "./POSTFIRE_CLEAN_DATA.geojson"
gdf = gpd.read_file(filename)

gdf = gdf.set_crs("EPSG:3310", allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)

# visuals
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.15)

# draw default layers
gdf_base.plot(ax=ax, markersize=15, color="crimson", alpha=0.8, zorder=2)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)

def show_specific_fire(fire_name):
  ax.clear()

  fire_gdf = gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]
    
  fire_gdf.plot(ax=ax, markersize=15, color="crimson", alpha=0.8, zorder=2)
  ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=1)

  print(len(fire_gdf))
  
  plt.draw()
fires_list = ["palisades", "mountain", "eaton", "franklin", "line", "bridge"]
show_specific_fire(fires_list[0])
ax.set_title("california fire")
plt.show()
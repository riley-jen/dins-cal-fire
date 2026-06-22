import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# prep
filename = '../files/POSTFIRE_CLEAN_DATA.geojson'
gdf = gpd.read_file(filename)

gdf = gdf.set_crs('EPSG:3310', allow_override=True)
gdf_base = gdf.to_crs(epsg=3857)


# --- fire filtering ---
damage_list = ['no damage', 'affected (>0-10%)', 'minor (10-25%)', 'major (25-50%)', 'destroyed (>50%)', 'inaccessible']
color_code = ['green', 'yellow', 'orange', 'red', 'black', 'gray']
color_dict = dict(zip(damage_list, color_code))

# draw plot
def show_fire_structure(ax, fire_name):
  fire_gdf = gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]
  
  # plot each color of points separately
  for damage, color in color_dict.items():
    damage_gdf = fire_gdf[(fire_gdf['DAMAGE'].str.lower()) == damage]

    if len(damage_gdf) > 0:
      damage_gdf.plot(ax=ax, categorical=True, markersize=2, label=damage, color=color, alpha=0.8, zorder=2)

  make_legend(ax)

# make legend
def make_legend(ax):
  handles, labels = ax.get_legend_handles_labels()
  legend_lookup = dict(zip([label.lower() for label in labels], handles))

  sorted_handles = []
  sorted_labels = []
  
  for damage in damage_list:
    if damage in labels:
      sorted_labels.append(damage)
      sorted_handles.append(legend_lookup[damage])
    
  ax.legend(sorted_handles, sorted_labels, markerscale=3, title='Damage Rating', loc='upper right', frameon=True, facecolor='white')

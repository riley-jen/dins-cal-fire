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
damage_count = dict(zip(damage_list, [0] * len(damage_list)))
total = 0

color_code = ['green', 'yellow', 'orange', 'red', 'black', 'gray']
color_dict = dict(zip(damage_list, color_code))

# draw map plot
def show_fire_structure(map_ax, pie_ax, fire_name):
  global total
  fire_gdf = gdf_base[(gdf_base['INCIDENTNAME'].str.lower()) == fire_name]
  total = len(fire_gdf)
  
  # plot each color of points separately
  for damage, color in color_dict.items():
    damage_gdf = fire_gdf[(fire_gdf['DAMAGE'].str.lower()) == damage]
    damage_count[damage] = len(damage_gdf)

    if len(damage_gdf) > 0:
      damage_gdf.plot(ax=map_ax, categorical=True, markersize=2, label=damage, color=color, alpha=0.8, zorder=2)

  make_map_legend(map_ax)

  # for pie chart
  wedges,_,percentages = pie_ax.pie(damage_count.values(), labels=None, colors=color_code, autopct='%1.1f%%', startangle=90)
  for text in percentages:
    text.set_visible(False)
  make_pie_legend(pie_ax, wedges, percentages)

# make legend for map
def make_map_legend(ax):
  handles, labels = ax.get_legend_handles_labels()
  legend_lookup = dict(zip([label.lower() for label in labels], handles))

  sorted_handles = []
  sorted_labels = []
  
  for damage in damage_list:
    if damage in labels:
      sorted_labels.append(damage)
      sorted_handles.append(legend_lookup[damage])
    
  ax.legend(sorted_handles, sorted_labels, markerscale=3, title='Damage Rating', loc='upper right', 
    bbox_to_anchor=(0.96, 0.95), bbox_transform=ax.figure.transFigure, frameon=True, facecolor='white')

# make legend for pie
def make_pie_legend(ax, wedges, percentages):
  texts = []
  counts = list(damage_count.values())
  
  for i in range(len(counts)):
    texts.append(str(counts[i]) + ' (' + percentages[i].get_text() + ')')

  ax.legend(wedges, texts, markerscale=3, 
    title='Total structures: ' + str(total), loc='lower right', 
    bbox_to_anchor=(0.96, 0.5), bbox_transform=ax.figure.transFigure, frameon=True, facecolor='white')

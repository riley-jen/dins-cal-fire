import geopandas as gpd
import matplotlib.pyplot as plt

filename = "./POSTFIRE_CLEAN_DATA.geojson"
gdf = gpd.read_file(filename)
print("Total rows to plot: ", len(gdf))

gdf.plot(legend=True)
plt.show()
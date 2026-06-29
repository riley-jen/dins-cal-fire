import matplotlib.pyplot as plt
from plot.damage.plot_damage_window import make_damage_window
from plot.material.plot_material_window import make_material_window

damage_fig = plt.figure(figsize=(8, 8))
make_damage_window(damage_fig)

material_fig = plt.figure(figsize=(8, 8))
make_material_window(material_fig)

plt.show()

import matplotlib.pyplot as plt
from damage.plot_damage_window import make_damage_window
from material.plot_material_window import make_material_window, plot_fire_material

damage_fig = plt.figure(figsize=(8, 8))

material_fig = plt.figure(figsize=(8, 8))
make_material_window(material_fig)

make_damage_window(damage_fig, plot_fire_material)

plt.show()

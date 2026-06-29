import matplotlib.pyplot as plt


# --- VARIABLES ---
fig = None
material_ax = None


# --- SET UP ---

def make_material_window(input_figure):
  global fig, material_ax
  fig = input_figure

  fig.canvas.manager.set_window_title('Material Window')
  material_ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
  material_ax.axis('off')

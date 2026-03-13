import os
import matplotlib

# If no display is available (headless environment), use Agg backend and save output to file.
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from matplotlib.widgets import Button

# --- Simple 2D flow simulation (particles moving rightward) ---

NUM_PARTICLES = 100
DT = 0.03
FLOW_SPEED = 0.5
SHOW_VECTORS = True

# Domain
X_MIN, X_MAX = 0, 1
Y_MIN, Y_MAX = 0, 1

# Initialize particles
particles = np.random.rand(NUM_PARTICLES, 2)

# Create plot
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_aspect('equal')
ax.set_title('Simple Particle Flow Simulation')
ax.set_xlabel('x')
ax.set_ylabel('y')

scatter = ax.scatter(particles[:, 0], particles[:, 1], s=30, c='tab:red')

# Create a fixed quiver grid for the velocity field
grid_x, grid_y = np.meshgrid(np.linspace(X_MIN, X_MAX, 12), np.linspace(Y_MIN, Y_MAX, 12))

# Define a velocity field: rightward flow with a small sinusoidal vertical component
def velocity_field(x, y):
    vx = FLOW_SPEED * (1 + 0.2 * np.sin(2 * np.pi * y))
    vy = 0.2 * np.cos(2 * np.pi * x)
    return vx, vy

vx_grid, vy_grid = velocity_field(grid_x, grid_y)
quiver = ax.quiver(grid_x, grid_y, vx_grid, vy_grid, color='tab:blue', alpha=0.7)

# Toggle button for showing/hiding vectors
button_ax = fig.add_axes([0.72, 0.05, 0.2, 0.08])
button = Button(button_ax, 'Toggle Flow Vectors')


def toggle_vectors(event):
    global SHOW_VECTORS
    SHOW_VECTORS = not SHOW_VECTORS
    quiver.set_visible(SHOW_VECTORS)
    fig.canvas.draw_idle()

button.on_clicked(toggle_vectors)

# Animation update

def update(frame):
    global particles
    vx, vy = velocity_field(particles[:, 0], particles[:, 1])

    particles[:, 0] += vx * DT
    particles[:, 1] += vy * DT

    # Wrap particles around the domain (toroidal)
    particles[:, 0] = np.mod(particles[:, 0] - X_MIN, X_MAX - X_MIN) + X_MIN
    particles[:, 1] = np.mod(particles[:, 1] - Y_MIN, Y_MAX - Y_MIN) + Y_MIN

    scatter.set_offsets(particles)
    return scatter,

anim = FuncAnimation(fig, update, interval=30, blit=False)

# If there is no display, save the animation to a GIF instead of showing a window.
if not os.environ.get('DISPLAY'):
    out_path = "flow.gif"
    print(f"No DISPLAY detected; saving animation to {out_path} (this may take a moment)...")
    anim.save(out_path, writer=PillowWriter(fps=20))
    print(f"Saved: {out_path}")
else:
    plt.show()

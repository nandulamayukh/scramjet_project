import numpy as np
import matplotlib

# Use a GUI backend so the plot window appears (assumes $DISPLAY is set).
# This script animates particles moving through a simple flow field.
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulation parameters
NUM_PARTICLES = 200
DT = 0.03  # time step
SPEED = 0.25  # scale of particle velocity

# Initialize particle positions in [0, 1] x [0, 1]
pos = np.random.rand(NUM_PARTICLES, 2)

# Create plot
fig, ax = plt.subplots(figsize=(6, 6))
scat = ax.scatter(pos[:, 0], pos[:, 1], s=30, c="tab:cyan", edgecolors="k")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("equal")
ax.set_title("Particle Flow Simulation")
ax.set_xlabel("x")
ax.set_ylabel("y")

# Define a velocity field (here: a swirling vortex centered at (0.5, 0.5))
def velocity_field(p):
    """Return velocity (vx, vy) for each position p."""
    center = np.array([0.5, 0.5])
    rel = p - center

    # simple rotational field + small radial push
    vx = -rel[:, 1] + 0.3 * (p[:, 0] - 0.5)
    vy = rel[:, 0] + 0.3 * (p[:, 1] - 0.5)
    return np.stack([vx, vy], axis=1)

# Update loop for animation
def update(frame):
    global pos
    v = velocity_field(pos)
    pos = pos + v * DT * SPEED

    # Wrap particles around the domain [0,1] x [0,1]
    pos %= 1.0

    scat.set_offsets(pos)
    return (scat,)

ani = FuncAnimation(fig, update, interval=30, blit=True)

# Keep window open until closed by user
plt.show(block=True)

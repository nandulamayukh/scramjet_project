import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from matplotlib.gridspec import GridSpec
import tkinter as tk
from tkinter import filedialog
import os

# ── CONFIG ──────────────────────────────────────────────
X_COLUMN = "x"     # Column name to use as X axis
Y_COLUMN = "y"     # Column name to use as Y axis
PLOT_TYPE = "line" # "line", "scatter", "bar", "area"
# ────────────────────────────────────────────────────────

# ── FILE PICKER ──────────────────────────────────────────
root = tk.Tk()
root.withdraw()
csv_files = filedialog.askopenfilenames(
    title="Select CSV files to load",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)
root.destroy()

if not csv_files:
    print("No files selected. Exiting.")
    exit()

# ── LOAD DATA ────────────────────────────────────────────
datasets = {}
for path in csv_files:
    try:
        df = pd.read_csv(path)
        name = os.path.basename(path)
        if X_COLUMN not in df.columns or Y_COLUMN not in df.columns:
            print(f"Warning: '{name}' missing column '{X_COLUMN}' or '{Y_COLUMN}'. "
                  f"Found: {list(df.columns)}")
            continue
        datasets[name] = df
        print(f"Loaded: {name}  ({len(df)} rows)")
    except Exception as e:
        print(f"Could not load {path}: {e}")

if not datasets:
    print("No valid datasets loaded. Exiting.")
    exit()

# ── FIGURE LAYOUT ────────────────────────────────────────
n_files = len(datasets)
checkbox_height = max(0.15, min(0.05 * n_files + 0.08, 0.4))

fig = plt.figure(figsize=(12, 6))
fig.patch.set_facecolor("#1e1e2e")

gs = GridSpec(
    1, 2,
    figure=fig,
    width_ratios=[4, 1],
    left=0.07, right=0.97,
    top=0.93, bottom=0.10,
    wspace=0.05
)

ax = fig.add_subplot(gs[0])
ax.set_facecolor("#13131f")
ax.tick_params(colors="#cdd6f4")
ax.xaxis.label.set_color("#cdd6f4")
ax.yaxis.label.set_color("#cdd6f4")
ax.title.set_color("#cdd6f4")
for spine in ax.spines.values():
    spine.set_edgecolor("#45475a")
ax.grid(True, linestyle="--", alpha=0.3, color="#585b70")
ax.set_xlabel(X_COLUMN)
ax.set_ylabel(Y_COLUMN)
ax.set_title("CSV Plotter", fontsize=13, fontweight="bold", pad=10)

# Right panel anchor (invisible)
right_ax = fig.add_subplot(gs[1])
right_ax.set_visible(False)

COLORS = [
    "#89b4fa", "#a6e3a1", "#fab387", "#f38ba8",
    "#cba6f7", "#f9e2af", "#94e2d5", "#eba0ac"
]

# ── PLOT DATA ────────────────────────────────────────────
lines = {}
for i, (name, df) in enumerate(datasets.items()):
    color = COLORS[i % len(COLORS)]
    x = df[X_COLUMN]
    y = df[Y_COLUMN]
    if PLOT_TYPE == "line":
        ln, = ax.plot(x, y, color=color, linewidth=1.5, label=name)
    elif PLOT_TYPE == "scatter":
        ln = ax.scatter(x, y, color=color, s=15, label=name)
    elif PLOT_TYPE == "area":
        ax.fill_between(x, y, alpha=0.2, color=color)
        ln, = ax.plot(x, y, color=color, linewidth=1.5, label=name)
    elif PLOT_TYPE == "bar":
        ln = ax.bar(x, y, color=color, alpha=0.7, label=name)
    lines[name] = ln

legend = ax.legend(
    loc="upper left", fontsize=8,
    facecolor="#313244", edgecolor="#45475a", labelcolor="#cdd6f4"
)

# ── CHECKBOXES ───────────────────────────────────────────
right_pos = right_ax.get_position()
cb_left   = right_pos.x0 + 0.01
cb_bottom = right_pos.y1 - checkbox_height - 0.02
cb_width  = right_pos.width - 0.01

check_ax = fig.add_axes([cb_left, cb_bottom, cb_width, checkbox_height])
check_ax.set_facecolor("#313244")
for spine in check_ax.spines.values():
    spine.set_edgecolor("#45475a")

labels = list(datasets.keys())
check = widgets.CheckButtons(
    check_ax,
    labels,
    actives=[True] * len(labels)
)

for text in check.labels:
    text.set_color("#cdd6f4")
    text.set_fontsize(8)
for rect in check.rectangles:
    rect.set_facecolor("#1e1e2e")
    rect.set_edgecolor("#89b4fa")
for line_pair in check.lines:
    for ln in line_pair:
        ln.set_color("#89b4fa")
        ln.set_linewidth(1.5)

def on_check(label):
    idx = labels.index(label)
    visible = check.get_status()[idx]
    obj = lines[label]
    if hasattr(obj, "set_visible"):
        obj.set_visible(visible)
    else:  # BarContainer
        for bar in obj:
            bar.set_visible(visible)
    # Rebuild legend with only visible items
    handles, lbls = [], []
    for name, ln in lines.items():
        if check.get_status()[labels.index(name)]:
            if hasattr(ln, "get_label"):
                handles.append(ln)
                lbls.append(name)
    ax.legend(
        handles, lbls,
        loc="upper left", fontsize=8,
        facecolor="#313244", edgecolor="#45475a", labelcolor="#cdd6f4"
    )
    fig.canvas.draw_idle()

check.on_clicked(on_check)

# ── COORDINATE BOX ───────────────────────────────────────
coord_bottom = cb_bottom - 0.13
coord_ax = fig.add_axes([cb_left, coord_bottom, cb_width, 0.10])
coord_ax.set_facecolor("#313244")
coord_ax.set_xticks([])
coord_ax.set_yticks([])
for spine in coord_ax.spines.values():
    spine.set_edgecolor("#45475a")

coord_ax.text(
    0.5, 0.82, "Cursor Position",
    transform=coord_ax.transAxes,
    ha="center", va="top",
    color="#89b4fa", fontsize=8, fontweight="bold"
)
coord_text = coord_ax.text(
    0.5, 0.35, "x: —\ny: —",
    transform=coord_ax.transAxes,
    ha="center", va="center",
    color="#cdd6f4", fontsize=9,
    fontfamily="monospace"
)

def on_mouse_move(event):
    if event.inaxes == ax and event.xdata is not None:
        coord_text.set_text(f"x: {event.xdata:.4f}\ny: {event.ydata:.4f}")
    else:
        coord_text.set_text("x: —\ny: —")
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)

plt.show()
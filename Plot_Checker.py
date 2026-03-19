import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

PLOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Plots")


def find_csv_files():
    if not os.path.isdir(PLOTS_DIR):
        return []
    return [f for f in os.listdir(PLOTS_DIR) if f.lower().endswith(".csv")]


def load_and_plot(selected_files, ax, canvas):
    ax.clear()
    if not selected_files:
        canvas.draw()
        return

    for filename in selected_files:
        path = os.path.join(PLOTS_DIR, filename)
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            cols = df.columns.tolist()

            if len(cols) < 2:
                messagebox.showwarning("Skip", f"{filename}: needs at least 2 columns.")
                continue

            x_col, y_col = cols[0], cols[1]
            label = os.path.splitext(filename)[0]
            ax.plot(df[x_col], df[y_col], marker="o", markersize=4, linewidth=1.5, label=label)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read {filename}:\n{e}")

    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    canvas.draw()


def build_gui():
    root = tk.Tk()
    root.title("CSV Plot Selector")
    root.resizable(True, True)

    # ── Left panel: file list ──────────────────────────────────────────────
    left = tk.Frame(root, width=220, bg="#f5f5f5")
    left.pack(side=tk.LEFT, fill=tk.Y, padx=0)
    left.pack_propagate(False)

    tk.Label(left, text="CSV files in /Plots",
             font=("Helvetica", 11, "bold"), bg="#f5f5f5",
             anchor="w").pack(fill=tk.X, padx=12, pady=(14, 4))

    tk.Frame(left, height=1, bg="#d0d0d0").pack(fill=tk.X, padx=12)

    scroll_frame = tk.Frame(left, bg="#f5f5f5")
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    canvas_scroll = tk.Canvas(scroll_frame, bg="#f5f5f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas_scroll.yview)
    inner = tk.Frame(canvas_scroll, bg="#f5f5f5")

    inner.bind("<Configure>",
               lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
    canvas_scroll.create_window((0, 0), window=inner, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar.set)

    canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    check_vars = {}
    csv_files = find_csv_files()

    # ── Right panel: matplotlib chart ─────────────────────────────────────
    right = tk.Frame(root)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    fig, ax = plt.subplots(figsize=(8, 5), tight_layout=True)
    mpl_canvas = FigureCanvasTkAgg(fig, master=right)
    mpl_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_change(*_):
        selected = [f for f, var in check_vars.items() if var.get()]
        load_and_plot(selected, ax, mpl_canvas)

    def refresh_file_list():
        for widget in inner.winfo_children():
            widget.destroy()
        check_vars.clear()

        files = find_csv_files()
        if not files:
            tk.Label(inner, text="No CSV files found.",
                     bg="#f5f5f5", fg="#999", font=("Helvetica", 10),
                     wraplength=190).pack(anchor="w", padx=4, pady=8)
            return

        for f in sorted(files):
            var = tk.BooleanVar(value=False)
            check_vars[f] = var
            cb = tk.Checkbutton(inner, text=f, variable=var, command=on_change,
                                bg="#f5f5f5", activebackground="#f5f5f5",
                                font=("Helvetica", 10), anchor="w", wraplength=190)
            cb.pack(fill=tk.X, padx=4, pady=2)

    # ── Bottom buttons ─────────────────────────────────────────────────────
    btn_bar = tk.Frame(left, bg="#f5f5f5")
    btn_bar.pack(fill=tk.X, padx=8, pady=(0, 10))

    def select_all():
        for var in check_vars.values():
            var.set(True)
        on_change()

    def deselect_all():
        for var in check_vars.values():
            var.set(False)
        on_change()

    ttk.Button(btn_bar, text="Select all",   command=select_all).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
    ttk.Button(btn_bar, text="Clear",        command=deselect_all).pack(side=tk.LEFT, expand=True, fill=tk.X)

    ttk.Button(left, text="↺  Refresh file list", command=refresh_file_list).pack(
        fill=tk.X, padx=8, pady=(0, 12))

    refresh_file_list()
    root.mainloop()


if __name__ == "__main__":
    build_gui()
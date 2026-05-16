import os
import sys
import threading
import datetime as dt

# Agrega la carpeta donde está este archivo al path,
# sin importar desde dónde se ejecute
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from util import generar_ciudades_con_distancias, calculate_path_distance
from util_nearest_neighbor import nearest_neighbor
from TSP import TSP

# ── Paleta ────────────────────────────────────────────────────────────────────
BG        = "#1e1e2e"
BG2       = "#2a2a3e"
BG3       = "#313145"
ACCENT    = "#7c9ef8"
ACCENT2   = "#a6e3a1"
ACCENT3   = "#f38ba8"
TEXT      = "#cdd6f4"
TEXT_DIM  = "#6c7086"
BTN_ACT   = "#45475a"

CASES = {
    "Caso 1": {
        "desc": "LP sin heurísticas\n10 · 20 · 30 · 40 · 50 ciudades",
        "color": ACCENT,
    },
    "Caso 2": {
        "desc": "Heurística de límites\n70 ciudades — con vs sin",
        "color": ACCENT2,
    },
    "Caso 3": {
        "desc": "Heurística vecinos cercanos\n100 ciudades — con vs sin",
        "color": ACCENT3,
    },
}


class TSPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Travelling Salesman Problem — MSDS 6004")
        self.configure(bg=BG)
        self.state("zoomed") if sys.platform == "win32" else self.attributes("-zoomed", True) if sys.platform == "linux" else None
        self.geometry("1400x860")
        self.minsize(1100, 700)

        self.current_case = tk.StringVar(value="Caso 1")
        self._running = False

        self._build_sidebar()
        self._build_main()
        self._show_case("Caso 1")

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=BG2, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / title
        tk.Label(self.sidebar, text="TSP", font=("Helvetica Neue", 32, "bold"),
                 bg=BG2, fg=ACCENT).pack(pady=(30, 0))
        tk.Label(self.sidebar, text="Travelling Salesman\nProblem",
                 font=("Helvetica Neue", 11), bg=BG2, fg=TEXT_DIM,
                 justify="center").pack(pady=(4, 24))

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # Case buttons
        self.case_btns = {}
        for case, info in CASES.items():
            frame = tk.Frame(self.sidebar, bg=BG2)
            frame.pack(fill="x", padx=12, pady=4)

            btn = tk.Button(
                frame, text=case,
                font=("Helvetica Neue", 13, "bold"),
                bg=BG3, fg=TEXT, bd=0, relief="flat",
                activebackground=BTN_ACT, activeforeground=TEXT,
                cursor="hand2", anchor="w", padx=16, pady=10,
                command=lambda c=case: self._show_case(c)
            )
            btn.pack(fill="x")
            desc = tk.Label(frame, text=info["desc"],
                            font=("Helvetica Neue", 9), bg=BG2,
                            fg=TEXT_DIM, justify="left", padx=28)
            desc.pack(fill="x")
            self.case_btns[case] = btn

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=20, pady=16)

        # Params frame
        self.params_frame = tk.Frame(self.sidebar, bg=BG2)
        self.params_frame.pack(fill="x", padx=16)

        # Run button
        self.run_btn = tk.Button(
            self.sidebar, text="▶  Ejecutar",
            font=("Helvetica Neue", 13, "bold"),
            bg=ACCENT, fg=BG, bd=0, relief="flat",
            activebackground="#5a7de0", activeforeground=BG,
            cursor="hand2", padx=16, pady=12,
            command=self._run_case
        )
        self.run_btn.pack(fill="x", padx=12, pady=(16, 4))

        # Status label
        self.status_var = tk.StringVar(value="Listo")
        self.status_lbl = tk.Label(
            self.sidebar, textvariable=self.status_var,
            font=("Helvetica Neue", 10), bg=BG2, fg=TEXT_DIM,
            wraplength=200, justify="center"
        )
        self.status_lbl.pack(pady=6)

    # ── MAIN AREA ─────────────────────────────────────────────────────────────
    def _build_main(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        # Header bar
        self.header = tk.Frame(self.main, bg=BG3, height=54)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.header_title = tk.Label(
            self.header, text="", font=("Helvetica Neue", 16, "bold"),
            bg=BG3, fg=TEXT, padx=24
        )
        self.header_title.pack(side="left", fill="y")
        self.header_sub = tk.Label(
            self.header, text="", font=("Helvetica Neue", 11),
            bg=BG3, fg=TEXT_DIM, padx=8
        )
        self.header_sub.pack(side="left", fill="y")

        # Results bar
        self.results_bar = tk.Frame(self.main, bg=BG2, height=42)
        self.results_bar.pack(fill="x")
        self.results_bar.pack_propagate(False)
        self.results_var = tk.StringVar(value="")
        tk.Label(self.results_bar, textvariable=self.results_var,
                 font=("Helvetica Neue", 11), bg=BG2, fg=ACCENT2,
                 padx=20).pack(side="left", fill="y")

        # Canvas area
        self.canvas_frame = tk.Frame(self.main, bg=BG)
        self.canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.fig = Figure(facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_placeholder()

    # ── PLACEHOLDER ───────────────────────────────────────────────────────────
    def _draw_placeholder(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(BG)
        ax.text(0.5, 0.5, "Selecciona un caso y presiona  ▶  Ejecutar",
                ha="center", va="center", fontsize=15,
                color=TEXT_DIM, transform=ax.transAxes)
        ax.axis("off")
        self.canvas.draw()

    # ── PARAM WIDGETS ─────────────────────────────────────────────────────────
    def _clear_params(self):
        for w in self.params_frame.winfo_children():
            w.destroy()
        self.param_vars = {}

    def _add_param(self, label, default, key):
        row = tk.Frame(self.params_frame, bg=BG2)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=("Helvetica Neue", 10),
                 bg=BG2, fg=TEXT_DIM, width=14, anchor="w").pack(side="left")
        var = tk.StringVar(value=str(default))
        entry = tk.Entry(row, textvariable=var,
                         font=("Helvetica Neue", 10),
                         bg=BG3, fg=TEXT, bd=0, relief="flat",
                         insertbackground=TEXT, width=8)
        entry.pack(side="left", padx=(4, 0))
        self.param_vars[key] = var

    def _add_check(self, label, default, key):
        var = tk.BooleanVar(value=default)
        row = tk.Frame(self.params_frame, bg=BG2)
        row.pack(fill="x", pady=3)
        tk.Checkbutton(row, text=label, variable=var,
                       font=("Helvetica Neue", 10),
                       bg=BG2, fg=TEXT_DIM, selectcolor=BG3,
                       activebackground=BG2, activeforeground=TEXT,
                       bd=0).pack(side="left")
        self.param_vars[key] = var

    # ── SHOW CASE (update sidebar params) ─────────────────────────────────────
    def _show_case(self, case):
        self.current_case.set(case)
        for c, btn in self.case_btns.items():
            btn.config(bg=BTN_ACT if c == case else BG3)

        info = CASES[case]
        self.header_title.config(text=case, fg=info["color"])
        self.header_sub.config(text=info["desc"].replace("\n", "  ·  "))
        self.results_var.set("")
        self._clear_params()
        self._draw_placeholder()

        if case == "Caso 1":
            self._add_param("Ciudades", "10,20,30,40,50", "n_list")
            self._add_param("mipgap", "0.05", "mipgap")
            self._add_param("Tiempo (s)", "30", "time_limit")
            self._add_check("Mostrar tee", False, "tee")
        elif case == "Caso 2":
            self._add_param("Ciudades", "70", "n")
            self._add_param("mipgap", "0.2", "mipgap")
            self._add_param("Tiempo (s)", "40", "time_limit")
            self._add_check("Mostrar tee", True, "tee")
        elif case == "Caso 3":
            self._add_param("Ciudades", "100", "n")
            self._add_param("mipgap", "0.05", "mipgap")
            self._add_param("Tiempo (s)", "60", "time_limit")
            self._add_check("Mostrar tee", True, "tee")

    # ── RUN ───────────────────────────────────────────────────────────────────
    def _run_case(self):
        if self._running:
            return
        self._running = True
        self.run_btn.config(state="disabled", text="⏳ Ejecutando...")
        self.status_var.set("Corriendo…")
        self.results_var.set("")

        case = self.current_case.get()
        thread = threading.Thread(target=self._execute, args=(case,), daemon=True)
        thread.start()

    def _execute(self, case):
        try:
            if case == "Caso 1":
                self._exec_caso1()
            elif case == "Caso 2":
                self._exec_caso2()
            elif case == "Caso 3":
                self._exec_caso3()
        except Exception as e:
            self.status_var.set(f"Error: {e}")
        finally:
            self._running = False
            self.run_btn.config(state="normal", text="▶  Ejecutar")

    # ── PLOT HELPER ───────────────────────────────────────────────────────────
    def _plot_route(self, ax, ciudades, ruta, title, color="red", show_labels=False):
        ax.set_facecolor(BG)
        xs = [ciudades[c][0] for c in ruta]
        ys = [ciudades[c][1] for c in ruta]
        ax.plot(xs, ys, '-o', color=color, markersize=3.5,
                linewidth=0.9, markerfacecolor=color)
        if show_labels:
            for c in ruta[:-1]:
                ax.text(ciudades[c][0], ciudades[c][1], c,
                        fontsize=6, color=TEXT_DIM)
        ax.set_title(title, color=TEXT, fontsize=10, fontweight="bold", pad=8)
        ax.tick_params(colors=TEXT_DIM, labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor(BG3)
        ax.set_facecolor(BG)
        ax.grid(True, color=BG3, linewidth=0.5)

    # ── CASO 1 ────────────────────────────────────────────────────────────────
    def _exec_caso1(self):
        n_list_str = self.param_vars["n_list"].get()
        n_list = [int(x.strip()) for x in n_list_str.split(",")]
        mipgap = float(self.param_vars["mipgap"].get())
        time_limit = int(self.param_vars["time_limit"].get())
        tee = self.param_vars["tee"].get()

        data = []
        for i, n in enumerate(n_list):
            self.status_var.set(f"Ciudad {n} ({i+1}/{len(n_list)})…")
            ciudades, distancias = generar_ciudades_con_distancias(n)

            t0 = dt.datetime.now()
            tsp = TSP(ciudades, distancias, heuristics=[])
            ruta_lp = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
            elapsed = (dt.datetime.now() - t0).total_seconds()

            ruta_nn = nearest_neighbor(ciudades, distancias)
            dist_lp = calculate_path_distance(distancias, ruta_lp)
            dist_nn = calculate_path_distance(distancias, ruta_nn)
            data.append((n, ciudades, ruta_lp, dist_lp, ruta_nn, dist_nn, elapsed))

        # draw
        self.status_var.set("Graficando…")
        self.fig.clear()
        self.fig.patch.set_facecolor(BG)

        n_cols = len(n_list)
        gs = self.fig.add_gridspec(2, n_cols, hspace=0.4, wspace=0.3,
                                   top=0.92, bottom=0.06, left=0.04, right=0.98)

        result_parts = []
        for col, (n, ciudades, ruta_lp, dist_lp, ruta_nn, dist_nn, elapsed) in enumerate(data):
            mejora = (dist_nn - dist_lp) / dist_nn * 100
            ax_lp = self.fig.add_subplot(gs[0, col])
            ax_nn = self.fig.add_subplot(gs[1, col])
            show = n <= 15
            self._plot_route(ax_lp, ciudades, ruta_lp,
                             f"LP — {n}c\n{dist_lp:.1f}  ({elapsed:.0f}s)", ACCENT, show)
            self._plot_route(ax_nn, ciudades, ruta_nn,
                             f"Vecino Cercano — {n}c\n{dist_nn:.1f}", ACCENT3, show)
            result_parts.append(f"{n}c: LP {dist_lp:.0f} vs NN {dist_nn:.0f} ({mejora:+.1f}%)")

        self.fig.suptitle("Caso 1 — LP sin heurísticas vs Vecino Cercano",
                          color=TEXT, fontsize=13, fontweight="bold")
        self.canvas.draw()
        self.results_var.set("   |   ".join(result_parts))
        self.status_var.set("✓ Completado")

    # ── CASO 2 ────────────────────────────────────────────────────────────────
    def _exec_caso2(self):
        n = int(self.param_vars["n"].get())
        mipgap = float(self.param_vars["mipgap"].get())
        time_limit = int(self.param_vars["time_limit"].get())
        tee = self.param_vars["tee"].get()

        ciudades, distancias = generar_ciudades_con_distancias(n)

        self.status_var.set("CON heurística de límites…")
        t0 = dt.datetime.now()
        tsp_con = TSP(ciudades, distancias, heuristics=["limitar_funcion_objetivo"])
        ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        t_con = (dt.datetime.now() - t0).total_seconds()
        dist_con = calculate_path_distance(distancias, ruta_con)

        self.status_var.set("SIN heurística…")
        t0 = dt.datetime.now()
        tsp_sin = TSP(ciudades, distancias, heuristics=[])
        ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        t_sin = (dt.datetime.now() - t0).total_seconds()
        dist_sin = calculate_path_distance(distancias, ruta_sin)

        diferencia = (dist_sin - dist_con) / dist_sin * 100

        self.status_var.set("Graficando…")
        self.fig.clear()
        self.fig.patch.set_facecolor(BG)
        gs = self.fig.add_gridspec(1, 2, hspace=0.3, wspace=0.25,
                                   top=0.88, bottom=0.06, left=0.04, right=0.98)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax2 = self.fig.add_subplot(gs[0, 1])

        self._plot_route(ax1, ciudades, ruta_con,
                         f"CON heurística de límites\nDistancia: {dist_con:.2f}  ({t_con:.0f}s)", ACCENT2)
        self._plot_route(ax2, ciudades, ruta_sin,
                         f"SIN heurística\nDistancia: {dist_sin:.2f}  ({t_sin:.0f}s)", ACCENT3)

        self.fig.suptitle(
            f"Caso 2 — {n} ciudades | mipgap={mipgap} | límite={time_limit}s",
            color=TEXT, fontsize=13, fontweight="bold"
        )
        self.canvas.draw()

        ganador = "CON heurística" if dist_con < dist_sin else "SIN heurística"
        self.results_var.set(
            f"CON: {dist_con:.2f}   SIN: {dist_sin:.2f}   "
            f"Diferencia: {diferencia:+.1f}%   Mejor: {ganador}"
        )
        self.status_var.set("✓ Completado")

    # ── CASO 3 ────────────────────────────────────────────────────────────────
    def _exec_caso3(self):
        n = int(self.param_vars["n"].get())
        mipgap = float(self.param_vars["mipgap"].get())
        time_limit = int(self.param_vars["time_limit"].get())
        tee = self.param_vars["tee"].get()

        ciudades, distancias = generar_ciudades_con_distancias(n)

        self.status_var.set("CON heurística vecinos cercanos…")
        t0 = dt.datetime.now()
        tsp_con = TSP(ciudades, distancias, heuristics=["vecino_cercano"])
        ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        t_con = (dt.datetime.now() - t0).total_seconds()
        dist_con = calculate_path_distance(distancias, ruta_con)

        self.status_var.set("SIN heurística…")
        t0 = dt.datetime.now()
        tsp_sin = TSP(ciudades, distancias, heuristics=[])
        ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        t_sin = (dt.datetime.now() - t0).total_seconds()
        dist_sin = calculate_path_distance(distancias, ruta_sin)

        self.status_var.set("Vecino Cercano (referencia)…")
        ruta_nn = nearest_neighbor(ciudades, distancias)
        dist_nn = calculate_path_distance(distancias, ruta_nn)

        diferencia = (dist_sin - dist_con) / dist_sin * 100

        self.status_var.set("Graficando…")
        self.fig.clear()
        self.fig.patch.set_facecolor(BG)
        gs = self.fig.add_gridspec(1, 3, hspace=0.3, wspace=0.25,
                                   top=0.88, bottom=0.06, left=0.03, right=0.99)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax3 = self.fig.add_subplot(gs[0, 2])

        self._plot_route(ax1, ciudades, ruta_con,
                         f"CON heurística vecinos\nDistancia: {dist_con:.2f}  ({t_con:.0f}s)", ACCENT)
        self._plot_route(ax2, ciudades, ruta_sin,
                         f"SIN heurística\nDistancia: {dist_sin:.2f}  ({t_sin:.0f}s)", ACCENT2)
        self._plot_route(ax3, ciudades, ruta_nn,
                         f"Vecino Cercano (ref.)\nDistancia: {dist_nn:.2f}", ACCENT3)

        self.fig.suptitle(
            f"Caso 3 — {n} ciudades | mipgap={mipgap} | límite={time_limit}s",
            color=TEXT, fontsize=13, fontweight="bold"
        )
        self.canvas.draw()

        ganador = "CON heurística" if dist_con < dist_sin else "SIN heurística"
        self.results_var.set(
            f"CON: {dist_con:.2f}   SIN: {dist_sin:.2f}   NN: {dist_nn:.2f}   "
            f"Diferencia LP: {diferencia:+.1f}%   Mejor LP: {ganador}"
        )
        self.status_var.set("✓ Completado")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = TSPApp()
    app.mainloop()

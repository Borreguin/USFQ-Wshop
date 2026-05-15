import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.lines import Line2D

from maze_model import MazeModel
from solvers import ALL_SOLVERS, MAZE_NAMES, SolverResult

# ── palette ───────────────────────────────────────────────────────────────────
BG_DARK  = '#1A252F'
BG_MID   = '#2C3E50'
BG_PANEL = '#34495E'
BG_GRAPH = '#0D1B2A'
FG_WHITE = '#ECF0F1'
FG_DIM   = '#95A5A6'
ACCENT   = '#27AE60'
WARNING  = '#F39C12'
PATH_CLR = '#3498DB'

# RGB float triplets used for imshow animation
_C_WALL    = [0.17, 0.24, 0.31]
_C_PASS    = [0.93, 0.94, 0.95]
_C_START   = [0.15, 0.68, 0.38]
_C_END     = [0.91, 0.30, 0.24]
_C_VISITED = [0.95, 0.61, 0.07]   # orange — explored
_C_PATH    = [0.20, 0.60, 0.86]   # blue   — solution

_CELL_RGB = {'#': _C_WALL, ' ': _C_PASS, 'E': _C_START, 'S': _C_END}


def _make_arr(maze: MazeModel) -> np.ndarray:
    """Build an (H, W, 3) float array representing the initial maze colours."""
    arr = np.ones((maze.rows, maze.cols, 3))
    for r in range(maze.rows):
        for c, ch in enumerate(maze.grid[r]):
            arr[r, c] = _CELL_RGB.get(ch, _C_PASS)
    return arr


def _style_ax(ax):
    ax.set_facecolor(BG_GRAPH)
    ax.tick_params(colors=FG_WHITE)
    for sp in ax.spines.values():
        sp.set_color('#4A5568')


def _toolbar(fig, parent):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    tb_frame = tk.Frame(parent, bg=BG_DARK)
    tb_frame.pack(fill='x')
    NavigationToolbar2Tk(canvas, tb_frame)
    return canvas


# ── application ───────────────────────────────────────────────────────────────
class MazeApp:
    _EXP_FRAMES = 60    # number of frames for exploration animation
    _PATH_FRAMES = 30   # number of frames for path animation
    _DELAY_MS = 25      # ms between exploration frames
    _PATH_DELAY = 45    # ms between path frames

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Maze Solver — MSDS 6004 IA · Grupo 6")
        self.root.geometry("1250x840")
        self.root.configure(bg=BG_DARK)

        self.maze: MazeModel | None = None
        self.results: list[SolverResult] = []
        self._stop_anim = False
        self._anim_arrs: list[np.ndarray] = []
        self._anim_imgs: list = []

        self._build_ui()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        hdr = tk.Frame(self.root, bg='#141E26', pady=8)
        hdr.pack(fill='x')
        tk.Label(hdr, text="Maze Solver — Algoritmos de Busqueda",
                 font=('Helvetica', 16, 'bold'), bg='#141E26', fg=FG_WHITE).pack()
        tk.Label(hdr,
                 text="MSDS 6004  Grupo 6  |  BFS  DFS  A*  Grover (Quantum-Inspired)",
                 font=('Helvetica', 9), bg='#141E26', fg=FG_DIM).pack()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=BG_MID, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[14, 6],
                        font=('Helvetica', 10, 'bold'),
                        background=BG_PANEL, foreground=FG_WHITE)
        style.map('TNotebook.Tab', background=[('selected', ACCENT)])

        nb = ttk.Notebook(self.root)
        nb.pack(fill='both', expand=True, padx=6, pady=6)

        t1 = tk.Frame(nb, bg=BG_MID)
        t2 = tk.Frame(nb, bg=BG_DARK)
        t3 = tk.Frame(nb, bg=BG_DARK)

        nb.add(t1, text='  Configuracion  ')
        nb.add(t2, text='  Grafo  ')
        nb.add(t3, text='  Complejidad  ')

        self._build_config_tab(t1)
        self._build_graph_tab(t2)
        self._build_complexity_tab(t3)

    # ── Tab 1: controls + animated maze + results table ───────────────────────
    def _build_config_tab(self, parent):
        # ── left control panel ────────────────────────────────────────────────
        left = tk.Frame(parent, bg=BG_PANEL, padx=18, pady=18, width=235)
        left.pack(side='left', fill='y')
        left.pack_propagate(False)

        def L(text, **kw):
            pady = kw.pop('pady', None)
            kw.setdefault('bg', BG_PANEL)
            kw.setdefault('fg', FG_WHITE)
            kw.setdefault('font', ('Helvetica', 10))
            kw.setdefault('anchor', 'w')
            widget = tk.Label(left, text=text, **kw)
            widget.pack(fill='x', **({'pady': pady} if pady else {}))

        L("Configuracion", font=('Helvetica', 13, 'bold'), pady=(0, 12))

        L("Laberinto:")
        self._maze_var = tk.StringVar(value=MAZE_NAMES[0])
        ttk.Combobox(left, textvariable=self._maze_var,
                     values=MAZE_NAMES, state='readonly').pack(fill='x', pady=(2, 10))

        L("Algoritmo:")
        self._algo_var = tk.StringVar(value='Todos')
        ttk.Combobox(left, textvariable=self._algo_var,
                     values=['Todos'] + [s.name for s in ALL_SOLVERS],
                     state='readonly').pack(fill='x', pady=(2, 16))

        self._run_btn = tk.Button(
            left, text="  RESOLVER", command=self._run_solve,
            bg=ACCENT, fg='white', font=('Helvetica', 12, 'bold'),
            relief='flat', pady=10, cursor='hand2',
            activebackground='#1E8449')
        self._run_btn.pack(fill='x', pady=(0, 8))

        self._status_var = tk.StringVar(value="Listo.")
        tk.Label(left, textvariable=self._status_var, bg=BG_PANEL, fg=WARNING,
                 font=('Helvetica', 9, 'italic'), wraplength=200,
                 justify='left').pack(fill='x')

        tk.Frame(left, bg=BG_PANEL, height=14).pack()
        L("Complejidades:", font=('Helvetica', 10, 'bold'))
        tk.Label(left,
                 text=("BFS    O(V+E)    optimo\n"
                       "DFS    O(V+E)    no optimo\n"
                       "A*     O(E logV) optimo\n"
                       "Grover O(sqrt N) cuantico"),
                 bg=BG_PANEL, fg='#BDC3C7', font=('Courier', 9),
                 justify='left').pack(anchor='w', pady=(2, 0))

        tk.Frame(left, bg=BG_PANEL, height=12).pack()
        L("Leyenda animacion:", font=('Helvetica', 10, 'bold'))
        for hex_clr, label in [('#27AE60', 'Inicio (E)'),
                                ('#E74C3C', 'Salida (S)'),
                                ('#F39C12', 'Nodo explorado'),
                                ('#3498DB', 'Camino optimo')]:
            row = tk.Frame(left, bg=BG_PANEL)
            row.pack(fill='x', pady=1)
            tk.Canvas(row, width=13, height=13, bg=hex_clr,
                      highlightthickness=0).pack(side='left')
            tk.Label(row, text=f"  {label}", bg=BG_PANEL, fg='#BDC3C7',
                     font=('Helvetica', 8)).pack(side='left')

        # ── right panel: maze canvas (top) + table (bottom) ──────────────────
        right = tk.Frame(parent, bg=BG_MID)
        right.pack(side='right', fill='both', expand=True)

        # maze animation figure
        maze_frame = tk.Frame(right, bg=BG_DARK)
        maze_frame.pack(fill='both', expand=True)

        self._anim_fig = plt.figure(facecolor=BG_DARK, figsize=(9, 5))
        ax0 = self._anim_fig.add_subplot(111)
        ax0.set_facecolor(BG_DARK)
        ax0.text(0.5, 0.5, 'Selecciona un laberinto y presiona RESOLVER',
                 ha='center', va='center', color=FG_DIM, fontsize=11,
                 transform=ax0.transAxes)
        ax0.axis('off')
        self._anim_canvas = FigureCanvasTkAgg(self._anim_fig, master=maze_frame)
        self._anim_canvas.get_tk_widget().pack(fill='both', expand=True)

        # results table (fixed height)
        tbl_frame = tk.Frame(right, bg=BG_MID, height=185)
        tbl_frame.pack(fill='x', padx=4, pady=(0, 4))
        tbl_frame.pack_propagate(False)

        cols = (
            'Algoritmo', 'Pasos', 'Nodos', 'Tiempo (ms)',
            'POR', 'Penetrance', 'Overhead', 'EBF', 'Oracle k', 'Estado',
        )
        col_widths = (110, 58, 65, 90, 62, 85, 80, 92, 70, 105)
        self._result_tree = ttk.Treeview(tbl_frame, columns=cols,
                                         show='headings', height=4)
        for col, w in zip(cols, col_widths):
            self._result_tree.heading(col, text=col)
            self._result_tree.column(col, width=w, anchor='center', minwidth=w)

        vsb = ttk.Scrollbar(tbl_frame, orient='vertical',
                            command=self._result_tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient='horizontal',
                            command=self._result_tree.xview)
        self._result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._result_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

    # ── Tab 2: grafo (top) | search tree (bottom) ────────────────────────────
    def _build_graph_tab(self, parent):
        hdr = tk.Frame(parent, bg=BG_MID, pady=6, padx=10)
        hdr.pack(fill='x')

        tk.Label(hdr, text="Arbol de busqueda — algoritmo:",
                 bg=BG_MID, fg=FG_WHITE, font=('Helvetica', 10)).pack(side='left')
        self._tree_algo_var = tk.StringVar(value=ALL_SOLVERS[0].name)
        cb = ttk.Combobox(hdr, textvariable=self._tree_algo_var,
                          values=[s.name for s in ALL_SOLVERS],
                          state='readonly', width=16)
        cb.pack(side='left', padx=(8, 0))
        cb.bind('<<ComboboxSelected>>', lambda _: self._refresh_graph_tab())

        tk.Label(hdr,
                 text="↑ Grafo completo   ↓ Árbol de búsqueda",
                 bg=BG_MID, fg=FG_DIM, font=('Helvetica', 8, 'italic'),
                 ).pack(side='right', padx=8)

        self._graph_fig, (self._ax_graph, self._ax_tree) = plt.subplots(
            2, 1, figsize=(14, 10),
            facecolor=BG_DARK,
            gridspec_kw={'hspace': 0.38},
        )

        for ax, msg in [(self._ax_graph, 'Grafo del laberinto'),
                        (self._ax_tree,  'Arbol de busqueda')]:
            ax.set_facecolor(BG_GRAPH)
            ax.text(0.5, 0.5, f'{msg}\n(ejecuta RESOLVER primero)',
                    ha='center', va='center', color=FG_DIM, fontsize=10,
                    transform=ax.transAxes)
            ax.axis('off')

        self._graph_canvas = _toolbar(self._graph_fig, parent)

    # ── Tab 3: complexity charts ──────────────────────────────────────────────
    def _build_complexity_tab(self, parent):
        self._cplx_fig = plt.figure(figsize=(11, 7), facecolor=BG_DARK)
        self._cplx_fig.text(0.5, 0.5, 'Ejecuta RESOLVER primero',
                            ha='center', va='center', color=FG_DIM, fontsize=12)
        self._cplx_canvas = _toolbar(self._cplx_fig, parent)

    # ── solver thread ─────────────────────────────────────────────────────────
    def _run_solve(self):
        self._stop_anim = True          # cancel any running animation
        self._run_btn.config(state='disabled', text='Ejecutando...')
        self._status_var.set("Cargando laberinto...")
        threading.Thread(target=self._solve_thread, daemon=True).start()

    def _solve_thread(self):
        try:
            self.maze = MazeModel.from_name(self._maze_var.get())
            algo = self._algo_var.get()
            solvers = ALL_SOLVERS if algo == 'Todos' else [
                s for s in ALL_SOLVERS if s.name == algo]

            self.results = []
            for s in solvers:
                self._status_var.set(f"Ejecutando {s.name}...")
                self.results.append(
                    s.solve(self.maze.graph, self.maze.start, self.maze.end))

            self.root.after(0, self._on_solve_done)
        except Exception as exc:
            self.root.after(0, lambda e=exc: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self._run_btn.config(
                state='normal', text='  RESOLVER'))

    def _on_solve_done(self):
        self._status_var.set(f"Animando {len(self.results)} algoritmo(s)…")
        self._update_table()
        self._setup_anim_figure()
        self._stop_anim = False
        self._run_anim_exploration(0)
        self._refresh_graph_tab()
        self._update_complexity_tab()

    # ── results table ─────────────────────────────────────────────────────────
    def _update_table(self):
        for row in self._result_tree.get_children():
            self._result_tree.delete(row)

        total = self.maze.node_count
        optimal = min((r.steps for r in self.results if r.found), default=1)

        for r in self.results:
            if r.found:
                m = r.compute_metrics(optimal, total)
                steps   = str(r.steps)
                por     = f"{m.path_optimality_ratio:.4f}"
                pen     = f"{m.search_penetrance:.4f}"
                ovh     = f"{m.search_overhead:.4f}"
                ebf     = f"{m.effective_branching_factor:.6f}"
                oc      = str(m.oracle_calls) if m.oracle_calls > 0 else "—"
                estado  = "Encontrado"
            else:
                steps = por = pen = ovh = ebf = oc = "N/A"
                estado = "No encontrado"

            self._result_tree.insert('', 'end', values=(
                r.algorithm, steps, r.nodes_visited,
                f"{r.elapsed_ms:.3f}",
                por, pen, ovh, ebf, oc, estado,
            ))

    # ── animated maze (Tab 1) ─────────────────────────────────────────────────
    def _setup_anim_figure(self):
        self._anim_fig.clear()
        self._anim_arrs.clear()
        self._anim_imgs.clear()

        maze = self.maze
        n = len(self.results)
        ncols = min(n, 2)
        nrows = math.ceil(n / ncols)
        self._anim_fig.patch.set_facecolor(BG_DARK)

        for idx, res in enumerate(self.results):
            ax = self._anim_fig.add_subplot(nrows, ncols, idx + 1)
            ax.set_facecolor(BG_DARK)

            arr = _make_arr(maze)
            self._anim_arrs.append(arr)

            img = ax.imshow(arr, interpolation='nearest', aspect='auto')
            self._anim_imgs.append(img)

            ax.set_xticks([])
            ax.set_yticks([])
            steps_lbl = str(res.steps) if res.found else 'N/A'
            ax.set_title(
                f"{res.algorithm}  |  Pasos: {steps_lbl}  |  "
                f"Nodos: {res.nodes_visited}  |  {res.elapsed_ms:.2f} ms",
                color=FG_WHITE, fontsize=8, pad=3)

        self._anim_fig.tight_layout(pad=0.4)
        self._anim_canvas.draw()

        # precompute batched frame indices
        max_exp = max((len(r.exploration_order) for r in self.results), default=0)
        max_pth = max((len(r.path) for r in self.results if r.path), default=0)
        self._exp_batch = max(1, max_exp // self._EXP_FRAMES)
        self._pth_batch = max(1, max_pth // self._PATH_FRAMES)
        self._max_exp   = max_exp
        self._max_pth   = max_pth

    def _run_anim_exploration(self, frame: int):
        if self._stop_anim:
            return
        i0 = frame * self._exp_batch
        i1 = i0 + self._exp_batch
        changed = False

        for res, arr in zip(self.results, self._anim_arrs):
            for node in res.exploration_order[i0:i1]:
                r, c = node
                if self.maze.grid[r][c] not in ('E', 'S'):
                    arr[r, c] = _C_VISITED
                    changed = True

        if changed:
            for img, arr in zip(self._anim_imgs, self._anim_arrs):
                img.set_data(arr)
            self._anim_canvas.draw_idle()

        if i0 < self._max_exp:
            self.root.after(self._DELAY_MS,
                            lambda: self._run_anim_exploration(frame + 1))
        else:
            self.root.after(220, lambda: self._run_anim_path(0))

    def _run_anim_path(self, frame: int):
        if self._stop_anim:
            return
        i0 = frame * self._pth_batch
        i1 = i0 + self._pth_batch
        changed = False

        for res, arr in zip(self.results, self._anim_arrs):
            if not res.path:
                continue
            for node in res.path[i0:i1]:
                r, c = node
                if self.maze.grid[r][c] not in ('E', 'S'):
                    arr[r, c] = _C_PATH
                    changed = True

        if changed:
            for img, arr in zip(self._anim_imgs, self._anim_arrs):
                img.set_data(arr)
            self._anim_canvas.draw_idle()

        if i0 < self._max_pth:
            self.root.after(self._PATH_DELAY,
                            lambda: self._run_anim_path(frame + 1))
        else:
            self._status_var.set(
                f"Completado — {len(self.results)} algoritmo(s) en {self.maze.name}")

    # ── graph + search-tree tab ───────────────────────────────────────────────
    def _refresh_graph_tab(self):
        if not self.results or not self.maze:
            return

        maze = self.maze
        graph = maze.graph
        nodes = list(graph.keys())

        sel = self._tree_algo_var.get()
        tree_res = next((r for r in self.results if r.algorithm == sel),
                        self.results[0])
        path_set: set = set()
        for r in self.results:
            if r.found:
                path_set = set(r.path)
                break

        # ── left: full adjacency graph ────────────────────────────────────────
        ax_g = self._ax_graph
        ax_g.clear()
        _style_ax(ax_g)

        for (r0, c0), nbs in graph.items():
            for (nr, nc) in nbs:
                if (nr, nc) > (r0, c0):
                    ax_g.plot([c0, nc], [-r0, -nr],
                              color='#4A5568', lw=0.5, alpha=0.6, zorder=1)

        xs = [c for _, c in nodes]
        ys = [-r for r, _ in nodes]
        nc_c, nc_s = [], []
        for pos in nodes:
            if pos == maze.start:   nc_c.append('#27AE60'); nc_s.append(90)
            elif pos == maze.end:   nc_c.append('#E74C3C'); nc_s.append(90)
            elif pos in path_set:   nc_c.append(PATH_CLR); nc_s.append(22)
            else:                   nc_c.append('#5D6D7E'); nc_s.append(7)
        ax_g.scatter(xs, ys, c=nc_c, s=nc_s, zorder=3, linewidths=0)

        ax_g.legend(handles=[
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#27AE60',
                   markersize=8, label='Inicio (E)'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#E74C3C',
                   markersize=8, label='Salida (S)'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor=PATH_CLR,
                   markersize=6, label='Camino'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#5D6D7E',
                   markersize=5, label='Nodo libre'),
        ], facecolor=BG_MID, labelcolor=FG_WHITE, fontsize=7, loc='upper right')

        ax_g.set_title(
            f"Grafo del laberinto — {maze.name}     "
            f"{maze.node_count} nodos   {maze.edge_count} aristas",
            color=FG_WHITE, fontsize=10, pad=8)
        ax_g.set_xticks([]); ax_g.set_yticks([])
        ax_g.set_aspect('auto')

        # ── right: search tree ────────────────────────────────────────────────
        ax_t = self._ax_tree
        ax_t.clear()
        _style_ax(ax_t)

        cf = tree_res.came_from
        exp = tree_res.exploration_order
        order_map = {node: i for i, node in enumerate(exp)}
        n_exp = max(len(exp), 1)
        path_s = set(tree_res.path) if tree_res.path else set()

        # tree edges (parent → child connections from came_from)
        for node, parent in cf.items():
            if parent is not None:
                r0, c0 = node
                rp, cp = parent
                ax_t.plot([cp, c0], [-rp, -r0],
                          color='#5D6D7E', lw=0.6, alpha=0.65, zorder=1)

        # highlight path edges
        if tree_res.path:
            for i in range(len(tree_res.path) - 1):
                r0, c0 = tree_res.path[i]
                r1, c1 = tree_res.path[i + 1]
                ax_t.plot([c0, c1], [-r0, -r1],
                          color=PATH_CLR, lw=1.8, alpha=0.9, zorder=2)

        # nodes coloured by discovery order
        t_nodes = list(cf.keys())
        t_xs = [c for _, c in t_nodes]
        t_ys = [-r for r, _ in t_nodes]
        norm_order = [order_map.get(n, 0) / n_exp for n in t_nodes]

        sc = ax_t.scatter(t_xs, t_ys, c=norm_order, cmap='plasma',
                          s=12, zorder=3, linewidths=0, vmin=0, vmax=1)

        # overlay special nodes
        for pos in t_nodes:
            r, c = pos
            if pos == maze.start:
                ax_t.scatter([c], [-r], c='#27AE60', s=90, zorder=6, linewidths=0)
            elif pos == maze.end:
                ax_t.scatter([c], [-r], c='#E74C3C', s=90, zorder=6, linewidths=0)
            elif pos in path_s and pos not in (maze.start, maze.end):
                ax_t.scatter([c], [-r], c=PATH_CLR, s=20, zorder=5, linewidths=0)

        cb = self._graph_fig.colorbar(sc, ax=ax_t, fraction=0.015, pad=0.01)
        cb.set_label('Orden de descubrimiento  (oscuro=primero · claro=último)',
                     color=FG_DIM, fontsize=7)
        cb.ax.tick_params(labelcolor=FG_DIM, labelsize=6)

        ax_t.legend(handles=[
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#27AE60',
                   markersize=8, label='Inicio'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor='#E74C3C',
                   markersize=8, label='Salida'),
            Line2D([0],[0], marker='o', color='w', markerfacecolor=PATH_CLR,
                   markersize=6, label='Camino optimo'),
            Line2D([0],[0], color='#5D6D7E', lw=1, label='Arista del arbol'),
            Line2D([0],[0], color=PATH_CLR,  lw=2, label='Arista del camino'),
        ], facecolor=BG_MID, labelcolor=FG_WHITE, fontsize=7, loc='upper right')

        ax_t.set_title(
            f"Árbol de búsqueda — {tree_res.algorithm}     "
            f"{len(cf)} nodos descubiertos   color = orden de exploración",
            color=FG_WHITE, fontsize=10, pad=8)
        ax_t.set_xticks([]); ax_t.set_yticks([])
        ax_t.set_aspect('auto')

        self._graph_fig.tight_layout(rect=[0, 0, 0.985, 1])
        self._graph_canvas.draw()

    # ── complexity tab ────────────────────────────────────────────────────────
    def _update_complexity_tab(self):
        self._cplx_fig.clear()
        self._cplx_fig.patch.set_facecolor(BG_DARK)

        results = self.results
        names  = [r.algorithm for r in results]
        colors = [r.color for r in results]
        nodes  = [r.nodes_visited for r in results]
        steps  = [r.steps if r.found else 0 for r in results]
        times  = [r.elapsed_ms for r in results]

        axes = [self._cplx_fig.add_subplot(2, 2, i) for i in range(1, 5)]
        ax1, ax2, ax3, ax4 = axes
        for ax in axes:
            _style_ax(ax)

        def bar_chart(ax, vals, title, ylabel):
            bars = ax.bar(names, vals, color=colors, edgecolor='white', lw=0.5)
            ax.set_title(title, color=FG_WHITE, fontsize=10)
            ax.set_ylabel(ylabel, color=FG_DIM, fontsize=8)
            ax.tick_params(axis='x', colors=FG_WHITE, labelsize=8)
            ax.tick_params(axis='y', colors=FG_DIM, labelsize=7)
            top = max(vals) if max(vals) > 0 else 1
            for b, v in zip(bars, vals):
                lbl = f"{v:.2f}" if isinstance(v, float) else str(v)
                ax.text(b.get_x() + b.get_width() / 2,
                        b.get_height() + top * 0.02, lbl,
                        ha='center', va='bottom', color=FG_WHITE, fontsize=7)

        bar_chart(ax1, nodes, "Nodos explorados",            "Nodos")
        bar_chart(ax2, steps, "Longitud del camino (pasos)", "Pasos")
        bar_chart(ax3, times, "Tiempo de ejecucion (ms)",    "ms")

        N = max(self.maze.node_count, 2)
        x = np.linspace(1, N, 300)
        ax4.plot(x, x,            color='#4472C4', lw=2,      label='O(N) — BFS/DFS')
        ax4.plot(x, x*np.log2(x), color='#70AD47', lw=2, ls='--', label='O(N logN) — A*')
        ax4.plot(x, np.sqrt(x),   color='#9B59B6', lw=2, ls=':',  label='O(sqrt N) — Grover')
        ax4.axvline(N, color='white', lw=0.8, ls='--', alpha=0.4, label=f'N={N}')
        ax4.set_title("Complejidad teorica", color=FG_WHITE, fontsize=10)
        ax4.set_xlabel("N (nodos)", color=FG_DIM, fontsize=8)
        ax4.set_ylabel("Operaciones", color=FG_DIM, fontsize=8)
        ax4.set_xlim(1, N)
        ax4.tick_params(colors=FG_DIM, labelsize=7)
        ax4.legend(fontsize=7, facecolor=BG_MID, labelcolor=FG_WHITE, loc='upper left')

        self._cplx_fig.suptitle(
            f"Analisis de Complejidad — {self.maze.name}",
            color=FG_WHITE, fontsize=12, fontweight='bold')
        self._cplx_fig.tight_layout()
        self._cplx_canvas.draw()
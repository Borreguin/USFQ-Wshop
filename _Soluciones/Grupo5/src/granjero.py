"""
Acertijo del Granjero | Diseño Orientado a Objetos
Clases: State, FarmerPuzzle, PuzzleVisualizer
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple


# ── Entidad de dominio ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class State:
    """
    Estado del puzzle: posicion de cada actor (0=izquierda, 1=derecha).
    Inmutable y hashable para poder usarse en conjuntos/diccionarios.
    """
    farmer:  int
    wolf:    int
    goat:    int
    cabbage: int

    def is_valid(self) -> bool:
        if self.wolf == self.goat and self.farmer != self.wolf:
            return False
        if self.goat == self.cabbage and self.farmer != self.goat:
            return False
        return True

    def successors(self) -> List[Tuple["State", str]]:
        """Genera todos los estados validos alcanzables desde este."""
        results = []
        new_f = 1 - self.farmer
        # 0 = solo, 1 = lobo, 2 = cabra, 3 = col
        items = [("solo", None), ("Lobo", "wolf"),
                 ("Cabra", "goat"), ("Col", "cabbage")]
        for label, attr in items:
            if attr is not None and getattr(self, attr) != self.farmer:
                continue  # el item no esta en el mismo lado que el granjero
            kwargs = {
                "farmer":  new_f,
                "wolf":    1 - self.wolf    if attr == "wolf"    else self.wolf,
                "goat":    1 - self.goat    if attr == "goat"    else self.goat,
                "cabbage": 1 - self.cabbage if attr == "cabbage" else self.cabbage,
            }
            ns = State(**kwargs)
            if ns.is_valid():
                direction = "->" if new_f == 1 else "<-"
                results.append((ns, f"Granjero {direction} ({label})"))
        return results

    def label(self) -> str:
        actors = ["Granjero", "Lobo", "Cabra", "Col"]
        vals   = [self.farmer, self.wolf, self.goat, self.cabbage]
        left  = [a[0] for a, v in zip(actors, vals) if v == 0] or ["vacio"]
        right = [a[0] for a, v in zip(actors, vals) if v == 1] or ["vacio"]
        return f"I:{''.join(left)}\nD:{''.join(right)}"

    def __repr__(self) -> str:
        side = lambda v: "Der" if v else "Izq"
        return (f"State(F={side(self.farmer)}, W={side(self.wolf)}, "
                f"G={side(self.goat)}, C={side(self.cabbage)})")


INITIAL_STATE = State(0, 0, 0, 0)
GOAL_STATE    = State(1, 1, 1, 1)


# ── Solucionador (BFS) ────────────────────────────────────────────────────────

class FarmerPuzzle:
    """Resuelve el puzzle usando BFS y construye el grafo completo de estados."""

    def __init__(self):
        self._solution: Optional[List[Tuple[State, str]]] = None
        self._graph:    Optional[nx.DiGraph]              = None

    def solve(self) -> List[Tuple[State, str]]:
        """Retorna lista de (estado, accion) desde INITIAL hasta GOAL."""
        queue   = deque([(INITIAL_STATE, [(INITIAL_STATE, "Inicio")])])
        visited = {INITIAL_STATE}
        while queue:
            state, path = queue.popleft()
            if state == GOAL_STATE:
                self._solution = path
                return path
            for ns, action in state.successors():
                if ns not in visited:
                    visited.add(ns)
                    queue.append((ns, path + [(ns, action)]))
        self._solution = []
        return []

    @property
    def solution(self) -> List[Tuple[State, str]]:
        if self._solution is None:
            self.solve()
        return self._solution

    def build_graph(self) -> nx.DiGraph:
        """Construye el grafo completo de todos los estados validos."""
        if self._graph is not None:
            return self._graph
        G = nx.DiGraph()
        visited = set()
        queue = deque([INITIAL_STATE])
        visited.add(INITIAL_STATE)
        while queue:
            state = queue.popleft()
            G.add_node(state)
            for ns, action in state.successors():
                item = action.split("(")[1].rstrip(")")
                G.add_edge(state, ns, action=item)
                if ns not in visited:
                    visited.add(ns)
                    queue.append(ns)
        self._graph = G
        return G

    def print_solution(self):
        sol = self.solution
        print(f"\nSolucion en {len(sol)-1} pasos:\n")
        for i, (state, action) in enumerate(sol):
            print(f"  Paso {i:2d} | {action:30s} | {state}")


# ── Visualizador ──────────────────────────────────────────────────────────────

class PuzzleVisualizer:
    """Genera las figuras del acertijo del granjero."""

    ICONS = {"Granjero": "G", "Lobo": "W", "Cabra": "A", "Col": "C"}
    NAMES = ["Granjero", "Lobo", "Cabra", "Col"]

    def __init__(self, puzzle: FarmerPuzzle):
        self._puzzle = puzzle

    def _draw_step(self, ax, state: State, title: str):
        ax.set_xlim(0, 10); ax.set_ylim(0, 6)
        ax.set_facecolor("#e8f4fc"); ax.axis("off")
        ax.set_title(title, fontsize=8, fontweight="bold")

        # Rio
        river = mpatches.FancyBboxPatch(
            (4.5, 0), 1, 6, boxstyle="round,pad=0.1",
            facecolor="#7ec8e3", edgecolor="none")
        ax.add_patch(river)
        ax.text(5, 3, "RIO", ha="center", va="center",
                fontsize=8, color="white", fontweight="bold")

        pos_left  = [(1, 4.5), (1, 3), (1, 1.5), (2.5, 3)]
        pos_right = [(8, 4.5), (8, 3), (8, 1.5), (6.5, 3)]
        vals  = [state.farmer, state.wolf, state.goat, state.cabbage]
        names = ["Granjero", "Lobo", "Cabra", "Col"]
        colors = ["#4caf50", "#f44336", "#ff9800", "#795548"]

        for idx, (name, side, color) in enumerate(zip(names, vals, colors)):
            pos = pos_left[idx] if side == 0 else pos_right[idx]
            circle = mpatches.Circle(pos, 0.45, color=color,
                                     zorder=3, linewidth=0)
            ax.add_patch(circle)
            ax.text(pos[0], pos[1], name[0], ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold", zorder=4)
            ax.text(pos[0], pos[1]-0.65, name, ha="center", va="center",
                    fontsize=6, zorder=4)

        # Barca
        bx = 3.2 if state.farmer == 0 else 6.8
        boat = mpatches.FancyBboxPatch(
            (bx-0.55, 2.55), 1.1, 0.45,
            boxstyle="round,pad=0.05",
            facecolor="#f0c060", edgecolor="brown", zorder=5)
        ax.add_patch(boat)
        ax.text(bx, 2.78, "~", ha="center", va="center",
                fontsize=12, color="brown", zorder=6)

    def plot_steps(self) -> plt.Figure:
        sol = self._puzzle.solution
        n   = len(sol)
        cols = min(n, 4)
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols,
                                  figsize=(cols * 3.2, rows * 3))
        fig.suptitle("Acertijo del Granjero – Secuencia BFS",
                     fontsize=13, fontweight="bold")
        axes_flat = axes.flatten() if hasattr(axes, "flatten") else [axes]
        for i, (state, action) in enumerate(sol):
            self._draw_step(axes_flat[i],
                            state,
                            f"Paso {i}\n{action}" if i < n else f"Paso {i}")
        for i in range(n, len(axes_flat)):
            axes_flat[i].axis("off")
        plt.tight_layout()
        return fig

    def plot_graph(self) -> plt.Figure:
        sol   = self._puzzle.solution
        G     = self._puzzle.build_graph()
        sol_states = [s for s, _ in sol]
        path_edges = list(zip(sol_states[:-1], sol_states[1:]))

        fig, ax = plt.subplots(figsize=(14, 9))
        fig.suptitle("Grafo de Estados – Acertijo del Granjero",
                     fontsize=13, fontweight="bold")
        pos = nx.spring_layout(G, seed=42, k=2.5)
        labels = {s: s.label() for s in G.nodes()}

        node_colors = []
        for node in G.nodes():
            if node == INITIAL_STATE:
                node_colors.append("#4caf50")
            elif node == GOAL_STATE:
                node_colors.append("#f44336")
            elif node in sol_states:
                node_colors.append("#2196f3")
            else:
                node_colors.append("#b0bec5")

        edge_colors = ["#ff5722" if e in path_edges else "#cfd8dc"
                       for e in G.edges()]
        edge_widths = [3.0 if e in path_edges else 0.8
                       for e in G.edges()]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                               node_size=1800, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=labels,
                                font_size=6, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                               width=edge_widths, arrows=True,
                               arrowsize=15, ax=ax,
                               connectionstyle="arc3,rad=0.15")
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=nx.get_edge_attributes(G, "action"),
            font_size=6, ax=ax)

        legend = [
            mpatches.Patch(color="#4caf50", label="Estado inicial"),
            mpatches.Patch(color="#f44336", label="Estado objetivo"),
            mpatches.Patch(color="#2196f3", label="En la solucion"),
            mpatches.Patch(color="#b0bec5", label="Explorado"),
        ]
        ax.legend(handles=legend, loc="upper left", fontsize=9)
        ax.axis("off")
        plt.tight_layout()
        return fig

    def save_all(self, save_dir: str):
        import os
        os.makedirs(save_dir, exist_ok=True)
        self.plot_steps().savefig(
            os.path.join(save_dir, "granjero_01_pasos.png"),
            dpi=150, bbox_inches="tight")
        self.plot_graph().savefig(
            os.path.join(save_dir, "granjero_02_grafo.png"),
            dpi=150, bbox_inches="tight")
        plt.close("all")
        print(f"  Granjero: 2 imagenes -> {save_dir}/")

    def show(self):
        self.plot_steps()
        self.plot_graph()
        plt.show()

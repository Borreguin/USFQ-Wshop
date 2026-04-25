"""
Torre de Hanoi | Diseño Orientado a Objetos
Clases: Disk, Tower, HanoiState, HanoiSolver, HanoiVisualizer
"""

from __future__ import annotations
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# ── Entidades del dominio ─────────────────────────────────────────────────────

@dataclass
class Disk:
    """Disco identificado por su tamano (1=mas pequeno)."""
    size: int

    @property
    def color(self) -> str:
        palette = ["#e53935","#fb8c00","#fdd835","#43a047",
                   "#00acc1","#3949ab","#8e24aa","#6d4c41","#546e7a","#78909c"]
        return palette[(self.size - 1) % len(palette)]

    def __repr__(self) -> str:
        return f"Disk({self.size})"


class Tower:
    """Pila de discos con nombre. Solo permite apilar discos mas pequenos encima."""

    def __init__(self, name: str, disks: Optional[List[Disk]] = None):
        self.name  = name
        self._disks: List[Disk] = disks[:] if disks else []

    def push(self, disk: Disk):
        if self._disks and self._disks[-1].size < disk.size:
            raise ValueError(
                f"No se puede colocar Disk({disk.size}) sobre Disk({self._disks[-1].size})")
        self._disks.append(disk)

    def pop(self) -> Disk:
        if not self._disks:
            raise IndexError(f"Torre {self.name} esta vacia")
        return self._disks.pop()

    @property
    def top(self) -> Optional[Disk]:
        return self._disks[-1] if self._disks else None

    @property
    def disks(self) -> List[Disk]:
        return list(self._disks)

    def __len__(self) -> int:
        return len(self._disks)

    def __repr__(self) -> str:
        return f"Tower({self.name}, {self._disks})"

    def copy(self) -> Tower:
        return Tower(self.name, self._disks[:])


class HanoiState:
    """Instantanea de las tres torres en un momento dado."""

    def __init__(self, towers: List[Tower]):
        self.towers = {t.name: t.copy() for t in towers}

    def snapshot(self) -> dict:
        return {name: t.disks[:] for name, t in self.towers.items()}

    def __repr__(self) -> str:
        return str({k: [d.size for d in v.disks] for k, v in self.towers.items()})


# ── Solucionador ──────────────────────────────────────────────────────────────

class HanoiSolver:
    """
    Resuelve la Torre de Hanoi de forma recursiva y registra cada movimiento
    junto con el estado completo de las torres.
    """

    def __init__(self, n: int):
        self.n = n
        self._moves:  List[Tuple[str, str]] = []        # (origen, destino)
        self._states: List[HanoiState]      = []        # snapshot tras cada movimiento

    def solve(self) -> "HanoiSolver":
        towers = {
            "A": Tower("A", [Disk(i) for i in range(self.n, 0, -1)]),
            "B": Tower("B"),
            "C": Tower("C"),
        }
        self._moves  = []
        self._states = [HanoiState(list(towers.values()))]
        self._recurse(self.n, towers, "A", "C", "B")
        return self

    def _recurse(self, n: int, towers: dict, src: str, dst: str, aux: str):
        if n == 1:
            disk = towers[src].pop()
            towers[dst].push(disk)
            self._moves.append((src, dst))
            self._states.append(HanoiState(list(towers.values())))
        else:
            self._recurse(n-1, towers, src, aux, dst)
            self._recurse(1,   towers, src, dst, aux)
            self._recurse(n-1, towers, aux, dst, src)

    @property
    def moves(self) -> List[Tuple[str, str]]:
        return self._moves

    @property
    def states(self) -> List[HanoiState]:
        return self._states

    @property
    def total_moves(self) -> int:
        return len(self._moves)

    def print_moves(self):
        print(f"\nTorre de Hanoi ({self.n} discos) -> {self.total_moves} movimientos\n")
        for i, (s, d) in enumerate(self._moves, 1):
            print(f"  Movimiento {i:3d}: Torre {s} -> Torre {d}")


# ── Visualizador ──────────────────────────────────────────────────────────────

class HanoiVisualizer:
    """Genera animacion y graficos de analisis del Hanoi."""

    TOWER_X = {"A": 1.5, "B": 4.5, "C": 7.5}
    BASE_Y   = 0.3
    DISK_H   = 0.55

    def __init__(self, solver: HanoiSolver):
        self._solver = solver

    def _draw_state(self, ax, state: HanoiState,
                    move_info: Optional[Tuple[str, str]],
                    step: int, total: int):
        ax.clear()
        ax.set_xlim(0, 9)
        ax.set_ylim(0, self._solver.n * self.DISK_H + 2)
        ax.set_facecolor("#1a1a2e")
        ax.axis("off")
        src, dst = move_info if move_info else (None, None)
        title = f"Movimiento {step}/{total}"
        if src and dst:
            title += f"  |  Torre {src} -> Torre {dst}"
        ax.set_title(title, color="white", fontsize=11, fontweight="bold")

        base = mpatches.FancyBboxPatch(
            (0.2, self.BASE_Y - 0.2), 8.6, 0.2,
            boxstyle="round,pad=0.05",
            facecolor="#e0e0e0", edgecolor="none")
        ax.add_patch(base)

        for tname, tx in self.TOWER_X.items():
            pole = mpatches.FancyBboxPatch(
                (tx - 0.08, self.BASE_Y), 0.16,
                self._solver.n * self.DISK_H + 0.5,
                boxstyle="round,pad=0.04",
                facecolor="#9e9e9e", edgecolor="none")
            ax.add_patch(pole)
            color = "#ff5722" if tname in (src, dst) else "white"
            ax.text(tx, self.BASE_Y - 0.5, f"Torre {tname}",
                    ha="center", va="top", fontsize=10,
                    color=color, fontweight="bold")

            disks = state.towers[tname].disks
            for level, disk in enumerate(disks):
                width = 0.3 + disk.size * 0.6
                dy = self.BASE_Y + level * self.DISK_H
                rect = mpatches.FancyBboxPatch(
                    (tx - width/2, dy), width, self.DISK_H - 0.08,
                    boxstyle="round,pad=0.05",
                    facecolor=disk.color, edgecolor="black", linewidth=0.8)
                ax.add_patch(rect)
                ax.text(tx, dy + self.DISK_H/2 - 0.04, str(disk.size),
                        ha="center", va="center",
                        fontsize=9, color="white", fontweight="bold")

    def animate(self) -> plt.Figure:
        states = self._solver.states
        moves  = self._solver.moves
        total  = len(moves)
        fig, ax = plt.subplots(
            figsize=(10, max(5, self._solver.n * 0.8 + 2)))
        fig.patch.set_facecolor("#1a1a2e")

        def update(frame):
            state = states[frame]
            move  = moves[frame-1] if frame > 0 else None
            self._draw_state(ax, state, move, frame, total)

        interval = max(200, 1200 - self._solver.n * 80)
        ani = animation.FuncAnimation(
            fig, update, frames=len(states),
            interval=interval, repeat=True)
        return fig, ani

    def plot_analysis(self) -> Tuple[plt.Figure, plt.Figure]:
        moves = self._solver.moves
        n     = self._solver.n
        total = self._solver.total_moves

        from_c = {"A": 0, "B": 0, "C": 0}
        to_c   = {"A": 0, "B": 0, "C": 0}
        for s, d in moves:
            from_c[s] += 1
            to_c[d]   += 1

        towers = ["A", "B", "C"]
        bar_colors = ["#2196f3", "#ff9800", "#4caf50"]

        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig1.suptitle(f"Torre de Hanoi ({n} discos) – Movimientos",
                      fontweight="bold")
        ax1.bar(towers, [from_c[t] for t in towers],
                color=bar_colors, edgecolor="black")
        ax1.set_title("Movimientos como origen")
        ax1.set_ylabel("Cantidad")
        for i, v in enumerate([from_c[t] for t in towers]):
            ax1.text(i, v+0.1, str(v), ha="center", fontweight="bold")
        ax2.bar(towers, [to_c[t] for t in towers],
                color=bar_colors, edgecolor="black")
        ax2.set_title("Movimientos como destino")
        ax2.set_ylabel("Cantidad")
        for i, v in enumerate([to_c[t] for t in towers]):
            ax2.text(i, v+0.1, str(v), ha="center", fontweight="bold")
        plt.tight_layout()

        ns    = range(1, 13)
        costs = [2**k - 1 for k in ns]
        fig2, ax3 = plt.subplots(figsize=(7, 4))
        ax3.plot(list(ns), costs, marker="o",
                 color="darkorange", linewidth=2)
        ax3.axvline(n, color="red", linestyle="--",
                    label=f"n={n} ({total} mov.)")
        ax3.set_title("Complejidad O(2^n - 1)", fontweight="bold")
        ax3.set_xlabel("Numero de discos (n)")
        ax3.set_ylabel("Movimientos minimos")
        ax3.legend(); ax3.grid(True, alpha=0.3)
        ax3.fill_between(list(ns), costs, alpha=0.1, color="darkorange")
        plt.tight_layout()

        return fig1, fig2

    def plot_final_state(self) -> plt.Figure:
        """Imagen estatica del estado final (todos los discos en Torre C)."""
        fig, ax = plt.subplots(
            figsize=(10, max(5, self._solver.n * 0.8 + 2)))
        fig.patch.set_facecolor("#1a1a2e")
        final = self._solver.states[-1]
        self._draw_state(ax, final, None,
                         self._solver.total_moves,
                         self._solver.total_moves)
        return fig

    def save_all(self, save_dir: str):
        import os
        os.makedirs(save_dir, exist_ok=True)
        self.plot_final_state().savefig(
            os.path.join(save_dir, "hanoi_01_estado_final.png"),
            dpi=150, bbox_inches="tight")
        fig1, fig2 = self.plot_analysis()
        fig1.savefig(os.path.join(save_dir, "hanoi_02_movimientos.png"),
                     dpi=150, bbox_inches="tight")
        fig2.savefig(os.path.join(save_dir, "hanoi_03_complejidad.png"),
                     dpi=150, bbox_inches="tight")
        plt.close("all")
        print(f"  Hanoi: 3 imagenes -> {save_dir}/")

    def show(self):
        fig, ani = self.animate()
        self.plot_analysis()
        plt.show()

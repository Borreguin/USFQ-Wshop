"""
Torre de Hanoi – solución recursiva
Visualización: animación de cada movimiento con matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation

# ── Lógica recursiva ─────────────────────────────────────────────────────────

def hanoi(n: int, origen: str, destino: str, auxiliar: str, moves: list):
    if n == 1:
        moves.append((origen, destino))
        return
    hanoi(n - 1, origen, auxiliar, destino, moves)
    moves.append((origen, destino))
    hanoi(n - 1, auxiliar, destino, origen, moves)


# ── Estado de las torres ─────────────────────────────────────────────────────

def build_states(n: int):
    """Genera todos los estados intermedios a partir de la lista de movimientos."""
    towers = {"A": list(range(n, 0, -1)), "B": [], "C": []}
    states = [({k: list(v) for k, v in towers.items()}, None, None)]

    moves = []
    hanoi(n, "A", "C", "B", moves)

    for src, dst in moves:
        disk = towers[src].pop()
        towers[dst].append(disk)
        states.append(({k: list(v) for k, v in towers.items()}, src, dst))

    return states, moves


# ── Visualización ─────────────────────────────────────────────────────────────

COLORS = plt.cm.get_cmap("tab10")
TOWER_X = {"A": 1.5, "B": 4.5, "C": 7.5}
BASE_Y   = 0.3
DISK_H   = 0.55
MAX_DISKS = 10

def draw_state(ax, state_dict, move_info, step, total, n):
    ax.clear()
    ax.set_xlim(0, 9)
    ax.set_ylim(0, n * DISK_H + 2)
    ax.set_facecolor("#1a1a2e")
    ax.axis("off")

    src, dst = move_info if move_info else (None, None)
    title = f"Movimiento {step}/{total}"
    if src and dst:
        title += f"  |  Torre {src} → Torre {dst}"
    ax.set_title(title, color="white", fontsize=11, fontweight="bold")

    # Base
    base = mpatches.FancyBboxPatch((0.2, BASE_Y - 0.2), 8.6, 0.2,
                                    boxstyle="round,pad=0.05",
                                    facecolor="#e0e0e0", edgecolor="none")
    ax.add_patch(base)

    for tower_name, tx in TOWER_X.items():
        # Palo
        pole = mpatches.FancyBboxPatch((tx - 0.08, BASE_Y), 0.16, n * DISK_H + 0.5,
                                        boxstyle="round,pad=0.04",
                                        facecolor="#9e9e9e", edgecolor="none")
        ax.add_patch(pole)

        # Etiqueta
        color = "#ff5722" if tower_name in (src, dst) else "white"
        ax.text(tx, BASE_Y - 0.5, f"Torre {tower_name}", ha="center", va="top",
                fontsize=10, color=color, fontweight="bold")

        # Discos
        disks = state_dict[tower_name]
        for level, disk in enumerate(disks):
            width = 0.3 + disk * 0.6
            dy = BASE_Y + level * DISK_H
            color = COLORS(disk / (n + 1))
            rect = mpatches.FancyBboxPatch((tx - width / 2, dy), width, DISK_H - 0.08,
                                            boxstyle="round,pad=0.05",
                                            facecolor=color, edgecolor="black", linewidth=0.8)
            ax.add_patch(rect)
            ax.text(tx, dy + DISK_H / 2 - 0.04, str(disk),
                    ha="center", va="center", fontsize=9, color="white", fontweight="bold")


def main():
    n = int(input("Número de discos (recomendado 3-5): ") or "4")
    n = max(1, min(n, MAX_DISKS))

    moves = []
    hanoi(n, "A", "C", "B", moves)
    total_moves = 2**n - 1
    print(f"\nTorre de Hanoi con {n} discos → {total_moves} movimientos\n")
    for i, (s, d) in enumerate(moves, 1):
        print(f"  Movimiento {i:3d}: Torre {s} → Torre {d}")

    states, move_list = build_states(n)
    total = len(move_list)

    # ── Animación ────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, max(5, n * 0.8 + 2)))
    fig.patch.set_facecolor("#1a1a2e")

    def animate(frame):
        state_dict, src, dst = states[frame]
        draw_state(ax, state_dict, (src, dst) if src else None,
                   frame, total, n)

    interval = max(200, 1200 - n * 80)   # más discos → más rápido
    ani = animation.FuncAnimation(
        fig, animate, frames=len(states),
        interval=interval, repeat=True
    )

    # ── Gráfico de conteo de movimientos por torre ───────────────────────────
    from_counts = {"A": 0, "B": 0, "C": 0}
    to_counts   = {"A": 0, "B": 0, "C": 0}
    for s, d in move_list:
        from_counts[s] += 1
        to_counts[d]   += 1

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig2.suptitle(f"Torre de Hanoi ({n} discos) – Análisis de Movimientos", fontweight="bold")

    towers = ["A", "B", "C"]
    bar_colors = ["#2196f3", "#ff9800", "#4caf50"]
    ax1.bar(towers, [from_counts[t] for t in towers], color=bar_colors, edgecolor="black")
    ax1.set_title("Movimientos como origen")
    ax1.set_ylabel("Cantidad")
    for i, v in enumerate([from_counts[t] for t in towers]):
        ax1.text(i, v + 0.1, str(v), ha="center", fontweight="bold")

    ax2.bar(towers, [to_counts[t] for t in towers], color=bar_colors, edgecolor="black")
    ax2.set_title("Movimientos como destino")
    ax2.set_ylabel("Cantidad")
    for i, v in enumerate([to_counts[t] for t in towers]):
        ax2.text(i, v + 0.1, str(v), ha="center", fontweight="bold")

    # Curva de complejidad
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ns = range(1, 13)
    costs = [2**k - 1 for k in ns]
    ax3.plot(list(ns), costs, marker="o", color="darkorange", linewidth=2)
    ax3.axvline(n, color="red", linestyle="--", label=f"n={n} ({total_moves} mov.)")
    ax3.set_title("Complejidad O(2ⁿ − 1) – Torre de Hanoi", fontweight="bold")
    ax3.set_xlabel("Número de discos (n)")
    ax3.set_ylabel("Movimientos mínimos")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.fill_between(list(ns), costs, alpha=0.1, color="darkorange")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

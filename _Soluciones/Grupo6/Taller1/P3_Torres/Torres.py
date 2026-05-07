import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

NUM_DISKS = 4
towers = {1: list(range(NUM_DISKS, 0, -1)), 2: [], 3: []}
moves = []


def hanoi(n, source, target, auxiliary):
    if n == 1:
        moves.append((source, target))
        return
    hanoi(n - 1, source, auxiliary, target)
    moves.append((source, target))
    hanoi(n - 1, auxiliary, target, source)


def draw_towers(state, move_num, total_moves, from_peg=None, to_peg=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, NUM_DISKS + 3)
    ax.set_facecolor("#f5f0e8")
    fig.patch.set_facecolor("#f5f0e8")
    ax.axis("off")

    colors = ["#e74c3c", "#f39c12", "#2ecc71", "#3498db", "#9b59b6", "#1abc9c"]
    tower_x = {1: 2, 2: 6, 3: 10}
    labels = {1: "Origen", 2: "Auxiliar", 3: "Destino"}

    for peg, x in tower_x.items():
        # Base
        ax.add_patch(mpatches.FancyBboxPatch(
            (x - 1.5, 0), 3, 0.2, boxstyle="round,pad=0.05",
            facecolor="#795548", edgecolor="black"))
        # Pole
        ax.add_patch(mpatches.FancyBboxPatch(
            (x - 0.1, 0.2), 0.2, NUM_DISKS + 1.5, boxstyle="round,pad=0.05",
            facecolor="#795548", edgecolor="black"))
        # Label
        ax.text(x, -0.4, labels[peg], ha="center", fontsize=11, fontweight="bold",
                color="#4a4a4a")
        # Peg number
        ax.text(x, NUM_DISKS + 2.2, f"Torre {peg}", ha="center", fontsize=9,
                color="#888888")

    for peg, disks in state.items():
        x = tower_x[peg]
        for i, disk in enumerate(disks):
            width = disk * 0.55 + 0.4
            color = colors[(disk - 1) % len(colors)]
            highlight = (peg == to_peg and i == len(disks) - 1)
            edgecolor = "gold" if highlight else "black"
            lw = 2.5 if highlight else 1
            ax.add_patch(mpatches.FancyBboxPatch(
                (x - width / 2, 0.3 + i * 0.55), width, 0.45,
                boxstyle="round,pad=0.05",
                facecolor=color, edgecolor=edgecolor, linewidth=lw))
            ax.text(x, 0.3 + i * 0.55 + 0.22, str(disk),
                    ha="center", va="center", fontsize=11,
                    fontweight="bold", color="white")

    title = f"Torres de Hanoi — Movimiento {move_num} / {total_moves}"
    if from_peg and to_peg:
        title += f"\n  Disco movido: Torre {from_peg} → Torre {to_peg}"
    ax.set_title(title, fontsize=13, fontweight="bold", color="#2c3e50", pad=12)

    plt.tight_layout()
    return fig


def simulate():
    state = {1: list(range(NUM_DISKS, 0, -1)), 2: [], 3: []}
    snapshots = [(dict({k: list(v) for k, v in state.items()}), 0, None, None)]

    for step, (src, dst) in enumerate(moves, 1):
        disk = state[src].pop()
        state[dst].append(disk)
        snapshots.append((dict({k: list(v) for k, v in state.items()}), step, src, dst))

    return snapshots


if __name__ == "__main__":
    hanoi(NUM_DISKS, 1, 3, 2)
    total = len(moves)
    print(f"Número de discos: {NUM_DISKS}")
    print(f"Movimientos mínimos necesarios: {total}  (2^n - 1 = {2**NUM_DISKS - 1})\n")

    for i, (src, dst) in enumerate(moves, 1):
        print(f"  Movimiento {i:2d}: Torre {src} → Torre {dst}")

    snapshots = simulate()

    plt.ion()
    for snap in snapshots:
        state, move_num, from_peg, to_peg = snap
        fig = draw_towers(state, move_num, total, from_peg, to_peg)
        plt.pause(1.2)
        plt.close(fig)

    plt.ioff()

    # Final state
    final_state, *_ = snapshots[-1]
    fig = draw_towers(final_state, total, total)
    plt.title("Torres de Hanoi — ¡Completado!", fontsize=14, fontweight="bold", color="#27ae60")
    plt.tight_layout()
    plt.savefig("hanoi_resultado_final.png", dpi=150, bbox_inches="tight")
    print(f"\nSolución completada en {total} movimientos.")
    print("Imagen final guardada en hanoi_resultado_final.png")
    plt.show()
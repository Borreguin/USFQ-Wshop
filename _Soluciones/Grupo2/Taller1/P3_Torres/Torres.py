import matplotlib.pyplot as plt
import matplotlib.patches as patches


def hanoi(n, origen, destino, auxiliar, movimientos):
    if n == 1:
        movimientos.append((origen, destino))
        return
    hanoi(n - 1, origen, auxiliar, destino, movimientos)
    movimientos.append((origen, destino))
    hanoi(n - 1, auxiliar, destino, origen, movimientos)


def visualizar_estado(torres, paso, mov_desc, n_discos, ax):
    ax.clear()
    ax.set_xlim(0, 9)
    ax.set_ylim(0, n_discos + 2)
    ax.set_facecolor("#f5f0e8")
    ax.set_title(f"Paso {paso}: {mov_desc}", fontsize=13, fontweight="bold")
    ax.axis("off")

    posiciones_x = [1.5, 4.5, 7.5]
    nombres = ["Torre A (Origen)", "Torre B (Auxiliar)", "Torre C (Destino)"]
    cmap = plt.get_cmap("RdYlGn")

    for i, (px, nombre) in enumerate(zip(posiciones_x, nombres)):
        ax.add_patch(patches.Rectangle((px - 0.08, 0), 0.16, n_discos + 1,
                                       color="#5c3d1e", zorder=2))
        ax.add_patch(patches.Rectangle((px - 1.3, 0), 2.6, 0.15,
                                       color="#5c3d1e", zorder=2))
        ax.text(px, -0.4, nombre, ha="center", fontsize=8, color="#333333")

        for nivel, disco in enumerate(torres[i]):
            ancho = 0.3 + (disco / n_discos) * 1.8
            color = cmap(1 - disco / (n_discos + 1))
            rect = patches.FancyBboxPatch(
                (px - ancho / 2, nivel + 0.18), ancho, 0.6,
                boxstyle="round,pad=0.05", linewidth=1.2,
                edgecolor="black", facecolor=color, zorder=3
            )
            ax.add_patch(rect)
            ax.text(px, nivel + 0.48, str(disco), ha="center", va="center",
                    fontsize=9, fontweight="bold", color="white", zorder=4)


def resolver_torres(n_discos=3):
    movimientos = []
    hanoi(n_discos, 0, 2, 1, movimientos)

    torres = [list(range(n_discos, 0, -1)), [], []]
    nombres_torres = ["A", "B", "C"]

    _, ax = plt.subplots(figsize=(10, 5))
    plt.subplots_adjust(bottom=0.15)

    estados = [([list(t) for t in torres], 0, f"Estado inicial ({n_discos} discos en Torre A)")]

    for idx, (orig, dest) in enumerate(movimientos):
        disco = torres[orig].pop()
        torres[dest].append(disco)
        desc = f"Mover disco {disco}: Torre {nombres_torres[orig]} → Torre {nombres_torres[dest]}"
        estados.append(([list(t) for t in torres], idx + 1, desc))

    print(f"\nTorre de Hanoi con {n_discos} discos")
    print(f"Total de movimientos: {2**n_discos - 1}\n")
    for i, (_, paso, desc) in enumerate(estados[1:], 1):
        print(f"  Paso {i:2d}: {desc}")

    for torres_estado, paso, desc in estados:
        visualizar_estado(torres_estado, paso, desc, n_discos, ax)
        plt.pause(0.8)

    plt.show()


if __name__ == "__main__":
    n = int(input("Ingresa el número de discos (recomendado 3-6): "))
    resolver_torres(n_discos=n)

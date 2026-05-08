import random
import string
import math
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


def generar_ciudades(n_cities: int, seed: int = 123):
    random.seed(seed)
    cities = {}
    for i in range(n_cities):
        ciudad = f"{random.choice(string.ascii_uppercase)}{random.randint(0,9)}"
        x = round(random.uniform(-100, 100), 1)
        y = round(random.uniform(-100, 100), 1)
        cities[ciudad] = (x, y)
    return cities


def calcular_distancia(ciudad1, ciudad2):
    x1, y1 = ciudad1
    x2, y2 = ciudad2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def generar_distancias(ciudades):
    distancias = {}
    for ciudad1, coord1 in ciudades.items():
        for ciudad2, coord2 in ciudades.items():
            if ciudad1 != ciudad2:
                distancias[(ciudad1, ciudad2)] = calcular_distancia(coord1, coord2)
    return distancias


def generar_ciudades_con_distancias(n_cities: int):
    ciudades = generar_ciudades(n_cities)
    distancias = generar_distancias(ciudades)
    return ciudades, distancias


def calcular_distancia_ruta(ciudades, ruta):
    total = 0
    n = len(ruta)
    for i in range(n):
        c1 = ruta[i]
        c2 = ruta[(i + 1) % n]
        total += calcular_distancia(ciudades[c1], ciudades[c2])
    return total


def plotear_ruta(ciudades, ruta, mostrar_anotaciones=True):
    ruta = list(ruta)
    coordenadas_x = [ciudades[c][0] for c in ruta] + [ciudades[ruta[0]][0]]
    coordenadas_y = [ciudades[c][1] for c in ruta] + [ciudades[ruta[0]][1]]

    plt.figure(figsize=(8, 6))
    plt.scatter(coordenadas_x, coordenadas_y, color='blue', label='Ciudades')
    plt.plot(coordenadas_x, coordenadas_y, linestyle='-', marker='o', color='red', label='Mejor Ruta')

    if mostrar_anotaciones:
        for i, ciudad in enumerate(ruta):
            plt.text(coordenadas_x[i] + 1, coordenadas_y[i] + 1, ciudad, fontsize=8)

    distancia = calcular_distancia_ruta(ciudades, ruta)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title(f'TSP – Mejor Ruta  |  Distancia total: {distancia:.2f}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def animar_construccion(ciudades, pasos, intervalo_ms=300, mostrar_anotaciones=True):
    """
    Muestra una animación de cómo se construye/mejora la ruta paso a paso.
    pasos: lista de listas de ciudades (cada elemento es la ruta en ese paso)
    """
    nombres = list(ciudades.keys())
    all_x = [ciudades[c][0] for c in nombres]
    all_y = [ciudades[c][1] for c in nombres]

    fig, ax = plt.subplots(figsize=(9, 7))

    def dibujar_frame(frame_idx):
        ax.clear()
        ruta = pasos[frame_idx]
        xs = [ciudades[c][0] for c in ruta] + [ciudades[ruta[0]][0]]
        ys = [ciudades[c][1] for c in ruta] + [ciudades[ruta[0]][1]]

        ax.scatter(all_x, all_y, color='steelblue', s=60, zorder=3)
        ax.plot(xs, ys, '-o', color='tomato', linewidth=1.5, markersize=5, zorder=2)
        ax.scatter([xs[0]], [ys[0]], color='gold', s=120, zorder=4, label='Inicio')

        if mostrar_anotaciones:
            for c in ruta:
                cx, cy = ciudades[c]
                ax.text(cx + 1, cy + 1, c, fontsize=7)

        dist = calcular_distancia_ruta(ciudades, ruta)
        fase = "Construcción (Vecino más cercano)" if frame_idx < len(pasos) // 2 + 1 else "Mejora (2-opt)"
        ax.set_title(f'TSP  |  Paso {frame_idx + 1}/{len(pasos)}  |  {fase}\nDistancia: {dist:.2f}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

    ani = FuncAnimation(fig, dibujar_frame, frames=len(pasos),
                        interval=intervalo_ms, repeat=False)
    plt.tight_layout()
    return ani


def animar_dos_fases(ciudades, pasos_construccion, pasos_mejora,
                     intervalo_ms=250, mostrar_anotaciones=True):
    """
    Animación con dos fases diferenciadas por color:
      - Azul: construcción greedy (vecino más cercano)
      - Rojo: mejora 2-opt
    """
    nombres = list(ciudades.keys())
    all_x = [ciudades[c][0] for c in nombres]
    all_y = [ciudades[c][1] for c in nombres]

    pasos = [(p, 'greedy') for p in pasos_construccion] + \
            [(p, 'twoopt') for p in pasos_mejora]

    fig, ax = plt.subplots(figsize=(9, 7))

    def dibujar_frame(i):
        ax.clear()
        ruta, fase = pasos[i]
        xs = [ciudades[c][0] for c in ruta] + [ciudades[ruta[0]][0]]
        ys = [ciudades[c][1] for c in ruta] + [ciudades[ruta[0]][1]]

        color = 'royalblue' if fase == 'greedy' else 'tomato'
        label_fase = 'Vecino más cercano (greedy)' if fase == 'greedy' else '2-opt (mejora local)'

        ax.scatter(all_x, all_y, color='dimgray', s=50, zorder=3)
        ax.plot(xs, ys, '-o', color=color, linewidth=1.8, markersize=5, zorder=2, label=label_fase)
        ax.scatter([xs[0]], [ys[0]], color='gold', s=140, zorder=4, label='Ciudad origen')

        if mostrar_anotaciones:
            for c in ruta:
                cx, cy = ciudades[c]
                ax.text(cx + 1, cy + 1, c, fontsize=7)

        dist = calcular_distancia_ruta(ciudades, ruta)
        ax.set_title(f'TSP – Paso {i + 1}/{len(pasos)}\nFase: {label_fase}  |  Distancia acumulada: {dist:.2f}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)

    ani = FuncAnimation(fig, dibujar_frame, frames=len(pasos),
                        interval=intervalo_ms, repeat=False)
    plt.tight_layout()
    return ani

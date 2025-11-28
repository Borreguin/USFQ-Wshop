import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def hanoi(n, origen, destino, auxiliar, movimientos):
    """
    Genera la lista de movimientos óptimos de Hanoi.
    movimientos: lista donde se guardan tuplas (poste_origen, poste_destino)
    """
    if n == 1:
        movimientos.append((origen, destino))
        return

    hanoi(n - 1, origen, auxiliar, destino, movimientos)
    movimientos.append((origen, destino))
    hanoi(n - 1, auxiliar, destino, origen, movimientos)


def generar_estados(n, movimientos, origen=0):
    """
    A partir de la lista de movimientos, construye todos los estados de las torres.
    cada estado es una lista con 3 torres (listas).
    """
    torres = [[], [], []]
    torres[origen] = list(range(n, 0, -1))  # [n, n-1, ..., 1]

    estados = [ [t.copy() for t in torres] ]  # estado inicial

    for (desde, hasta) in movimientos:
        disco = torres[desde].pop()    # saco disco superior
        torres[hasta].append(disco)    # lo pongo arriba en destino
        estados.append([x.copy() for x in torres])

    return estados


def animar_hanoi(n, estados):

    fig, ax = plt.subplots(figsize=(8, 4))

    # posiciones x de las 3 torres
    centros = [0, 6, 12]

    def dibujar_estado(estado):
        ax.clear()

        # límites del gráfico
        ax.set_xlim(-3, 15)
        ax.set_ylim(0, n + 1)

        # dibujar "postes" de las torres
        for c in centros:
            ax.plot([c, c], [0, n + 0.5], linewidth=2)

        # dibujar discos
        for indice_poste, torre in enumerate(estado):
            for nivel, disco in enumerate(torre):
                # ancho del disco proporcional a su tamaño
                ancho = disco * 1.2
                izquierda = centros[indice_poste] - ancho / 2
                y = nivel + 0.5
                ax.barh(y=y, width=ancho, left=izquierda, height=0.8)

        ax.set_xticks(centros)
        ax.set_xticklabels(["A", "B", "C"])
        ax.set_yticks([])
        ax.set_title("Torre de Hanoi - Animación paso a paso")

    def actualizar(cuadro):
        dibujar_estado(estados[cuadro])

    animacion = FuncAnimation(fig, actualizar, frames=len(estados), interval=700, repeat=False)
    plt.show()


if __name__ == "__main__":
    n = 4
    print(f"Resolviendo Torres de Hanoi para {n} discos:")

    movimientos = []
    hanoi(n, origen=0, destino=2, auxiliar=1, movimientos=movimientos)

    # imprimir movimientos
    for i, (desde, hasta) in enumerate(movimientos, 1):
        print(f"{i}. Mover disco de {['A','B','C'][desde]} a {['A','B','C'][hasta]}")

    # generar estados y animar
    estados = generar_estados(n, movimientos, origen=0)
    animar_hanoi(n, estados)

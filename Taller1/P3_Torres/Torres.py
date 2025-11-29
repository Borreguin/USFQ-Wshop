

import matplotlib.pyplot as plt
import time

# Configuración inicial
num_discos = 3
torres = {
    "A": list(range(num_discos, 0, -1)),  # discos en A (del más grande al más pequeño)
    "B": [],
    "C": []
}

# Función para dibujar las torres
def dibujar_torres(torres, movimiento=None):
    plt.clf()
    colores = ["#F79320", "#B4C7E7", "#DCD3CC", "#4A6A8A", "#0F253E"]

    # Dibujar cada torre
    for i, torre in enumerate(["A", "B", "C"]):
        discos = torres[torre]
        for j, disco in enumerate(discos):
            plt.bar(i, 0.5, bottom=j, width=disco/num_discos,
                    color=colores[disco % len(colores)], align="center")

    plt.xticks([0, 1, 2], ["A", "B", "C"])
    plt.yticks(range(num_discos+1))
    plt.title(f"Torre de Hanoi - {movimiento if movimiento else ''}")
    plt.pause(1)

# Algoritmo recursivo
def mover_discos(n, origen, destino, auxiliar):
  # Caso Base
    if n == 1:
        disco = torres[origen].pop()
        torres[destino].append(disco)
        dibujar_torres(torres, f"Mover disco {disco} de {origen} a {destino}")
        return
  # Paso recursivo
    mover_discos(n-1, origen, auxiliar, destino)
    disco = torres[origen].pop()
    torres[destino].append(disco)
    dibujar_torres(torres, f"Mover disco {disco} de {origen} a {destino}")
    mover_discos(n-1, auxiliar, destino, origen)

# Ejecutar
plt.figure(figsize=(6,6))
dibujar_torres(torres, "Estado inicial")
mover_discos(num_discos, "A", "C", "B")
plt.show()
from collections import deque

# Cada elemento es una tupla: (granjero, lobo, cabra, col)
# Valores posibles: 'L' (izquierda), 'R' (derecha)

def es_estado_valido(estado):
    granjero, lobo, cabra, col = estado

    # Si el granjero no está con el lobo y la cabra están juntos -> la cabra muere
    if granjero != lobo and lobo == cabra:
        return False

    # Si el granjero no está con la cabra y la cabra y la col están juntos -> la col muere
    if granjero != cabra and cabra == col:
        return False

    return True
def mover(estado, quien):
    """
    Mueve al granjero solo o con 'quien' (puede ser 'lobo', 'cabra', 'col' o None).
    Devuelve el nuevo estado.
    """
    granjero, lobo, cabra, col = estado

    # Cambiar de lado
    nuevo_lado = 'R' if granjero == 'L' else 'L'
    granjero = nuevo_lado

    if quien == "lobo" and lobo != nuevo_lado:
        lobo = nuevo_lado
    elif quien == "cabra" and cabra != nuevo_lado:
        cabra = nuevo_lado
    elif quien == "col" and col != nuevo_lado:
        col = nuevo_lado

    return (granjero, lobo, cabra, col)


def vecinos(estado):
    granjero, lobo, cabra, col = estado
    movimientos = []

    # El granjero siempre se mueve. Puede ir solo:
    movimientos.append(("solo", mover(estado, None)))

    # ...o con el elemento que esté en su misma orilla:
    if lobo == granjero:
        movimientos.append(("lobo", mover(estado, "lobo")))
    if cabra == granjero:
        movimientos.append(("cabra", mover(estado, "cabra")))
    if col == granjero:
        movimientos.append(("col", mover(estado, "col")))

    # Devolver solo los estados válidos
    return [(quien, est) for quien, est in movimientos if es_estado_valido(est)]


def bfs_resolver():
    inicio = ('L', 'L', 'L', 'L')
    meta = ('R', 'R', 'R', 'R')

    cola = deque()
    cola.append(inicio)

    # Para reconstruir el camino
    padres = {inicio: (None, None)}  # estado: (estado_anterior, movimiento_desde_anterior)

    while cola:
        actual = cola.popleft()
        if actual == meta:
            break

        for quien, siguiente in vecinos(actual):
            if siguiente not in padres:  # no visitado
                padres[siguiente] = (actual, quien)
                cola.append(siguiente)

    # Reconstruimos el camino desde la meta
    if meta not in padres:
        return None

    camino = []
    estado = meta
    while estado is not None:
        anterior, quien = padres[estado]
        camino.append((estado, quien))
        estado = anterior

    camino.reverse()  # del inicio a la meta
    return camino


def imprimir_camino(camino):
    print("Solución del acertijo (granjero, lobo, cabra, col):")
    for i, (estado, quien) in enumerate(camino):
        granjero, lobo, cabra, col = estado
        if i == 0:
            print(f"Paso {i}: Estado inicial -> {estado}")
        else:
            texto_quien = "solo" if quien == "solo" or quien is None else f"con la {quien}"
            print(f"Paso {i}: El granjero cruza {texto_quien} -> {estado}")


if __name__ == "__main__":
    camino = bfs_resolver()
    if camino is None:
        print("No se encontró solución.")
    else:
        imprimir_camino(camino)






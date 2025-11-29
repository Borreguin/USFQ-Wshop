from collections import deque
from typing import List, Tuple, Dict, Optional

State = Tuple[int, int, int, int]  # (granjero, zorro, cabra, col)

NOMBRES = ["Granjero", "Zorro", "Cabra", "Col"]


def es_estado_valido(estado: State) -> bool:
    """Verifica que el estado cumpla las reglas:
    - El zorro no puede quedarse solo con la cabra sin el granjero.
    - La cabra no puede quedarse sola con la col sin el granjero.
    """
    granjero, zorro, cabra, col = estado

    for side in (0, 1):
        # Zorro y cabra juntos sin granjero
        if zorro == cabra == side and granjero != side:
            return False
        # Cabra y col juntos sin granjero
        if cabra == col == side and granjero != side:
            return False

    return True


def generar_vecinos(estado: State) -> List[Tuple[State, str]]:
    """Genera todos los estados vecinos válidos desde 'estado',
    junto con una descripción del movimiento."""
    granjero, zorro, cabra, col = estado
    vecinos = []

    lado_actual = granjero
    lado_opuesto = 1 - lado_actual

    # 1) Granjero solo
    nuevo_estado = (lado_opuesto, zorro, cabra, col)
    if es_estado_valido(nuevo_estado):
        vecinos.append((nuevo_estado, "El granjero cruza solo"))

    # 2) Granjero + Zorro
    if zorro == lado_actual:
        nuevo_estado = (lado_opuesto, lado_opuesto, cabra, col)
        if es_estado_valido(nuevo_estado):
            vecinos.append((nuevo_estado, "El granjero cruza con el zorro"))

    # 3) Granjero + Cabra
    if cabra == lado_actual:
        nuevo_estado = (lado_opuesto, zorro, lado_opuesto, col)
        if es_estado_valido(nuevo_estado):
            vecinos.append((nuevo_estado, "El granjero cruza con la cabra"))

    # 4) Granjero + Col
    if col == lado_actual:
        nuevo_estado = (lado_opuesto, zorro, cabra, lado_opuesto)
        if es_estado_valido(nuevo_estado):
            vecinos.append((nuevo_estado, "El granjero cruza con la col"))

    return vecinos


def bfs_resolver(inicio: State, objetivo: State) -> Optional[List[Tuple[State, str]]]:
    """Aplica BFS para encontrar una secuencia de movimientos desde 'inicio' hasta 'objetivo'.
    Devuelve una lista de (estado, descripción_movimiento) desde el inicio al objetivo."""
    cola = deque()
    cola.append(inicio)

    visitados = set()
    visitados.add(inicio)

    # Para reconstruir el camino: estado -> (estado_padre, descripcion_movimiento)
    padres: Dict[State, Tuple[Optional[State], str]] = {inicio: (None, "Estado inicial")}

    while cola:
        actual = cola.popleft()

        if actual == objetivo:
            # Reconstruir el camino
            camino: List[Tuple[State, str]] = []
            estado = actual
            while estado is not None:
                padre, mov = padres[estado]
                camino.append((estado, mov))
                estado = padre
            camino.reverse()
            return camino

        for vecino, desc in generar_vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padres[vecino] = (actual, desc)
                cola.append(vecino)

    return None  # No hay solución (no debería pasar en este puzzle)


def formatear_estado(estado: State) -> str:
    """Devuelve una representación textual amigable del estado."""
    granjero, zorro, cabra, col = estado
    izquierda = []
    derecha = []

    posiciones = [granjero, zorro, cabra, col]
    for pos, nombre in zip(posiciones, NOMBRES):
        if pos == 0:
            izquierda.append(nombre)
        else:
            derecha.append(nombre)

    return f"Izquierda: {', '.join(izquierda) or '---'} | Derecha: {', '.join(derecha) or '---'}"


if __name__ == '__main__':
    inicio = (0, 0, 0, 0)  # todos a la izquierda
    objetivo = (1, 1, 1, 1)  # todos a la derecha

    solucion = bfs_resolver(inicio, objetivo)

    if solucion is None:
        print("No se encontró solución.")
    else:
        print("Solución encontrada:\n")
        for i, (estado, mov) in enumerate(solucion):
            if i == 0:
                print(f"Paso {i}: {formatear_estado(estado)} ({mov})")
            else:
                print(f"Paso {i}: {mov}")
                print(f"         {formatear_estado(estado)}")

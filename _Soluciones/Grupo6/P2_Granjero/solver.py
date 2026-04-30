from collections import deque
from typing import List, Optional, Tuple
from estado import Estado
from grafo_rio import obtener_vecinos

def resolver_bfs() -> Optional[List[Tuple[str, Estado]]]:
    inicio   = Estado(granjero=0, lobo=0, cabra=0, col=0)
    objetivo = Estado(granjero=1, lobo=1, cabra=1, col=1)

    cola     = deque()
    cola.append([(None, inicio)])
    visitados = {inicio}

    while cola:
        camino = cola.popleft()
        _, estado_actual = camino[-1]

        if estado_actual == objetivo:
            return camino

        for accion, vecino in obtener_vecinos(estado_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(camino + [(accion, vecino)])

    return None

def imprimir_solucion(camino):
    print("\n=== SOLUCIÓN: Problema del Granjero ===\n")
    for paso, (accion, estado) in enumerate(camino):
        if accion is None:
            print(f"Paso 0 — Estado inicial")
        else:
            print(f"Paso {paso} — {accion}")
        print(f"         {estado}\n")
    print(f"Total de pasos: {len(camino) - 1}")

if __name__ == "__main__":
    camino = resolver_bfs()
    if camino:
        imprimir_solucion(camino)
    else:
        print("No hay solución")
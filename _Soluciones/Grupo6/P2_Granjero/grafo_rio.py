from typing import List, Tuple
from estado import Estado

def obtener_vecinos(estado: Estado) -> List[Tuple[str, Estado]]:
    g  = estado.granjero
    ng = 1 - g
    acciones = []

    acciones.append(("Granjero cruza solo",
                     Estado(ng, estado.lobo, estado.cabra, estado.col)))

    if estado.lobo == g:
        acciones.append(("Granjero lleva lobo",
                         Estado(ng, ng, estado.cabra, estado.col)))

    if estado.cabra == g:
        acciones.append(("Granjero lleva cabra",
                         Estado(ng, estado.lobo, ng, estado.col)))

    if estado.col == g:
        acciones.append(("Granjero lleva col",
                         Estado(ng, estado.lobo, estado.cabra, ng)))

    return [(accion, nuevo)
            for accion, nuevo in acciones
            if nuevo.es_valido()]
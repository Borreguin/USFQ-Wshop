"""
util_two_opt.py
================

Heuristica 2-opt y deteccion geometrica de cruces para TSP euclidiano.

Estas funciones se desarrollaron originalmente en el notebook ``P2.ipynb``
(seccion F del taller) y se exponen aqui como modulo reutilizable, sin
modificar las utilidades previas (``util.py``, ``util_nearest_neighbor.py``,
``TSP.py``).

API publica:

* ``segmentos_se_cruzan(p1, p2, p3, p4) -> bool``
* ``contar_cruces(ciudades, ruta) -> int``
* ``two_opt_first_improvement(ciudades, distancias, ruta_inicial)
  -> (ruta_mejorada, historial)``
* ``two_opt_best_improvement(ciudades, distancias, ruta_inicial)
  -> (ruta_mejorada, historial)``

La ``ruta`` se asume como una lista de nombres de ciudad, cerrada
(``ruta[0] == ruta[-1]``) o no; ambas variantes son aceptadas y la salida
siempre se devuelve cerrada.
"""

from typing import List, Tuple, Dict


# ---------------------------------------------------------------------------
# Deteccion geometrica de cruces (test de orientacion via producto cruzado)
# ---------------------------------------------------------------------------
def segmentos_se_cruzan(p1, p2, p3, p4) -> bool:
    """True si los segmentos (p1,p2) y (p3,p4) se cruzan estrictamente.

    Cada punto es una tupla (x, y). No se considera contacto colineal
    (probabilidad 0 con coordenadas continuas aleatorias).
    """
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


# Alias "privado" para mantener compatibilidad con el notebook
_segmentos_se_cruzan = segmentos_se_cruzan


def contar_cruces(ciudades: Dict[str, Tuple[float, float]],
                  ruta: List[str]) -> int:
    """Cuenta cuantas parejas de aristas se cruzan en la ruta dada."""
    n = len(ruta)
    cruces = 0
    for i in range(n - 1):
        for j in range(i + 2, n - 1):
            if i == 0 and j == n - 2:
                # mismas aristas del cierre del ciclo
                continue
            a, b = ruta[i], ruta[i + 1]
            c, d = ruta[j], ruta[j + 1]
            if segmentos_se_cruzan(ciudades[a], ciudades[b],
                                   ciudades[c], ciudades[d]):
                cruces += 1
    return cruces


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _dist_lookup(distancias: dict):
    """Devuelve una funcion ``d(a, b)`` que tolera la ausencia de la diagonal
    y el orden de las claves en ``distancias``."""
    def d(a, b):
        key = (a, b) if (a, b) in distancias else (b, a)
        return distancias[key]
    return d


def _normalizar(ruta_inicial: List[str]) -> List[str]:
    """Devuelve el tour sin la ciudad final repetida (formato interno 2-opt)."""
    tour = list(ruta_inicial)
    if tour and tour[-1] == tour[0]:
        tour = tour[:-1]
    return tour


# ---------------------------------------------------------------------------
# 2-opt First Improvement
# ---------------------------------------------------------------------------
def two_opt_first_improvement(ciudades, distancias, ruta_inicial):
    """Mejora local 2-opt (first improvement).

    Aplica el primer swap que reduzca la distancia y reinicia el barrido.
    Retorna ``(ruta_mejorada_cerrada, historial)`` donde ``historial`` es una
    lista de dicts ``{'iteracion': int, 'distancia': float}``.
    """
    tour = _normalizar(ruta_inicial)
    n = len(tour)
    dist = _dist_lookup(distancias)

    d_actual = sum(dist(tour[i], tour[(i + 1) % n]) for i in range(n))
    historia = []
    it = 0
    mejoro = True

    while mejoro:
        mejoro = False
        it += 1
        for i in range(n - 1):
            for k in range(i + 2, n):
                a, b = tour[i], tour[(i + 1) % n]
                c, d_node = tour[k], tour[(k + 1) % n]
                delta = (dist(a, c) + dist(b, d_node)
                         - dist(a, b) - dist(c, d_node))
                if delta < -1e-10:
                    tour[i + 1:k + 1] = tour[i + 1:k + 1][::-1]
                    d_actual += delta
                    mejoro = True
                    break
            if mejoro:
                break
        if mejoro:
            historia.append({'iteracion': it, 'distancia': round(d_actual, 4)})

    return tour + [tour[0]], historia


# ---------------------------------------------------------------------------
# 2-opt Best Improvement
# ---------------------------------------------------------------------------
def two_opt_best_improvement(ciudades, distancias, ruta_inicial):
    """Mejora local 2-opt (best improvement).

    En cada pasada aplica el swap con mayor mejora absoluta. Suele requerir
    menos iteraciones que ``two_opt_first_improvement`` a costa de un coste
    por iteracion mayor.
    Retorna ``(ruta_mejorada_cerrada, historial)``.
    """
    tour = _normalizar(ruta_inicial)
    n = len(tour)
    dist = _dist_lookup(distancias)

    d_actual = sum(dist(tour[i], tour[(i + 1) % n]) for i in range(n))
    historia = []
    it = 0
    mejoro = True

    while mejoro:
        it += 1
        mejor_delta = 0
        mejor_i, mejor_k = -1, -1
        for i in range(n - 1):
            for k in range(i + 2, n):
                a, b = tour[i], tour[(i + 1) % n]
                c, d_node = tour[k], tour[(k + 1) % n]
                delta = (dist(a, c) + dist(b, d_node)
                         - dist(a, b) - dist(c, d_node))
                if delta < mejor_delta - 1e-10:
                    mejor_delta = delta
                    mejor_i, mejor_k = i, k
        if mejor_i >= 0:
            tour[mejor_i + 1:mejor_k + 1] = tour[mejor_i + 1:mejor_k + 1][::-1]
            d_actual += mejor_delta
            historia.append({'iteracion': it, 'distancia': round(d_actual, 4)})
            mejoro = True
        else:
            mejoro = False

    return tour + [tour[0]], historia


__all__ = [
    'segmentos_se_cruzan',
    'contar_cruces',
    'two_opt_first_improvement',
    'two_opt_best_improvement',
]

"""
tsp_anti_cruces.py
==================

Implementacion del cutting plane casero anti-cruces para TSP euclidiano
(opcion 3 del enunciado F del Taller 3).

La idea es resolver iterativamente un MTZ basico en Pyomo + GLPK, detectar
cruces geometricos en el tour incumbente y agregar restricciones de la forma::

    x[a, b] + x[b, a] + x[c, d] + x[d, c] <= 1

para cada par de aristas que se cruzan. El proceso se repite hasta obtener
un tour libre de cruces o agotar ``max_iter``.

Este modulo se desarrollo en el notebook ``P2.ipynb`` y se expone aqui sin
modificar las utilidades previas.
"""

import time
from typing import Dict, Tuple, List

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

from util import generar_ciudades_con_distancias, calculate_path_distance
from util_two_opt import contar_cruces, segmentos_se_cruzan


# ---------------------------------------------------------------------------
# Construccion del modelo MTZ (indexado por nombres de ciudad)
# ---------------------------------------------------------------------------
def construir_modelo_mtz(ciudades_loc: Dict[str, Tuple[float, float]],
                         distancias_loc: Dict[Tuple[str, str], float]):
    """Construye el modelo MTZ basico (sin heuristicas) en Pyomo.

    Indexado por *nombres* de ciudad (claves de ``ciudades_loc``), porque
    ``distancias_loc`` es un dict ``{(nombreA, nombreB): dist}`` que no
    contiene la diagonal (ver ``util.generar_distancias``).
    """
    nombres = list(ciudades_loc.keys())
    n = len(nombres)
    ciudad_inicial = nombres[0]
    nombres_resto = nombres[1:]

    m = pyo.ConcreteModel()
    m.N = pyo.Set(initialize=nombres)
    m.M = pyo.Set(initialize=nombres)
    m.U = pyo.Set(initialize=nombres_resto)
    m.x = pyo.Var(m.N, m.M, within=pyo.Binary)
    m.u = pyo.Var(m.N, within=pyo.NonNegativeIntegers, bounds=(0, n - 1))

    m.obj = pyo.Objective(
        expr=sum(distancias_loc[i, j] * m.x[i, j]
                 for i in m.N for j in m.M if i != j),
        sense=pyo.minimize,
    )

    def _no_self(model, i):
        return model.x[i, i] == 0
    m.no_self = pyo.Constraint(m.N, rule=_no_self)

    def _entrada(model, j):
        return sum(model.x[i, j] for i in model.N if i != j) == 1
    m.entrada = pyo.Constraint(m.N, rule=_entrada)

    def _salida(model, i):
        return sum(model.x[i, j] for j in model.M if i != j) == 1
    m.salida = pyo.Constraint(m.N, rule=_salida)

    def _mtz(model, i, j):
        if i != j and i != ciudad_inicial and j != ciudad_inicial:
            return model.u[i] - model.u[j] + n * model.x[i, j] <= n - 1
        return pyo.Constraint.Skip
    m.mtz = pyo.Constraint(m.N, m.M, rule=_mtz)

    return m


def ruta_desde_modelo(m, ciudades_loc: Dict[str, Tuple[float, float]]):
    """Reconstruye la ruta como lista cerrada de nombres de ciudad.

    Devuelve ``None`` si el modelo no tiene una solucion entera completa
    (por ejemplo, si el solver agoto su tiempo sin incumbente).
    """
    nombres = list(ciudades_loc.keys())
    n = len(nombres)
    ciudad_inicial = nombres[0]
    sucesor = {}
    for i in nombres:
        for j in nombres:
            if i == j:
                continue
            v = pyo.value(m.x[i, j])
            if v is not None and v > 0.5:
                sucesor[i] = j
                break
    if ciudad_inicial not in sucesor or len(sucesor) < n:
        return None
    ruta = [ciudad_inicial]
    actual = ciudad_inicial
    for _ in range(n):
        actual = sucesor.get(actual)
        if actual is None:
            return None
        ruta.append(actual)
    return ruta


# ---------------------------------------------------------------------------
# Bucle principal: cutting plane anti-cruces
# ---------------------------------------------------------------------------
def tsp_anti_cruces_iterativo(n_cities: int = 20,
                              time_limit: int = 15,
                              max_iter: int = 20,
                              tee: bool = False,
                              ciudades_loc: Dict = None,
                              distancias_loc: Dict = None,
                              verbose: bool = True) -> dict:
    """Cutting plane anti-cruces (opcion 3 del enunciado F).

    Resuelve, detecta cruces, anade restricciones
    ``x[a,b] + x[b,a] + x[c,d] + x[d,c] <= 1`` para cada par de aristas
    cruzadas y repite hasta que el tour no tenga cruces o se agote
    ``max_iter``.

    Parametros
    ----------
    n_cities : int
        Numero de ciudades a generar si no se entregan ``ciudades_loc``.
    time_limit : int
        Tiempo limite (segundos) por llamada al solver GLPK.
    max_iter : int
        Maximo de iteraciones del cutting plane.
    tee : bool
        Pasar la salida del solver a stdout.
    ciudades_loc, distancias_loc : dict, opcional
        Si se entregan, se reutilizan; si no, se generan con la semilla
        por defecto de ``generar_ciudades_con_distancias``.
    verbose : bool
        Imprimir progreso por iteracion.

    Retorna
    -------
    dict
        ``{'ruta', 'distancia', 'historial', 'ciudades', 'distancias',
        'convergio'}``.
    """
    if ciudades_loc is None or distancias_loc is None:
        ciudades_loc, distancias_loc = generar_ciudades_con_distancias(n_cities)

    m = construir_modelo_mtz(ciudades_loc, distancias_loc)

    solver = SolverFactory("glpk")
    solver.options['tmlim'] = time_limit

    m.cortes_anti_cruces = pyo.ConstraintList()

    historial: List[dict] = []
    cortes_acumulados = 0
    ruta = None
    dist_actual = None

    for it in range(1, max_iter + 1):
        t0 = time.perf_counter()
        solver.solve(m, tee=tee)
        t_solve = time.perf_counter() - t0

        ruta = ruta_desde_modelo(m, ciudades_loc)
        if ruta is None:
            if verbose:
                print(f"  Iter {it:>2}: el solver no devolvio tour completo "
                      f"(timeout?). Aborto.")
            break

        dist_actual = calculate_path_distance(distancias_loc, ruta)
        cruces = contar_cruces(ciudades_loc, ruta)
        historial.append({
            'iteracion': it,
            'distancia': round(dist_actual, 2),
            'cruces': cruces,
            'cortes_acumulados': cortes_acumulados,
            'tiempo_solver_s': round(t_solve, 2),
        })
        if verbose:
            print(f"  Iter {it:>2}: dist = {dist_actual:>8.2f}, "
                  f"cruces = {cruces:>2}, cortes acumulados = "
                  f"{cortes_acumulados:>3}, t = {t_solve:.2f} s")

        if cruces == 0:
            if verbose:
                print(f"  ✓ Tour sin cruces alcanzado en {it} iteraciones.")
            return {
                'ruta': ruta, 'distancia': dist_actual,
                'historial': historial,
                'ciudades': ciudades_loc, 'distancias': distancias_loc,
                'convergio': True,
            }

        # Anadir cortes para cada par de aristas que se cruzan
        nuevos = 0
        nlist = len(ruta)
        for i in range(nlist - 1):
            for j in range(i + 2, nlist - 1):
                if i == 0 and j == nlist - 2:
                    continue
                a, b = ruta[i], ruta[i + 1]
                c, d = ruta[j], ruta[j + 1]
                if segmentos_se_cruzan(ciudades_loc[a], ciudades_loc[b],
                                       ciudades_loc[c], ciudades_loc[d]):
                    m.cortes_anti_cruces.add(
                        m.x[a, b] + m.x[b, a] + m.x[c, d] + m.x[d, c] <= 1
                    )
                    nuevos += 1
        cortes_acumulados += nuevos

    if verbose:
        print(f"  ! max_iter={max_iter} alcanzado sin eliminar todos los cruces.")
    return {
        'ruta': ruta, 'distancia': dist_actual, 'historial': historial,
        'ciudades': ciudades_loc, 'distancias': distancias_loc,
        'convergio': False,
    }


__all__ = [
    'construir_modelo_mtz',
    'ruta_desde_modelo',
    'tsp_anti_cruces_iterativo',
]


if __name__ == "__main__":
    print("── Cutting plane anti-cruces (n=20, MTZ + cortes manuales) ──")
    res = tsp_anti_cruces_iterativo(n_cities=20, time_limit=15, max_iter=10)
    print(f"\nDistancia final: {res['distancia']:.2f}  "
          f"(convergio={res['convergio']})")

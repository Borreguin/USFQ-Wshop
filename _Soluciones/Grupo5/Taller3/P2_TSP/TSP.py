import pyomo.environ as pyo
import re
import sys
import os
import datetime as dt
from typing import List, Sequence
# Referencia: https://baobabsoluciones.es/blog/2020/10/01/problema-del-viajante/

# Imports compatibles con ejecucion directa (python TSP.py) e importacion como paquete
try:
    from Taller3.P2_TSP.util import (
        generar_ciudades_con_distancias, get_min_distance, get_max_distance,
        get_average_distance, get_average_distance_for_city, get_min_distances,
        get_max_distances, delta_time_mm_ss, get_path, calculate_path_distance,
        plotear_ruta, two_opt_improve,
    )
    from Taller3.P2_TSP.util_nearest_neighbor import nearest_neighbor
except ImportError:
    _dir = os.path.dirname(os.path.realpath(__file__))
    if _dir not in sys.path:
        sys.path.append(_dir)
    from util import (                                          # type: ignore[import]
        generar_ciudades_con_distancias, get_min_distance, get_max_distance,
        get_average_distance, get_average_distance_for_city, get_min_distances,
        get_max_distances, delta_time_mm_ss, get_path, calculate_path_distance,
        plotear_ruta, two_opt_improve,
    )
    from util_nearest_neighbor import nearest_neighbor         # type: ignore[import]


class TSP:
    def __init__(self, ciudades, distancias, heuristics: List[str]):
        self.max_possible_distance = None
        self.min_possible_distance = None
        self.ciudades = ciudades
        self.distancias = distancias
        self.heuristics = heuristics
        self.min_distance = get_min_distance(distancias)
        self.max_distance = get_max_distance(distancias)
        self.average_distance = get_average_distance(distancias)
        self.average_distance_for_city = get_average_distance_for_city(distancias)
        self.min_distance_for_city = get_min_distances(distancias)
        self.max_distance_for_city = get_max_distances(distancias)
        self.cal_min_max_distances()

    def cal_min_max_distances(self):
        # Estimación de límites para la distancia total del recorrido.
        # Se usa la media entre la distancia mínima y la media como referencia.
        medium_low_distance = (self.min_distance + self.average_distance) / 2
        # Límite inferior: 25% del "recorrido ideal" estimado
        self.min_possible_distance = medium_low_distance * len(self.ciudades) * 0.25
        # Límite superior: 60% del "recorrido ideal" estimado
        self.max_possible_distance = medium_low_distance * len(self.ciudades) * 0.6

    def print_min_max_distances(self):
        print(f"  Dist. min entre nodos   : {self.min_distance:.2f}")
        print(f"  Dist. max entre nodos   : {self.max_distance:.2f}")
        print(f"  Dist. promedio nodos    : {self.average_distance:.2f}")
        print(f"  Dist. total min posible : {self.min_possible_distance:.2f}")
        print(f"  Dist. total max posible : {self.max_possible_distance:.2f}")
        print(f"  Heuristicas aplicadas   : {self.heuristics}")

    def encontrar_la_ruta_mas_corta(self, mipgap, time_limit, tee):
        start_time = dt.datetime.now()

        _model = pyo.ConcreteModel()   # modelo de programación entera mixta

        cities = list(self.ciudades.keys())
        n_cities = len(cities)

        # --- CONJUNTOS ---
        # M y N representan el mismo conjunto de ciudades (origen y destino)
        _model.M = pyo.Set(initialize=self.ciudades.keys())
        _model.N = pyo.Set(initialize=self.ciudades.keys())
        # U = todas las ciudades menos la primera (para restricciones de subtour)
        _model.U = pyo.Set(initialize=cities[1:])

        # --- VARIABLES ---
        # x[i,j] = 1 si el viajante va de ciudad i a ciudad j, 0 si no
        _model.x = pyo.Var(_model.N, _model.M, within=pyo.Binary)
        # u[i] = variable auxiliar entera (Miller-Tucker-Zemlin) para evitar subtours
        _model.u = pyo.Var(_model.N, bounds=(0, n_cities - 1), within=pyo.NonNegativeIntegers)

        # --- FUNCIÓN OBJETIVO: minimizar distancia total ---
        def obj_rule(model):
            # Suma distancia[i,j] * x[i,j] para todos los pares distintos
            return sum(
                self.distancias[i, j] * model.x[i, j]
                for i in model.N for j in model.M if i != j
            )
        _model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        # --- RESTRICCIÓN 1: exactamente una llegada a cada ciudad ---
        def regla_una_entrada(model, city_j):
            return sum(model.x[i, city_j] for i in model.N if city_j != i) == 1
        _model.one_way_i_j = pyo.Constraint(_model.M, rule=regla_una_entrada)

        # --- RESTRICCIÓN 2: exactamente una salida de cada ciudad ---
        def regla_una_salida(model, city_i):
            return sum(model.x[city_i, j] for j in model.M if city_i != j) == 1
        _model.one_way_j_i = pyo.Constraint(_model.N, rule=regla_una_salida)

        # --- RESTRICCIÓN 3: eliminación de subtours (MTZ) ---
        # Sin esta restricción el solver podría hacer varios ciclos cortos
        # en lugar de un único recorrido completo.
        # La condición u[i] - u[j] + n*x[i,j] <= n-1 fuerza un orden
        # único de visita, imposibilitando los ciclos cerrados parciales.
        def rule_formando_path(model, i, j):
            if i != j:
                return model.u[i] - model.u[j] + model.x[i, j] * n_cities <= n_cities - 1
            return pyo.Constraint.Skip
        _model.complete_path = pyo.Constraint(_model.U, _model.N, rule=rule_formando_path)

        # --- RESTRICCIÓN 4: no viajar a la misma ciudad ---
        def rule_no_self(model, i, j):
            if i == j:
                return model.x[i, j] == 0
            return pyo.Constraint.Skip
        _model.no_self_travel = pyo.Constraint(_model.N, _model.M, rule=rule_no_self)

        # ---------------------------------------------------------------
        # HEURÍSTICAS OPCIONALES
        # ---------------------------------------------------------------

        # HEURÍSTICA A: Limitar la función objetivo (caso 2)
        # En lugar de buscar en todo [0, +inf), acotamos la búsqueda al
        # rango [min_posible, max_posible]. El solver puede podar ramas
        # del árbol B&B que claramente no caen en ese rango → más rápido.
        if "limitar_funcion_objetivo" in self.heuristics:
            _model.obj_lower = pyo.Constraint(
                expr=_model.obj >= self.min_possible_distance)
            _model.obj_upper = pyo.Constraint(
                expr=_model.obj <= self.max_possible_distance)

        # HEURÍSTICA B: Vecino cercano (caso 3)
        # Restringe que el costo de ir de i a j no supere el promedio local de i.
        # Si i ya tiene distancias promedio bajas, lo obligamos a elegir
        # sólo vecinos cercanos, reduciendo el espacio de búsqueda.
        if "vecino_cercano" in self.heuristics:
            def rule_vecino_cercano(model, i, j):
                if i == j:
                    return pyo.Constraint.Skip
                if self.average_distance_for_city[i] > self.average_distance:
                    return pyo.Constraint.Skip
                threshold = (
                    self.average_distance_for_city[i] + self.min_distance_for_city[i]
                ) / 2
                return model.x[i, j] * self.distancias[i, j] <= threshold
            _model.nearest_neighbor = pyo.Constraint(
                _model.N, _model.M, rule=rule_vecino_cercano)

        # --- RESOLVER ---
        solver = pyo.SolverFactory('glpk')
        solver.options['mipgap'] = mipgap    # tolerancia: para cuando gap <= mipgap
        solver.options['tmlim'] = time_limit  # tiempo máximo en segundos
        # tee=True muestra el log completo de GLPK (ver literal B)
        results = solver.solve(_model, tee=tee)

        execution_time = dt.datetime.now() - start_time
        print(f"  Tiempo LP               : {delta_time_mm_ss(execution_time)}")
        self.print_min_max_distances()

        if results.solver.termination_condition == pyo.TerminationCondition.optimal:
            print("  --> Ruta OPTIMA encontrada")
        else:
            print("  --> Tiempo agotado: mejor solucion encontrada hasta ahora")

        # Extraer las aristas activas (x[i,j] = 1) y reconstruir el camino
        edges = {}
        valid_paths = []
        for v in _model.component_data_objects(pyo.Var):
            if v.domain == pyo.Boolean and v.value is not None and v.value > 0:
                edge = re.search(r'\[(\w\d)*,(\w\d)*]', v.name)
                city1, city2 = edge.group(1), edge.group(2)
                key = f"{city1}_{city2}"
                if key not in valid_paths:
                    valid_paths += [f"{city1}_{city2}", f"{city2}_{city1}"]
                    edges[city1] = city2

        initial_city = cities[0]
        path = get_path(edges, initial_city, [])
        path.append(path[0])   # cerrar el ciclo volviendo a la ciudad inicial
        distance = calculate_path_distance(self.distancias, path)
        print(f"  Distancia total LP      : {distance:.2f}")
        return path

    def plotear_resultado(self, ruta: Sequence[str | None], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, self.distancias, ruta, mostrar_anotaciones)


# =============================================================================
# LITERAL A: Loop 10-50 ciudades comparando LP vs Vecino Cercano
# mipgap=0.05 significa que el solver para cuando la solución está a
# no más del 5% del óptimo teórico → solución "suficientemente buena"
# =============================================================================
def study_case_1():
    print("\n" + "="*60)
    print("CASO 1 - LP vs Vecino Cercano (mipgap=0.05, limite=30s)")
    print("="*60)
    city_counts = [10, 20, 30, 40, 50]

    for n_cities in city_counts:
        print(f"\n--- {n_cities} ciudades ---")
        ciudades, distancias = generar_ciudades_con_distancias(n_cities)

        # Vecino cercano: O(n^2), siempre termina en tiempo despreciable
        start_nn = dt.datetime.now()
        ruta_nn = nearest_neighbor(ciudades, distancias)
        time_nn = dt.datetime.now() - start_nn
        dist_nn = calculate_path_distance(distancias, ruta_nn)
        print(f"  Vecino Cercano          : dist={dist_nn:.2f}, t={delta_time_mm_ss(time_nn)}")

        # LP: puede no converger en 30s para n >= 30
        heuristics = []
        tsp = TSP(ciudades, distancias, heuristics)
        ruta_lp = tsp.encontrar_la_ruta_mas_corta(
            mipgap=0.05, time_limit=30, tee=False)

        if ruta_lp:
            tsp.plotear_resultado(ruta_lp, mostrar_anotaciones=(n_cities <= 20))


# =============================================================================
# LITERAL B: Parámetro tee
# tee=True hace que GLPK imprima en pantalla todo su proceso interno:
#   - Relajación LP: solución continua del problema (cota inferior)
#   - Iteraciones Branch & Bound: el árbol de búsqueda de soluciones enteras
#   - Cada línea muestra: iteración, mejor cota, gap actual, tiempo
#   - El gap va bajando hasta alcanzar el mipgap especificado o el tiempo límite
# Sirve para entender por qué el solver tarda más con más ciudades.
# =============================================================================
def study_case_1_tee():
    print("\n" + "="*60)
    print("CASO 1B - tee=True (20 ciudades, log completo de GLPK)")
    print("="*60)
    n_cities = 20
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    heuristics = []
    tsp = TSP(ciudades, distancias, heuristics)
    # tee=True: imprime el log completo del solver Branch & Bound
    ruta = tsp.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=30, tee=True)
    tsp.plotear_resultado(ruta)


# =============================================================================
# LITERAL C: Heurística de límites a la función objetivo
# Con heurística: el solver acota el espacio de búsqueda → más rápido
# Sin heurística: el solver busca en [0, +inf) → más lento
# RIESGO: si los límites son muy estrechos y la solución óptima cae fuera,
#   el modelo es infactible → no hay solución. Por eso no sirve para cualquier caso.
# =============================================================================
def study_case_2():
    n_cities = 70
    for use_heuristic in [True, False]:
        label = "CON" if use_heuristic else "SIN"
        print(f"\n{'='*60}")
        print(f"CASO 2 - {label} heuristica de limites (70 ciudades)")
        print("="*60)
        ciudades, distancias = generar_ciudades_con_distancias(n_cities)
        heuristics = ['limitar_funcion_objetivo'] if use_heuristic else []
        tsp = TSP(ciudades, distancias, heuristics)
        ruta = tsp.encontrar_la_ruta_mas_corta(mipgap=0.2, time_limit=40, tee=True)
        if ruta:
            tsp.plotear_resultado(ruta, False)


# =============================================================================
# LITERAL D: Heurística de vecinos cercanos
# Con heurística: restringe las aristas a vecinos "cercanos" → espacio más pequeño
# Sin heurística: todas las aristas son válidas → espacio completo
# LIMITACIÓN: si la restricción es demasiado estricta puede eliminar la solución
#   óptima del espacio factible, entregando una ruta subóptima o infactible.
# =============================================================================
def study_case_3():
    n_cities = 100
    for use_heuristic in [True, False]:
        label = "CON" if use_heuristic else "SIN"
        print(f"\n{'='*60}")
        print(f"CASO 3 - {label} heuristica vecino cercano (100 ciudades)")
        print("="*60)
        ciudades, distancias = generar_ciudades_con_distancias(n_cities)
        heuristics = ['vecino_cercano'] if use_heuristic else []
        tsp = TSP(ciudades, distancias, heuristics)
        ruta = tsp.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=60, tee=True)
        if ruta:
            tsp.plotear_resultado(ruta, False)


def study_nearest_neighbor(n_cities):
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    ruta = nearest_neighbor(ciudades, distancias)
    plotear_ruta(ciudades, distancias, ruta, True)


# =============================================================================
# LITERAL F (OPCIONAL): Heuristica 2-opt — eliminar cruces de caminos
#
# Problema: el solver LP y el vecino cercano pueden generar rutas con aristas
# que se cruzan. Cuando dos aristas se cruzan en el plano Euclidiano, siempre
# es posible eliminar el cruce invirtiendo el segmento entre ellas, obteniendo
# una ruta estrictamente mas corta.
#
# Algoritmo 2-opt:
#   1. Para cada par de aristas (A->B) y (C->D) de la ruta actual:
#      - Eliminar ambas aristas
#      - Reconectar invirtiendo el segmento: A->C ... B->D
#   2. Si la nueva distancia es menor, aceptar el cambio
#   3. Repetir hasta que no haya ningun par de aristas que mejore la ruta
#
# Complejidad: O(n^2) por iteracion, practico hasta ~1000 ciudades.
# No garantiza optimo global, pero elimina todos los cruces detectables
# mediante intercambios de 2 aristas.
#
# Implementacion: funcion two_opt_improve() en util.py, aplicada como
# pos-procesamiento sobre cualquier ruta (LP, vecino cercano, etc.).
# =============================================================================
def study_case_f():
    n_cities = 100
    print(f"\n{'='*60}")
    print("CASO F - Heuristica 2-opt: eliminar cruces de caminos")
    print("="*60)

    ciudades, distancias = generar_ciudades_con_distancias(n_cities)

    # --- Baseline: vecino cercano sin 2-opt ---
    ruta_nn = nearest_neighbor(ciudades, distancias)
    dist_nn = calculate_path_distance(distancias, ruta_nn)
    print(f"\n  Vecino cercano (sin 2-opt): {dist_nn:.2f}")

    # --- Vecino cercano + 2-opt ---
    start = dt.datetime.now()
    ruta_nn_2opt = two_opt_improve(ruta_nn, distancias)
    elapsed = dt.datetime.now() - start
    dist_nn_2opt = calculate_path_distance(distancias, ruta_nn_2opt)
    mejora_nn = (dist_nn - dist_nn_2opt) / dist_nn * 100
    print(f"  Vecino cercano + 2-opt    : {dist_nn_2opt:.2f}  "
          f"(mejora: {mejora_nn:.1f}%,  t={delta_time_mm_ss(elapsed)})")
    plotear_ruta(ciudades, distancias, ruta_nn_2opt, mostrar_anotaciones=False)

    # --- LP (con heuristica vecino cercano) + 2-opt ---
    print(f"\n  Ejecutando LP (mipgap=0.05, limite=60s) ...")
    heuristics = ['vecino_cercano']
    tsp = TSP(ciudades, distancias, heuristics)
    ruta_lp = tsp.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=60, tee=False)

    if ruta_lp:
        dist_lp = calculate_path_distance(distancias, ruta_lp)
        print(f"  LP (sin 2-opt)            : {dist_lp:.2f}")

        start = dt.datetime.now()
        ruta_lp_2opt = two_opt_improve(ruta_lp, distancias)
        elapsed = dt.datetime.now() - start
        dist_lp_2opt = calculate_path_distance(distancias, ruta_lp_2opt)
        mejora_lp = (dist_lp - dist_lp_2opt) / dist_lp * 100
        print(f"  LP + 2-opt                : {dist_lp_2opt:.2f}  "
              f"(mejora: {mejora_lp:.1f}%,  t={delta_time_mm_ss(elapsed)})")

        print(f"\n  Resumen comparativo ({n_cities} ciudades):")
        print(f"    Vecino cercano           : {dist_nn:.2f}")
        print(f"    Vecino cercano + 2-opt   : {dist_nn_2opt:.2f}  ({mejora_nn:.1f}% mejor)")
        print(f"    LP                       : {dist_lp:.2f}")
        print(f"    LP + 2-opt               : {dist_lp_2opt:.2f}  ({mejora_lp:.1f}% mejor)")
        plotear_ruta(ciudades, distancias, ruta_lp_2opt, mostrar_anotaciones=False)


if __name__ == "__main__":
    print("Referencia: vecino cercano con 100 ciudades")
    study_nearest_neighbor(100)

    study_case_1()        # Literal A: loop 10-50 ciudades
    study_case_1_tee()    # Literal B: activar tee
    study_case_2()        # Literal C: heuristica de limites
    study_case_3()        # Literal D: heuristica vecino cercano
    study_case_f()        # Literal F: heuristica 2-opt (eliminar cruces)

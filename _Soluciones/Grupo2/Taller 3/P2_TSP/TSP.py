import pyomo.environ as pyo
import re
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

# Asegurar que glpsol.exe esté en PATH (winglpk Windows)
_glpk_candidates = [
    r'C:\Users\Manuel Pillapa\Downloads\winglpk-4.65\glpk-4.65\w64',
    r'C:\glpk\glpk-4.65\w64',
    r'C:\glpk\w64',
]
for _d in _glpk_candidates:
    if os.path.isfile(os.path.join(_d, 'glpsol.exe')) and _d not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + _d
        break

from util import *
from util_nearest_neighbor import nearest_neighbor
# https://baobabsoluciones.es/blog/2020/10/01/problema-del-viajante/

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
        medium_low_distance = (self.min_distance + self.average_distance) / 2
        self.min_possible_distance = medium_low_distance * len(self.ciudades) * 0.25
        self.max_possible_distance = medium_low_distance * len(self.ciudades) * 0.6


    def print_min_max_distances(self):
        print(f"Distancia mínima entre nodos: {self.min_distance}")
        print(f"Distancia máxima entre nodos: {self.max_distance}")
        print(f"Distancia promedio entre nodos: {self.average_distance}")
        print(f"Distancia Total mínima posible: {self.min_possible_distance}")
        print(f"Distancia Total máxima posible: {self.max_possible_distance}")
        print(f"Heurísticas aplicadas: {self.heuristics}")

    def encontrar_la_ruta_mas_corta(self, mipgap, time_limit, tee):
        start_time = dt.datetime.now()

        _model = pyo.ConcreteModel()

        cities = list(self.ciudades.keys())
        n_cities = len(cities)


        # Sets to work with (conjuntos)
        _model.M = pyo.Set(initialize=self.ciudades.keys())
        _model.N = pyo.Set(initialize=self.ciudades.keys())

        # Index for the dummy variable u
        _model.U = pyo.Set(initialize=cities[1:])

        # Variables
        _model.x = pyo.Var(_model.N, _model.M, within=pyo.Binary)
        _model.u = pyo.Var(_model.N, bounds=(0, n_cities - 1), within=pyo.NonNegativeIntegers)

        # Objetive Function: (función objetivo a minimizar)
        def obj_rule(model):
            return sum(self.distancias[i, j] * model.x[i, j] for i in model.N for j in model.M if i != j)

        _model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        # Restricciones
        # Desde cada ciudad exactamente una arista
        def regla_una_entrada_una_salida_por_ciudad_desde(model, city_j):
            return sum(model.x[i, city_j]  for i in model.N if city_j != i) == 1

        _model.one_way_i_j = pyo.Constraint(_model.M, rule=regla_una_entrada_una_salida_por_ciudad_desde)

        # Hacia cada ciudad exactamente una arista
        def regla_una_entrada_una_salida_por_ciudad_hacia(model, city_i):
            return sum(model.x[city_i, j] for j in model.M if city_i != j) == 1

        _model.one_way_j_i = pyo.Constraint(_model.N, rule=regla_una_entrada_una_salida_por_ciudad_hacia)

        def rule_formando_path(model, i, j):
            if i != j:
                return model.u[i] - model.u[j] + model.x[i, j] * n_cities <= n_cities - 1
            else:
                # No se puede ir de una ciudad a la misma
                return pyo.Constraint.Skip

        _model.complete_path = pyo.Constraint(_model.U, _model.N, rule=rule_formando_path)

        def rule_asegurar_viaje(model, i, j):
            if i == j:
                return model.x[i, j] == 0
            return pyo.Constraint.Skip
        _model.no_self_travel = pyo.Constraint(_model.N, _model.M, rule=rule_asegurar_viaje)

        # Heurísticas:

        # Añadiendo limites a la función objetivo como una heurística
        if "limitar_funcion_objetivo" in self.heuristics:
            _model.obj_lower_bound = pyo.Constraint(expr=_model.obj >= self.min_possible_distance)
            _model.obj_upper_bound = pyo.Constraint(expr=_model.obj <= self.max_possible_distance)

        if "vecino_cercano" in self.heuristics:
            def rule_vecino_cercano(model, i, j):
                if i == j:
                    return pyo.Constraint.Skip
                print(i, self.min_distance, self.average_distance,  self.min_distance_for_city[i], self.max_distance_for_city[i], self.average_distance_for_city[i])
                if self.average_distance_for_city[i] > self.average_distance:
                     return pyo.Constraint.Skip
                expr = model.x[i,j] * self.distancias[i,j] <= (self.average_distance_for_city[i] + self.min_distance_for_city[i])/2
                return expr
            _model.nearest_neighbor = pyo.Constraint(_model.N, _model.M, rule=rule_vecino_cercano)

        # Initialize empty set for dynamic constraints (optional)
        # _model.subtour_constraint = pyo.ConstraintList()


        # Resolver el modelo con GLPK (requiere glpsol.exe en PATH)
        solver = pyo.SolverFactory('glpk')
        solver.options['mipgap'] = mipgap
        solver.options['tmlim'] = time_limit
        results = solver.solve(_model, tee=tee)

        execution_time = dt.datetime.now() - start_time
        print(f"Tiempo de ejecución: {delta_time_mm_ss(execution_time)}")
        self.print_min_max_distances()

        # Si GLPK no encontró solución factible en el tiempo dado, usar NN como fallback
        has_solution = any(
            v.value is not None
            for v in _model.component_data_objects(pyo.Var)
            if v.domain == pyo.Boolean
        )
        if not has_solution:
            print("Sin solución factible dentro del tiempo límite. Usando Vecino Más Cercano.")
            return nearest_neighbor(self.ciudades, self.distancias)

        tc = results.solver.termination_condition
        if tc == pyo.TerminationCondition.optimal or str(tc) == 'optimal':
            print("Ruta óptima encontrada:")
        else:
            print(f"Mejor solución factible encontrada (estado GLPK: {tc}):")

        edges = dict()
        valid_paths = []
        for v in _model.component_data_objects(pyo.Var):
            if v.domain == pyo.Boolean and v.value is not None and v.value > 0:
                edge = re.search(r'\[(\w\d)*,(\w\d)*]', v.name)
                city1, city2 = edge.group(1), edge.group(2)
                key = f"{city1}_{city2}"
                # Esto evita caer en ciclos cerrados
                if key not in valid_paths:
                    valid_paths += [f"{city1}_{city2}", f"{city2}_{city1}"]
                    edges[city1] = city2

        initial_city = cities[0]
        path = get_path(edges, initial_city, [])
        path.append(path[0])
        distance = calculate_path_distance(self.distancias, path)
        print("Distancia total recorrida:", distance)
        return path



    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, self.distancias, ruta, mostrar_anotaciones)

def study_nearest_neighbor(n_cities):
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    ruta = nearest_neighbor(ciudades, distancias)
    plotear_ruta(ciudades, distancias, ruta, True)


def study_case_1():
    """
    A + B: LP vs Vecino Más Cercano para 10, 20, 30, 40, 50 ciudades.
    mipgap=0.05, tiempo_limite=30s.
    tee=True activado: muestra iteraciones internas del solver GLPK (Punto B).
    """
    city_sizes = [10, 20, 30, 40, 50]
    mipgap = 0.05
    time_limit = 30
    tee = True  # B: activado para mostrar salida interna del solver GLPK

    resultados = []
    ultimo_tsp = None
    ultima_ruta_lp = None
    ultima_ruta_nn = None

    print("\n" + "=" * 75)
    print("CASO 1: LP (Pyomo/GLPK) vs Vecino Más Cercano")
    print("mipgap=0.05 | tiempo_limite=30s | tee=True (salida GLPK visible)")
    print("=" * 75)

    for n_cities in city_sizes:
        ciudades, distancias = generar_ciudades_con_distancias(n_cities)

        # Programación Lineal (Pyomo + GLPK)
        tsp = TSP(ciudades, distancias, [])
        t0 = dt.datetime.now()
        ruta_lp = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        t_lp = (dt.datetime.now() - t0).total_seconds()
        dist_lp = calculate_path_distance(distancias, ruta_lp)

        # Heurística Vecino Más Cercano
        t0 = dt.datetime.now()
        ruta_nn = nearest_neighbor(ciudades, distancias)
        t_nn = (dt.datetime.now() - t0).total_seconds()
        dist_nn = calculate_path_distance(distancias, ruta_nn)

        resultados.append((n_cities, t_lp, dist_lp, t_nn, dist_nn))
        ultimo_tsp = tsp
        ultima_ruta_lp = ruta_lp
        ultima_ruta_nn = ruta_nn

    # Tabla resumen comparativa
    print("\n" + "=" * 75)
    print(f"{'N':>5} | {'T_LP(s)':>9} | {'Dist_LP':>10} | {'T_NN(s)':>9} | {'Dist_NN':>10} | {'Mejora%':>7}")
    print("-" * 75)
    for n, t_lp, d_lp, t_nn, d_nn in resultados:
        mejora = (d_nn - d_lp) / d_nn * 100 if d_nn > 0 else 0
        print(f"{n:>5} | {t_lp:>9.3f} | {d_lp:>10.2f} | {t_nn:>9.5f} | {d_nn:>10.2f} | {mejora:>6.1f}%")
    print("=" * 75)

    # Graficar soluciones para el caso de 50 ciudades (último de la lista)
    if ultimo_tsp is not None:
        print("\nGráfica LP (50 ciudades):")
        ultimo_tsp.plotear_resultado(ultima_ruta_lp)
        print("Gráfica Vecino Más Cercano (50 ciudades):")
        plotear_ruta(ultimo_tsp.ciudades, ultimo_tsp.distancias, ultima_ruta_nn, True)


def study_case_2():
    """
    C: 70 ciudades. Comparación con y sin heurística de límites a la función objetivo.
    """
    n_cities = 70
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    mipgap = 0.2
    time_limit = 40
    tee = True

    print("\n" + "=" * 65)
    print("CASO 2a: 70 ciudades CON heurística 'limitar_funcion_objetivo'")
    print("=" * 65)
    tsp_con = TSP(ciudades, distancias, ['limitar_funcion_objetivo'])
    t0 = dt.datetime.now()
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    t_con = (dt.datetime.now() - t0).total_seconds()
    dist_con = calculate_path_distance(distancias, ruta_con)
    tsp_con.plotear_resultado(ruta_con, False)

    print("\n" + "=" * 65)
    print("CASO 2b: 70 ciudades SIN heurística")
    print("=" * 65)
    tsp_sin = TSP(ciudades, distancias, [])
    t0 = dt.datetime.now()
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    t_sin = (dt.datetime.now() - t0).total_seconds()
    dist_sin = calculate_path_distance(distancias, ruta_sin)
    tsp_sin.plotear_resultado(ruta_sin, False)

    print("\n--- Resumen Caso 2 (70 ciudades) ---")
    print(f"Con heurística (límites FO):  tiempo={t_con:.2f}s  distancia={dist_con:.2f}")
    print(f"Sin heurística:               tiempo={t_sin:.2f}s  distancia={dist_sin:.2f}")


def study_case_3():
    """
    D: 100 ciudades. Comparación con y sin heurística de vecino cercano.
    """
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    mipgap = 0.05
    time_limit = 60
    tee = True

    print("\n" + "=" * 65)
    print("CASO 3a: 100 ciudades CON heurística 'vecino_cercano'")
    print("=" * 65)
    tsp_con = TSP(ciudades, distancias, ['vecino_cercano'])
    t0 = dt.datetime.now()
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    t_con = (dt.datetime.now() - t0).total_seconds()
    dist_con = calculate_path_distance(distancias, ruta_con)
    tsp_con.plotear_resultado(ruta_con, False)

    print("\n" + "=" * 65)
    print("CASO 3b: 100 ciudades SIN heurística")
    print("=" * 65)
    tsp_sin = TSP(ciudades, distancias, [])
    t0 = dt.datetime.now()
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    t_sin = (dt.datetime.now() - t0).total_seconds()
    dist_sin = calculate_path_distance(distancias, ruta_sin)
    tsp_sin.plotear_resultado(ruta_sin, False)

    print("\n--- Resumen Caso 3 (100 ciudades) ---")
    print(f"Con heurística (vecino cercano):  tiempo={t_con:.2f}s  distancia={dist_con:.2f}")
    print(f"Sin heurística:                   tiempo={t_sin:.2f}s  distancia={dist_sin:.2f}")


if __name__ == "__main__":
    print("TSP con Pyomo/GLPK — Análisis de Heurísticas")
    print("Referencia: solución Vecino Más Cercano (100 ciudades)")
    study_nearest_neighbor(100)

    # A + B: tiempos para 10-50 ciudades y análisis del parámetro tee
    study_case_1()

    # C: heurística de límites a la función objetivo (70 ciudades)
    # study_case_2()

    # D: heurística de vecino cercano (100 ciudades)
    # study_case_3()
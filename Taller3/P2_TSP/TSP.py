import pyomo.environ as pyo
import re
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

from util import *
from util_nearest_neighbor import nearest_neighbor


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
        self.max_possible_distance = medium_low_distance * len(self.ciudades) * 0.60

    def print_min_max_distances(self):
        print(f"  Distancia mínima entre nodos:    {self.min_distance:.2f}")
        print(f"  Distancia máxima entre nodos:    {self.max_distance:.2f}")
        print(f"  Distancia promedio entre nodos:  {self.average_distance:.2f}")
        print(f"  Distancia Total mínima posible:  {self.min_possible_distance:.2f}")
        print(f"  Distancia Total máxima posible:  {self.max_possible_distance:.2f}")
        print(f"  Heurísticas aplicadas:           {self.heuristics}")

    def encontrar_la_ruta_mas_corta(self, mipgap, time_limit, tee):
        start_time = dt.datetime.now()

        _model = pyo.ConcreteModel()

        cities = list(self.ciudades.keys())
        n_cities = len(cities)

        # Sets
        _model.M = pyo.Set(initialize=self.ciudades.keys())
        _model.N = pyo.Set(initialize=self.ciudades.keys())
        _model.U = pyo.Set(initialize=cities[1:])

        # Variables
        _model.x = pyo.Var(_model.N, _model.M, within=pyo.Binary)
        _model.u = pyo.Var(_model.N, bounds=(0, n_cities - 1), within=pyo.NonNegativeIntegers)

        # Función objetivo
        def obj_rule(model):
            return sum(self.distancias[i, j] * model.x[i, j]
                       for i in model.N for j in model.M if i != j)
        _model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        # Restricción: exactamente 1 entrada por ciudad
        def regla_entrada(model, city_j):
            return sum(model.x[i, city_j] for i in model.N if city_j != i) == 1
        _model.one_way_i_j = pyo.Constraint(_model.M, rule=regla_entrada)

        # Restricción: exactamente 1 salida por ciudad
        def regla_salida(model, city_i):
            return sum(model.x[city_i, j] for j in model.M if city_i != j) == 1
        _model.one_way_j_i = pyo.Constraint(_model.N, rule=regla_salida)

        # Restricción MTZ: eliminar subtours
        def rule_formando_path(model, i, j):
            if i != j:
                return model.u[i] - model.u[j] + model.x[i, j] * n_cities <= n_cities - 1
            else:
                return pyo.Constraint.Skip
        _model.complete_path = pyo.Constraint(_model.U, _model.N, rule=rule_formando_path)

        # Restricción: no viajar a la misma ciudad
        def rule_asegurar_viaje(model, i, j):
            if i == j:
                return model.x[i, j] == 0
            return pyo.Constraint.Skip
        _model.no_self_travel = pyo.Constraint(_model.N, _model.M, rule=rule_asegurar_viaje)

        # ── HEURÍSTICA 1: Límites a la función objetivo ──────────────────────
        if "limitar_funcion_objetivo" in self.heuristics:
            _model.obj_lower_bound = pyo.Constraint(
                expr=_model.obj >= self.min_possible_distance)
            _model.obj_upper_bound = pyo.Constraint(
                expr=_model.obj <= self.max_possible_distance)

        # ── HEURÍSTICA 2: Vecino cercano ─────────────────────────────────────
        if "vecino_cercano" in self.heuristics:
            def rule_vecino_cercano(model, i, j):
                if i == j:
                    return pyo.Constraint.Skip
                if self.average_distance_for_city[i] > self.average_distance:
                    return pyo.Constraint.Skip
                expr = (model.x[i, j] * self.distancias[i, j] <=
                        (self.average_distance_for_city[i] + self.min_distance_for_city[i]) / 2)
                return expr
            _model.nearest_neighbor = pyo.Constraint(
                _model.N, _model.M, rule=rule_vecino_cercano)

        # Resolver
        solver = pyo.SolverFactory('glpk')
        solver.options['mipgap'] = mipgap
        solver.options['tmlim'] = time_limit
        results = solver.solve(_model, tee=tee)

        execution_time = dt.datetime.now() - start_time
        print(f"  Tiempo de ejecución: {delta_time_mm_ss(execution_time)}")
        self.print_min_max_distances()

        if results.solver.termination_condition == pyo.TerminationCondition.optimal:
            print("  >> Ruta óptima encontrada.")
        else:
            print("  >> Tiempo agotado — mejor solución encontrada hasta ahora:")

        edges = dict()
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
        path.append(path[0])
        distance = calculate_path_distance(self.distancias, path)
        print(f"  Distancia total recorrida: {distance:.2f}")
        return path

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, self.distancias, ruta, mostrar_anotaciones)


# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCIA: Vecino cercano puro
# ═══════════════════════════════════════════════════════════════════════════════
def run_referencia_vecino_cercano():
    print("\n" + "="*60)
    print("REFERENCIA: Vecino cercano — 100 ciudades")
    print("="*60)
    ciudades, distancias = generar_ciudades_con_distancias(100)
    ruta = nearest_neighbor(ciudades, distancias)
    dist = calculate_path_distance(distancias, ruta)
    print(f"  Distancia vecino cercano: {dist:.2f}")
    plotear_ruta(ciudades, distancias, ruta, True)


# ═══════════════════════════════════════════════════════════════════════════════
# CASO 1: Sin heurísticas — 10, 20, 30, 40, 50 ciudades
# ═══════════════════════════════════════════════════════════════════════════════
def run_caso_1():
    print("\n" + "="*60)
    print("CASO 1: Sin heurísticas (mipgap=0.05, límite=30s)")
    print("="*60)
    for n in [10, 20, 30, 40, 50]:
        print(f"\n--- {n} ciudades ---")
        ciudades, distancias = generar_ciudades_con_distancias(n)

        # LP sin heurísticas
        tsp = TSP(ciudades, distancias, heuristics=[])
        ruta_lp = tsp.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=30, tee=False)

        # Vecino cercano (comparación)
        ruta_nn = nearest_neighbor(ciudades, distancias)
        dist_nn = calculate_path_distance(distancias, ruta_nn)
        print(f"  Distancia vecino cercano:  {dist_nn:.2f}")

        # Mostrar gráfica solo para 10 y 50 (opcional, descomenta si quieres todas)
        if n in [10, 50]:
            tsp.plotear_resultado(ruta_lp, n <= 20)


# ═══════════════════════════════════════════════════════════════════════════════
# CASO 2: Heurística de límites — 70 ciudades (con y sin)
# ═══════════════════════════════════════════════════════════════════════════════
def run_caso_2():
    print("\n" + "="*60)
    print("CASO 2: Heurística de límites — 70 ciudades (mipgap=0.2, límite=40s)")
    print("="*60)

    ciudades, distancias = generar_ciudades_con_distancias(70)

    print("\n--- CON heurística: limitar_funcion_objetivo ---")
    tsp_con = TSP(ciudades, distancias, heuristics=['limitar_funcion_objetivo'])
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap=0.2, time_limit=40, tee=True)
    tsp_con.plotear_resultado(ruta_con, False)

    print("\n--- SIN heurística ---")
    tsp_sin = TSP(ciudades, distancias, heuristics=[])
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap=0.2, time_limit=40, tee=True)
    tsp_sin.plotear_resultado(ruta_sin, False)


# ═══════════════════════════════════════════════════════════════════════════════
# CASO 3: Heurística vecinos cercanos — 100 ciudades (con y sin)
# ═══════════════════════════════════════════════════════════════════════════════
def run_caso_3():
    print("\n" + "="*60)
    print("CASO 3: Heurística vecinos cercanos — 100 ciudades (mipgap=0.05, límite=60s)")
    print("="*60)

    ciudades, distancias = generar_ciudades_con_distancias(100)

    print("\n--- CON heurística: vecino_cercano ---")
    tsp_con = TSP(ciudades, distancias, heuristics=['vecino_cercano'])
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=60, tee=True)
    tsp_con.plotear_resultado(ruta_con, False)

    print("\n--- SIN heurística ---")
    tsp_sin = TSP(ciudades, distancias, heuristics=[])
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap=0.05, time_limit=60, tee=True)
    tsp_sin.plotear_resultado(ruta_sin, False)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — Descomenta el caso que quieras correr
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    # run_referencia_vecino_cercano()
    # run_caso_1()
    # run_caso_2()
    run_caso_3()
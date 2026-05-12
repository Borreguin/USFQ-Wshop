import pyomo.environ as pyo
import re
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

from util import *
from util_nearest_neighbor import nearest_neighbor
# Funcionalidad anadida en el Taller 3 (seccion F del notebook P2.ipynb):
# 2-opt + deteccion de cruces (post-procesamiento) y cutting plane anti-cruces
# (cortes "dentro del modelo"). Se importa de forma defensiva para no romper
# escenarios donde Pyomo/GLPK no esten disponibles al cargar este modulo.
from util_two_opt import (
    two_opt_first_improvement,
    two_opt_best_improvement,
    contar_cruces,
)
try:
    from tsp_anti_cruces import tsp_anti_cruces_iterativo
except Exception:  # pragma: no cover - fallback si pyomo no esta instalado
    tsp_anti_cruces_iterativo = None
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


        # Resolver el modelo
        solver = pyo.SolverFactory('glpk')
        solver.options['mipgap'] = mipgap
        solver.options['tmlim'] = time_limit
        results = solver.solve(_model, tee=tee)

        execution_time = dt.datetime.now() - start_time
        print(f"Tiempo de ejecución: {delta_time_mm_ss(execution_time)}")
        self.print_min_max_distances()

        # Mostrar resultados
        if results.solver.termination_condition == pyo.TerminationCondition.optimal:
            print("Ruta óptima encontrada:")
        else:
            print("No se encontró una solución óptima, la siguiente es la mejor solución encontrada:")

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

    # ------------------------------------------------------------------
    # Funcionalidad anadida en el Taller 3 (seccion F)
    # ------------------------------------------------------------------
    def contar_cruces_en(self, ruta: List[str]) -> int:
        """Cuenta cuantos pares de aristas se cruzan en ``ruta``.

        Es un wrapper sobre :func:`util_two_opt.contar_cruces` que
        utiliza las ciudades almacenadas en la instancia.
        """
        return contar_cruces(self.ciudades, ruta)

    def aplicar_2opt(self, ruta: List[str], estrategia: str = "best"):
        """Aplica 2-opt como post-procesamiento sobre ``ruta``.

        Parametros
        ----------
        ruta : list
            Tour inicial (cerrado o abierto).
        estrategia : {'best', 'first'}
            'best' usa best-improvement; 'first' usa first-improvement.

        Retorna
        -------
        dict
            ``{'ruta', 'distancia', 'historial', 'iteraciones',
            'cruces_iniciales', 'cruces_finales'}``.
        """
        if estrategia not in ("best", "first"):
            raise ValueError("estrategia debe ser 'best' o 'first'")

        cruces_ini = contar_cruces(self.ciudades, ruta)
        if estrategia == "best":
            ruta_out, hist = two_opt_best_improvement(
                self.ciudades, self.distancias, ruta)
        else:
            ruta_out, hist = two_opt_first_improvement(
                self.ciudades, self.distancias, ruta)

        return {
            'ruta': ruta_out,
            'distancia': calculate_path_distance(self.distancias, ruta_out),
            'historial': hist,
            'iteraciones': len(hist),
            'cruces_iniciales': cruces_ini,
            'cruces_finales': contar_cruces(self.ciudades, ruta_out),
        }

def study_nearest_neighbor(n_cities):
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    ruta = nearest_neighbor(ciudades, distancias)
    plotear_ruta(ciudades, distancias, ruta, True)

def study_case_1():
    # tal vez un loop para probar 10, 20, 30, 40, 50 ciudades?
    n_cities = 50
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    heuristics = []
    mipgap = 0.05
    time_limit = 30
    tee = False
    tsp = TSP(ciudades, distancias, heuristics)
    ruta = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 70
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    # con heuristicas
    heuristics = ['limitar_funcion_objetivo']
    # sin heuristicas
    # heuristics = []
    tsp = TSP(ciudades, distancias, heuristics)
    mipgap = 0.2
    time_limit = 40
    tee = True
    ruta = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    tsp.plotear_resultado(ruta, False)

def study_case_3():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    # con heuristicas
    heuristics = ['vecino_cercano']
    # sin heuristicas
    # heuristics = []
    tsp = TSP(ciudades, distancias, heuristics)
    mipgap = 0.05
    time_limit = 60
    tee = True
    ruta = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    tsp.plotear_resultado(ruta, False)


# ----------------------------------------------------------------------
# Casos de estudio anadidos para la seccion F del Taller 3.
# ----------------------------------------------------------------------
def study_case_F_2opt(n_cities: int = 100):
    """Vecino mas cercano + 2-opt como post-procesamiento.

    Replica la "Aplicacion 1" de la seccion F del notebook P2.ipynb:
    se construye un tour con NN, se cuentan cruces, se aplican 2-opt
    First y Best Improvement y se compara distancia/cruces.
    """
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias, heuristics=[])

    ruta_nn = nearest_neighbor(ciudades, distancias)
    dist_nn = calculate_path_distance(distancias, ruta_nn)
    cruces_nn = tsp.contar_cruces_en(ruta_nn)
    print(f"NN (n={n_cities}): dist={dist_nn:.2f}  cruces={cruces_nn}")

    res_first = tsp.aplicar_2opt(ruta_nn, estrategia="first")
    res_best = tsp.aplicar_2opt(ruta_nn, estrategia="best")
    print(f"NN + 2-opt First : dist={res_first['distancia']:.2f}  "
          f"cruces={res_first['cruces_finales']}  "
          f"iter={res_first['iteraciones']}")
    print(f"NN + 2-opt Best  : dist={res_best['distancia']:.2f}  "
          f"cruces={res_best['cruces_finales']}  "
          f"iter={res_best['iteraciones']}")

    tsp.plotear_resultado(res_best['ruta'], mostrar_anotaciones=False)
    return {'nn': ruta_nn, 'first': res_first, 'best': res_best}


def study_case_F_anti_cruces(n_cities: int = 20, time_limit: int = 15,
                             max_iter: int = 10):
    """Cutting plane casero anti-cruces (heuristica DENTRO del modelo).

    Replica la implementacion de la opcion 3 del enunciado F: resuelve
    iterativamente un MTZ y agrega cortes ``x[a,b]+x[b,a]+x[c,d]+x[d,c] <= 1``
    por cada par de aristas que se cruzan, hasta convergencia o
    ``max_iter``.
    """
    if tsp_anti_cruces_iterativo is None:
        raise RuntimeError(
            "tsp_anti_cruces no esta disponible (probablemente Pyomo o GLPK "
            "no estan instalados en el entorno)."
        )
    res = tsp_anti_cruces_iterativo(
        n_cities=n_cities, time_limit=time_limit, max_iter=max_iter)
    print(f"Distancia final: {res['distancia']:.2f}  "
          f"convergio={res['convergio']}")
    plotear_ruta(res['ciudades'], res['distancias'], res['ruta'], False)
    return res


if __name__ == "__main__":
    print("Se ha colocado un límite de tiempo de 30 segundos para la ejecución del modelo.")
    # as reference, see nearest neighbor heuristic
    study_nearest_neighbor(100)
    # Solve the TSP problem
    # study_case_1()
    # study_case_2()
    study_case_3()
    # Casos anadidos en el Taller 3 (seccion F):
    # study_case_F_2opt(100)
    # study_case_F_anti_cruces(20)
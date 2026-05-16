print("[DEBUG] Ejecutando TSP.py desde:", __file__)
import pyomo.environ as pyo
import re
import sys, os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

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
        elif results.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit:
            print("\n[INFO] El solver alcanzó el límite de tiempo. Se muestra la mejor solución encontrada hasta el momento.")
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




    def plotear_resultado(
        self,
        ruta: List[str],
        mostrar_anotaciones: bool = True,
        titulo: str = "",
        guardar: bool = True,
        nombre_archivo: str = ""
    ):
        import matplotlib.pyplot as plt
        import os

        print(f"[DEBUG] Entrando a plotear_resultado con nombre_archivo={nombre_archivo}")
        plt.figure(figsize=(8, 6))

        # Coordenadas de todas las ciudades
        x_ciudades = [coord[0] for coord in self.ciudades.values()]
        y_ciudades = [coord[1] for coord in self.ciudades.values()]

        # Coordenadas de la ruta
        x_ruta = [self.ciudades[ciudad][0] for ciudad in ruta]
        y_ruta = [self.ciudades[ciudad][1] for ciudad in ruta]

        # Distancia total
        distancia = calculate_path_distance(self.distancias, ruta)

        # Graficar ciudades
        plt.scatter(x_ciudades, y_ciudades, color="blue", label="Ciudades")

        # Graficar ruta
        plt.plot(x_ruta, y_ruta, color="red", marker="o", label="Mejor Ruta")

        # Anotaciones
        if mostrar_anotaciones:
            for ciudad, (x, y) in self.ciudades.items():
                plt.text(x, y, ciudad, fontsize=8)

        # Título
        if titulo == "":
            titulo = f"({len(self.ciudades)}) Ciudades (Distancia: {distancia:.2f})"
        else:
            titulo = f"{titulo} | Distancia: {distancia:.2f}"

        plt.title(titulo)
        plt.xlabel("Coordenada X")
        plt.ylabel("Coordenada Y")
        plt.grid(True)
        plt.legend()

        # Guardar imagen SIEMPRE
        carpeta = os.path.join(current_dir, "images_P2")
        os.makedirs(carpeta, exist_ok=True)
        ruta_guardado = os.path.join(carpeta, nombre_archivo)
        print(f"[DEBUG] Guardando imagen en: {ruta_guardado}")
        plt.savefig(ruta_guardado, dpi=300, bbox_inches="tight")
        print(f"[DEBUG] Imagen guardada correctamente en: {ruta_guardado}")

        plt.show()
        plt.close()


def study_nearest_neighbor(n_cities):
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    ruta = nearest_neighbor(ciudades, distancias)
    plotear_ruta(ciudades, distancias, ruta, True)

def study_case_1():

    for n_cities in [10, 20, 30, 40, 50]:

        print("\n==========================")
        print(f"Comparando con {n_cities} ciudades")
        print("==========================")

        ciudades, distancias = generar_ciudades_con_distancias(n_cities)


        # 1. MODELO LP SIN HEURÍSTICA

        heuristics = []
        tsp = TSP(ciudades, distancias, heuristics)

        start_time = dt.datetime.now()

        ruta_lp = tsp.encontrar_la_ruta_mas_corta(
            mipgap=0.05,
            time_limit=30,
            tee=False
        )

        tiempo_lp = dt.datetime.now() - start_time
        distancia_lp = calculate_path_distance(distancias, ruta_lp)

        tsp.plotear_resultado(
            ruta_lp,
            False,
            titulo=f"LP sin heurística - {n_cities} ciudades",
            guardar=True,
            nombre_archivo=f"LP_sin_heuristica_{n_cities}.png"
        )


        # 2. HEURÍSTICA VECINO CERCANO

        start_time = dt.datetime.now()

        ruta_nn = nearest_neighbor(ciudades, distancias)

        tiempo_nn = dt.datetime.now() - start_time
        distancia_nn = calculate_path_distance(distancias, ruta_nn)

        tsp.plotear_resultado(
            ruta_nn,
            False,
            titulo=f"Heurística Vecino Cercano - {n_cities} ciudades",
            guardar=True,
            nombre_archivo=f"Heuristica_vecino_cercano_{n_cities}.png"
        )

   
        # RESULTADOS
       
        print("\nResultados:")

        print(
            f"LP sin heurística - "
            f"Tiempo: {delta_time_mm_ss(tiempo_lp)}, "
            f"Distancia: {distancia_lp}"
        )

        print(
            f"Heurística vecino cercano - "
            f"Tiempo: {delta_time_mm_ss(tiempo_nn)}, "
            f"Distancia: {distancia_nn}"
        )

def study_case_2():
    n_cities = 70
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    # con heuristicas
    heuristics_dict = {'con heuristica': ['limitar_funcion_objetivo'],
                       'sin heuristica': []
                       }
    # sin heuristicas
    # heuristics = []
    mipgap = 0.2
    time_limit = 40
    tee = True
    rutas = {}
    for heuristics in heuristics_dict.keys():
        print("\n==========================")
        print(f"Probando {heuristics}:\n")
        tsp = TSP(ciudades, distancias, heuristics_dict[heuristics])
        ruta = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
        rutas[heuristics] = ruta
        nombre_archivo = f"ruta_{n_cities}_ciudades_{heuristics.replace(' ', '_')}"
        tsp.plotear_resultado(ruta, False, nombre_archivo)
        print("\n==========================")
    print("\nComparando resultados:\n")
    for heuristics in heuristics_dict.keys():
        print(f"Ruta obtenida {heuristics}: {rutas[heuristics]}")
        print(f"Distancia total recorrida {heuristics}: {calculate_path_distance(distancias, rutas[heuristics])}\n")

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

def general_study_case(n_cities, heuristics, mipgap, time_limit, tee):
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias, heuristics)
    ruta = tsp.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    tsp.plotear_resultado(ruta, False)



# LITERAL D
# Comparación del modelo con y sin la heurística de vecinos cercanos para 100 ciudades
def study_case_3_literal_D():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)

    mipgap = 0.05
    time_limit = 180  # límite de tiempo 3 minutos
    tee = True

    print("\n[PARTE D] INICIO: Comparación del modelo con y sin la heurística de vecinos cercanos para 100 ciudades\n")
    print(f"Directorio actual de ejecución: {os.getcwd()}")
    print(f"Directorio esperado para imágenes: {os.path.join(current_dir, 'images_P2')}")

    print("\nCaso 3: Sin heurística de vecinos cercanos\n")
    heuristics_sin = []

    tsp_sin = TSP(ciudades, distancias, heuristics_sin)
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    distancia_sin = calculate_path_distance(distancias, ruta_sin)
    print("[DEBUG] Llamando a plotear_resultado para LP sin heurística...")
    tsp_sin.plotear_resultado(ruta_sin, False, titulo="LP sin heurística - 100 ciudades", guardar=True, nombre_archivo="LP_sin_heuristica_100.png")
    print("[DEBUG] Imagen sin heurística generada.")

    print("\nCaso 3: Con heurística de vecinos cercanos\n")
    heuristics_con = ['vecino_cercano']
    tsp_con = TSP(ciudades, distancias, heuristics_con)
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap, time_limit, tee)
    distancia_con = calculate_path_distance(distancias, ruta_con)
    print("[DEBUG] Llamando a plotear_resultado para LP con heurística vecino cercano...")
    tsp_con.plotear_resultado(ruta_con, False, titulo="LP con heurística vecino cercano - 100 ciudades", guardar=True, nombre_archivo="LP_con_vecino_cercano_100.png")
    print("[DEBUG] Imagen con heurística generada.")

    print("\n[PARTE D] FIN: Resultados de la comparación\n")
    print("Comparación de resultados:")
    print(f"Sin heurística: Distancia = {distancia_sin}")
    print(f"Con heurística vecino cercano: Distancia = {distancia_con}")
    print("\nExplicación:")
    print("La heurística de vecinos cercanos ayuda a guiar el modelo hacia soluciones más eficientes, reduciendo el espacio de búsqueda y, en muchos casos, obteniendo recorridos más cortos en menor tiempo. Sin embargo, su efectividad puede depender de la distribución de las ciudades y no garantiza siempre la mejor solución para todos los casos.")

study_case_3_literal_D()


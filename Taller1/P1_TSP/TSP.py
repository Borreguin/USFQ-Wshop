print("Script started.")
from typing import List
from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
print("Imports successful.")

class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias
        self.lista_ciudades = list(ciudades.keys())
        print("Lista de ciudades:", self.lista_ciudades)

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        gestor = pywrapcp.RoutingIndexManager(len(self.lista_ciudades), 1, 0)
        modelo = pywrapcp.RoutingModel(gestor)
        print(f"Gestor initialized with {len(self.lista_ciudades)} cities.")

        def distancia_callback(from_index, to_index):
            from_node = gestor.IndexToNode(from_index)
            to_node = gestor.IndexToNode(to_index)
            ciudad_from = self.lista_ciudades[from_node]
            ciudad_to = self.lista_ciudades[to_node]
            if (ciudad_from, ciudad_to) in self.distancias:
                return int(self.distancias[(ciudad_from, ciudad_to)])
            elif (ciudad_to, ciudad_from) in self.distancias:
                return int(self.distancias[(ciudad_to, ciudad_from)])
            else:
                raise KeyError(f"Distance between {ciudad_from} and {ciudad_to} not found.")

        transit_callback_index = modelo.RegisterTransitCallback(distancia_callback)
        modelo.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        parametros_busqueda = pywrapcp.DefaultRoutingSearchParameters()
        parametros_busqueda.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solucion = modelo.SolveWithParameters(parametros_busqueda)

        if not solucion:
            print("No se encontró solución")
            return []

        indice = modelo.Start(0)
        ruta_indices = []
        while not modelo.IsEnd(indice):
            nodo = gestor.IndexToNode(indice)
            ruta_indices.append(nodo)
            indice = solucion.Value(modelo.NextVar(indice))
        ruta_indices.append(ruta_indices[0])

        return [self.lista_ciudades[i] for i in ruta_indices] 


    def plotear_resultado(self, ruta: List[int], mostrar_anotaciones: bool = True):
        if not ruta:
            print("La ruta está vacía. No se puede plotear el resultado.")
            return
    
        #coordenadas_x = [self.ciudades[ciudad][0] for ciudad in ruta]
        #coordenadas_y = [self.ciudades[ciudad][1] for ciudad in ruta]

        #coordenadas_x.append(coordenadas_x[0])
        #coordenadas_y.append(coordenadas_y[0])
        
       # import matplotlib.pyplot as plt

        #plt.figure(figsize=(8, 6))
        #plt.plot(coordenadas_x, coordenadas_y, 'ro-', label='Ruta')

        #if mostrar_anotaciones:
          #  for i, ciudad in enumerate(ruta):
         #       plt.annotate(ciudad, (coordenadas_x[i], coordenadas_y[i]))

        #plt.title('Ruta más corta encontrada')
        #plt.xlabel('Coordenada X')
        #plt.ylabel('Coordenada Y')
        #plt.grid(True)
        #plt.legend()
        #plt.show()
        
        #nombres_ruta = [self.lista_ciudades[i] for i in ruta]
        #print("Ruta convertida a nombres:", nombres_ruta)
        print("Ruta recibida:", ruta)
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    print("study_case_1 started.")
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    print("Ciudades generadas:", ciudades)
    print("Distancias generadas:", distancias)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    print("Ruta encontrada:", ruta)
    if ruta:
        tsp.plotear_resultado(ruta)
    else:
        print("No se pudo encontrar una ruta.")

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta, True)


if __name__ == "__main__":
    study_case_2()

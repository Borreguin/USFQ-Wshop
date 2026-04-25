from typing import List
import random
from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias
        self.destinos = {}
        keys = list(distancias.keys())
        for ciudad in ciudades:
            if ciudad not in self.destinos:
                self.destinos[ciudad] = {}
            for key in keys:
                if ciudad == key[0]:
                    self.destinos[ciudad][key[1]] = distancias[key]
    
    def closest_city(self, city, visited_cities, include = False):
        min_distance = float('inf')
        closest_city = None
        for cities in self.destinos[city]:
            if (include or cities not in visited_cities) and self.destinos[city][cities] < min_distance:
                min_distance = self.destinos[city][cities]
                closest_city = cities
        return closest_city, min_distance

    def encontrar_la_ruta_mas_corta(self):
        print("Pensando...........")
        distances = []
        start_city = list(self.ciudades.keys())[random.randint(0, len(self.ciudades) - 1)]
        back_to_origin = False
        visited_cities = {start_city: True}
        path = [start_city]
        while not back_to_origin:
            closest_city, distance = self.closest_city(path[len(path) - 1], visited_cities, len(visited_cities) == len(self.ciudades) - 1)
            back_to_origin = closest_city == start_city
            distances.append(distance)
            path.append(closest_city)
            visited_cities[closest_city] = True
        return path

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)

def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = ciudades.keys()
    # ruta = tsp.encontrar_la_ruta_mas_corta()
    # tsp.plotear_resultado(ruta, False)


if __name__ == "__main__":
    # Solve the TSP problem
    study_case_1()
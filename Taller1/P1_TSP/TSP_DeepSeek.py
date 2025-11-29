from typing import List, Tuple
import itertools
import time

from util import plotear_ruta, generar_ciudades_con_distancias #Imporacion de las funciones del codigo 'util'


class TSP: 
    def __init__(self, ciudades, distancias): #TSP definido con sus atributos
        self.ciudades = ciudades
        self.distancias = distancias
        self.mejor_ruta = None
        self.mejor_distancia = float('inf')

    def calcular_distancia_ruta(self, ruta: List[str]) -> float: 
        """Calcula la distancia total de una ruta"""
        distancia_total = 0
        n = len(ruta)
        for i in range(n):
            ciudad_actual = ruta[i]
            ciudad_siguiente = ruta[(i + 1) % n]  # Para cerrar el ciclo
            distancia_total += self.distancias.get((ciudad_actual, ciudad_siguiente), 0)
        return distancia_total

    def encontrar_la_ruta_mas_corta_fuerza_bruta(self) -> Tuple[List[str], float]:
        """Resuelve TSP usando fuerza bruta (solo para n pequeños)"""
        ciudades_lista = list(self.ciudades.keys())
        mejor_ruta = None
        mejor_distancia = float('inf')
        
        # Generar todas las permutaciones posibles
        for permutacion in itertools.permutations(ciudades_lista[1:]):
            ruta = [ciudades_lista[0]] + list(permutacion)
            distancia = self.calcular_distancia_ruta(ruta)
            
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_ruta = ruta.copy()
        
        self.mejor_ruta = mejor_ruta
        self.mejor_distancia = mejor_distancia
        return mejor_ruta, mejor_distancia

    def encontrar_la_ruta_mas_corta_vecino_mas_cercano(self) -> Tuple[List[str], float]:
        """Algoritmo del vecino más cercano (aproximado)"""
        ciudades_lista = list(self.ciudades.keys())
        if not ciudades_lista:
            return [], 0
        
        ciudades_por_visitar = set(ciudades_lista)
        ruta = [ciudades_lista[0]]
        ciudades_por_visitar.remove(ciudades_lista[0])
        
        while ciudades_por_visitar:
            ciudad_actual = ruta[-1]
            ciudad_mas_cercana = None
            distancia_mas_cercana = float('inf')
            
            for ciudad in ciudades_por_visitar:
                distancia = self.distancias.get((ciudad_actual, ciudad), float('inf'))
                if distancia < distancia_mas_cercana:
                    distancia_mas_cercana = distancia
                    ciudad_mas_cercana = ciudad
            
            if ciudad_mas_cercana:
                ruta.append(ciudad_mas_cercana)
                ciudades_por_visitar.remove(ciudad_mas_cercana)
        
        distancia_total = self.calcular_distancia_ruta(ruta)
        self.mejor_ruta = ruta
        self.mejor_distancia = distancia_total
        return ruta, distancia_total

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        """Método principal que selecciona el algoritmo según el tamaño del problema"""
        n = len(self.ciudades)
        
        if n <= 10:
            print(f"Usando fuerza bruta para {n} ciudades...")
            ruta, distancia = self.encontrar_la_ruta_mas_corta_fuerza_bruta()
        else:
            print(f"Usando algoritmo del vecino más cercano para {n} ciudades...")
            ruta, distancia = self.encontrar_la_ruta_mas_corta_vecino_mas_cercano()
        
        print(f"Distancia total de la mejor ruta: {distancia:.2f}")
        return ruta

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    
    print("=== Caso de estudio 1 (10 ciudades) ===")
    print(f"Ciudades: {list(ciudades.keys())}")
    
    inicio = time.time()
    ruta = tsp.encontrar_la_ruta_mas_corta()
    fin = time.time()
    
    print(f"Mejor ruta encontrada: {ruta}")
    print(f"Tiempo de ejecución: {fin - inicio:.2f} segundos")
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    
    print("\n=== Caso de estudio 2 (100 ciudades) ===")
    
    inicio = time.time()
    ruta = tsp.encontrar_la_ruta_mas_corta()
    fin = time.time()
    
    print(f"Tiempo de ejecución: {fin - inicio:.2f} segundos")
    tsp.plotear_resultado(ruta, False)


if __name__ == "__main__":
    # Solve the TSP problem
    study_case_1()
    study_case_2()

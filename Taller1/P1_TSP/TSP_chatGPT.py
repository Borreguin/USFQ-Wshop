from typing import List, Tuple, Dict
import itertools

from util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades: Dict[str, Tuple[float, float]], distancias: Dict[Tuple[str, str], float]):
        self.ciudades = ciudades
        self.distancias = distancias

    def costo_ruta(self, ruta: List[str]) -> float:
        total = 0
        for i in range(len(ruta) - 1):
            total += self.distancias[(ruta[i], ruta[i+1])]
        total += self.distancias[(ruta[-1], ruta[0])]  # volver al inicio
        return total

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        ciudades_lista = list(self.ciudades.keys())
        ciudad_inicial = ciudades_lista[0]
        mejores_ciudades = ciudades_lista[1:]

        mejor_ruta = None
        mejor_costo = float('inf')

        for perm in itertools.permutations(mejores_ciudades):
            ruta = [ciudad_inicial] + list(perm)
            costo = self.costo_ruta(ruta)

            if costo < mejor_costo:
                mejor_costo = costo
                mejor_ruta = ruta

        return mejor_ruta

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        from util import plotear_ruta
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


# Integración con study_case_1 y study_case_2

def study_case_1():
    from util import generar_ciudades_con_distancias
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)

    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta)


def study_case_2():
    from util import generar_ciudades_con_distancias
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)

    # Para 100 ciudades, fuerza bruta es imposible → usar ruta aleatoria como placeholder
    ruta = list(ciudades.keys())
    tsp.plotear_resultado(ruta, mostrar_anotaciones=False)


if __name__ == "__main__":
    study_case_1()

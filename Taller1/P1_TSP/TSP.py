from typing import List

from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    def calcular_largo_ruta(self, ruta: List[str]) -> int:
        distancia_total = 0.0
        n = len(ruta)

        for i in range(n):
            ciudad1 = ruta[i]
            ciudad2 = ruta[(i + 1) % n] #La ultima ciudad va a ser la 1ra en la sig iteracion
            distancia_total += self.distancias[(ciudad1, ciudad2)]
        return distancia_total

    def encontrar_la_ruta_mas_corta(self) -> list:
        # Implementacion de 2-opt Heuristic
        ruta_actual = list(self.ciudades.keys())
        n = len(ruta_actual)
        improved = True

        while improved:
            improved = False
            mejor_distancia = self.calcular_largo_ruta(ruta_actual)

            for i in range(1, n - 1):  # 1er nodo
                for j in range(i + 1, n):  # Ultimo nodo
                    ruta_nueva = ruta_actual[:i] + ruta_actual[i:j + 1][::-1] + ruta_actual[j + 1:]
                    nueva_distancia = self.calcular_largo_ruta(ruta_nueva)

                    if nueva_distancia < mejor_distancia:
                        mejor_distancia = nueva_distancia
                        ruta_actual = ruta_nueva
                        improved = True

        return ruta_actual

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = ciudades.keys()
    print(f"Ruta: {ruta}")
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta, False)


if __name__ == "__main__":
    study_case_1()
    # study_case_2()
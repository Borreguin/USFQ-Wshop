from typing import List

from util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        ciudades = list(self.ciudades.keys())

        inicio = ciudades[0]
        ruta = [inicio]

        no_visitadas = set(ciudades)
        no_visitadas.remove(inicio)

        actual = inicio

        while no_visitadas:
            siguiente = min(
                no_visitadas,
                key=lambda ciudad: self.distancias[(actual, ciudad)]
            )
            ruta.append(siguiente)
            no_visitadas.remove(siguiente)
            actual = siguiente

        ruta.append(inicio)
        return ruta

    def calcular_distancia_total(self, ruta: List[str]) -> float:
        distancia_total = 0
        for i in range(len(ruta) - 1):
            distancia_total += self.distancias[(ruta[i], ruta[i + 1])]
        return distancia_total

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)

    ruta = tsp.encontrar_la_ruta_mas_corta()
    distancia = tsp.calcular_distancia_total(ruta)

    print("\n--- RESULTADOS STUDY CASE 1 ---")
    print("Mejor ruta encontrada:")
    print(" → ".join(ruta))
    print(f"Distancia total: {distancia:.2f}")

    tsp.plotear_resultado(ruta)


def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)

    ruta = tsp.encontrar_la_ruta_mas_corta()
    distancia = tsp.calcular_distancia_total(ruta)

    print("\n--- RESULTADOS STUDY CASE 2 ---")
    print("Mejor ruta encontrada (Nearest Neighbor):")
    print(" → ".join(ruta))
    print(f"Distancia total: {distancia:.2f}")

    tsp.plotear_resultado(ruta, mostrar_anotaciones=False)


if __name__ == "__main__":
    study_case_1()

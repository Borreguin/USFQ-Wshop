from typing import List

from util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    def encontrar_la_ruta_mas_corta(self):
        pass
        # implementación aquí
        # Si no hay ciudades, ruta vacía
        if not self.ciudades:
            return []

        # Lista de nombres de ciudades (A1, B3, etc.)
        ciudades = list(self.ciudades.keys())

        # Escogemos simplemente la primera como ciudad inicial
        ciudad_actual = ciudades[0]

        # Conjunto de ciudades que todavía no visitamos
        no_visitadas = set(ciudades)
        no_visitadas.remove(ciudad_actual)

        # La ruta va a ser una lista ordenada de nombres de ciudades
        ruta = [ciudad_actual]

        # Mientras queden ciudades por visitar
        while no_visitadas:
            # Elegir la ciudad no visitada más cercana a la ciudad_actual
            ciudad_siguiente = min(
                no_visitadas,
                key=lambda c: self.distancias[(ciudad_actual, c)]
            )

            ruta.append(ciudad_siguiente)
            no_visitadas.remove(ciudad_siguiente)
            ciudad_actual = ciudad_siguiente

        # IMPORTANTE: la función de ploteo ya cierra el ciclo (regresa al inicio)
        # añadiendo la primera ciudad al final, así que aquí solo devolvemos
        # el recorrido abierto.
        return ruta

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = ciudades.keys()
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta, False)


if __name__ == "__main__":
    # Solve the TSP problem
    study_case_1()
    study_case_2()
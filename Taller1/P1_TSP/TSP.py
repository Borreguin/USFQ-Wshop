from typing import List

from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    def encontrar_la_ruta_mas_corta(self):
        pass
        # implementación aquí

    def plotear_resultado(
            self,
            ruta: List[str],
            mostrar_anotaciones: bool = True,
            save_path: str = None
    ):
        """Visualiza la ruta encontrada y opcionalmente la guarda"""
        plotear_ruta(
            self.ciudades,
            ruta,
            mostrar_anotaciones,
            save_path
        )


def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()

    print(f"\nRuta óptima encontrada: {' → '.join(ruta)} → {ruta[0]}")
    print(f"Distancia total: {tsp.ultima_distancia:.2f} unidades")

    tsp.plotear_resultado(
        ruta,
        save_path="../images/tsp_10_ciudades.png" )


def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()

    print(f"\nRuta encontrada (primeras 10): {' → '.join(ruta[:10])} → ...")
    print(f"Distancia total: {tsp.ultima_distancia:.2f} unidades")

    tsp.plotear_resultado(
        ruta,
        mostrar_anotaciones=False,
        save_path="../images/tsp_100_ciudades.png"
    )


if __name__ == "__main__":
    # Solve the TSP problem
    study_case_1()
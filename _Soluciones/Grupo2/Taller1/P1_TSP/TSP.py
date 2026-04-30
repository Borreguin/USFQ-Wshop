import sys, os
# Agrega USFQ-Wshop al path cuando se corre directamente
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from typing import List
from matplotlib import pyplot as plt

from Taller1.P1_TSP.util import (
    plotear_ruta,
    generar_ciudades_con_distancias,
    calcular_distancia_ruta,
    animar_dos_fases,
)


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    # ------------------------------------------------------------------ #
    #  Algoritmo principal                                                 #
    # ------------------------------------------------------------------ #

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        """
        Estrategia en dos fases:
          1. Vecino más cercano  – construye una ruta greedy en O(n²)
          2. 2-opt               – mejora la ruta intercambiando aristas en O(n²) por iteración
        Retorna la lista ordenada de ciudades (ciclo cerrado implícito: último→primero).
        """
        ruta = self._vecino_mas_cercano()
        ruta = self._dos_opt(ruta)
        return ruta

    def resolver_con_animacion(self, intervalo_ms: int = 300,
                               mostrar_anotaciones: bool = True):
        """
        Igual que encontrar_la_ruta_mas_corta pero graba cada paso
        y muestra la animación al finalizar.
        """
        ruta, pasos_greedy = self._vecino_mas_cercano(guardar_pasos=True)
        ruta, pasos_opt = self._dos_opt(ruta, guardar_pasos=True)

        print(f"  Ciudades          : {len(self.ciudades)}")
        print(f"  Pasos greedy      : {len(pasos_greedy)}")
        print(f"  Pasos 2-opt       : {len(pasos_opt)}")
        print(f"  Distancia inicial : {calcular_distancia_ruta(self.ciudades, pasos_greedy[-1]):.2f}")
        print(f"  Distancia final   : {calcular_distancia_ruta(self.ciudades, ruta):.2f}")

        ani = animar_dos_fases(self.ciudades, pasos_greedy, pasos_opt,
                               intervalo_ms=intervalo_ms,
                               mostrar_anotaciones=mostrar_anotaciones)
        return ruta, ani

    # ------------------------------------------------------------------ #
    #  Fase 1 – Vecino más cercano (greedy constructivo)                  #
    # ------------------------------------------------------------------ #

    def _vecino_mas_cercano(self, ciudad_inicio: str = None, guardar_pasos: bool = False):
        ciudades = self.ciudades
        nombres = list(ciudades.keys())

        if ciudad_inicio is None:
            ciudad_inicio = nombres[0]

        visitadas = {ciudad_inicio}
        ruta = [ciudad_inicio]
        pasos = [ruta[:]]

        while len(ruta) < len(nombres):
            actual = ruta[-1]
            mejor_vecino = None
            mejor_dist = float('inf')

            for candidato in nombres:
                if candidato in visitadas:
                    continue
                d = self.distancias.get((actual, candidato),
                                        self.distancias.get((candidato, actual), float('inf')))
                if d < mejor_dist:
                    mejor_dist = d
                    mejor_vecino = candidato

            ruta.append(mejor_vecino)
            visitadas.add(mejor_vecino)

            if guardar_pasos:
                pasos.append(ruta[:])

        if guardar_pasos:
            return ruta, pasos
        return ruta

    # ------------------------------------------------------------------ #
    #  Fase 2 – 2-opt (mejora local)                                      #
    # ------------------------------------------------------------------ #

    def _dos_opt(self, ruta: List[str], guardar_pasos: bool = False):
        """
        Invierte segmentos de la ruta cuando el cruce elimina dos aristas costosas.
        Itera hasta no encontrar mejora (convergencia local).
        """
        ciudades = self.ciudades
        mejor = ruta[:]
        pasos = []
        mejoro = True

        while mejoro:
            mejoro = False
            n = len(mejor)
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Distancia antes del intercambio
                    d_antes = (
                        _dist(ciudades, mejor[i - 1], mejor[i]) +
                        _dist(ciudades, mejor[j], mejor[(j + 1) % n])
                    )
                    # Distancia después de invertir el segmento [i..j]
                    d_despues = (
                        _dist(ciudades, mejor[i - 1], mejor[j]) +
                        _dist(ciudades, mejor[i], mejor[(j + 1) % n])
                    )
                    if d_despues < d_antes - 1e-10:
                        mejor[i:j + 1] = mejor[i:j + 1][::-1]
                        mejoro = True
                        if guardar_pasos:
                            pasos.append(mejor[:])

        if guardar_pasos:
            if not pasos:           # si ya era óptimo localmente
                pasos.append(mejor[:])
            return mejor, pasos
        return mejor

    # ------------------------------------------------------------------ #
    #  Helpers de salida                                                   #
    # ------------------------------------------------------------------ #

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


# ------------------------------------------------------------------ #
#  Función auxiliar (módulo-level)                                    #
# ------------------------------------------------------------------ #

def _dist(ciudades, a, b):
    ax, ay = ciudades[a]
    bx, by = ciudades[b]
    return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


# ------------------------------------------------------------------ #
#  Casos de estudio                                                    #
# ------------------------------------------------------------------ #

def study_case_1():
    print("=== Caso 1: 10 ciudades ===")
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta, ani = tsp.resolver_con_animacion(intervalo_ms=500, mostrar_anotaciones=True)  # <- desempacar
    plt.show()  # <- mostrar antes de que se destruya
    return ruta, ani


def study_case_2():
    print("=== Caso 2: 100 ciudades ===")
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta, ani = tsp.resolver_con_animacion(intervalo_ms=80, mostrar_anotaciones=False)  # <- desempacar
    plt.show()  # <- mostrar antes de que se destruya
    return ruta, ani


if __name__ == "__main__":
    ruta, ani = study_case_1()  # <- guardar ani para que no se destruya

from typing import List, Tuple
import random

from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias

    def calcular_distancia_ruta(self, ruta: List[str]) -> float:
        """
        Calcula la distancia total de una ruta.

        Args:
            ruta: Lista de ciudades en orden

        Returns:
            float: Distancia total de la ruta
        """
        distancia_total = 0
        for i in range(len(ruta)):
            ciudad_actual = ruta[i]
            ciudad_siguiente = ruta[(i + 1) % len(ruta)]  # Ciclo: última ciudad -> primera ciudad
            distancia_total += self.distancias[(ciudad_actual, ciudad_siguiente)]
        return distancia_total

    def vecino_mas_cercano(self, ciudad_inicio: str = None) -> Tuple[List[str], float]:
        """
        Algoritmo del Vecino Más Cercano (Nearest Neighbor).

        DESCRIPCIÓN:
        - Algoritmo greedy que siempre elige la ciudad no visitada más cercana
        - Complejidad: O(n²)
        - Garantiza una solución, pero no siempre la óptima
        - Rápido y efectivo para problemas medianos

        VENTAJAS:
        - Simple de implementar
        - Tiempo de ejecución rápido
        - Buena aproximación inicial

        DESVENTAJAS:
        - No garantiza solución óptima
        - Sensible a la ciudad inicial

        Args:
            ciudad_inicio: Ciudad desde la que comenzar (si None, usa la primera)

        Returns:
            Tuple[List[str], float]: (ruta, distancia_total)
        """
        ciudades_list = list(self.ciudades.keys())

        if not ciudades_list:
            return [], 0

        # Usar ciudad especificada o la primera
        ciudad_actual = ciudad_inicio if ciudad_inicio else ciudades_list[0]
        ruta = [ciudad_actual]
        ciudades_no_visitadas = set(ciudades_list)
        ciudades_no_visitadas.remove(ciudad_actual)

        # Construir ruta visitando siempre la ciudad más cercana
        while ciudades_no_visitadas:
            ciudad_mas_cercana = min(
                ciudades_no_visitadas,
                key=lambda ciudad: self.distancias.get((ciudad_actual, ciudad), float('inf'))
            )
            ruta.append(ciudad_mas_cercana)
            ciudades_no_visitadas.remove(ciudad_mas_cercana)
            ciudad_actual = ciudad_mas_cercana

        distancia = self.calcular_distancia_ruta(ruta)
        return ruta, distancia

    def vecino_mas_cercano_mejorado(self) -> Tuple[List[str], float]:
        """
        Mejora del algoritmo del Vecino Más Cercano.

        DESCRIPCIÓN:
        - Ejecuta el algoritmo desde múltiples puntos iniciales
        - Selecciona el mejor resultado
        - Complejidad: O(n³)

        VENTAJAS:
        - Mejor solución que el simple
        - Sigue siendo relativamente rápido

        DESVENTAJAS:
        - Más lento que una única ejecución

        Returns:
            Tuple[List[str], float]: (mejor_ruta, mejor_distancia)
        """
        ciudades_list = list(self.ciudades.keys())
        mejor_ruta = None
        mejor_distancia = float('inf')

        # Probar desde cada ciudad como inicio
        for ciudad_inicio in ciudades_list:
            ruta, distancia = self.vecino_mas_cercano(ciudad_inicio)
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_ruta = ruta

        return mejor_ruta, mejor_distancia

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        """
        Encuentra la ruta más corta usando el Algoritmo del Vecino Más Cercano Mejorado.

        REPRESENTACIÓN DEL PROBLEMA TSP:
        1. ESTADO: Cada ruta es un estado, representado como una permutación de ciudades
        2. ESPACIO DE BÚSQUEDA: Todas las permutaciones posibles (n! permutaciones)
        3. OBJETIVO: Minimizar la distancia total del ciclo
        4. RESTRICCIONES:
           - Visitar cada ciudad exactamente una vez
           - Regresar a la ciudad inicial
           - Distancias simétricas

        COMPLEJIDAD:
        - Problema: NP-Completo
        - Para n ciudades: n! posibles rutas
        - Solución óptima requiere exploración exponencial

        Returns:
            List[str]: Lista de ciudades en orden de la ruta más corta
        """
        ruta, distancia = self.vecino_mas_cercano_mejorado()
        self.ultima_distancia = distancia  # Guardar para referencia
        return ruta

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        """Visualiza la ruta encontrada"""
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    """Caso de prueba 1: 10 ciudades"""
    print("=" * 80)
    print("ESTUDIO DE CASO 1: TSP con 10 ciudades")
    print("=" * 80)
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)

    print(f"\nCiudades generadas: {list(ciudades.keys())}")

    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()

    print(f"\nRuta óptima encontrada: {' → '.join(ruta)} → {ruta[0]}")
    print(f"Distancia total: {tsp.ultima_distancia:.2f} unidades")

    tsp.plotear_resultado(ruta)

def study_case_2():
    """Caso de prueba 2: 100 ciudades"""
    print("\n" + "=" * 80)
    print("ESTUDIO DE CASO 2: TSP con 100 ciudades")
    print("=" * 80)
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)

    print(f"\nNúmero de ciudades: {len(ciudades)}")
    print(f"Espacio de búsqueda: {n_cities}! permutaciones posibles")

    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()

    print(f"\nRuta encontrada (primeras 10): {' → '.join(ruta[:10])} → ...")
    print(f"Distancia total: {tsp.ultima_distancia:.2f} unidades")

    tsp.plotear_resultado(ruta, False)


if __name__ == "__main__":
    # Solve the TSP problem
    study_case_1()
    study_case_2()

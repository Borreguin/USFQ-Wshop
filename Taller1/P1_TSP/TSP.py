from typing import List

from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias
        
    def calcular_distancia_total(self, ruta: List[str]) -> float:
        """Calcula la distancia total de una ruta dada (ida y vuelta)."""
        total = 0
        num_ciudades = len(ruta)
        for i in range(num_ciudades):
            # Obtiene la ciudad actual y la siguiente (la última conecta con la primera)
            ciudad_actual = ruta[i]
            ciudad_siguiente = ruta[(i + 1) % num_ciudades]
            
            # Sumamos la distancia usando el diccionario pre-calculado
            total += self.distancias[(ciudad_actual, ciudad_siguiente)]
        return total
        
    def encontrar_la_ruta_mas_corta(self, temp_inicial=10000, tasa_enfriamiento=0.995):
        """
        Implementación del algoritmo de Recocido Simulado (Simulated Annealing).
        """
        # 1. Estado Inicial: Generamos una ruta aleatoria
        ruta_actual = list(self.ciudades.keys())
        random.shuffle(ruta_actual)
        
        distancia_actual = self.calcular_distancia_total(ruta_actual)

        # Guardamos la mejor ruta encontrada hasta el momento
        mejor_ruta = ruta_actual[:]
        mejor_distancia = distancia_actual

        temperatura = temp_inicial

        # 2. Bucle de Optimización
        while temperatura > 1:
            # --- Crear un vecino (Perturbación) ---
            # Elegimos dos índices al azar e intercambiamos las ciudades
            nueva_ruta = ruta_actual[:]
            i, j = random.sample(range(len(nueva_ruta)), 2)
            nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]

            nueva_distancia = self.calcular_distancia_total(nueva_ruta)

            # --- Criterio de Aceptación (Metropolis) ---
            # Si la nueva ruta es mejor (menor distancia), la aceptamos siempre.
            # Si es peor, la aceptamos con una probabilidad basada en la temperatura.
            delta = nueva_distancia - distancia_actual
            
            if delta < 0 or random.random() < math.exp(-delta / temperatura):
                ruta_actual = nueva_ruta
                distancia_actual = nueva_distancia

                # Actualizamos el récord global si encontramos algo mejor
                if distancia_actual < mejor_distancia:
                    mejor_ruta = ruta_actual[:]
                    mejor_distancia = distancia_actual
                    # Opcional: Imprimir progreso para ver cómo mejora
                    # print(f"Mejora encontrada: {mejor_distancia:.2f} a Temp: {temperatura:.2f}")

            # 3. Enfriamiento
            temperatura *= tasa_enfriamiento

        print(f"Algoritmo finalizado. Mejor distancia encontrada: {mejor_distancia:.2f}")
        return mejor_ruta

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)


def study_case_1():
    print("--- Caso de Estudio 1 (10 ciudades) ---")
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    
    # Ejecutamos el algoritmo
    ruta_optima = tsp.encontrar_la_ruta_mas_corta()
    
    tsp.plotear_resultado(ruta_optima)

def study_case_2():
    print("\n--- Caso de Estudio 2 (100 ciudades) ---")
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    
    # Para 100 ciudades, quizás queramos una temperatura inicial más alta o enfriamiento más lento
    ruta_optima = tsp.encontrar_la_ruta_mas_corta(temp_inicial=50000, tasa_enfriamiento=0.999)
    
    tsp.plotear_resultado(ruta_optima, mostrar_anotaciones=False)


if __name__ == "__main__":
    study_case_1()
    study_case_2()

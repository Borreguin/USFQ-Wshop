import sys
from util import imprimir_detalle_ruta
class TSPHeldKarp:
    def __init__(self, distancias):
        self.n = len(distancias)
        self.distancias = distancias
        # Máscara final: todos los bits en 1 (ej: 1111 para 4 ciudades)
        #<< desplaza bits a la izquierda. 1 << 4 = 10000
        #(1 << n) crea un número con un 1 seguido de n ceros. 10000 - 1 = 01111  = 1111
        #(1 << n) - 1 convierte eso en n unos.
        #Se usa para representar “todas las ciudades visitadas”.
        self.VISITED_ALL = (1 << self.n) - 1
        
        # Tabla de memorización: [mascara][ciudad_actual]
        self.memo = [[None for _ in range(self.n)] for _ in range(1 << self.n)]

    def resolver(self):
        # 1. Ejecutar el algoritmo recursivo para llenar la tabla memo
        # Empezamos en ciudad 0, máscara 1
        costo_minimo = self._buscar_camino(1, 0)
        
        # 2. Reconstruir el camino paso a paso usando la tabla llena
        ruta = self._reconstruir_ruta()
        return costo_minimo, ruta

    #Funcion recursiva con memorización
    # mascara es un número binario donde cada bit indica si una ciudad fue visitada.
    #mascara = 0110
    #      ||||
    #      |||└─ ciudad 0 visitada? 0 = no
    #      ||└── ciudad 1 visitada? 1 = sí
    #      |└─── ciudad 2 visitada? 1 = sí
    #      └──── ciudad 3 visitada? 0 = no

    def _buscar_camino(self, mascara, pos):
        # CASO BASE: Si ya visitamos todas (máscara llena)
        # El costo es la distancia de vuelta al origen (0)
        if mascara == self.VISITED_ALL:
            return self.distancias[pos][0]

        # Si ya calculamos este estado, lo devolvemos (Memorización)
        if self.memo[mascara][pos] is not None:
            return self.memo[mascara][pos]

        res = float('inf')

        # Intentamos ir a ciudades NO visitadas
        for next_city in range(self.n):
            #next_city = 2
            #1 << 2 = 0100
            #mascara = 0110
            #0110 & 0100 = 0100 ≠ 0  → ciudad 2 ya fue visitada
            if (mascara & (1 << next_city)) == 0: # Si bit es 0
                #Esto prende el bit de la ciudad siguiente.
                #mascara:       0110
                #1 << next:     0001
                #OR:            0111  <-- ahora la ciudad 0 está marcada como visitada
                nueva_mascara = mascara | (1 << next_city)
                
                # Costo = viaje a next + recursión desde next
                nuevo_costo = self.distancias[pos][next_city] + self._buscar_camino(nueva_mascara, next_city)
                
                # Actualizamos el mínimo
                if nuevo_costo < res:
                    res = nuevo_costo

        self.memo[mascara][pos] = res
        return res

    def _reconstruir_ruta(self):
        ruta = [0] # Empezamos en 0
        mascara = 1
        pos = 0
        
        # Iteramos hasta completar todas las ciudades
        while mascara != self.VISITED_ALL:
            mejor_siguiente = -1
            
            for next_city in range(self.n):
                # Solo miramos ciudades no visitadas
                if (mascara & (1 << next_city)) == 0:
                    
                    nueva_mascara = mascara | (1 << next_city)
                    costo_restante = 0
                    
                    # Si al ir a 'next_city' completamos todas las visitas,
                    # el costo restante es simplemente volver a 0 (distancias[next][0])
                    # No buscamos en 'memo' porque el caso base no se guarda ahí.
                    if nueva_mascara == self.VISITED_ALL:
                        costo_restante = self.distancias[next_city][0]
                    else:
                        # Si no hemos terminado, consultamos la tabla memo
                        if self.memo[nueva_mascara][next_city] is not None:
                            costo_restante = self.memo[nueva_mascara][next_city]
                        else:
                            continue # Si es None, no es un camino válido

                    # Calculamos el costo total de esta opción
                    costo_actual = self.distancias[pos][next_city] + costo_restante
                    
                    # Verificamos si coincide con el óptimo guardado en memo
                    # (Usamos una pequeña tolerancia 1e-9 por seguridad con flotantes)
                    if abs(costo_actual - self.memo[mascara][pos]) < 1e-9:
                        mejor_siguiente = next_city
                        break
            
            if mejor_siguiente != -1:
                ruta.append(mejor_siguiente)
                mascara = mascara | (1 << mejor_siguiente)
                pos = mejor_siguiente
            else:
                # Si no encuentra camino (no debería pasar), rompe para evitar loop infinito
                break
                
        ruta.append(0) # Agregar el retorno al origen
        return ruta



# --- EJECUCIÓN ---

# Matriz del ejemplo
grafo_distancias = [
    [0, 10, 15, 20], # Desde el nodo 0 a otros
    [10, 0, 35, 25], # Desde el nodo 1 a otros
    [15, 35, 0, 30], # Desde el nodo 2 a otros
    [20, 25, 30, 0] # Desde el nodo 3 a otros
]

tsp = TSPHeldKarp(grafo_distancias)
costo, ruta = tsp.resolver()

# Usamos la nueva función visual
imprimir_detalle_ruta(grafo_distancias, ruta, costo)
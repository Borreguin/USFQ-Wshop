







from collections import deque

# Paso 2: Función de Validación (Reglas de Seguridad)
def es_seguro(estado):
    granjero, lobo, cabra, col = estado
    
    # Si el lobo y la cabra están juntos, y el granjero no está con ellos: Peligro
    if lobo == cabra and granjero != lobo:
        return False
    # Si la cabra y la col están juntas, y el granjero no está con ellas: Peligro
    if cabra == col and granjero != cabra:
        return False
        
    return True

# Paso 3: Definir las Transiciones (Movimientos Posibles)
def obtener_sucesores(estado):
    sucesores = []
    granjero, lobo, cabra, col = estado
    
    # El granjero cruza a la orilla opuesta (de 0 a 1, o de 1 a 0)
    nuevo_granjero = 1 - granjero
    
    # 1. El granjero viaja solo
    sucesores.append((nuevo_granjero, lobo, cabra, col))
    
    # 2. El granjero viaja con el lobo (si están en la misma orilla)
    if granjero == lobo:
        sucesores.append((nuevo_granjero, 1 - lobo, cabra, col))
        
    # 3. El granjero viaja con la cabra
    if granjero == cabra:
        sucesores.append((nuevo_granjero, lobo, 1 - cabra, col))
        
    # 4. El granjero viaja con la col
    if granjero == col:
        sucesores.append((nuevo_granjero, lobo, cabra, 1 - col))
        
    # Retornamos solo los movimientos que no rompen las reglas
    return [sucesor for sucesor in sucesores if es_seguro(sucesor)]

# Paso 4: Algoritmo de Búsqueda (BFS)
def resolver_acertijo():
    estado_inicial = (0, 0, 0, 0)
    estado_objetivo = (1, 1, 1, 1)
    
    # La cola almacena tuplas de: (estado_actual, camino_hasta_ahora)
    cola = deque([(estado_inicial, [estado_inicial])])
    # Conjunto para no evaluar el mismo estado dos veces
    visitados = set()
    visitados.add(estado_inicial)
    
    while cola:
        estado_actual, camino = cola.popleft()
        
        # ¿Llegamos a la meta?
        if estado_actual == estado_objetivo:
            return camino
            
        # Evaluar los siguientes movimientos posibles
        for siguiente_estado in obtener_sucesores(estado_actual):
            if siguiente_estado not in visitados:
                visitados.add(siguiente_estado)
                # Añadir a la cola el nuevo estado y actualizar el historial del camino
                cola.append((siguiente_estado, camino + [siguiente_estado]))
                
    return None

# Paso 5: Visualización de Resultados
def imprimir_solucion(camino):
    if not camino:
        print("No se encontró solución.")
        return
        
    nombres = ['Granjero', 'Lobo', 'Cabra', 'Col']
    
    print(f"¡Solución encontrada en {len(camino) - 1} movimientos!\n")
    print("-" * 50)
    
    for i, estado in enumerate(camino):
        orilla_izq = [nombres[j] for j in range(4) if estado[j] == 0]
        orilla_der = [nombres[j] for j in range(4) if estado[j] == 1]
        
        texto_izq = ", ".join(orilla_izq) if orilla_izq else "Ninguno"
        texto_der = ", ".join(orilla_der) if orilla_der else "Ninguno"
        
        print(f"Paso {i}:")
        print(f"  Orilla Inicial : [{texto_izq}]")
        print(f"  ~~~~~~~~ RÍO ~~~~~~~~ ")
        print(f"  Orilla Destino : [{texto_der}]")
        print("-" * 50)

# Ejecutar el programa
if __name__ == "__main__":
    camino_solucion = resolver_acertijo()
    imprimir_solucion(camino_solucion)
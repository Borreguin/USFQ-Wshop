import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# --- 1. Definición del Problema y las Restricciones ---

def estado_es_seguro(estado):
    """Verifica si un estado es seguro (no hay depredación)."""
    g, l, c, r = estado

    # Si el granjero NO está con el lobo y la cabra, deben estar separados.
    # OJO: Si el granjero y la cabra están juntos (g==c), son seguros.
    # Si el granjero NO está con ellos (g!=l y g!=c), deben estar separados (l!=c).
    if l == c and g != l:
        return False  # Lobo se come a la cabra

    # Si el granjero NO está con la cabra y la col, deben estar separados.
    if c == r and g != c:
        return False  # Cabra se come la col
        
    return True

# Posibles transiciones:
# 0: Cruza solo
# 1: Cruza con el Lobo
# 2: Cruza con la Cabra
# 3: Cruza con la Col
TRANSICIONES = [0, 1, 2, 3] # Representa el índice del ítem que acompaña al granjero (0=solo)


# --- 2. Búsqueda de la Solución (BFS) ---

def resolver_acertijo():
    """Implementa el algoritmo BFS para encontrar el camino de la solución."""
    
    # Estado inicial: (Granjero, Lobo, Cabra, Col) -> (1, 1, 1, 1) Orilla inicial
    inicio = (1, 1, 1, 1)
    # Estado objetivo: (0, 0, 0, 0) Orilla final
    objetivo = (0, 0, 0, 0)

    # Inicialización de BFS
    cola = deque([[inicio]])  # Cola de caminos a explorar
    visitados = {inicio}      # Conjunto de estados ya visitados
    
    # Grafo para la visualización
    G = nx.DiGraph()
    G.add_node(inicio)

    while cola:
        camino_actual = cola.popleft()
        estado_actual = camino_actual[-1]

        if estado_actual == objetivo:
            # ¡Solución encontrada!
            return camino_actual, G

        # El granjero cambia de orilla:
        # Si está en 1 (orilla inicial), va a 0 (orilla final).
        # Si está en 0 (orilla final), va a 1 (orilla inicial).
        nueva_orilla_granjero = 1 - estado_actual[0]

        # Iterar sobre las posibles transiciones
        for t in TRANSICIONES:
            # Nuevo estado tentativo (mutable)
            nuevo_estado_lista = list(estado_actual)
            
            # El granjero siempre cambia de orilla
            nuevo_estado_lista[0] = nueva_orilla_granjero
            
            # Si el granjero lleva un ítem (t > 0)
            if t > 0:
                # El ítem debe estar en la misma orilla que el granjero para cruzar
                if estado_actual[t] == estado_actual[0]:
                    # El ítem se mueve a la nueva orilla
                    nuevo_estado_lista[t] = nueva_orilla_granjero
                else:
                    # El ítem no está con el granjero, no puede moverse en esta transición
                    continue

            nuevo_estado = tuple(nuevo_estado_lista)
            
            # Verificar seguridad y si es un estado nuevo
            if estado_es_seguro(nuevo_estado) and nuevo_estado not in visitados:
                visitados.add(nuevo_estado)
                
                # Extender el camino y agregarlo a la cola
                nuevo_camino = camino_actual + [nuevo_estado]
                cola.append(nuevo_camino)
                
                # Agregar arista al grafo para la visualización
                G.add_edge(estado_actual, nuevo_estado)

    return None, G # No se encontró solución

# Obtener la solución y el grafo
solucion_camino, grafo_estados = resolver_acertijo()


# --- 3. Visualización de los Resultados ---

def formatear_estado(estado_tupla):
    """Convierte la tupla de estado a una cadena legible para el grafo."""
    nombres = ["G", "L", "C", "R"] # Granero, Lobo, Cabra, Col
    orilla_in, orilla_fin = [], []
    
    for i, pos in enumerate(estado_tupla):
        if pos == 1:
            orilla_in.append(nombres[i])
        else:
            orilla_fin.append(nombres[i])
            
    # Formato: "Orilla IN: [G, L] | Orilla OUT: [C, R]"
    return f'IN: [{", ".join(orilla_in)}] | OUT: [{", ".join(orilla_fin)}]'

def visualizar_solucion(camino, grafo):
    """Dibuja el grafo de estados, resaltando el camino de la solución."""
    
    posiciones = nx.spring_layout(grafo, seed=42) # Posicionamiento de nodos
    
    # Mapear estados (tuplas) a cadenas legibles para la visualización
    etiquetas_nodos = {nodo: formatear_estado(nodo) for nodo in grafo.nodes}
    
    # 1. Dibujar el grafo completo
    plt.figure(figsize=(16, 10))
    nx.draw_networkx_nodes(grafo, posiciones, node_color='lightblue', node_size=2500)
    nx.draw_networkx_labels(grafo, posiciones, etiquetas_nodos, font_size=8)
    nx.draw_networkx_edges(grafo, posiciones, edge_color='gray', arrows=True, arrowsize=20, alpha=0.5)

    if camino:
        # 2. Resaltar el camino de la solución
        aristas_solucion = [(camino[i], camino[i+1]) for i in range(len(camino) - 1)]
        nodos_solucion = set(camino)
        
        # Resaltar nodos de la solución
        nx.draw_networkx_nodes(grafo, posiciones, nodelist=list(nodos_solucion), node_color='lightgreen', node_size=3000)

        # Resaltar aristas de la solución
        nx.draw_networkx_edges(grafo, posiciones, edgelist=aristas_solucion, edge_color='red', width=2.5, arrows=True, arrowstyle='->', arrowsize=30)
        
        plt.title('Acertijo del Granjero y el Bote: Grafo de Estados y Solución (BFS)', fontsize=16)
        
        print("\n¡SOLUCIÓN ENCONTRADA!")
        print(f"El camino más corto requiere {len(camino) - 1} movimientos:")
        
        for i, estado in enumerate(camino):
            if i == 0:
                print(f"Paso {i}: INICIO -> {formatear_estado(estado)}")
            else:
                estado_anterior = camino[i-1]
                # Determinar el ítem que se movió para el paso
                movimiento = "Solo"
                if estado[1] != estado_anterior[1]: movimiento = "Lobo"
                elif estado[2] != estado_anterior[2]: movimiento = "Cabra"
                elif estado[3] != estado_anterior[3]: movimiento = "Col"

                print(f"Paso {i}: Cruza con el **{movimiento}** -> {formatear_estado(estado)}")

    else:
        plt.title('Acertijo del Granjero y el Bote: Grafo de Estados (Sin Solución Encontrada)', fontsize=16)
        print("\n❌ No se encontró una solución para el problema.")

    plt.axis('off')
    plt.show() # Muestra la visualización gráfica
    
# Ejecutar la visualización (si se encontró el camino)
if solucion_camino:
    visualizar_solucion(solucion_camino, grafo_estados)
else:
    visualizar_solucion(None, grafo_estados)


if __name__ == '__main__':
    print("Implementa el código aquí")
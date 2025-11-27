import matplotlib.pyplot as plt
import networkx as nx

# ----------------------------------------------------
# 1) Función recursiva: Generar movimientos
# ----------------------------------------------------
def hanoi(n, origen, auxiliar, destino, movimientos):
    """
    Genera la secuencia óptima de movimientos para la Torre de Hanoi.
    Cada movimiento es una tupla: (origen, destino)
    """
    if n == 1:
        movimientos.append((origen, destino))
    else:
        hanoi(n-1, origen, destino, auxiliar, movimientos)
        movimientos.append((origen, destino))
        hanoi(n-1, auxiliar, origen, destino, movimientos)

# ----------------------------------------------------
# 2) Convertir torres en un estado tipo tupla
# ----------------------------------------------------
def estado_a_tupla(torres_dict):
    """
    Convierte las torres en una tupla para usar como nodo en el grafo.
    Formato: (tuple(A), tuple(B), tuple(C))
    """
    return (
        tuple(torres_dict['A']),
        tuple(torres_dict['B']),
        tuple(torres_dict['C'])
    )

# ----------------------------------------------------
# 3) Generar estados completos según los movimientos
# ----------------------------------------------------
def generar_estados(n_discos, movimientos):
    """
    Simula los movimientos para obtener todos los estados del sistema.
    """
    # Estado inicial: todos los discos en A
    torres = {
        'A': list(range(n_discos, 0, -1)),  # disco más grande al fondo
        'B': [],
        'C': []
    }

    estados = [estado_a_tupla(torres)]  # guardar estado inicial

    # Aplicar cada movimiento
    for (orig, dest) in movimientos:
        disco = torres[orig].pop()   # remover disco
        torres[dest].append(disco)   # colocar disco
        estados.append(estado_a_tupla(torres))

    return estados

# ----------------------------------------------------
# 4) Graficar grafo del camino solución
# ----------------------------------------------------
def graficar_grafo_estados(estados):
    """
    Construye un grafo dirigido usando los estados como nodos.
    Cada arista conecta un estado con el siguiente.
    """
    G = nx.DiGraph()

    # Crear aristas estado_i → estado_{i+1}
    edges = [(estados[i], estados[i+1]) for i in range(len(estados)-1)]
    G.add_edges_from(edges)

    # Layout para dibujar el grafo
    plt.figure(figsize=(12, 7))
    pos = nx.spring_layout(G, seed=42)  # posición de nodos

    nx.draw_networkx(
        G, pos,
        with_labels=True,
        node_size=1200,
        font_size=7,
        node_color="lightblue",
        arrows=True
    )

    plt.title("Camino óptimo en la Torre de Hanoi (grafo de estados)")
    plt.axis("off")
    plt.show()

# ----------------------------------------------------
# 5) Función principal: Resolver + imprimir + graficar
# ----------------------------------------------------
def ejecutar_hanoi(n_discos=3):

    # 1. Resolver recursivamente
    movimientos = []
    hanoi(n_discos, 'A', 'B', 'C', movimientos)

    print(f"\nTotal de movimientos: {len(movimientos)} = 2^{n_discos} - 1\n")
    print("Secuencia de movimientos:")
    for i, (orig, dest) in enumerate(movimientos, 1):
        print(f"  {i}. {orig} → {dest}")

    # 2. Generar todos los estados
    estados = generar_estados(n_discos, movimientos)

    # 3. Graficar grafo del camino solución
    graficar_grafo_estados(estados)


if __name__ == '__main__':
    ejecutar_hanoi(n_discos=3) # cambiar si se requieren mas o menos discos
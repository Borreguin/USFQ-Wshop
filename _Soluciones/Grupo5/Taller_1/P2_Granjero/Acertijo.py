"""
Literal B - Acertijo del granjero y el bote

Este programa resuelve el problema clásico del granjero, el lobo,
la cabra y la col usando búsqueda en anchura (BFS).

Representación del problema:
- Cada estado se representa como una tupla:
  (granjero, lobo, cabra, col)

- 0 significa que el elemento está en la orilla izquierda.
- 1 significa que el elemento está en la orilla derecha.

Ejemplo:
(0, 0, 0, 0) significa que todos están en la orilla izquierda.
(1, 1, 1, 1) significa que todos cruzaron a la orilla derecha.

La búsqueda BFS permite encontrar una solución válida con el menor
número de movimientos posibles.
"""

from collections import deque
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================

# Esta línea identifica automáticamente la carpeta donde está este archivo.
# En tu caso será: Grupo5/P2_Granjero
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Todos los archivos generados se guardarán en la misma carpeta P2_Granjero.
OUTPUT_DIR = BASE_DIR


# ============================================================
# 2. DEFINICIÓN DEL PROBLEMA
# ============================================================

# Elementos del problema.
ITEMS = ["Granjero", "Lobo", "Cabra", "Col"]

# Estado inicial: todos están en la orilla izquierda.
START = (0, 0, 0, 0)

# Estado objetivo: todos deben llegar a la orilla derecha.
GOAL = (1, 1, 1, 1)


# ============================================================
# 3. VALIDACIÓN DE ESTADOS
# ============================================================

def is_valid(state):
    """
    Evalúa si un estado es seguro.

    Un estado NO es válido cuando:
    1. El lobo queda solo con la cabra sin el granjero.
    2. La cabra queda sola con la col sin el granjero.

    Parámetro:
    state: tupla con la ubicación de cada elemento.

    Retorna:
    True si el estado es seguro.
    False si el estado viola alguna regla.
    """

    g, w, c, v = state

    # Caso peligroso 1:
    # Si el lobo y la cabra están en la misma orilla,
    # pero el granjero no está con ellos, el lobo se come a la cabra.
    if w == c and g != w:
        return False

    # Caso peligroso 2:
    # Si la cabra y la col están en la misma orilla,
    # pero el granjero no está con ellas, la cabra se come la col.
    if c == v and g != c:
        return False

    return True


def action_name(item, direction):
    """
    Genera el texto descriptivo de cada movimiento.

    item:
    - None: el granjero cruza solo.
    - 1: cruza con el lobo.
    - 2: cruza con la cabra.
    - 3: cruza con la col.

    direction:
    - → indica movimiento hacia la derecha.
    - ← indica movimiento hacia la izquierda.
    """

    if item is None:
        return f"Granjero cruza solo {direction}"

    return f"Granjero cruza con {ITEMS[item]} {direction}"


# ============================================================
# 4. GENERACIÓN DE MOVIMIENTOS POSIBLES
# ============================================================

def successors(state):
    """
    Genera todos los estados posibles a partir del estado actual.

    La barca siempre debe ser manejada por el granjero.
    Por eso, en cada movimiento, el granjero cambia de orilla.

    El granjero puede:
    - cruzar solo
    - cruzar con el lobo
    - cruzar con la cabra
    - cruzar con la col

    Solo se aceptan los movimientos que generan estados válidos.
    """

    g, w, c, v = state
    possible_moves = []

    # Opciones de traslado:
    # None = granjero solo
    # 1 = lobo
    # 2 = cabra
    # 3 = col
    for item in [None, 1, 2, 3]:

        # Se copia el estado actual para modificarlo.
        new_state = list(state)

        # El granjero siempre cambia de orilla.
        new_state[0] = 1 - g

        # Si el granjero lleva un elemento,
        # ese elemento debe estar en la misma orilla que él.
        if item is not None:
            if state[item] != g:
                continue

            # El elemento transportado cambia de orilla.
            new_state[item] = 1 - state[item]

        # Convertimos la lista nuevamente a tupla.
        new_state = tuple(new_state)

        # Solo guardamos el movimiento si no rompe las reglas del problema.
        if is_valid(new_state):
            direction = "→" if new_state[0] == 1 else "←"
            possible_moves.append((new_state, action_name(item, direction)))

    return possible_moves


# ============================================================
# 5. ALGORITMO BFS
# ============================================================

def bfs():
    """
    Aplica búsqueda en anchura (BFS).

    BFS explora primero los caminos más cortos.
    Por eso es adecuado para este problema, ya que permite encontrar
    una solución con el menor número de movimientos.

    Retorna:
    - path: lista de estados desde el inicio hasta el objetivo.
    - actions: lista de acciones realizadas.
    """

    queue = deque()
    queue.append((START, [START], ["Inicio"]))

    visited = {START}

    while queue:
        state, path, actions = queue.popleft()

        # Si llegamos al objetivo, devolvemos la solución.
        if state == GOAL:
            return path, actions

        # Generamos los siguientes estados posibles.
        for next_state, action in successors(state):

            # Evitamos repetir estados ya visitados.
            if next_state not in visited:
                visited.add(next_state)
                queue.append(
                    (
                        next_state,
                        path + [next_state],
                        actions + [action]
                    )
                )

    return None, None


# ============================================================
# 6. FUNCIONES AUXILIARES PARA MOSTRAR ESTADOS
# ============================================================

def state_text(state):
    """
    Convierte un estado numérico en texto legible.

    Ejemplo:
    (0, 1, 0, 1)
    Orilla izquierda: Granjero, Cabra
    Orilla derecha: Lobo, Col
    """

    left = []
    right = []

    for i, value in enumerate(state):
        if value == 0:
            left.append(ITEMS[i])
        else:
            right.append(ITEMS[i])

    return left, right


def print_solution(path, actions):
    """
    Imprime la solución en consola.
    """

    print("\nSOLUCIÓN DEL ACERTIJO DEL GRANJERO Y EL BOTE")
    print("=" * 70)
    print(f"Solución encontrada en {len(path) - 1} movimientos.\n")

    for i, state in enumerate(path):
        left, right = state_text(state)

        print(f"Paso {i}: {actions[i]}")
        print(f"  Orilla izquierda: {left if left else 'Vacía'}")
        print(f"  Orilla derecha:   {right if right else 'Vacía'}")
        print("-" * 70)


def save_solution_txt(path, actions):
    """
    Guarda la solución en un archivo TXT dentro de P2_Granjero.
    Este archivo sirve como evidencia para el taller.
    """

    output_path = os.path.join(OUTPUT_DIR, "solucion_granjero.txt")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("SOLUCIÓN DEL ACERTIJO DEL GRANJERO Y EL BOTE\n")
        file.write("=" * 70 + "\n")
        file.write(f"Solución encontrada en {len(path) - 1} movimientos.\n\n")

        for i, state in enumerate(path):
            left, right = state_text(state)

            file.write(f"Paso {i}: {actions[i]}\n")
            file.write(f"  Estado numérico: {state}\n")
            file.write(f"  Orilla izquierda: {left if left else 'Vacía'}\n")
            file.write(f"  Orilla derecha:   {right if right else 'Vacía'}\n")
            file.write("-" * 70 + "\n")

    print(f"Archivo de solución guardado en: {output_path}")


# ============================================================
# 7. VISUALIZACIÓN DE LA SECUENCIA DE PASOS
# ============================================================

def draw_state(ax, state, title):
    """
    Dibuja visualmente un estado específico.

    Muestra:
    - orilla izquierda
    - río
    - orilla derecha
    - ubicación del granjero, lobo, cabra y col
    - ubicación de la barca
    """

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(title, fontsize=9)

    # Dibujo de las orillas.
    ax.add_patch(mpatches.Rectangle((0, 0), 4.2, 6, color="#d8f3dc"))
    ax.add_patch(mpatches.Rectangle((5.8, 0), 4.2, 6, color="#d8f3dc"))

    # Dibujo del río.
    ax.add_patch(mpatches.Rectangle((4.2, 0), 1.6, 6, color="#90e0ef"))
    ax.text(5, 3, "RÍO", ha="center", va="center", fontsize=10, fontweight="bold")

    # Letras usadas como íconos simples.
    icons = {
        "Granjero": "G",
        "Lobo": "L",
        "Cabra": "C",
        "Col": "V"
    }

    # Posiciones visuales en cada orilla.
    left_positions = [(1, 5), (1, 4), (1, 3), (1, 2)]
    right_positions = [(8.5, 5), (8.5, 4), (8.5, 3), (8.5, 2)]

    # Ubicación de cada elemento.
    for i, item in enumerate(ITEMS):
        side = state[i]
        x, y = left_positions[i] if side == 0 else right_positions[i]

        ax.text(
            x,
            y,
            f"{icons[item]} - {item}",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="black")
        )

    # La barca siempre está junto al granjero.
    boat_x = 3.5 if state[0] == 0 else 6.1
    ax.text(boat_x, 1, "BARCA", fontsize=8, fontweight="bold")


def visualize_steps(path, actions):
    """
    Crea una imagen con todos los pasos de la solución.
    La imagen se guarda dentro de P2_Granjero.
    """

    n = len(path)
    cols = 4
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 3))
    fig.suptitle(
        "Secuencia de solución - Acertijo del granjero",
        fontsize=14,
        fontweight="bold"
    )

    axes = axes.flatten()

    for i, state in enumerate(path):
        draw_state(axes[i], state, f"Paso {i}\n{actions[i]}")

    for j in range(len(path), len(axes)):
        axes[j].axis("off")

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "farmer_steps.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Imagen de pasos guardada en: {output_path}")


# ============================================================
# 8. VISUALIZACIÓN DEL GRAFO DE ESTADOS
# ============================================================

def short_label(state):
    """
    Genera etiquetas cortas para cada nodo del grafo.

    I = orilla izquierda
    D = orilla derecha

    Ejemplo:
    I: G,C
    D: L,V
    """

    left, right = state_text(state)

    left_code = ",".join([x[0] for x in left]) if left else "∅"
    right_code = ",".join([x[0] for x in right]) if right else "∅"

    return f"I: {left_code}\nD: {right_code}"


def build_graph():
    """
    Construye el grafo completo de estados válidos.

    Cada nodo representa un estado.
    Cada flecha representa un movimiento posible.
    """

    G = nx.DiGraph()
    queue = deque([START])
    visited = {START}

    while queue:
        state = queue.popleft()
        G.add_node(state)

        for next_state, action in successors(state):
            G.add_edge(state, next_state, label=action)

            if next_state not in visited:
                visited.add(next_state)
                queue.append(next_state)

    return G


def visualize_graph(path):
    """
    Dibuja el grafo de estados.

    Colores:
    - Verde: estado inicial.
    - Rojo: estado objetivo.
    - Azul: estados que forman parte de la solución.
    - Gris: otros estados válidos explorados.
    - Naranja: camino solución.
    """

    G = build_graph()
    path_edges = list(zip(path[:-1], path[1:]))

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(14, 9))
    plt.title(
        "Grafo de estados - Acertijo del granjero",
        fontsize=14,
        fontweight="bold"
    )

    node_colors = []

    for node in G.nodes:
        if node == START:
            node_colors.append("#4caf50")
        elif node == GOAL:
            node_colors.append("#f44336")
        elif node in path:
            node_colors.append("#2196f3")
        else:
            node_colors.append("#b0bec5")

    edge_colors = []
    edge_widths = []

    for edge in G.edges:
        if edge in path_edges:
            edge_colors.append("#ff5722")
            edge_widths.append(3)
        else:
            edge_colors.append("#cfd8dc")
            edge_widths.append(1)

    labels = {node: short_label(node) for node in G.nodes}
    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color=edge_colors,
        width=edge_widths,
        arrows=True,
        arrowsize=15,
        connectionstyle="arc3,rad=0.15"
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    legend = [
        mpatches.Patch(color="#4caf50", label="Estado inicial"),
        mpatches.Patch(color="#f44336", label="Estado objetivo"),
        mpatches.Patch(color="#2196f3", label="Estados de la solución"),
        mpatches.Patch(color="#b0bec5", label="Otros estados válidos"),
        mpatches.Patch(color="#ff5722", label="Camino solución")
    ]

    plt.legend(handles=legend, loc="upper left", fontsize=9)
    plt.axis("off")

    output_path = os.path.join(OUTPUT_DIR, "farmer_graph.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Imagen del grafo guardada en: {output_path}")


# ============================================================
# 9. FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """
    Ejecuta todo el flujo del programa:

    1. Resuelve el acertijo con BFS.
    2. Imprime la solución en consola.
    3. Guarda la solución en un archivo TXT.
    4. Genera imagen de la secuencia de pasos.
    5. Genera imagen del grafo de estados.
    """

    path, actions = bfs()

    if path is None:
        print("No se encontró solución.")
        return

    print_solution(path, actions)
    save_solution_txt(path, actions)
    visualize_steps(path, actions)
    visualize_graph(path)


if __name__ == "__main__":
    main()
"""
Literal B - Acertijo del granjero y el bote

Este programa resuelve el problema clasico del granjero, el lobo,
la cabra y la col usando busqueda en anchura (BFS).

Representacion del problema:
- Cada estado se representa como una tupla:
  (granjero, lobo, cabra, col)

- 0 significa que el elemento esta en la orilla izquierda.
- 1 significa que el elemento esta en la orilla derecha.

Ejemplo:
(0, 0, 0, 0) significa que todos estan en la orilla izquierda.
(1, 1, 1, 1) significa que todos cruzaron a la orilla derecha.

La busqueda BFS permite encontrar una solucion valida con el menor
numero de movimientos posibles.
"""

import sys
import os
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


# ============================================================
# 1. CONFIGURACION DE RUTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR


# ============================================================
# 2. DEFINICION DEL PROBLEMA
# ============================================================

ITEMS = ["Granjero", "Lobo", "Cabra", "Col"]
START = (0, 0, 0, 0)
GOAL  = (1, 1, 1, 1)


# ============================================================
# 3. VALIDACION DE ESTADOS
# ============================================================

def is_valid(state):
    """
    Evalua si un estado es seguro.
    Un estado NO es valido cuando:
    1. El lobo queda solo con la cabra sin el granjero.
    2. La cabra queda sola con la col sin el granjero.
    """
    g, w, c, v = state
    if w == c and g != w:
        return False
    if c == v and g != c:
        return False
    return True


def action_name(item, direction):
    """
    Genera el texto descriptivo de cada movimiento.
    item: None=solo, 1=lobo, 2=cabra, 3=col.
    direction: '->' o '<-'.
    """
    if item is None:
        return f"Granjero cruza solo {direction}"
    return f"Granjero cruza con {ITEMS[item]} {direction}"


# ============================================================
# 4. GENERACION DE MOVIMIENTOS POSIBLES
# ============================================================

def successors(state):
    """
    Genera todos los estados posibles a partir del estado actual.
    El granjero puede cruzar solo o llevar un item de su mismo lado.
    Solo se aceptan movimientos que generan estados validos.
    """
    g, w, c, v = state
    possible_moves = []

    for item in [None, 1, 2, 3]:
        new_state = list(state)
        new_state[0] = 1 - g

        if item is not None:
            if state[item] != g:
                continue
            new_state[item] = 1 - state[item]

        new_state = tuple(new_state)

        if is_valid(new_state):
            direction = "->" if new_state[0] == 1 else "<-"
            possible_moves.append((new_state, action_name(item, direction)))

    return possible_moves


# ============================================================
# 5. ALGORITMO BFS
# ============================================================

def bfs():
    """
    Aplica busqueda en anchura (BFS).
    BFS explora primero los caminos mas cortos, garantizando
    encontrar la solucion con el menor numero de movimientos.
    Retorna path (lista de estados) y actions (lista de acciones).
    """
    queue = deque()
    queue.append((START, [START], ["Inicio"]))
    visited = {START}

    while queue:
        state, path, actions = queue.popleft()

        if state == GOAL:
            return path, actions

        for next_state, action in successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((
                    next_state,
                    path + [next_state],
                    actions + [action]
                ))

    return None, None


# ============================================================
# 6. FUNCIONES AUXILIARES
# ============================================================

def state_text(state):
    """Convierte un estado numerico en listas de items por orilla."""
    left, right = [], []
    for i, value in enumerate(state):
        if value == 0:
            left.append(ITEMS[i])
        else:
            right.append(ITEMS[i])
    return left, right


def print_solution(path, actions):
    """Imprime la solucion en consola."""
    print("\nSOLUCION DEL ACERTIJO DEL GRANJERO Y EL BOTE")
    print("=" * 70)
    print(f"Solucion encontrada en {len(path) - 1} movimientos.\n")
    for i, state in enumerate(path):
        left, right = state_text(state)
        print(f"Paso {i}: {actions[i]}")
        print(f"  Estado numerico: {state}")
        print(f"  Orilla izquierda: {left if left else 'Vacia'}")
        print(f"  Orilla derecha:   {right if right else 'Vacia'}")
        print("-" * 70)


def save_solution_txt(path, actions):
    """Guarda la solucion en un archivo TXT."""
    output_path = os.path.join(OUTPUT_DIR, "solucion_granjero.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("SOLUCION DEL ACERTIJO DEL GRANJERO Y EL BOTE\n")
        f.write("=" * 70 + "\n")
        f.write(f"Solucion encontrada en {len(path) - 1} movimientos.\n\n")
        for i, state in enumerate(path):
            left, right = state_text(state)
            f.write(f"Paso {i}: {actions[i]}\n")
            f.write(f"  Estado numerico: {state}\n")
            f.write(f"  Orilla izquierda: {left if left else 'Vacia'}\n")
            f.write(f"  Orilla derecha:   {right if right else 'Vacia'}\n")
            f.write("-" * 70 + "\n")
    print(f"Archivo de solucion guardado en: {output_path}")


# ============================================================
# 7. VISUALIZACION DE LA SECUENCIA DE PASOS
# ============================================================

def draw_state(ax, state, title):
    """
    Dibuja visualmente un estado especifico mostrando las dos orillas,
    el rio, la posicion de cada elemento y la barca.
    """
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(title, fontsize=9)

    # Orillas
    ax.add_patch(mpatches.Rectangle((0, 0), 4.2, 6, color="#d8f3dc"))
    ax.add_patch(mpatches.Rectangle((5.8, 0), 4.2, 6, color="#d8f3dc"))

    # Rio
    ax.add_patch(mpatches.Rectangle((4.2, 0), 1.6, 6, color="#90e0ef"))
    ax.text(5, 3, "RIO", ha="center", va="center",
            fontsize=10, fontweight="bold")

    icons = {"Granjero": "G", "Lobo": "L", "Cabra": "C", "Col": "V"}
    left_positions  = [(1, 5), (1, 4), (1, 3), (1, 2)]
    right_positions = [(8.5, 5), (8.5, 4), (8.5, 3), (8.5, 2)]

    for i, item in enumerate(ITEMS):
        side = state[i]
        x, y = left_positions[i] if side == 0 else right_positions[i]
        ax.text(x, y, f"{icons[item]} - {item}", fontsize=9,
                bbox=dict(boxstyle="round", facecolor="white",
                          edgecolor="black"))

    # Barca junto al granjero
    boat_x = 3.5 if state[0] == 0 else 6.1
    ax.text(boat_x, 1, "BARCA", fontsize=8, fontweight="bold")


def visualize_steps(path, actions, save_dir=None):
    """
    Crea una imagen con todos los pasos de la solucion.
    Si save_dir es dado, guarda como granjero_01_pasos.png (headless).
    """
    n    = len(path)
    cols = 4
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 3))
    fig.suptitle("Secuencia de solucion - Acertijo del granjero",
                 fontsize=14, fontweight="bold")

    axes_flat = axes.flatten()
    for i, state in enumerate(path):
        draw_state(axes_flat[i], state, f"Paso {i}\n{actions[i]}")
    for j in range(len(path), len(axes_flat)):
        axes_flat[j].axis("off")

    plt.tight_layout()

    out_dir  = save_dir if save_dir else OUTPUT_DIR
    out_path = os.path.join(out_dir, "granjero_01_pasos.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"  Imagen de pasos guardada en: {out_path}")
    if save_dir is None:
        plt.show()
    plt.close()


# ============================================================
# 8. VISUALIZACION DEL GRAFO DE ESTADOS
# ============================================================

def short_label(state):
    """Genera etiquetas cortas I:/D: para cada nodo del grafo."""
    left, right = state_text(state)
    left_code  = ",".join([x[0] for x in left])  if left  else "Ø"
    right_code = ",".join([x[0] for x in right]) if right else "Ø"
    return f"I: {left_code}\nD: {right_code}"


def build_graph():
    """Construye el grafo completo de estados validos."""
    G       = nx.DiGraph()
    queue   = deque([START])
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


def visualize_graph(path, save_dir=None):
    """
    Dibuja el grafo de estados con la ruta optima resaltada.
    Si save_dir es dado, guarda como granjero_02_grafo.png (headless).
    Colores: verde=inicio, rojo=objetivo, azul=solucion, gris=otros.
    """
    G          = build_graph()
    path_edges = list(zip(path[:-1], path[1:]))
    pos        = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(14, 9))
    plt.title("Grafo de estados - Acertijo del granjero",
              fontsize=14, fontweight="bold")

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

    edge_colors, edge_widths = [], []
    for edge in G.edges:
        if edge in path_edges:
            edge_colors.append("#ff5722")
            edge_widths.append(3)
        else:
            edge_colors.append("#cfd8dc")
            edge_widths.append(1)

    labels      = {node: short_label(node) for node in G.nodes}
    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                           width=edge_widths, arrows=True,
                           arrowsize=15,
                           connectionstyle="arc3,rad=0.15")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    legend = [
        mpatches.Patch(color="#4caf50", label="Estado inicial"),
        mpatches.Patch(color="#f44336", label="Estado objetivo"),
        mpatches.Patch(color="#2196f3", label="Estados de la solucion"),
        mpatches.Patch(color="#b0bec5", label="Otros estados validos"),
        mpatches.Patch(color="#ff5722", label="Camino solucion"),
    ]
    plt.legend(handles=legend, loc="upper left", fontsize=9)
    plt.axis("off")

    out_dir  = save_dir if save_dir else OUTPUT_DIR
    out_path = os.path.join(out_dir, "granjero_02_grafo.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"  Imagen del grafo guardada en: {out_path}")
    if save_dir is None:
        plt.show()
    plt.close()


# ============================================================
# 9. FUNCION PRINCIPAL
# ============================================================

def main(save_dir=None):
    """
    Ejecuta el flujo completo:
    1. Resuelve el acertijo con BFS.
    2. Imprime la solucion en consola.
    3. Guarda la solucion en un archivo TXT.
    4. Genera imagen de la secuencia de pasos.
    5. Genera imagen del grafo de estados.
    """
    path, actions = bfs()

    if path is None:
        print("No se encontro solucion.")
        return

    print_solution(path, actions)
    save_solution_txt(path, actions)
    visualize_steps(path, actions, save_dir=save_dir)
    visualize_graph(path, save_dir=save_dir)


if __name__ == "__main__":
    _save = sys.argv[1] if len(sys.argv) > 1 else None
    main(save_dir=_save)

from collections import deque

# Definición de los elementos y las orillas
FARMER, WOLF, GOAT, CABBAGE = 'F', 'W', 'G', 'C'
LEFT, RIGHT = 0, 1

# Un estado se representará como una tupla:
# (posición_granjero, posición_lobo, posición_cabra, posición_col)
# donde 0 = orilla izquierda, 1 = orilla derecha

# Estado inicial: todos en la orilla izquierda
initial_state = (LEFT, LEFT, LEFT, LEFT)

# Estado objetivo: todos en la orilla derecha
goal_state = (RIGHT, RIGHT, RIGHT, RIGHT)

def is_valid_state(state):
    f_pos, w_pos, g_pos, c_pos = state

    # Si el lobo y la cabra están solos en una orilla (sin el granjero)
    if w_pos == g_pos and w_pos != f_pos:
        return False
    # Si la cabra y la col están solas en una orilla (sin el granjero)
    if g_pos == c_pos and g_pos != f_pos:
        return False
    return True

def get_next_states(current_state):
    f_pos, w_pos, g_pos, c_pos = current_state
    next_states = []

    # Posición de la otra orilla
    other_bank = 1 - f_pos

    # Movimientos posibles:
    # 1. Granjero cruza solo
    next_f_alone_state = (other_bank, w_pos, g_pos, c_pos)
    if is_valid_state(next_f_alone_state):
        next_states.append((next_f_alone_state, 'granjero solo'))

    # 2. Granjero cruza con el lobo (si están en la misma orilla)
    if f_pos == w_pos:
        next_fw_state = (other_bank, other_bank, g_pos, c_pos)
        if is_valid_state(next_fw_state):
            next_states.append((next_fw_state, 'granjero con lobo'))

    # 3. Granjero cruza con la cabra (si están en la misma orilla)
    if f_pos == g_pos:
        next_fg_state = (other_bank, w_pos, other_bank, c_pos)
        if is_valid_state(next_fg_state):
            next_states.append((next_fg_state, 'granjero con cabra'))

    # 4. Granjero cruza con la col (si están en la misma orilla)
    if f_pos == c_pos:
        next_fc_state = (other_bank, w_pos, g_pos, other_bank)
        if is_valid_state(next_fc_state):
            next_states.append((next_fc_state, 'granjero con col'))

    return next_states

def solve_farmer_riddle():
    queue = deque()
    queue.append((initial_state, []))  # (estado_actual, camino_hasta_aqui)

    visited = set()
    visited.add(initial_state)

    while queue:
        current_state, path = queue.popleft()

        if current_state == goal_state:
            return path

        for next_state, move_description in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                new_path = path + [(move_description, current_state, next_state)]
                queue.append((next_state, new_path))
    return None

def state_to_string(state):
    f, w, g, c = state
    left_bank = []
    right_bank = []

    if f == LEFT: left_bank.append(FARMER)
    else: right_bank.append(FARMER)

    if w == LEFT: left_bank.append(WOLF)
    else: right_bank.append(WOLF)

    if g == LEFT: left_bank.append(GOAT)
    else: right_bank.append(GOAT)

    if c == LEFT: left_bank.append(CABBAGE)
    else: right_bank.append(CABBAGE)

    return f"Orilla Izquierda: {', '.join(sorted(left_bank)) if left_bank else 'vacía'} | Orilla Derecha: {', '.join(sorted(right_bank)) if right_bank else 'vacía'}"






import networkx as nx
import matplotlib.pyplot as plt

def state_to_short_string(state):
    f, w, g, c = state
    left_items = []
    right_items = []

    if f == LEFT: left_items.append(FARMER)
    else: right_items.append(FARMER)

    if w == LEFT: left_items.append(WOLF)
    else: right_items.append(WOLF)

    if g == LEFT: left_items.append(GOAT)
    else: right_items.append(GOAT)

    if c == LEFT: left_items.append(CABBAGE)
    else: right_items.append(CABBAGE)

    return f"L: {''.join(sorted(left_items))}|R: {''.join(sorted(right_items))}"

def build_state_graph():
    G = nx.DiGraph() # Grafo dirigido
    queue = deque()
    queue.append(initial_state)

    visited_nodes = set()
    visited_nodes.add(initial_state)

    # Para almacenar todos los estados y sus conexiones
    all_states_and_transitions = []

    while queue:
        current = queue.popleft()

        # Agrega el estado actual como nodo si no existe
        if current not in G:
            G.add_node(current)

        for next_s, move_desc in get_next_states(current):
            all_states_and_transitions.append((current, next_s, move_desc))
            if next_s not in visited_nodes:
                visited_nodes.add(next_s)
                queue.append(next_s)

    # Una vez que tenemos todos los nodos y transiciones, agregamos los nodos y aristas al grafo
    for state in visited_nodes:
        G.add_node(state)

    for u, v, desc in all_states_and_transitions:
        G.add_edge(u, v, label=desc)

    return G





if __name__ == '__main__':
    solution_path = solve_farmer_riddle()

    if solution_path:
        print("\n¡Solución encontrada!\n")
        print(f"Estado Inicial: {state_to_string(initial_state)}")
        for i, (move_desc, prev_state, current_state) in enumerate(solution_path):
            print(f"\n--- Paso {i+1}: El {move_desc} ---")
            print(f"Antes: {state_to_string(prev_state)}")
            print(f"Después: {state_to_string(current_state)}")
        print(f"\nEstado Final: {state_to_string(goal_state)}")
    else:
        print("No se encontró solución.")
    # Construir el grafo
    state_graph = build_state_graph()

    # Preparar para la visualización
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(state_graph, k=0.8, iterations=50) # Layout para el grafo

    # Mapeo de estados a nombres cortos para la visualización
    node_labels = {state: state_to_short_string(state) for state in state_graph.nodes()}

    # Colores para los nodos
    node_colors = ['lightblue'] * len(state_graph.nodes())
    color_map = {node: 'lightblue' for node in state_graph.nodes()}

    # Resaltar el estado inicial y el objetivo
    color_map[initial_state] = 'green'
    color_map[goal_state] = 'red'

    # Dibujar las aristas generales (con flechas) - sin arrowsize explícito
    nx.draw_networkx_edges(state_graph, pos, edge_color='gray', alpha=0.5, style='dashed', arrows=True)


    # Resaltar la ruta de la solución
    solution_states = [initial_state] + [s_tuple for _, _, s_tuple in solution_path]

    solution_edges = []
    for i in range(len(solution_states) - 1):
        u = solution_states[i]
        v = solution_states[i+1]
        if state_graph.has_edge(u, v):
            solution_edges.append((u, v))
        # Asegurarse de que los nodos de la solución también estén coloreados
        color_map[u] = 'orange'
        color_map[v] = 'orange'

    # Dibujar las aristas de la solución (por encima de las generales, pero con flechas menos prominentes)
    nx.draw_networkx_edges(state_graph, pos, edgelist=solution_edges, edge_color='blue', alpha=0.9, arrows=True)


    # Dibujar los nodos
    nx.draw_networkx_nodes(state_graph, pos, node_color=[color_map[node] for node in state_graph.nodes()], node_size=3000, alpha=0.9)

    # Dibujar las etiquetas de los nodos
    nx.draw_networkx_labels(state_graph, pos, labels=node_labels, font_size=8, font_weight='bold')


    plt.title("Grafo de Estados del Acertijo del Granjero, Lobo, Cabra y Col", size=15)
    plt.axis('off') # Ocultar los ejes
    plt.show()

"""
El acertijo del granjero y el bote
Representación: búsqueda BFS en espacio de estados
Visualización: grafo de transiciones + secuencia de pasos
Estado: (lado_granjero, lado_lobo, lado_cabra, lado_col)  0=izq, 1=der
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import deque

# ── Modelo del problema ──────────────────────────────────────────────────────

ITEMS = ["Granjero", "Lobo", "Cabra", "Col"]
START = (0, 0, 0, 0)   # todos en orilla izquierda
GOAL  = (1, 1, 1, 1)   # todos en orilla derecha


def is_valid(state):
    g, w, c, v = state
    # Lobo se come la cabra sin granjero
    if w == c and g != w:
        return False
    # Cabra come la col sin granjero
    if c == v and g != c:
        return False
    return True


def successors(state):
    g, w, c, v = state
    results = []
    # Granjero cruza solo
    new_g = 1 - g
    for item in range(4):  # 0=nadie, 1=lobo, 2=cabra, 3=col
        s = list(state)
        s[0] = new_g
        if item > 0 and s[item] == g:   # lleva el ítem si está en su mismo lado
            s[item] = new_g
        elif item > 0:
            continue
        ns = tuple(s)
        if is_valid(ns):
            results.append((ns, item))
    return results


def bfs():
    queue = deque()
    queue.append((START, [START], ["Inicio"]))
    visited = {START}
    all_states = {START: []}   # state -> list of (parent, action)

    while queue:
        state, path, actions = queue.popleft()
        if state == GOAL:
            return path, actions, all_states
        for ns, item in successors(state):
            if ns not in visited:
                visited.add(ns)
                all_states[ns] = (state, item)
                queue.append((ns, path + [ns], actions + [_action_name(state, ns, item)]))
    return None, None, all_states


def _action_name(prev, curr, item):
    direction = "→" if curr[0] == 1 else "←"
    carry = ITEMS[item] if item > 0 else "solo"
    return f"Granjero {direction} ({carry})"


# ── Construcción del grafo completo de estados ───────────────────────────────

def build_full_graph():
    G = nx.DiGraph()
    visited = set()
    queue = deque([START])
    visited.add(START)
    while queue:
        state = queue.popleft()
        G.add_node(state)
        for ns, item in successors(state):
            G.add_edge(state, ns, action=ITEMS[item] if item else "solo")
            if ns not in visited:
                visited.add(ns)
                queue.append(ns)
    return G


def state_label(state):
    g, w, c, v = state
    left  = [ITEMS[i] for i, s in enumerate(state) if s == 0]
    right = [ITEMS[i] for i, s in enumerate(state) if s == 1]
    return f"I:{','.join([x[0] for x in left]) or '∅'}\nD:{','.join([x[0] for x in right]) or '∅'}"


# ── Visualización ─────────────────────────────────────────────────────────────

def draw_side(ax, state, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_facecolor("#e8f4fc")
    ax.set_title(title, fontsize=9)
    ax.axis("off")

    # Río
    river = mpatches.FancyBboxPatch((4.5, 0), 1, 6, boxstyle="round,pad=0.1",
                                     facecolor="#7ec8e3", edgecolor="none")
    ax.add_patch(river)
    ax.text(5, 3, "RÍO", ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    icons = {"Granjero": "👨‍🌾", "Lobo": "🐺", "Cabra": "🐐", "Col": "🥬"}
    positions_left  = [(1, 4.5), (1, 3), (1, 1.5), (2.5, 3)]
    positions_right = [(8, 4.5), (8, 3), (8, 1.5), (6.5, 3)]

    g, w, c, v = state
    items = [("Granjero", g), ("Lobo", w), ("Cabra", c), ("Col", v)]
    for idx, (name, side) in enumerate(items):
        pos = positions_left[idx] if side == 0 else positions_right[idx]
        ax.text(pos[0], pos[1], icons[name], fontsize=18, ha="center", va="center")
        ax.text(pos[0], pos[1] - 0.6, name, fontsize=7, ha="center", va="center")

    # Barca
    barca_x = 3.2 if g == 0 else 6.8
    boat = mpatches.FancyBboxPatch((barca_x - 0.5, 2.6), 1, 0.4,
                                    boxstyle="round,pad=0.05", facecolor="#f0c060", edgecolor="brown")
    ax.add_patch(boat)
    ax.text(barca_x, 2.8, "🚣", fontsize=10, ha="center", va="center")


def main():
    path, actions, _ = bfs()
    if path is None:
        print("Sin solución")
        return

    print(f"\nSolución encontrada en {len(path)-1} pasos:\n")
    for i, (state, action) in enumerate(zip(path, actions)):
        g, w, c, v = state
        print(f"  Paso {i:2d} | {action:30s} | Granjero={'Der' if g else 'Izq'} | "
              f"Lobo={'Der' if w else 'Izq'} | Cabra={'Der' if c else 'Izq'} | Col={'Der' if v else 'Izq'}")

    # ── Panel de pasos ──────────────────────────────────────────────────────
    n = len(path)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    fig1, axes = plt.subplots(rows, cols, figsize=(cols * 3.5, rows * 3))
    fig1.suptitle("Acertijo del Granjero – Secuencia de Pasos (BFS)", fontsize=13, fontweight="bold")
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
    for i, state in enumerate(path):
        draw_side(axes[i], state, f"Paso {i}\n{actions[i]}" if i < len(actions) else f"Paso {i}")
    for i in range(len(path), len(axes)):
        axes[i].axis("off")
    plt.tight_layout()

    # ── Grafo de transiciones ───────────────────────────────────────────────
    G = build_full_graph()
    path_edges = list(zip(path[:-1], path[1:]))

    fig2, ax2 = plt.subplots(figsize=(14, 9))
    fig2.suptitle("Grafo de Estados – Acertijo del Granjero", fontsize=13, fontweight="bold")

    pos = nx.spring_layout(G, seed=42, k=2.5)
    labels = {s: state_label(s) for s in G.nodes()}

    node_colors = []
    for node in G.nodes():
        if node == START:
            node_colors.append("#4caf50")
        elif node == GOAL:
            node_colors.append("#f44336")
        elif node in path:
            node_colors.append("#2196f3")
        else:
            node_colors.append("#b0bec5")

    edge_colors = ["#ff5722" if e in path_edges else "#cfd8dc" for e in G.edges()]
    edge_widths = [3.0 if e in path_edges else 0.8 for e in G.edges()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800, ax=ax2)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=6, ax=ax2)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                           arrows=True, arrowsize=15, ax=ax2,
                           connectionstyle="arc3,rad=0.15")
    edge_labels = nx.get_edge_attributes(G, "action")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, ax=ax2)

    legend = [
        mpatches.Patch(color="#4caf50", label="Estado inicial"),
        mpatches.Patch(color="#f44336", label="Estado objetivo"),
        mpatches.Patch(color="#2196f3", label="En la solución"),
        mpatches.Patch(color="#b0bec5", label="Estado explorado"),
    ]
    ax2.legend(handles=legend, loc="upper left", fontsize=9)
    ax2.axis("off")
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()

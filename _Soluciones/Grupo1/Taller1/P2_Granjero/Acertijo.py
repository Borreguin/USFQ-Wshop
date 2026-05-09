from collections import deque
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from textwrap import wrap
import matplotlib.pyplot as plt

State = tuple[int, int, int, int]

ITEMS = (
    (1, "Lobo"),
    (2, "Cabra"),
    (3, "Col"),
)

START: State = (0, 0, 0, 0)
GOAL: State = (1, 1, 1, 1)


@dataclass(frozen=True)
class Step:
    state: State
    action: str


def is_safe(state: State) -> bool:
    """Return True when no unsafe pair is left alone without the farmer."""
    farmer, wolf, goat, cabbage = state
    if wolf == goat != farmer:
        return False
    if goat == cabbage != farmer:
        return False
    return True


def format_bank(state: State, side: int) -> str:
    names = ["Granjero"] if state[0] == side else []
    for index, label in ITEMS:
        if state[index] == side:
            names.append(label)
    return ", ".join(names) if names else "-"


def describe_state(state: State) -> str:
    return f"Izquierda: {format_bank(state, 0)} | Derecha: {format_bank(state, 1)}"


def move_description(item_index: int | None, destination: int) -> str:
    side_name = "derecha" if destination == 1 else "izquierda"
    if item_index is None:
        return f"El granjero cruza solo hacia la {side_name}"
    item_name = dict(ITEMS)[item_index]
    return f"El granjero lleva a {item_name.lower()} hacia la {side_name}"


def generate_moves(state: State):
    farmer_side = state[0]
    destination = 1 - farmer_side

    next_state = list(state)
    next_state[0] = destination
    candidate = tuple(next_state)
    if is_safe(candidate):
        yield candidate, move_description(None, destination)

    for item_index, _ in ITEMS:
        if state[item_index] != farmer_side:
            continue
        next_state = list(state)
        next_state[0] = destination
        next_state[item_index] = destination
        candidate = tuple(next_state)
        if is_safe(candidate):
            yield candidate, move_description(item_index, destination)


def build_state_graph() -> dict[State, list[tuple[State, str]]]:
    graph: dict[State, list[tuple[State, str]]] = {}
    for state in product((0, 1), repeat=4):
        if not is_safe(state):
            continue
        graph[state] = list(generate_moves(state))
    return graph


def build_exploration_tree(
    graph: dict[State, list[tuple[State, str]]]
) -> dict[State, list[tuple[State, str]]]:
    tree: dict[State, list[tuple[State, str]]] = {state: [] for state in graph}
    visited: set[State] = {START}
    seen_links: set[frozenset[State]] = set()
    queue = deque([START])

    while queue:
        current = queue.popleft()
        for next_state, action in graph[current]:
            link = frozenset((current, next_state))
            if link in seen_links:
                continue
            seen_links.add(link)
            tree[current].append((next_state, action))
            if next_state in visited:
                continue
            visited.add(next_state)
            queue.append(next_state)

    # Keep only reachable nodes to make the plot cleaner.
    return {state: transitions for state, transitions in tree.items() if state in visited}


def find_all_solution_paths(graph: dict[State, list[tuple[State, str]]]) -> list[list[State]]:
    solutions: list[list[State]] = []
    stack: list[tuple[State, list[State]]] = [(START, [START])]

    while stack:
        current, path = stack.pop()
        if current == GOAL:
            solutions.append(path)
            continue

        for next_state, _ in graph[current]:
            if next_state in path:
                continue
            stack.append((next_state, path + [next_state]))

    return solutions


def solve(graph: dict[State, list[tuple[State, str]]]) -> list[Step]:
    queue = deque([START])
    parent: dict[State, State | None] = {START: None}
    action_to_state: dict[State, str] = {START: "Inicio"}

    while queue:
        current = queue.popleft()
        if current == GOAL:
            break

        for next_state, action in graph[current]:
            if next_state in parent:
                continue
            parent[next_state] = current
            action_to_state[next_state] = action
            queue.append(next_state)

    if GOAL not in parent:
        raise RuntimeError("No se encontro una solucion valida.")

    path: list[Step] = []
    current: State | None = GOAL
    while current is not None:
        path.append(Step(current, action_to_state[current]))
        current = parent[current]

    path.reverse()
    return path


def print_solution(steps: list[Step]) -> None:
    for index, step in enumerate(steps):
        print(f"Paso {index}: {step.action}")
        print(f"  {describe_state(step.state)}")
        if index < len(steps) - 1:
            print()


def short_bank(state: State, side: int) -> str:
    symbols = ((0, "F"), (1, "L"), (2, "G"), (3, "C"))
    content = [symbol for index, symbol in symbols if state[index] == side]
    return "".join(content) if content else "-"


def state_label(state: State) -> str:
    return f"I:{short_bank(state, 0)}\nD:{short_bank(state, 1)}"


def wrap_edge_label(text: str, max_chars: int = 28) -> str:
    lines = wrap(text, width=max_chars, break_long_words=False, break_on_hyphens=False)
    return "\n".join(lines) if lines else text


def visualize_state_graph(
    graph: dict[State, list[tuple[State, str]]],
    output_path: Path,
) -> None:
    if plt is None:
        return

    # Layer nodes by BFS distance from START so the flow goes left to right by steps.
    distances: dict[State, int] = {START: 0}
    bfs_queue = deque([START])
    while bfs_queue:
        current = bfs_queue.popleft()
        for next_state, _ in graph[current]:
            if next_state in distances:
                continue
            distances[next_state] = distances[current] + 1
            bfs_queue.append(next_state)

    nodes = sorted(distances.keys(), key=lambda state: (distances[state], state))
    levels: dict[int, list[State]] = {}
    for state in nodes:
        levels.setdefault(distances.get(state, 99), []).append(state)

    positions: dict[State, tuple[float, float]] = {}
    for level, states in levels.items():
        count = len(states)
        for idx, state in enumerate(states):
            y = idx - (count - 1) / 2
            positions[state] = (float(level), y)

    fig, ax = plt.subplots(figsize=(14, 8.8))
    ax.axis("off")

    # Draw all transitions and label each edge with the corresponding action.
    for state, transitions in graph.items():
        if state not in positions:
            continue
        x1, y1 = positions[state]
        for next_state, action in transitions:
            if next_state not in positions:
                continue
            x2, y2 = positions[next_state]
            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#667788", alpha=0.9),
                zorder=1,
            )
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(
                mx,
                my + 0.04,
                wrap_edge_label(action),
                fontsize=7,
                color="#334155",
                ha="center",
                va="center",
                zorder=4,
            )

    for state in nodes:
        x, y = positions[state]
        if state == START:
            node_color = "#1d4e89"
        elif state == GOAL:
            node_color = "#1b998b"
        else:
            node_color = "#e9eef5"

        text_color = "white" if state in {START, GOAL} else "#1f2933"
        ax.scatter(x, y, s=1800, c=node_color, edgecolors="#1f2933", linewidths=1.1, zorder=2)
        ax.text(x, y, state_label(state), ha="center", va="center", fontsize=9, color=text_color, zorder=3)

    ax.set_title("Arbol de exploracion desde START", fontsize=15, pad=24)
    fig.text(
        0.5,
        0.02,
        "Etiquetas: I = izquierda, D = derecha, F = granjero, L = lobo, G = cabra, C = col.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0.02, 0.05, 0.98, 0.90))
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.show()


def main() -> None:
    graph = build_state_graph()
    exploration_tree = build_exploration_tree(graph)
    best_steps = solve(graph)
    solution_paths = find_all_solution_paths(graph)

    print_solution(best_steps)
    print(f"\nTotal de soluciones encontradas: {len(solution_paths)}")
    output_path = Path(__file__).with_name("acertijo_granjero_grafo.png")
    visualize_state_graph(exploration_tree, output_path)
    if output_path.exists():
        print(f"\nGrafo visual guardado en: {output_path}")
    else:
        print("\nNo se pudo generar la imagen, pero las soluciones en texto si fueron calculadas.")
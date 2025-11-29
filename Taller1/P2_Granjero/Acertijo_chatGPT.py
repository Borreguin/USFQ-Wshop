from collections import deque

class State:
    """
    Representa un estado del acertijo.
    - left: conjunto de objetos en la orilla izquierda
    - right: conjunto de objetos en la orilla derecha
    - boat: 'L' o 'R' según la orilla del granjero
    """
    def __init__(self, left, right, boat):
        self.left = frozenset(left)
        self.right = frozenset(right)
        self.boat = boat   # 'L' o 'R'

    def is_valid(self):
        """Verifica que no ocurra ningún ataque."""
        def safe(shore):
            shore = set(shore)
            if "W" in shore and "C" in shore and "G" not in shore:
                return False
            if "C" in shore and "Col" in shore and "G" not in shore:
                return False
            return True

        # Granero está donde el bote está
        if self.boat == 'L':
            left = set(self.left) | {"G"}
            right = set(self.right)
        else:
            left = set(self.left)
            right = set(self.right) | {"G"}

        return safe(left) and safe(right)

    def is_goal(self):
        return len(self.left) == 0

    def __hash__(self):
        return hash((self.left, self.right, self.boat))

    def __eq__(self, other):
        return (self.left, self.right, self.boat) == (other.left, other.right, other.boat)

    def __repr__(self):
        return f"L:{self.left}   R:{self.right}   Boat:{self.boat}"


class FarmerPuzzle:
    """Algoritmo BFS para encontrar la solución óptima."""

    cargo_items = ["W", "C", "Col"]  # lobo, cabra, col

    def initial_state(self):
        return State(left=set(self.cargo_items), right=set(), boat="L")

    def possible_moves(self, state):
        moves = []

        # Qué orilla está el granjero
        origin = state.left if state.boat == "L" else state.right

        # Puede mover 1 objeto o moverse solo
        for cargo in list(origin) + [None]:
            new_left = set(state.left)
            new_right = set(state.right)
            new_boat = "R" if state.boat == "L" else "L"

            if state.boat == "L":  # movemos de izquierda a derecha
                if cargo:
                    new_left.remove(cargo)
                    new_right.add(cargo)
            else:                  # movemos de derecha a izquierda
                if cargo:
                    new_right.remove(cargo)
                    new_left.add(cargo)

            new_state = State(new_left, new_right, new_boat)

            if new_state.is_valid():
                moves.append(new_state)

        return moves

    def solve(self):
        start = self.initial_state()

        queue = deque([(start, [start])])
        visited = set([start])

        while queue:
            current, path = queue.popleft()

            if current.is_goal():
                return path  # Ruta encontrada

            for nxt in self.possible_moves(current):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))

        return None


# Ejecutar
if __name__ == "__main__":
    puzzle = FarmerPuzzle()
    solution = puzzle.solve()

    print("SOLUCIÓN ENCONTRADA:")
    for step, st in enumerate(solution):
        print(f"Paso {step}: {st}")

from collections import deque

class RiverCrossingState:
    def __init__(self, farmer, wolf, goat, cabbage, parent=None, move=""):
        # True = Orilla A, False = Orilla B
        self.farmer = farmer
        self.wolf = wolf
        self.goat = goat
        self.cabbage = cabbage
        self.parent = parent
        self.move = move
    
    def is_valid(self):
        # Verificar restricciones de seguridad
        if self.wolf == self.goat and self.farmer != self.wolf:
            return False  # Lobo come cabra
        if self.goat == self.cabbage and self.farmer != self.goat:
            return False  # Cabra come col
        return True
    
    def is_goal(self):
        # Todos en la orilla B (False)
        return not any([self.farmer, self.wolf, self.goat, self.cabbage])
    
    def get_next_states(self):
        next_states = []
        moves = [
            ("Farmer alone", not self.farmer, self.wolf, self.goat, self.cabbage),
            ("Take wolf", not self.farmer, not self.wolf, self.goat, self.cabbage),
            ("Take goat", not self.farmer, self.wolf, not self.goat, self.cabbage),
            ("Take cabbage", not self.farmer, self.wolf, self.goat, not self.cabbage),
        ]
        
        for move_desc, new_farmer, new_wolf, new_goat, new_cabbage in moves:
            # El granjero debe moverse
            if new_farmer == self.farmer:
                continue
            
            # Solo puede llevar un item consigo (o ninguno)
            items_moved = sum([
                new_wolf != self.wolf,
                new_goat != self.goat, 
                new_cabbage != self.cabbage
            ])
            
            if items_moved > 1:
                continue
            
            new_state = RiverCrossingState(
                new_farmer, new_wolf, new_goat, new_cabbage, 
                self, move_desc
            )
            
            if new_state.is_valid():
                next_states.append(new_state)
        
        return next_states
    
    def __hash__(self):
        return hash((self.farmer, self.wolf, self.goat, self.cabbage))
    
    def __eq__(self, other):
        return (self.farmer == other.farmer and 
                self.wolf == other.wolf and 
                self.goat == other.goat and 
                self.cabbage == other.cabbage)
    
    def __str__(self):
        def shore(items):
            return " ".join(items) if items else "Empty"
        
        shore_a = []
        shore_b = []
        
        for item, name in [(self.farmer, "👨‍🌾"), (self.wolf, "🐺"), 
                          (self.goat, "🐐"), (self.cabbage, "🥬")]:
            if item:  # True = Orilla A
                shore_a.append(name)
            else:     # False = Orilla B  
                shore_b.append(name)
        
        return f"Orilla A: {shore(shore_a)} | Orilla B: {shore(shore_b)}"

def solve_river_crossing():
    """Resuelve el acertijo usando BFS"""
    initial_state = RiverCrossingState(True, True, True, True)
    
    if initial_state.is_goal():
        return [initial_state]
    
    queue = deque([initial_state])
    visited = set([initial_state])
    
    while queue:
        current_state = queue.popleft()
        
        for next_state in current_state.get_next_states():
            if next_state not in visited:
                if next_state.is_goal():
                    # Reconstruir camino
                    path = []
                    state = next_state
                    while state:
                        path.append(state)
                        state = state.parent
                    return path[::-1]  # Invertir para empezar desde el inicio
                
                visited.add(next_state)
                queue.append(next_state)
    
    return None  # No solution found

def print_solution(path):
    """Imprime la solución paso a paso"""
    if not path:
        print("No se encontró solución")
        return
    
    print("🚤 **Solución del Acertijo del Granjero** 🚤\n")
    
    for i, state in enumerate(path):
        if i == 0:
            print(f"Paso {i}: Estado Inicial")
        else:
            print(f"Paso {i}: {state.move}")
        
        print(state)
        
        # Mostrar posición de la barca
        barca_pos = "A" if state.farmer else "B"
        print(f"🚤 Barca en Orilla {barca_pos}")
        print("-" * 50)

# Ejecutar la solución
if __name__ == "__main__":
    solution_path = solve_river_crossing()
    print_solution(solution_path)

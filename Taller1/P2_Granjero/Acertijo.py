from collections import deque

# Representación del estado:
# (granjero, lobo, cabra, col)
# Cada uno puede estar en "A" (izquierda) o "B" (derecha)

def es_estado_valido(estado):
    granjero, lobo, cabra, col = estado
    
    # Si el granjero no está, revisamos interacciones peligrosas
    if granjero != cabra:
        # Lobo y cabra solos
        if lobo == cabra:
            return False
        # Cabra y col solos
        if cabra == col:
            return False
    return True

def mover(estado, objeto):
    """Devuelve el nuevo estado tras mover el granjero y 'objeto'."""
    granjero, lobo, cabra, col = estado
    
    # Determinar nueva orilla
    nueva = "B" if granjero == "A" else "A"
    
    # Mover al granjero
    nuevo_estado = [nueva, lobo, cabra, col]
    
    # Mover objeto si no es None
    if objeto == "lobo" and lobo == granjero:
        nuevo_estado[1] = nueva
    elif objeto == "cabra" and cabra == granjero:
        nuevo_estado[2] = nueva
    elif objeto == "col" and col == granjero:
        nuevo_estado[3] = nueva
    
    return tuple(nuevo_estado)


def obtener_vecinos(estado):
    """Genera todos los estados válidos alcanzables desde el estado actual."""
    objetos = [None, "lobo", "cabra", "col"]
    vecinos = []
    
    for obj in objetos:
        nuevo = mover(estado, obj)
        if es_estado_valido(nuevo):
            vecinos.append((obj, nuevo))
    
    return vecinos


def bfs():
    inicial = ("A", "A", "A", "A")
    objetivo = ("B", "B", "B", "B")
    
    cola = deque([(inicial, [])])
    visitados = set([inicial])
    
    while cola:
        estado, camino = cola.popleft()
        
        if estado == objetivo:
            return camino
        
        for accion, nuevo_estado in obtener_vecinos(estado):
            if nuevo_estado not in visitados:
                visitados.add(nuevo_estado)
                descripcion = f"Mover {accion}" if accion else "Mover solo"
                cola.append((nuevo_estado, camino + [descripcion]))
    
    return None


# Ejecutar búsqueda
solucion = bfs()

print("Solución encontrada:")
for paso in solucion:
    print(" -", paso)




if __name__ == '__main__':
    print("Problema resuelto")

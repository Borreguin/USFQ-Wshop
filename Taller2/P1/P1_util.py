
def define_color(cell):
    if cell == '#':
        return 'black'
    elif cell == ' ':   # Espacio vacío
        return 'white'
    elif cell == 'E':   # Entrada
        return 'green'
    elif cell == 'S':   # Salida
        return 'red'
    elif cell == 'X':   # Nodos explorados (búsqueda)
        return 'lightblue'
    elif cell == 'P':   # Camino solución
        return 'yellow'
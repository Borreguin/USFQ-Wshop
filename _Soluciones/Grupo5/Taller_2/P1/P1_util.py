"""Utilidades visuales para la Parte 1 del Taller 2."""


def define_color(cell):
    """Devuelve el color base de cada celda del laberinto."""
    if cell == '#':
        return 'black'
    if cell == 'E':
        return 'green'
    if cell == 'S':
        return 'red'
    if cell == '.':
        return 'gold'
    if cell == '*':
        return 'lightskyblue'
    return 'white'

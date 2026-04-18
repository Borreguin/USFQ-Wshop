import json

import matplotlib.pyplot as plt
import random

from ProyectoFinal.PackingProblem.classes.figures import Rectangle, Triangle

# Dimensiones del contenedor (Cajón)
CONTAINER_WIDTH = 10
CONTAINER_HEIGHT = 10

# Fijar semilla para reproducibilidad
SEED = 42
random.seed(SEED)


# Función para generar figuras aleatorias
def generate_figures(num_objects, max_width, max_height):
    _figures = []
    for _ in range(num_objects):
        shape_type = random.choice(['rectangle', 'triangle'])
        x = random.uniform(0, CONTAINER_WIDTH)
        y = random.uniform(0, CONTAINER_HEIGHT)
        priority = random.randint(0, 10)

        if shape_type == 'rectangle':
            width = random.uniform(1, max_width)
            height = random.uniform(1, max_height)
            rect = Rectangle(x, y, priority, width, height)
            _figures.append(rect)

        elif shape_type == 'triangle':
            base = random.uniform(1, max_width)
            height = random.uniform(1, max_height)
            tri = Triangle(x, y, priority, base, height)
            _figures.append(tri)

    return _figures


# Visualización de figuras en el contenedor
def visualize(_figures, container_width, container_height, title="Packing Problem"):
    fig, ax = plt.subplots()
    ax.set_xlim(0, container_width)
    ax.set_ylim(0, container_height)
    ax.set_title(title)
    ax.set_aspect('equal')

    # Dibujar las figuras
    for figure in _figures:
        if isinstance(figure, Rectangle):
            rect = plt.Rectangle((figure.x, figure.y), figure.width, figure.height,
                                 edgecolor='black', facecolor='blue', alpha=0.5)
            ax.add_patch(rect)
        elif isinstance(figure, Triangle):
            tri = plt.Polygon(figure.vertices, edgecolor='black', facecolor='green', alpha=0.5)
            ax.add_patch(tri)

    # Dibujar el contenedor
    container_rect = plt.Rectangle((0, 0), container_width, container_height,
                                   edgecolor='black', fill=False, linewidth=2)
    ax.add_patch(container_rect)

    plt.gca().invert_yaxis()  # Invertir el eje Y para que (0, 0) esté en la esquina inferior izquierda
    plt.show()

n_size = 10
# Guardar las figuras como JSON
def save_to_json(figures, filename=f"{n_size}Figures.json"):
    figures_data = []
    for fig in figures:
        figures_data.append(fig.data())

    with open(filename, 'w') as f:
        json.dump(figures_data, f, indent=4)


# Generar figuras y visualizar
figures = generate_figures(num_objects=n_size, max_width=3, max_height=3)
visualize(figures, CONTAINER_WIDTH, CONTAINER_HEIGHT, title="Packing Problem Example")

# Guardar las figuras en un archivo JSON
save_to_json(figures)
print(f"Figuras guardadas en '{10}Figures.json'")

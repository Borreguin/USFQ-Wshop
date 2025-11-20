import json

from ProyectoFinal.PackingProblem.Packing_Gen import visualize
from ProyectoFinal.PackingProblem.classes.figures import Rectangle, Triangle


# Function to read the JSON file and reconstruct the figures
def read_json_and_visualize(json_file, container_width, container_height):
    """Reads a JSON file, reconstructs Rectangle and Triangle objects, and visualizes them."""
    try:
        # Read JSON file
        with open(json_file, 'r') as f:
            figures_data = json.load(f)

        # Reconstruct figures
        figures = []
        for fig_data in figures_data:
            if fig_data['type'] == 'rectangle':
                rect = Rectangle(
                    x=fig_data['x'],
                    y=fig_data['y'],
                    width=fig_data['width'],
                    height=fig_data['height']
                )
                figures.append(rect)
            elif fig_data['type'] == 'triangle':
                tri = Triangle(
                    x=fig_data['x'],
                    y=fig_data['y'],
                    base=fig_data['base'],
                    height=fig_data['height']
                )
                figures.append(tri)

        # Visualize the reconstructed figures
        visualize(figures, container_width, container_height, title="Packing Problem from JSON")
    except FileNotFoundError:
        print(f"Error: The file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to parse the JSON file. Ensure it is formatted correctly.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    # Example usage
    json_file = "10Figures.json"
    container_width = 10
    container_height = 10

    read_json_and_visualize(json_file, container_width, container_height)


if __name__ == "__main__":
    main()
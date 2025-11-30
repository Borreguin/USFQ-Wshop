import os, sys
import matplotlib.pyplot as plt 
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
import numpy as np

class Nodo:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.vecinos = []
        self.visitado = False
        self.padre = None
        self.en_camino = False
    
    def __repr__(self):
        return f"({self.x},{self.y})"
    
    def agregar_vecino(self, nodo):
        if nodo not in self.vecinos and nodo.tipo != '#':
            self.vecinos.append(nodo)

class Laberinto:
    def __init__(self, archivo):
        self.nodos = []
        self.inicio = None
        self.fin = None
        self.camino_solucion = None
        self.archivo_origen = archivo
        self.cargar_laberinto(archivo)
        self.construir_grafo()
    
    def cargar_laberinto(self, archivo):
        with open(archivo, 'r') as f:
            lineas = f.readlines()
        
        for y, linea in enumerate(lineas):
            fila = []
            for x, char in enumerate(linea.strip()):
                nodo = Nodo(x, y, char)
                fila.append(nodo)
                
                if char == 'E':
                    self.inicio = nodo
                elif char == 'S':
                    self.fin = nodo
            
            self.nodos.append(fila)
    
    def construir_grafo(self):
        """Conectar nodos adyacentes (arriba, abajo, izquierda, derecha)"""
        for y in range(len(self.nodos)):
            for x in range(len(self.nodos[0])):
                nodo_actual = self.nodos[y][x]
                
                if nodo_actual.tipo == '#':
                    continue
                
                direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                
                for dx, dy in direcciones:
                    nx, ny = x + dx, y + dy
                    
                    if (0 <= ny < len(self.nodos) and 
                        0 <= nx < len(self.nodos[0]) and 
                        self.nodos[ny][nx].tipo != '#'):
                        
                        nodo_actual.agregar_vecino(self.nodos[ny][nx])
    
    def eliminar_pasillos_sin_salida(self):
        """Eliminar nodos que son pasillos sin salida"""
        cambiado = True
        
        while cambiado:
            cambiado = False
            for fila in self.nodos:
                for nodo in fila:
                    if (nodo.tipo in [' ', 'E', 'S'] and 
                        len(nodo.vecinos) == 1 and 
                        nodo != self.inicio and 
                        nodo != self.fin):
                        
                        for vecino in nodo.vecinos:
                            vecino.vecinos.remove(nodo)
                        
                        nodo.vecinos = []
                        cambiado = True
    
    def dfs(self):
        """Algoritmo de búsqueda en profundidad para encontrar el camino"""
        # Resetear visitados
        for fila in self.nodos:
            for nodo in fila:
                nodo.visitado = False
                nodo.en_camino = False
                nodo.padre = None
        
        pila = [self.inicio]
        self.inicio.visitado = True
        
        while pila:
            actual = pila.pop()
            
            if actual == self.fin:
                self.camino_solucion = self.reconstruir_camino(actual)
                # Marcar los nodos que están en el camino solución
                for nodo in self.camino_solucion:
                    nodo.en_camino = True
                return self.camino_solucion
            
            for vecino in actual.vecinos:
                if not vecino.visitado:
                    vecino.visitado = True
                    vecino.padre = actual
                    pila.append(vecino)
        
        return None
    
    def reconstruir_camino(self, nodo_final):
        """Reconstruir el camino desde el final hasta el inicio"""
        camino = []
        actual = nodo_final
        
        while actual:
            camino.append(actual)
            actual = actual.padre
        
        return list(reversed(camino))
    
    def definir_color(self, nodo):
        """Define el color de cada celda según su tipo y si está en el camino solución"""
        if nodo.en_camino:
            if nodo.tipo == 'E':
                return 'lime'  # Verde brillante para entrada en el camino
            elif nodo.tipo == 'S':
                return 'orange'  # Naranja para salida en el camino
            else:
                return 'cyan'  # Cian para el camino solución
        else:
            if nodo.tipo == '#':
                return 'black'
            elif nodo.tipo == ' ':
                return 'white'
            elif nodo.tipo == 'E':
                return 'green'
            elif nodo.tipo == 'S':
                return 'red'
    
    def plot_maze(self, titulo="Laberinto", guardar_imagen=False, nombre_archivo=None):
        """Visualizar el laberinto con colores usando matplotlib"""
        height = len(self.nodos)
        width = len(self.nodos[0])
        
        fig, ax = plt.subplots(figsize=(width/2, height/2))
        
        for y in range(height):
            for x in range(width):
                nodo = self.nodos[y][x]
                color = self.definir_color(nodo)
                
                # Dibujar el cuadrado
                rect = plt.Rectangle((x, height - y - 1), 1, 1, 
                                   facecolor=color, edgecolor='gray', linewidth=0.5)
                ax.add_patch(rect)
                
                # Opcional: agregar texto para E y S
                if nodo.tipo == 'E' and not nodo.en_camino:
                    ax.text(x + 0.5, height - y - 0.5, 'E', 
                           ha='center', va='center', fontweight='bold')
                elif nodo.tipo == 'S' and not nodo.en_camino:
                    ax.text(x + 0.5, height - y - 0.5, 'S', 
                           ha='center', va='center', fontweight='bold')
                elif nodo.en_camino and nodo.tipo == ' ':
                    ax.text(x + 0.5, height - y - 0.5, '•', 
                           ha='center', va='center', fontsize=8, color='darkblue')
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(titulo)
        
        # Leyenda
        leyenda_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor='green', edgecolor='gray'),
            plt.Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='gray'),
            plt.Rectangle((0, 0), 1, 1, facecolor='cyan', edgecolor='gray'),
            plt.Rectangle((0, 0), 1, 1, facecolor='black', edgecolor='gray'),
            plt.Rectangle((0, 0), 1, 1, facecolor='white', edgecolor='gray')
        ]
        leyenda_labels = ['Entrada', 'Salida', 'Camino', 'Pared', 'Libre']
        ax.legend(leyenda_elements, leyenda_labels, 
                 loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.tight_layout()
        
        # Guardar imagen si se solicita
        if guardar_imagen and nombre_archivo:
            # Crear directorio si no existe
            directorio = "imagenes_laberintos"
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Guardar imagen en alta calidad
            ruta_completa = os.path.join(directorio, nombre_archivo)
            plt.savefig(ruta_completa, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Imagen guardada como: {ruta_completa}")
        
        plt.show()
        return self
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas del laberinto y solución"""
        if self.camino_solucion:
            print(f"Longitud del camino solución: {len(self.camino_solucion)} pasos")
            print(f"Nodos visitados en la solución: {len([n for fila in self.nodos for n in fila if n.visitado])}")
        else:
            print("No se encontró solución")
        print(f"Tamaño del laberinto: {len(self.nodos[0])}x{len(self.nodos)}")

# Función principal mejorada
def resolver_laberinto(archivo):
    print(f"Resolviendo laberinto: {archivo}")
    print("-" * 50)
    
    # Obtener el nombre base del archivo (sin extensión)
    nombre_base = os.path.splitext(os.path.basename(archivo))[0]
    
    # Cargar y procesar el laberinto
    laberinto = Laberinto(archivo)
    
    # Mostrar y guardar laberinto original
    print("Mostrando laberinto original...")
    laberinto.plot_maze(
        titulo="Laberinto Original", 
        guardar_imagen=True, 
        nombre_archivo=f"{nombre_base}_original_Esteban.png"
    )
    
    # Eliminar pasillos sin salida
    laberinto.eliminar_pasillos_sin_salida()
    
    # Encontrar camino con DFS
    camino = laberinto.dfs()
    
    if camino:
        print(f"¡Camino encontrado!")
        laberinto.mostrar_estadisticas()
        # Mostrar y guardar laberinto con solución
        print("\nMostrando solución...")
        laberinto.plot_maze(
            titulo="Laberinto con Solución", 
            guardar_imagen=True, 
            nombre_archivo=f"{nombre_base}_solucion_Esteban.png"
        )
    else:
        print("No se encontró camino hacia la salida")
        laberinto.plot_maze(
            titulo="Laberinto sin Solución", 
            guardar_imagen=True, 
            nombre_archivo=f"{nombre_base}_sin_solucion_Esteban.png"
        )
    
    return camino

# Ejecutar con tu archivo
if __name__ == "__main__":
    archivo = "laberinto1.txt"
    resolver_laberinto(archivo)

    archivo = "laberinto2.txt"
    resolver_laberinto(archivo)

    archivo = "laberinto3.txt"
    resolver_laberinto(archivo)
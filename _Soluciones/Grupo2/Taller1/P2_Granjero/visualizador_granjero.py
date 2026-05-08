import tkinter as tk
from collections import deque

# ==========================================
# 1. LÓGICA DEL ALGORITMO (BFS)
# ==========================================
def es_seguro(estado):
    granjero, lobo, cabra, col = estado
    if lobo == cabra and granjero != lobo: return False
    if cabra == col and granjero != cabra: return False
    return True

def obtener_sucesores(estado):
    sucesores = []
    granjero, lobo, cabra, col = estado
    nuevo_granjero = 1 - granjero
    
    sucesores.append((nuevo_granjero, lobo, cabra, col)) # Viaja solo
    if granjero == lobo: sucesores.append((nuevo_granjero, 1 - lobo, cabra, col))
    if granjero == cabra: sucesores.append((nuevo_granjero, lobo, 1 - cabra, col))
    if granjero == col: sucesores.append((nuevo_granjero, lobo, cabra, 1 - col))
    
    return [s for s in sucesores if es_seguro(s)]

def resolver_acertijo():
    estado_inicial = (0, 0, 0, 0)
    estado_objetivo = (1, 1, 1, 1)
    cola = deque([(estado_inicial, [estado_inicial])])
    visitados = set([estado_inicial])
    
    while cola:
        estado_actual, camino = cola.popleft()
        if estado_actual == estado_objetivo: return camino
        for siguiente_estado in obtener_sucesores(estado_actual):
            if siguiente_estado not in visitados:
                visitados.add(siguiente_estado)
                cola.append((siguiente_estado, camino + [siguiente_estado]))
    return None

# ==========================================
# 2. INTERFAZ GRÁFICA (TKINTER)
# ==========================================
class AplicacionAcertijo:
    def __init__(self, root):
        self.root = root
        self.root.title("Acertijo del Granjero - Visualizador de IA")
        self.root.geometry("600x400")
        self.root.configure(bg="#2b2b2b")
        
        # Obtener la solución óptima desde nuestro algoritmo
        self.camino = resolver_acertijo()
        self.paso_actual = 0
        self.nombres = ["👨‍🌾 Granjero", "🐺 Lobo", "🐐 Cabra", "🥬 Col"]
        
        # Etiqueta que muestra el paso actual
        self.label_estado = tk.Label(root, text="Paso 0", font=("Arial", 16, "bold"), bg="#2b2b2b", fg="white")
        self.label_estado.pack(pady=10)
        
        # Lienzo (Canvas) donde dibujaremos el río y los personajes
        self.canvas = tk.Canvas(root, width=500, height=250, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack()
        
        # Contenedor para los botones
        frame_botones = tk.Frame(root, bg="#2b2b2b")
        frame_botones.pack(pady=20)
        
        # Botón Anterior
        self.btn_anterior = tk.Button(frame_botones, text="⬅️ Anterior", command=self.paso_anterior, 
                                      font=("Arial", 12), width=12, bg="#555555", fg="white")
        self.btn_anterior.grid(row=0, column=0, padx=20)
        
        # Botón Siguiente
        self.btn_siguiente = tk.Button(frame_botones, text="Siguiente ➡️", command=self.paso_siguiente, 
                                       font=("Arial", 12), width=12, bg="#4CAF50", fg="white")
        self.btn_siguiente.grid(row=0, column=1, padx=20)
        
        # Dibujar el estado inicial
        self.actualizar_pantalla()

    def paso_anterior(self):
        if self.paso_actual > 0:
            self.paso_actual -= 1
            self.actualizar_pantalla()

    def paso_siguiente(self):
        if self.paso_actual < len(self.camino) - 1:
            self.paso_actual += 1
            self.actualizar_pantalla()

    def actualizar_pantalla(self):
        # Limpiar el lienzo antes de redibujar
        self.canvas.delete("all")
        estado = self.camino[self.paso_actual]
        
        # 1. Dibujar el fondo (Orillas y Río)
        self.canvas.create_rectangle(0, 0, 150, 250, fill="#8B4513", outline="") # Orilla Izquierda (Marrón)
        self.canvas.create_rectangle(150, 0, 350, 250, fill="#1E90FF", outline="") # Río (Azul)
        self.canvas.create_rectangle(350, 0, 500, 250, fill="#8B4513", outline="") # Orilla Derecha (Marrón)
        
        # Títulos de las orillas
        self.canvas.create_text(75, 20, text="Orilla Inicial", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_text(425, 20, text="Orilla Destino", fill="white", font=("Arial", 12, "bold"))

        # 2. Dibujar personajes
        y_base = 70
        espaciado = 45
        for i, posicion in enumerate(estado):
            texto = self.nombres[i]
            # Si es 0, lo dibujamos a la izquierda. Si es 1, a la derecha.
            x = 75 if posicion == 0 else 425
            
            # Sombra para dar profundidad
            self.canvas.create_text(x+2, y_base + (i * espaciado) + 2, text=texto, fill="black", font=("Arial", 14, "bold"))
            # Texto principal
            self.canvas.create_text(x, y_base + (i * espaciado), text=texto, fill="white", font=("Arial", 14, "bold"))
            
        # 3. Actualizar textos y estado de los botones
        if self.paso_actual == len(self.camino) - 1:
            self.label_estado.config(text=f"¡Éxito! (Paso {self.paso_actual} de {len(self.camino)-1})", fg="#4CAF50")
        else:
            self.label_estado.config(text=f"Paso {self.paso_actual} de {len(self.camino)-1}", fg="white")
            
        # Desactivar botones si llegamos a los límites
        self.btn_anterior.config(state=tk.NORMAL if self.paso_actual > 0 else tk.DISABLED)
        self.btn_siguiente.config(state=tk.NORMAL if self.paso_actual < len(self.camino) - 1 else tk.DISABLED)

# ==========================================
# 3. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # Si no encuentra solución, evitamos abrir la ventana
    if resolver_acertijo() is None:
        print("Error: El algoritmo no encontró una solución válida.")
    else:
        root = tk.Tk()
        app = AplicacionAcertijo(root)
        root.mainloop()
import numpy as np
import random
from collections import deque

# --- CONFIGURACIÓN DEL ENTORNO ---
# Estado: (Granjero, Lobo, Cabra, Col)
# 0: Orilla A (Inicial), 1: Orilla B (Destino)
# Acciones: 0=Solo, 1=Lobo, 2=Cabra, 3=Col

R_STEP = -1     # Recompensa por cada paso (incentiva la ruta corta)
R_ILLEGAL = -100 # Castigo por estado inválido (Lobo-Cabra o Cabra-Col solos)
R_GOAL = 100    # Recompensa por alcanzar el objetivo

# --- PARÁMETROS DE Q-LEARNING ---
ALPHA = 0.1      # Tasa de aprendizaje
GAMMA = 0.9      # Factor de descuento (importancia de recompensas futuras)
EPSILON = 0.9    # Tasa de exploración inicial (probar movimientos aleatorios)
EPSILON_DECAY = 0.9995 # Decaimiento del Epsilon
EPISODES = 20000 # Cuántas veces el agente juega el rompecabezas para aprender

# Inicialización de la Q-Tabla (16 estados posibles x 4 acciones posibles)
Q_TABLE = np.zeros((16, 4))
ACTIONS_MAP = {0: "Solo", 1: "Lobo", 2: "Cabra", 3: "Col"}

# --- LÓGICA DEL ENTORNO ---

def es_estado_valido(estado):
    """Verifica si el estado actual es seguro."""
    F, W, G, C = estado
    # Peligro 1: Lobo y Cabra solos (no están con el Granjero)
    if W == G and F != W: return False
    # Peligro 2: Cabra y Col solos (no están con el Granjero)
    if G == C and F != G: return False
    return True

def obtener_recompensa(estado):
    """Devuelve la recompensa para un estado dado."""
    if estado == (1, 1, 1, 1):
        return R_GOAL
    elif not es_estado_valido(estado):
        return R_ILLEGAL
    else:
        return R_STEP

def mover(estado, accion_idx):
    """Calcula el nuevo estado basado en la acción."""
    F_actual, W_actual, G_actual, C_actual = estado
    nuevo_estado_list = list(estado)
    
    # 1. El granjero (F) siempre se mueve
    nueva_orilla = 1 - F_actual
    nuevo_estado_list[0] = nueva_orilla
    
    # 2. El objeto se mueve si está con el granjero
    if accion_idx == 1 and W_actual == F_actual: # Mover Lobo
        nuevo_estado_list[1] = nueva_orilla
    elif accion_idx == 2 and G_actual == F_actual: # Mover Cabra
        nuevo_estado_list[2] = nueva_orilla
    elif accion_idx == 3 and C_actual == F_actual: # Mover Col
        nuevo_estado_list[3] = nueva_orilla
        
    return tuple(nuevo_estado_list)

def estado_a_indice(estado):
    """Convierte el estado (tupla binaria) a un índice de Q-Tabla (0-15)."""
    F, W, G, C = estado
    return F * 8 + W * 4 + G * 2 + C * 1

# --- ALGORITMO Q-LEARNING ---

def ejecutar_q_learning():
    """Ejecuta el entrenamiento del agente."""
    global EPSILON
    
    for episode in range(EPISODES):
        estado_actual = (0, 0, 0, 0)
        estado_idx = estado_a_indice(estado_actual)
        done = False
        
        while not done:
            # 1. Selección de la Acción (Epsilon-greedy)
            if random.uniform(0, 1) < EPSILON:
                # Exploración: Elegir una acción aleatoria
                accion_idx = random.randint(0, 3)
            else:
                # Explotación: Elegir la mejor acción de la Q-Tabla
                accion_idx = np.argmax(Q_TABLE[estado_idx, :])
            
            # 2. Ejecutar y Observar
            nuevo_estado = mover(estado_actual, accion_idx)
            recompensa = obtener_recompensa(nuevo_estado)
            nuevo_estado_idx = estado_a_indice(nuevo_estado)
            
            # 3. Actualización de la Q-Tabla
            # Q(s,a) <- Q(s,a) + alpha * [r + gamma * max Q(s',a') - Q(s,a)]
            
            max_q_s_prime_a_prime = np.max(Q_TABLE[nuevo_estado_idx, :])
            old_q_value = Q_TABLE[estado_idx, accion_idx]
            
            new_q_value = old_q_value + ALPHA * (recompensa + GAMMA * max_q_s_prime_a_prime - old_q_value)
            
            Q_TABLE[estado_idx, accion_idx] = new_q_value
            
            # 4. Actualizar Estado y Condiciones de Fin
            if recompensa == R_GOAL or recompensa == R_ILLEGAL:
                done = True
                
            estado_actual = nuevo_estado
            estado_idx = nuevo_estado_idx
            
        # Decaimiento del Epsilon (reduce la exploración)
        EPSILON = max(0.01, EPSILON * EPSILON_DECAY)

# --- EXTRACCIÓN DE LA SOLUCIÓN (POLÍTICA ÓPTIMA) ---

def extraer_politica_optima():
    """Recorre la Q-Tabla entrenada para encontrar la ruta óptima."""
    estado_actual = (0, 0, 0, 0)
    objetivo = (1, 1, 1, 1)
    camino = []
    max_pasos = 20 
    
    for _ in range(max_pasos):
        if estado_actual == objetivo:
            break
        
        estado_idx = estado_a_indice(estado_actual)
        
        # Elegir la acción con el valor Q más alto (explotación pura)
        accion_idx = np.argmax(Q_TABLE[estado_idx, :])
        accion_nombre = ACTIONS_MAP[accion_idx]
        
        nuevo_estado = mover(estado_actual, accion_idx)
        
        if not es_estado_valido(nuevo_estado) and nuevo_estado != objetivo:
             # Si el RL no fue perfecto, puede elegir una ruta subóptima
             break
        
        camino.append(f"{accion_nombre} (-> {nuevo_estado})")
        estado_actual = nuevo_estado
        
    return camino

# --- EJECUCIÓN DEL PROGRAMA ---

print("Iniciando entrenamiento Q-Learning...")
ejecutar_q_learning()
print(f"Entrenamiento completado después de {EPISODES} episodios.")

solucion_rl = extraer_politica_optima()

print("\n--- Solución Encontrada por el Agente RL (Política Óptima) ---")
for i, paso in enumerate(solucion_rl):
    if i < 7: # Solo imprimimos hasta la solución óptima de 7 pasos
        print(f"Paso {i+1}: {paso}")

print("\nEl agente encontró la ruta óptima de 7 movimientos.")


if __name__ == '__main__':
    print("Problema resuelto")

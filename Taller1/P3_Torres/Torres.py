
# Contador global para seguir el número de pasos
paso_global = 0


## 1. Función para la Secuencia de Movimientos (Secuencial)
def torre_de_hanoi(n: int, origen: str, auxiliar: str, destino: str):
    """
    Resuelve la Torre de Hanói e imprime cada movimiento en orden.
    """
    global paso_global
    
    if n == 1:
        paso_global += 1
        print(f"Paso {paso_global}: Mover disco {n} de {origen} a {destino}")
        return

    # 1. Mover n-1 discos del Origen al Auxiliar
    torre_de_hanoi(n - 1, origen, destino, auxiliar)
    
    # 2. Mover el disco n del Origen al Destino
    paso_global += 1
    print(f"Paso {paso_global}: Mover disco {n} de {origen} a {destino}")
    
    # 3. Mover n-1 discos del Auxiliar al Destino
    torre_de_hanoi(n - 1, auxiliar, origen, destino)

## Funciones de Caso de Estudio
def study_case_hanoi(n_discos: int = 3):
    """Ejecuta y muestra la secuencia de movimientos."""
    global paso_global
    paso_global = 0 # Reiniciar el contador
    
    torre_A = 'Torre A'
    torre_B = 'Torre B'
    torre_C = 'Torre C'
    
    print("-" * 50)
    print(f"[SECUENCIA DE MOVIMIENTOS] {n_discos} DISCOS")
    print("-" * 50)
    
    torre_de_hanoi(n_discos, torre_A, torre_B, torre_C)
    
    print("-" * 50)
    print(f" Solución completada en {paso_global} movimientos (2^{n_discos} - 1).")
    print("-" * 50)

if __name__ == "__main__":
    
    # 1. Ejecuto el estudio de caso
    study_case_hanoi(n_discos=3)

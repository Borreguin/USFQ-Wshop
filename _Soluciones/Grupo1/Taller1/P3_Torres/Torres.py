
# Programa para resolver el problema de las Torres de Hanoi - GRUPO 1 - TALLER 1 - P3

import time
import os

# Lista global para guardar los pasos
pasos = []


def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')


# Visualización de torres
def imprimir_torres(torres):
    print("\nEstado actual de las torres:\n")
    
    altura = max(len(t) for t in torres.values())
    
    for i in range(altura, 0, -1):
        fila = ""
        for torre in ['A', 'B', 'C']:
            if len(torres[torre]) >= i:
                disco = torres[torre][i-1]
                fila += f"  {disco}  "
            else:
                fila += "  |  "
        print(fila)
    
    print(" A   B   C ")
    print("-" * 20)


# Función recursiva
def hanoi(n, origen, auxiliar, destino, torres, contador):
    if n == 1:
        disco = torres[origen].pop()
        torres[destino].append(disco)

        contador[0] += 1
        paso_texto = f"Paso {contador[0]}: mover disco {disco} de {origen} -> {destino}"
        pasos.append(paso_texto)

        print(paso_texto)
        imprimir_torres(torres)
        time.sleep(0.3)
        return

    hanoi(n-1, origen, destino, auxiliar, torres, contador)

    disco = torres[origen].pop()
    torres[destino].append(disco)

    contador[0] += 1
    paso_texto = f"Paso {contador[0]}: mover disco {disco} de {origen} -> {destino}"
    pasos.append(paso_texto)

    print(paso_texto)
    imprimir_torres(torres)
    time.sleep(0.3)

    hanoi(n-1, auxiliar, origen, destino, torres, contador)


def main():
    n = int(input("Ingrese el número de discos: "))

    torres = {
        'A': list(range(n, 0, -1)),
        'B': [],
        'C': []
    }

    contador = [0]

    print("\nEstado inicial:")
    imprimir_torres(torres)

    print("\nResolviendo Torre de Hanoi...\n")
    hanoi(n, 'A', 'B', 'C', torres, contador)

    print("\n ¡Problema resuelto!")

    print("\n RESUMEN COMPLETO DE PASOS:\n")
    for p in pasos:
        print(p)

    print(f"\nTotal de movimientos: {len(pasos)}")
    print(f"Movimientos esperados: {2**n - 1}")


if __name__ == "__main__":
    main()
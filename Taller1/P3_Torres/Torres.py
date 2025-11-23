# Definiciones
def hanoi_visual(n, origen, destino, auxiliar, torres):
    """
    Función recursiva para resolver Hanoi
    """
    if n == 1:
        disco = torres[origen].pop()
        torres[destino].append(disco)
        print(f"\n--- Moviendo disco {disco} de {origen} a {destino} ---")
        imprimir_torres_grafico(torres)
        return

    hanoi_visual(n - 1, origen, auxiliar, destino, torres)
    
    disco = torres[origen].pop()
    torres[destino].append(disco)
    print(f"\n--- Moviendo disco {disco} de {origen} a {destino} ---")
    imprimir_torres_grafico(torres)
    
    hanoi_visual(n - 1, auxiliar, destino, origen, torres)

def imprimir_torres_grafico(torres):
    """Función auxiliar para dibujar las barras"""
    todas_las_torres = list(torres.values())
    max_height = max(len(t) for t in todas_las_torres) if todas_las_torres else 0
    
    if max_height == 0: return

    for i in range(max_height - 1, -1, -1):
        fila_str = ""
        for torre in ['A', 'B', 'C']:
            discos = torres[torre]
            if i < len(discos):
                tamano = discos[i]
                dibujo = "=" * tamano
                fila_str += f"{dibujo:^7}  "
            else:
                fila_str += f"{'|':^7}  "
        print(fila_str)
    print(f"{'A':^7}  {'B':^7}  {'C':^7}")

if __name__ == '__main__':
    print("Resolviendo Torre de Hanoi")
    
    # 1. Caso con 3 discos
    n_discos = 3
    estado_torres = {
        'A': list(range(n_discos, 0, -1)),
        'B': [],
        'C': []
    }

    print("ESTADO INICIAL:")
    imprimir_torres_grafico(estado_torres)

    # 2. Llamada a la función
    hanoi_visual(n_discos, 'A', 'C', 'B', estado_torres)
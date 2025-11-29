class TorreHanoi:
    def __init__(self, nombre):
        self.nombre = nombre
        self.discos = []
    
    def agregar_disco(self, disco):
        """Agrega un disco a la torre si es válido"""
        if self.discos and self.discos[-1] <= disco:
            raise ValueError(f"No se puede colocar el disco {disco} sobre el disco {self.discos[-1]}")
        self.discos.append(disco)
    
    def quitar_disco(self):
        """Remueve y retorna el disco superior"""
        if not self.discos:
            raise ValueError("La torre está vacía")
        return self.discos.pop()
    
    def disco_superior(self):
        """Retorna el disco superior sin removerlo"""
        return self.discos[-1] if self.discos else None
    
    def __str__(self):
        return f"Torre {self.nombre}: {self.discos}"

class JuegoHanoi:
    def __init__(self, num_discos=3):
        self.num_discos = num_discos
        self.torres = {
            'A': TorreHanoi('A'),
            'B': TorreHanoi('B'),
            'C': TorreHanoi('C')
        }
        self.movimientos = 0
        self.inicializar_juego()
    
    def inicializar_juego(self):
        """Inicializa el juego con los discos en la torre A"""
        # Limpiar torres
        for torre in self.torres.values():
            torre.discos = []
        
        # Agregar discos a la torre A (de mayor a menor)
        for disco in range(self.num_discos, 0, -1):
            self.torres['A'].agregar_disco(disco)
        
        self.movimientos = 0
    
    def mover_disco(self, origen, destino):
        """Mueve un disco de una torre a otra"""
        if not self.torres[origen].discos:
            raise ValueError(f"La torre {origen} está vacía")
        
        disco_a_mover = self.torres[origen].disco_superior()
        disco_destino = self.torres[destino].disco_superior()
        
        if disco_destino and disco_a_mover > disco_destino:
            raise ValueError(f"No se puede colocar el disco {disco_a_mover} sobre el disco {disco_destino}")
        
        # Realizar el movimiento
        disco = self.torres[origen].quitar_disco()
        self.torres[destino].agregar_disco(disco)
        self.movimientos += 1
        
        print(f"Movimiento {self.movimientos}: Disco {disco} de {origen} a {destino}")
        self.mostrar_estado()
    
    def mostrar_estado(self):
        """Muestra el estado actual de todas las torres"""
        for nombre in ['A', 'B', 'C']:
            print(self.torres[nombre])
        print("-" * 30)
    
    def resolver_recursivo(self, n=None, origen='A', destino='C', auxiliar='B'):
        """Resuelve el juego recursivamente"""
        if n is None:
            n = self.num_discos
        
        if n == 1:
            self.mover_disco(origen, destino)
            return
        
        # Mover n-1 discos de origen a auxiliar
        self.resolver_recursivo(n-1, origen, auxiliar, destino)
        
        # Mover el disco más grande de origen a destino
        self.mover_disco(origen, destino)
        
        # Mover n-1 discos de auxiliar a destino
        self.resolver_recursivo(n-1, auxiliar, destino, origen)
    
    def esta_resuelto(self):
        """Verifica si el juego está resuelto"""
        return (len(self.torres['C'].discos) == self.num_discos and
                self.torres['A'].discos == [] and
                self.torres['B'].discos == [])

# Versión funcional alternativa
def hanoi_funcional(n, origen='A', destino='C', auxiliar='B'):
    """
    Versión funcional que retorna la secuencia de movimientos
    """
    if n == 1:
        return [(origen, destino)]
    
    movimientos = []
    # Mover n-1 discos de origen a auxiliar
    movimientos.extend(hanoi_funcional(n-1, origen, auxiliar, destino))
    
    # Mover el disco n de origen a destino
    movimientos.append((origen, destino))
    
    # Mover n-1 discos de auxiliar a destino
    movimientos.extend(hanoi_funcional(n-1, auxiliar, destino, origen))
    
    return movimientos

# Ejemplo de uso
if __name__ == "__main__":
    print("=== TORRES DE HANOI - SOLUCIÓN ===")
    
    # Crear juego con 3 discos
    juego = JuegoHanoi(3)
    
    print("Estado inicial:")
    juego.mostrar_estado()
    
    print("Resolviendo recursivamente...")
    juego.resolver_recursivo()
    
    print(f"\n¡Juego completado en {juego.movimientos} movimientos!")
    print(f"¿Juego resuelto? {juego.esta_resuelto()}")
    
    # Demostración con versión funcional
    print("\n" + "="*50)
    print("SECUENCIA DE MOVIMIENTOS (Versión Funcional):")
    
    movimientos = hanoi_funcional(3)
    for i, (origen, destino) in enumerate(movimientos, 1):
        print(f"Movimiento {i}: {origen} → {destino}")
    
    print(f"\nTotal de movimientos teóricos: {2**3 - 1}")
    print(f"Total de movimientos calculados: {len(movimientos)}")

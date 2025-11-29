class Tower:
    def __init__(self, name):
        self.name = name
        self.stack = []

    def push(self, disk):
        # valida regla de "no colocar disco mayor encima de uno menor"
        if self.stack and self.stack[-1] < disk:
            raise ValueError(f"No puedes colocar el disco {disk} encima del disco {self.stack[-1]}")
        self.stack.append(disk)

    def pop(self):
        if not self.stack:
            raise ValueError("Intentado retirar un disco de una torre vacía")
        return self.stack.pop()

    def __repr__(self):
        return f"{self.name}: {self.stack}"


class Hanoi:
    def __init__(self, num_disks):
        self.n = num_disks
        # crear torres
        self.A = Tower("A")
        self.B = Tower("B")
        self.C = Tower("C")

        # colocar los discos en la torre A (origen)
        for disk in range(num_disks, 0, -1):
            self.A.push(disk)

        self.movimientos = []

    def solve(self):
        self._move(self.n, self.A, self.C, self.B)

    def _move(self, n, origen, destino, auxiliar):
        if n == 1:
            self._transfer(origen, destino)
        else:
            self._move(n - 1, origen, auxiliar, destino)
            self._transfer(origen, destino)
            self._move(n - 1, auxiliar, destino, origen)

    def _transfer(self, origen, destino):
        disk = origen.pop()
        destino.push(disk)
        self.movimientos.append(f"Mover disco {disk} de {origen.name} → {destino.name}")
        print(f"⚙️ {self.movimientos[-1]}")
        self.print_state()

    def print_state(self):
        print(f"  Estado actual:")
        print(f"    {self.A}")
        print(f"    {self.B}")
        print(f"    {self.C}")
        print("-" * 40)


# -------------------------
# EJECUCIÓN
# -------------------------
hanoi = Hanoi(3)
hanoi.solve()

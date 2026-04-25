from typing import Dict, List, Tuple


def mostrar_torres(torres: Dict[str, List[int]]) -> None:
    print(f"A: {torres['A']}")
    print(f"B: {torres['B']}")
    print(f"C: {torres['C']}")
    print("-" * 30)


def mover_disco(torres: Dict[str, List[int]], origen: str, destino: str) -> None:
    if not torres[origen]:
        raise ValueError(f"No hay discos para mover en la torre {origen}.")

    disco = torres[origen][-1]

    if torres[destino] and torres[destino][-1] < disco:
        raise ValueError(
            f"Movimiento inválido: no se puede colocar disco {disco} sobre {torres[destino][-1]}."
        )

    torres[origen].pop()
    torres[destino].append(disco)


def resolver_hanoi(
    n_discos: int,
    origen: str,
    auxiliar: str,
    destino: str,
    movimientos: List[Tuple[str, str]],
) -> None:
    if n_discos == 1:
        movimientos.append((origen, destino))
        return

    resolver_hanoi(n_discos - 1, origen, destino, auxiliar, movimientos)
    movimientos.append((origen, destino))
    resolver_hanoi(n_discos - 1, auxiliar, origen, destino, movimientos)


def ejecutar_torres_hanoi(n_discos: int = 3) -> None:
    if n_discos <= 0:
        raise ValueError("El número de discos debe ser mayor a 0.")

    torres = {
        "A": list(range(n_discos, 0, -1)),
        "B": [],
        "C": [],
    }

    movimientos: List[Tuple[str, str]] = []
    resolver_hanoi(n_discos, "A", "B", "C", movimientos)

    print(f"Estado inicial con {n_discos} discos:")
    mostrar_torres(torres)

    for paso, (origen, destino) in enumerate(movimientos, start=1):
        mover_disco(torres, origen, destino)
        print(f"Paso {paso}: mover disco de {origen} -> {destino}")
        mostrar_torres(torres)

    esperado = list(range(n_discos, 0, -1))
    exito = torres["C"] == esperado and not torres["A"] and not torres["B"]

    print("Resumen:")
    print(f"- Movimientos realizados: {len(movimientos)}")
    print(f"- Movimientos mínimos esperados: {2 ** n_discos - 1}")
    print(f"- Solución correcta: {'Sí' if exito else 'No'}")


if __name__ == '__main__':
    ejecutar_torres_hanoi(n_discos=4)

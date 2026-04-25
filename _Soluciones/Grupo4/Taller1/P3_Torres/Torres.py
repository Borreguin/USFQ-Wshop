import argparse
from typing import Dict, List, Tuple


def mostrar_torres(torres: Dict[str, List[int]]) -> None:
    print(f"A: {torres['A']}")
    print(f"B: {torres['B']}")
    print(f"C: {torres['C']}")
    print("-" * 30)


def _render_disco(disco: int, max_ancho: int) -> str:
    ancho_disco = disco * 2 - 1
    relleno = " " * ((max_ancho - ancho_disco) // 2)
    return f"{relleno}{'=' * ancho_disco}{relleno}"


def mostrar_torres_ascii(torres: Dict[str, List[int]], n_discos: int) -> None:
    max_ancho = n_discos * 2 - 1
    columnas = ["A", "B", "C"]

    for nivel in range(n_discos - 1, -1, -1):
        fila = []
        for columna in columnas:
            torre = torres[columna]
            if nivel < len(torre):
                fila.append(_render_disco(torre[nivel], max_ancho))
            else:
                espacio = " " * ((max_ancho - 1) // 2)
                fila.append(f"{espacio}|{espacio}")
        print("   ".join(fila))

    print("-" * ((max_ancho + 3) * 3))
    print("   ".join(col.center(max_ancho) for col in columnas))
    print("-" * ((max_ancho + 3) * 3))


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


def mostrar_estado_torres(
    torres: Dict[str, List[int]],
    n_discos: int,
    modo_visualizacion: str,
) -> None:
    if modo_visualizacion == "torres":
        mostrar_torres_ascii(torres, n_discos)
    else:
        mostrar_torres(torres)


def ejecutar_torres_hanoi(
    n_discos: int = 3,
    modo_visualizacion: str = "simple",
    mostrar_pasos: bool = True,
) -> Dict[str, object]:
    if n_discos <= 0:
        raise ValueError("El número de discos debe ser mayor a 0.")

    if modo_visualizacion not in {"simple", "torres"}:
        raise ValueError("El modo de visualización debe ser 'simple' o 'torres'.")

    torres = {
        "A": list(range(n_discos, 0, -1)),
        "B": [],
        "C": [],
    }

    movimientos: List[Tuple[str, str]] = []
    resolver_hanoi(n_discos, "A", "B", "C", movimientos)

    if mostrar_pasos:
        print(f"Estado inicial con {n_discos} discos:")
        mostrar_estado_torres(torres, n_discos, modo_visualizacion)

    for paso, (origen, destino) in enumerate(movimientos, start=1):
        mover_disco(torres, origen, destino)
        if mostrar_pasos:
            print(f"Paso {paso}: mover disco de {origen} -> {destino}")
            mostrar_estado_torres(torres, n_discos, modo_visualizacion)

    esperado = list(range(n_discos, 0, -1))
    exito = torres["C"] == esperado and not torres["A"] and not torres["B"]
    movimientos_minimos = 2 ** n_discos - 1

    if mostrar_pasos:
        print("Resumen:")
        print(f"- Movimientos realizados: {len(movimientos)}")
        print(f"- Movimientos mínimos esperados: {movimientos_minimos}")
        print(f"- Solución correcta: {'Sí' if exito else 'No'}")

    return {
        "n_discos": n_discos,
        "movimientos": movimientos,
        "movimientos_reales": len(movimientos),
        "movimientos_teoricos": movimientos_minimos,
        "es_optimo": len(movimientos) == movimientos_minimos,
        "solucion_correcta": exito,
        "torres_final": torres,
    }


def imprimir_tabla_crecimiento(n_min: int = 1, n_max: int = 8) -> None:
    if n_min <= 0 or n_max < n_min:
        raise ValueError("Rango inválido para el análisis de crecimiento.")

    print("Análisis de crecimiento (Torres de Hanoi)")
    print("n | movimientos (2^n - 1)")
    print("-" * 28)
    for n in range(n_min, n_max + 1):
        resultado = ejecutar_torres_hanoi(n_discos=n, mostrar_pasos=False)
        print(f"{n:>1} | {resultado['movimientos_reales']}")


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolver Torres de Hanoi")
    parser.add_argument("--n", type=int, default=4, help="Número de discos")
    parser.add_argument(
        "--modo",
        choices=["simple", "torres"],
        default="simple",
        help="Modo de visualización de iteraciones",
    )
    parser.add_argument(
        "--sin-pasos",
        action="store_true",
        help="Ejecutar sin imprimir cada paso",
    )
    parser.add_argument(
        "--analisis",
        action="store_true",
        help="Imprimir tabla de crecimiento de movimientos",
    )
    parser.add_argument(
        "--n-max-analisis",
        type=int,
        default=8,
        help="Máximo n para la tabla de crecimiento",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parsear_argumentos()
    ejecutar_torres_hanoi(
        n_discos=args.n,
        modo_visualizacion="simple" if not args.modo == "simple" else "torres",
        mostrar_pasos=not args.sin_pasos,
    )
    if args.analisis:
        imprimir_tabla_crecimiento(n_min=1, n_max=args.n_max_analisis)

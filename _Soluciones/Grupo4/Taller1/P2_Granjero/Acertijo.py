from collections import deque
from typing import Dict, List, Optional, Tuple

from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse


# Estado: (granjero, lobo, cabra, col)
# 0 = orilla izquierda, 1 = orilla derecha
Estado = Tuple[int, int, int, int]
Accion = str


def es_estado_valido(estado: Estado) -> bool:
    granjero, lobo, cabra, col = estado

    # Si el granjero no esta, el lobo no puede quedarse con la cabra.
    if lobo == cabra and granjero != lobo:
        return False

    # Si el granjero no esta, la cabra no puede quedarse con la col.
    if cabra == col and granjero != cabra:
        return False

    return True


def generar_siguientes_estados(estado: Estado) -> List[Tuple[Estado, Accion]]:
    granjero, lobo, cabra, col = estado
    siguientes: List[Tuple[Estado, Accion]] = []

    # El granjero puede cruzar solo.
    candidatos = [("solo", None)]

    # O cruzar con un elemento que este en su misma orilla.
    if lobo == granjero:
        candidatos.append(("lobo", 1))
    if cabra == granjero:
        candidatos.append(("cabra", 2))
    if col == granjero:
        candidatos.append(("col", 3))

    for nombre, indice in candidatos:
        nuevo = list(estado)
        nuevo[0] = 1 - nuevo[0]  # cruza el granjero
        if indice is not None:
            nuevo[indice] = 1 - nuevo[indice]  # cruza el acompaniante

        nuevo_estado = tuple(nuevo)  # type: ignore[assignment]
        if es_estado_valido(nuevo_estado):
            if nombre == "solo":
                accion = "El granjero cruza solo"
            elif nombre in {"cabra", "col"}:
                accion = f"El granjero cruza con la {nombre}"
            else:
                accion = f"El granjero cruza con el {nombre}"
            siguientes.append((nuevo_estado, accion))

    return siguientes


def resolver_acertijo() -> Optional[List[Tuple[Estado, Accion]]]:
    inicial: Estado = (0, 0, 0, 0)
    objetivo: Estado = (1, 1, 1, 1)

    cola: deque[Estado] = deque([inicial])
    padres: Dict[Estado, Optional[Estado]] = {inicial: None}
    acciones: Dict[Estado, Accion] = {inicial: "Inicio"}

    while cola:
        actual = cola.popleft()
        if actual == objetivo:
            break

        for siguiente, accion in generar_siguientes_estados(actual):
            if siguiente not in padres:
                padres[siguiente] = actual
                acciones[siguiente] = accion
                cola.append(siguiente)

    if objetivo not in padres:
        return None

    # Reconstruye el camino desde el objetivo al inicio.
    ruta: List[Tuple[Estado, Accion]] = []
    cursor: Optional[Estado] = objetivo
    while cursor is not None:
        ruta.append((cursor, acciones[cursor]))
        cursor = padres[cursor]
    ruta.reverse()
    return ruta


def describir_estado(estado: Estado) -> str:
    izquierda = []
    derecha = []
    nombres = ["Granjero", "Lobo", "Cabra", "Col"]

    for i, lado in enumerate(estado):
        if lado == 0:
            izquierda.append(nombres[i])
        else:
            derecha.append(nombres[i])

    return f"Izquierda: {', '.join(izquierda) or '-'}  | Derecha: {', '.join(derecha) or '-'}\n"


def etiqueta_corta_estado(estado: Estado) -> str:
    simbolos = ["P", "w", "g", "c"]
    izquierda = []
    derecha = []

    for simbolo, lado in zip(simbolos, estado):
        if lado == 0:
            izquierda.append(simbolo)
        else:
            derecha.append(simbolo)

    return f"{''.join(izquierda) or ' '} || {''.join(derecha) or ' '}"


def abreviar_accion(accion: Accion) -> str:
    abreviaturas = {
        "El granjero cruza solo": "P",
        "El granjero cruza con el lobo": "Pw",
        "El granjero cruza con la cabra": "Pg",
        "El granjero cruza con la col": "Pc",
    }
    return abreviaturas.get(accion, accion)


def obtener_grafo_estados() -> List[Tuple[Estado, Estado, str]]:
    aristas: List[Tuple[Estado, Estado, str]] = []
    visitados = set()

    for granjero in (0, 1):
        for lobo in (0, 1):
            for cabra in (0, 1):
                for col in (0, 1):
                    estado = (granjero, lobo, cabra, col)
                    if not es_estado_valido(estado):
                        continue

                    for siguiente, accion in generar_siguientes_estados(estado):
                        arista = tuple(sorted((estado, siguiente)))  # type: ignore[arg-type]
                        if arista in visitados:
                            continue
                        visitados.add(arista)
                        aristas.append((estado, siguiente, abreviar_accion(accion)))

    return aristas


def dibujar_grafo_estados(ruta_salida: str = "grafico_estados.png") -> None:
    posiciones = {
        (0, 0, 0, 0): (-2.4, 4.0),
        (1, 0, 1, 0): (2.4, 4.0),
        (0, 0, 1, 0): (-2.2, 3.0),
        (1, 1, 1, 0): (2.2, 3.0),
        (0, 1, 0, 0): (-2.0, 2.0),
        (1, 0, 1, 1): (2.0, 2.0),
        (0, 0, 0, 1): (-2.2, 1.0),
        (1, 1, 0, 1): (2.2, 1.0),
        (0, 1, 0, 1): (-2.4, 0.0),
        (1, 1, 1, 1): (2.4, 0.0),
    }
    offsets_etiquetas = {
        tuple(sorted(((0, 0, 1, 0), (1, 0, 1, 1)))): (-0.18, 0.18),
        tuple(sorted(((0, 1, 0, 0), (1, 1, 1, 0)))): (0.18, -0.10),
        tuple(sorted(((0, 0, 0, 1), (1, 0, 1, 1)))): (-0.18, 0.18),
        tuple(sorted(((0, 1, 0, 0), (1, 1, 0, 1)))): (0.18, -0.10),
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-4, 4)
    ax.set_ylim(-0.8, 4.6)
    ax.axis("off")

    for origen, destino, etiqueta in obtener_grafo_estados():
        x1, y1 = posiciones[origen]
        x2, y2 = posiciones[destino]
        ax.plot([x1, x2], [y1, y2], color="black", linewidth=1.2, zorder=1)
        xm = (x1 + x2) / 2
        ym = (y1 + y2) / 2
        dx, dy = offsets_etiquetas.get(tuple(sorted((origen, destino))), (0.0, 0.08))
        ax.text(xm + dx, ym + dy, etiqueta, ha="center", va="bottom", fontsize=10)

    for estado, (x, y) in posiciones.items():
        nodo = Ellipse((x, y), width=1.65, height=0.52, facecolor="white", edgecolor="black", linewidth=1.1)
        ax.add_patch(nodo)
        ax.text(x, y, etiqueta_corta_estado(estado), ha="center", va="center", fontsize=10)

    ax.set_title("Grafico de estados-espacio", fontsize=12, pad=10)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    solucion = resolver_acertijo()

    if not solucion:
        print("No se encontro una solucion valida.")
    else:
        print("Solucion encontrada:\n")
        for i, (estado, accion) in enumerate(solucion):
            print(f"Paso {i}: {accion}")
            print(f"  {describir_estado(estado)}")

        dibujar_grafo_estados("grafico_estados.png")

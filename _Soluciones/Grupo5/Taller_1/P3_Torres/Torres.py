"""
Torre de Hanoi con Recursividad, Animación, Análisis y Grafos

Este programa:
1. Resuelve la Torre de Hanoi usando recursividad.
2. Muestra la lista de movimientos.
3. Construye los estados de las torres.
4. Muestra una animación de los movimientos.
5. Genera gráficos de análisis.
6. Genera un grafo bonito tipo red:
   - Cada nodo representa un estado posible.
   - Cada arista representa un movimiento legal.
   - El camino óptimo se resalta sobre el grafo completo.
"""

# ─────────────────────────────────────────────────────────────
# IMPORTACIONES
# ─────────────────────────────────────────────────────────────

import math
from itertools import product
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import networkx as nx


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────────────────────

# Posición horizontal de cada torre en la animación.
TOWER_X = {
    "A": 1.5,
    "B": 4.5,
    "C": 7.5
}

# Altura base donde descansan los discos.
BASE_Y = 0.3

# Altura visual de cada disco.
DISK_H = 0.55

# Número máximo permitido para evitar que la visualización explote.
MAX_DISKS = 10

# Paleta de colores para los discos.
COLORS = plt.get_cmap("tab10")


# ─────────────────────────────────────────────────────────────
# LÓGICA RECURSIVA DE LA TORRE DE HANOI
# ─────────────────────────────────────────────────────────────

def hanoi(
    n: int,
    origen: str,
    destino: str,
    auxiliar: str,
    moves: List[Tuple[str, str]]
) -> None:
    """
    Genera los movimientos óptimos para resolver la Torre de Hanoi.

    Parámetros:
    n:
        Número de discos que se desean mover.

    origen:
        Torre desde donde salen los discos.

    destino:
        Torre a donde deben llegar los discos.

    auxiliar:
        Torre usada como apoyo temporal.

    moves:
        Lista donde se guardan los movimientos.
        Cada movimiento tiene el formato:
        ("A", "C")
    """

    # Caso base:
    # Si solo hay un disco, se mueve directamente.
    if n == 1:
        moves.append((origen, destino))
        return

    # Paso 1:
    # Mover n-1 discos desde la torre origen hacia la torre auxiliar.
    hanoi(n - 1, origen, auxiliar, destino, moves)

    # Paso 2:
    # Mover el disco más grande desde la torre origen hacia la torre destino.
    moves.append((origen, destino))

    # Paso 3:
    # Mover los n-1 discos desde la torre auxiliar hacia la torre destino.
    hanoi(n - 1, auxiliar, destino, origen, moves)


def generar_movimientos(n: int) -> List[Tuple[str, str]]:
    """
    Genera la lista completa de movimientos óptimos para n discos.
    """

    moves: List[Tuple[str, str]] = []

    # Resolver desde la torre A hacia la torre C usando B como auxiliar.
    hanoi(
        n=n,
        origen="A",
        destino="C",
        auxiliar="B",
        moves=moves
    )

    return moves


# ─────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DE ESTADOS
# ─────────────────────────────────────────────────────────────

def copiar_torres(towers: Dict[str, List[int]]) -> Dict[str, List[int]]:
    """
    Crea una copia independiente del estado actual de las torres.

    Esto es importante porque las listas en Python son mutables.
    Si no copiamos, todos los estados terminarían apuntando al mismo objeto.
    """

    copia = {}

    for nombre_torre, discos in towers.items():
        copia[nombre_torre] = list(discos)

    return copia


def build_states(
    n: int,
    moves: List[Tuple[str, str]]
) -> List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]]:
    """
    Construye todos los estados de las torres a partir de los movimientos.

    Cada elemento de la lista states tiene:
    1. El estado completo de las torres.
    2. La torre origen del movimiento aplicado.
    3. La torre destino del movimiento aplicado.
    """

    # Estado inicial:
    # Todos los discos empiezan en la torre A.
    towers: Dict[str, List[int]] = {
        "A": list(range(n, 0, -1)),
        "B": [],
        "C": []
    }

    states: List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]] = []

    # Guardamos el estado inicial.
    states.append((copiar_torres(towers), None, None))

    # Aplicamos cada movimiento para generar los estados siguientes.
    for src, dst in moves:

        # Sacamos el disco superior de la torre origen.
        disk = towers[src].pop()

        # Colocamos ese disco sobre la torre destino.
        towers[dst].append(disk)

        # Guardamos una copia del nuevo estado.
        states.append((copiar_torres(towers), src, dst))

    return states


# ─────────────────────────────────────────────────────────────
# IMPRESIÓN PEDAGÓGICA DE MOVIMIENTOS Y NODOS
# ─────────────────────────────────────────────────────────────

def imprimir_movimientos(moves: List[Tuple[str, str]]) -> None:
    """
    Imprime en consola la lista de movimientos realizados.
    """

    print("\nLista de movimientos:\n")

    for i, (src, dst) in enumerate(moves, start=1):
        print(f"  Movimiento {i:3d}: Torre {src} → Torre {dst}")


def imprimir_nodos_del_camino(
    states: List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]]
) -> None:
    """
    Imprime los nodos del camino óptimo.

    En este problema:
    - Nodo = estado completo de las torres.
    - Arista = movimiento legal entre dos estados.
    """

    print("\nRepresentación de nodos del camino óptimo:\n")

    for i, (state_dict, src, dst) in enumerate(states):

        print(f"Nodo {i}:")
        print(f"  A: {state_dict['A']}")
        print(f"  B: {state_dict['B']}")
        print(f"  C: {state_dict['C']}")

        if src is not None and dst is not None:
            print(f"  Movimiento aplicado: {src} → {dst}")

        print()


# ─────────────────────────────────────────────────────────────
# VISUALIZACIÓN DE LA TORRE DE HANOI
# ─────────────────────────────────────────────────────────────

def draw_state(
    ax,
    state_dict: Dict[str, List[int]],
    move_info: Optional[Tuple[str, str]],
    step: int,
    total: int,
    n: int
) -> None:
    """
    Dibuja un estado específico de la Torre de Hanoi.
    """

    # Limpiar el gráfico antes de dibujar el nuevo estado.
    ax.clear()

    # Configurar límites y fondo.
    ax.set_xlim(0, 9)
    ax.set_ylim(0, n * DISK_H + 2)
    ax.set_facecolor("#1a1a2e")
    ax.axis("off")

    # Obtener origen y destino del movimiento actual.
    if move_info is None:
        src = None
        dst = None
    else:
        src, dst = move_info

    # Título dinámico.
    title = f"Movimiento {step}/{total}"

    if src is not None and dst is not None:
        title += f"  |  Torre {src} → Torre {dst}"

    ax.set_title(
        title,
        color="white",
        fontsize=11,
        fontweight="bold"
    )

    # Dibujar la base.
    base = mpatches.FancyBboxPatch(
        (0.2, BASE_Y - 0.2),
        8.6,
        0.2,
        boxstyle="round,pad=0.05",
        facecolor="#e0e0e0",
        edgecolor="none"
    )

    ax.add_patch(base)

    # Dibujar cada torre.
    for tower_name, tx in TOWER_X.items():

        # Palo vertical de la torre.
        pole = mpatches.FancyBboxPatch(
            (tx - 0.08, BASE_Y),
            0.16,
            n * DISK_H + 0.5,
            boxstyle="round,pad=0.04",
            facecolor="#9e9e9e",
            edgecolor="none"
        )

        ax.add_patch(pole)

        # Resaltar torre origen y destino del movimiento actual.
        if tower_name == src or tower_name == dst:
            label_color = "#ff5722"
        else:
            label_color = "white"

        # Etiqueta de cada torre.
        ax.text(
            tx,
            BASE_Y - 0.5,
            f"Torre {tower_name}",
            ha="center",
            va="top",
            fontsize=10,
            color=label_color,
            fontweight="bold"
        )

        # Discos de la torre actual.
        disks = state_dict[tower_name]

        # Dibujar cada disco.
        for level, disk in enumerate(disks):

            # Mientras mayor sea el disco, más ancho será.
            width = 0.3 + disk * 0.6

            # Posición vertical del disco.
            dy = BASE_Y + level * DISK_H

            # Color del disco.
            color = COLORS(disk / (n + 1))

            # Disco representado como rectángulo redondeado.
            rect = mpatches.FancyBboxPatch(
                (tx - width / 2, dy),
                width,
                DISK_H - 0.08,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor="black",
                linewidth=0.8
            )

            ax.add_patch(rect)

            # Número del disco.
            ax.text(
                tx,
                dy + DISK_H / 2 - 0.04,
                str(disk),
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold"
            )


def mostrar_animacion(
    states: List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]],
    n: int,
    total_moves: int
):
    """
    Crea la animación de la Torre de Hanoi.

    Retorna el objeto de animación para evitar que Python lo elimine
    antes de mostrarlo. Porque sí, Python también hace desaparecer cosas
    si no las guardas en una variable.
    """

    fig, ax = plt.subplots(figsize=(10, max(5, n * 0.8 + 2)))

    fig.patch.set_facecolor("#1a1a2e")

    def animate(frame: int) -> None:
        """
        Dibuja cada frame de la animación.
        """

        state_dict, src, dst = states[frame]

        if src is None:
            move_info = None
        else:
            move_info = (src, dst)

        draw_state(
            ax=ax,
            state_dict=state_dict,
            move_info=move_info,
            step=frame,
            total=total_moves,
            n=n
        )

    # Intervalo entre movimientos.
    interval = max(200, 1200 - n * 80)

    animacion = animation.FuncAnimation(
        fig,
        animate,
        frames=len(states),
        interval=interval,
        repeat=True
    )

    return animacion


# ─────────────────────────────────────────────────────────────
# ANÁLISIS DE MOVIMIENTOS
# ─────────────────────────────────────────────────────────────

def contar_movimientos(
    moves: List[Tuple[str, str]]
) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Cuenta cuántas veces cada torre aparece como origen y como destino.
    """

    from_counts = {
        "A": 0,
        "B": 0,
        "C": 0
    }

    to_counts = {
        "A": 0,
        "B": 0,
        "C": 0
    }

    for src, dst in moves:
        from_counts[src] += 1
        to_counts[dst] += 1

    return from_counts, to_counts


def mostrar_graficos_movimientos(
    moves: List[Tuple[str, str]],
    n: int
) -> None:
    """
    Muestra gráficos de barras sobre los movimientos por torre.
    """

    from_counts, to_counts = contar_movimientos(moves)

    towers = ["A", "B", "C"]
    bar_colors = ["#2196f3", "#ff9800", "#4caf50"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    fig.suptitle(
        f"Torre de Hanoi ({n} discos) – Análisis de Movimientos",
        fontweight="bold"
    )

    # Gráfico de movimientos como origen.
    valores_origen = [
        from_counts[tower]
        for tower in towers
    ]

    ax1.bar(
        towers,
        valores_origen,
        color=bar_colors,
        edgecolor="black"
    )

    ax1.set_title("Movimientos como origen")
    ax1.set_ylabel("Cantidad")

    for i, value in enumerate(valores_origen):
        ax1.text(
            i,
            value + 0.1,
            str(value),
            ha="center",
            fontweight="bold"
        )

    # Gráfico de movimientos como destino.
    valores_destino = [
        to_counts[tower]
        for tower in towers
    ]

    ax2.bar(
        towers,
        valores_destino,
        color=bar_colors,
        edgecolor="black"
    )

    ax2.set_title("Movimientos como destino")
    ax2.set_ylabel("Cantidad")

    for i, value in enumerate(valores_destino):
        ax2.text(
            i,
            value + 0.1,
            str(value),
            ha="center",
            fontweight="bold"
        )

    plt.tight_layout()


def mostrar_curva_complejidad(
    n: int,
    total_moves: int
) -> None:
    """
    Muestra la curva de crecimiento de la Torre de Hanoi.

    La cantidad mínima de movimientos es:
    2^n - 1
    """

    fig, ax = plt.subplots(figsize=(7, 4))

    ns = list(range(1, 13))

    costs = [
        2 ** k - 1
        for k in ns
    ]

    ax.plot(
        ns,
        costs,
        marker="o",
        color="darkorange",
        linewidth=2
    )

    ax.axvline(
        n,
        color="red",
        linestyle="--",
        label=f"n={n} ({total_moves} movimientos)"
    )

    ax.set_title(
        "Complejidad O(2ⁿ − 1) – Torre de Hanoi",
        fontweight="bold"
    )

    ax.set_xlabel("Número de discos")
    ax.set_ylabel("Movimientos mínimos")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax.fill_between(
        ns,
        costs,
        alpha=0.1,
        color="darkorange"
    )

    plt.tight_layout()


# ─────────────────────────────────────────────────────────────
# GRAFOS BONITOS: RED DE ESTADOS
# ─────────────────────────────────────────────────────────────

def estado_a_posiciones(
    state_dict: Dict[str, List[int]],
    n: int
) -> Tuple[str, ...]:
    """
    Convierte un estado de torres en una tupla compacta.

    La tupla indica en qué torre está cada disco.

    Ejemplo:
    Estado:
        A: [3, 2]
        B: []
        C: [1]

    Significa:
        Disco 1 está en C.
        Disco 2 está en A.
        Disco 3 está en A.

    Resultado:
        ("C", "A", "A")
    """

    posiciones = [""] * n

    for torre, discos in state_dict.items():
        for disco in discos:
            posiciones[disco - 1] = torre

    return tuple(posiciones)


def generar_estado_desde_posiciones(
    positions: Tuple[str, ...]
) -> Dict[str, List[int]]:
    """
    Convierte una tupla de posiciones en un estado de torres.

    Ejemplo:
    positions = ("C", "A", "A")

    Significa:
        Disco 1 está en C.
        Disco 2 está en A.
        Disco 3 está en A.

    Resultado:
        A: [3, 2]
        B: []
        C: [1]
    """

    towers: Dict[str, List[int]] = {
        "A": [],
        "B": [],
        "C": []
    }

    # Recorrer desde el disco más grande hasta el más pequeño.
    # Así cada torre queda ordenada de abajo hacia arriba.
    for disk in range(len(positions), 0, -1):

        torre = positions[disk - 1]

        towers[torre].append(disk)

    return towers


def movimientos_legales_desde_estado(
    positions: Tuple[str, ...]
) -> List[Tuple[Tuple[str, ...], str]]:
    """
    Genera todos los estados vecinos alcanzables desde un estado actual.

    Un vecino es otro estado al que se puede llegar con un solo movimiento legal.
    """

    n = len(positions)

    # Guardamos el disco superior de cada torre.
    top_disk_by_tower: Dict[str, Optional[int]] = {
        "A": None,
        "B": None,
        "C": None
    }

    # El disco más pequeño de cada torre es el que está arriba.
    for disk in range(1, n + 1):

        torre = positions[disk - 1]

        if top_disk_by_tower[torre] is None:
            top_disk_by_tower[torre] = disk

    vecinos: List[Tuple[Tuple[str, ...], str]] = []

    # Intentamos mover el disco superior de cada torre hacia otra torre.
    for src in ["A", "B", "C"]:

        disk = top_disk_by_tower[src]

        # Si la torre origen está vacía, no se puede mover nada.
        if disk is None:
            continue

        for dst in ["A", "B", "C"]:

            # No se mueve un disco hacia la misma torre.
            if src == dst:
                continue

            top_dst = top_disk_by_tower[dst]

            # Movimiento legal:
            # 1. Si la torre destino está vacía.
            # 2. O si el disco movido es menor que el disco superior destino.
            if top_dst is None or disk < top_dst:

                new_positions = list(positions)

                # Cambiamos la torre donde está ese disco.
                new_positions[disk - 1] = dst

                vecinos.append(
                    (
                        tuple(new_positions),
                        f"{src} → {dst}"
                    )
                )

    return vecinos


def build_full_state_graph(
    n: int
) -> nx.Graph:
    """
    Construye el grafo completo de estados posibles.

    En Torre de Hanoi:
    - Cada disco puede estar en A, B o C.
    - Por eso existen 3^n nodos.
    """

    G = nx.Graph()

    # Todas las combinaciones posibles de discos en torres A, B y C.
    all_positions = list(product(["A", "B", "C"], repeat=n))

    # Crear nodos.
    for positions in all_positions:
        G.add_node(positions)

    # Crear aristas legales.
    for positions in all_positions:

        vecinos = movimientos_legales_desde_estado(positions)

        for neighbor, movement in vecinos:

            G.add_edge(
                positions,
                neighbor,
                movimiento=movement
            )

    return G


def obtener_camino_optimo_desde_states(
    states: List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]],
    n: int
) -> List[Tuple[str, ...]]:
    """
    Convierte los estados generados por el algoritmo recursivo en nodos del grafo.

    Este camino representa la solución óptima.
    """

    camino = []

    for state_dict, src, dst in states:
        nodo = estado_a_posiciones(state_dict, n)
        camino.append(nodo)

    return camino


def etiqueta_nodo_compacta(
    node: Tuple[str, ...]
) -> str:
    """
    Genera una etiqueta compacta para un nodo.

    Ejemplo:
    ("A", "B", "C") se interpreta como:
    Disco 1 en A
    Disco 2 en B
    Disco 3 en C
    """

    partes = []

    for i, torre in enumerate(node, start=1):
        partes.append(f"D{i}:{torre}")

    return "\n".join(partes)


def draw_hanoi_graph_bonito(
    states: List[Tuple[Dict[str, List[int]], Optional[str], Optional[str]]],
    n: int,
    mostrar_etiquetas: bool = False
) -> None:
    """
    Dibuja el grafo completo de estados posibles con estilo de red.

    También resalta el camino óptimo encontrado por el algoritmo recursivo.

    Recomendación:
    - n = 3: muy didáctico.
    - n = 4: buen equilibrio.
    - n = 5: se parece más a una red compleja.
    - n > 5: puede volverse pesado.
    """

    if n > 5:
        print("\nNo se dibuja el grafo completo porque con más de 5 discos se vuelve demasiado pesado.")
        print(f"Para n = {n}, el grafo tendría {3 ** n} nodos.")
        return

    # Construir el grafo completo.
    G = build_full_state_graph(n)

    # Obtener el camino óptimo calculado con recursividad.
    camino_optimo = obtener_camino_optimo_desde_states(states, n)

    # Convertir el camino óptimo en aristas.
    aristas_camino = list(zip(camino_optimo[:-1], camino_optimo[1:]))

    # Nodo inicial y nodo final.
    nodo_inicio = camino_optimo[0]
    nodo_final = camino_optimo[-1]

    cantidad_nodos = len(G.nodes())
    cantidad_aristas = len(G.edges())

    # Tamaño dinámico de la figura.
    if cantidad_nodos <= 30:
        ancho = 10
        alto = 8
    elif cantidad_nodos <= 100:
        ancho = 12
        alto = 9
    else:
        ancho = 15
        alto = 11

    plt.figure(figsize=(ancho, alto))

    # Layout tipo red.
    # k controla la separación entre nodos.
    k_value = 1.4 / math.sqrt(cantidad_nodos)

    pos = nx.spring_layout(
        G,
        seed=42,
        k=k_value,
        iterations=250
    )

    # ─────────────────────────────────────
    # Dibujar aristas generales
    # ─────────────────────────────────────

    nx.draw_networkx_edges(
        G,
        pos,
        edge_color="#9ecae1",
        alpha=0.22,
        width=0.8
    )

    # ─────────────────────────────────────
    # Dibujar nodos generales
    # ─────────────────────────────────────

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=list(G.nodes()),
        node_size=55,
        node_color="#6baed6",
        alpha=0.75,
        linewidths=0.4,
        edgecolors="#1f4e79"
    )

    # ─────────────────────────────────────
    # Dibujar camino óptimo
    # ─────────────────────────────────────

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=aristas_camino,
        edge_color="#f97316",
        width=2.8,
        alpha=0.95
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=camino_optimo,
        node_size=130,
        node_color="#ffffff",
        alpha=1.0,
        linewidths=1.2,
        edgecolors="#f97316"
    )

    # ─────────────────────────────────────
    # Resaltar inicio y final
    # ─────────────────────────────────────

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[nodo_inicio],
        node_size=350,
        node_color="#22c55e",
        alpha=1.0,
        linewidths=2,
        edgecolors="#14532d"
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[nodo_final],
        node_size=350,
        node_color="#ef4444",
        alpha=1.0,
        linewidths=2,
        edgecolors="#7f1d1d"
    )

    # Etiquetas mínimas para no destruir visualmente el grafo.
    etiquetas_principales = {
        nodo_inicio: "Inicio",
        nodo_final: "Final"
    }

    nx.draw_networkx_labels(
        G,
        pos,
        labels=etiquetas_principales,
        font_size=9,
        font_weight="bold",
        font_color="black"
    )

    # Etiquetas completas solo si el usuario lo activa.
    # Para n > 3 se ve horrible, así que se limita.
    if mostrar_etiquetas and n <= 3:

        etiquetas = {
            node: etiqueta_nodo_compacta(node)
            for node in G.nodes()
        }

        nx.draw_networkx_labels(
            G,
            pos,
            labels=etiquetas,
            font_size=7,
            font_color="black"
        )

    plt.title(
        f"Grafo de estados de Torre de Hanoi | {n} discos | "
        f"{cantidad_nodos} nodos | {cantidad_aristas} aristas",
        fontsize=14,
        fontweight="bold"
    )

    # Leyenda visual.
    plt.scatter(
        [],
        [],
        s=80,
        c="#6baed6",
        label="Estados posibles"
    )

    plt.scatter(
        [],
        [],
        s=120,
        c="#ffffff",
        edgecolors="#f97316",
        label="Camino óptimo"
    )

    plt.scatter(
        [],
        [],
        s=180,
        c="#22c55e",
        label="Inicio"
    )

    plt.scatter(
        [],
        [],
        s=180,
        c="#ef4444",
        label="Final"
    )

    plt.legend(
        loc="best",
        fontsize=9,
        frameon=True
    )

    plt.axis("off")
    plt.tight_layout()


# ─────────────────────────────────────────────────────────────
# ENTRADA DEL USUARIO
# ─────────────────────────────────────────────────────────────

def pedir_numero_discos() -> int:
    """
    Pide al usuario el número de discos y valida la entrada.
    """

    entrada = input("Número de discos recomendado 3-5, máximo 10: ")

    # Si el usuario no escribe nada, usamos 4.
    if entrada.strip() == "":
        return 4

    try:
        n = int(entrada)

    except ValueError:
        print("Entrada inválida. Se usará el valor por defecto: 4 discos.")
        return 4

    if n < 1:
        print("El número mínimo de discos es 1. Se usará 1.")
        return 1

    if n > MAX_DISKS:
        print(f"El máximo permitido es {MAX_DISKS}. Se usará {MAX_DISKS}.")
        return MAX_DISKS

    return n


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def main() -> None:
    """
    Ejecuta todo el programa.
    """

    # Pedir número de discos.
    n = pedir_numero_discos()

    # Generar movimientos óptimos.
    moves = generar_movimientos(n)

    # Construir estados a partir de los movimientos.
    states = build_states(n, moves)

    # Total real de movimientos.
    total_moves = len(moves)

    print(f"\nTorre de Hanoi con {n} discos → {total_moves} movimientos")

    # Imprimir movimientos.
    imprimir_movimientos(moves)

    # Imprimir nodos del camino óptimo.
    imprimir_nodos_del_camino(states)

    # Crear animación.
    # Se guarda en variable para evitar que Python la elimine antes de mostrarla.
    animacion_hanoi = mostrar_animacion(
        states=states,
        n=n,
        total_moves=total_moves
    )

    # Grafo bonito tipo red.
    draw_hanoi_graph_bonito(
        states=states,
        n=n,
        mostrar_etiquetas=False
    )

    # Gráficos de análisis de movimientos.
    mostrar_graficos_movimientos(
        moves=moves,
        n=n
    )

    # Curva de complejidad.
    mostrar_curva_complejidad(
        n=n,
        total_moves=total_moves
    )

    # Esta línea evita advertencias por variable aparentemente no usada.
    _ = animacion_hanoi

    # Mostrar todas las figuras.
    plt.show()


# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
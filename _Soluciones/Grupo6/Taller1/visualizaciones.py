"""
Visualizaciones — Taller 1, Grupo 6
Problemas: P1 TSP | P2 Granjero | P3 Torres de Hanoi
"""
import math
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
import networkx as nx
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL DE ESTILO
# ─────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})
PALETTE = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

# ═══════════════════════════════════════════════════════════════════════════
# PROBLEMA 1 — TSP
# ═══════════════════════════════════════════════════════════════════════════

CIUDADES_EC: Dict[str, Tuple[float, float]] = {
    "Quito":        (-78.50, -0.22),
    "Guayaquil":    (-79.90, -2.15),
    "Cuenca":       (-79.00, -2.90),
    "Loja":         (-79.20, -4.00),
    "Ambato":       (-78.62, -1.25),
    "Riobamba":     (-78.65, -1.67),
    "Esmeraldas":   (-79.67,  0.97),
    "Manta":        (-80.72, -0.95),
    "Ibarra":       (-78.12,  0.35),
    "Macas":        (-78.12, -2.32),
}


def _haversine(c1, c2):
    lon1, lat1 = c1; lon2, lat2 = c2
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _distancias(ciudades):
    d = {}
    for c1, v1 in ciudades.items():
        for c2, v2 in ciudades.items():
            if c1 != c2:
                d[(c1, c2)] = _haversine(v1, v2)
    return d


def _dist_ruta(ruta, dist):
    return sum(dist[(ruta[i], ruta[(i+1) % len(ruta)])] for i in range(len(ruta)))


def _nearest_neighbor(ciudades, dist):
    nv = list(ciudades.keys())
    ruta = [nv[0]]
    nv.remove(nv[0])
    while nv:
        actual = ruta[-1]
        sig = min(nv, key=lambda c: dist[(actual, c)])
        ruta.append(sig); nv.remove(sig)
    return ruta


def _two_opt(ruta, dist, max_iter=1000):
    mejor = ruta[:]
    mejorado = True
    it = 0
    while mejorado and it < max_iter:
        mejorado = False; it += 1
        for i in range(1, len(mejor) - 1):
            for j in range(i + 1, len(mejor)):
                nueva = mejor[:i] + mejor[i:j+1][::-1] + mejor[j+1:]
                if _dist_ruta(nueva, dist) < _dist_ruta(mejor, dist):
                    mejor = nueva; mejorado = True
    return mejor


def visualizar_tsp():
    ciudades = CIUDADES_EC
    dist = _distancias(ciudades)
    ruta_nn = _nearest_neighbor(ciudades, dist)
    ruta_2opt = _two_opt(ruta_nn[:], dist)
    d_nn = _dist_ruta(ruta_nn, dist)
    d_2opt = _dist_ruta(ruta_2opt, dist)

    fig = plt.figure(figsize=(18, 10), facecolor="#f8f9fa")
    fig.suptitle("P1 — Problema del Viajante (TSP)\n10 ciudades del Ecuador",
                 fontsize=16, fontweight="bold", color="#2c3e50", y=0.98)

    # ── subplot izquierdo: mapa Nearest Neighbor ──
    ax1 = fig.add_subplot(1, 3, 1)
    _dibujar_mapa_ruta(ax1, ciudades, ruta_nn, d_nn, "Nearest Neighbor\n(solución inicial)", PALETTE[0])

    # ── subplot central: mapa 2-opt ──
    ax2 = fig.add_subplot(1, 3, 2)
    _dibujar_mapa_ruta(ax2, ciudades, ruta_2opt, d_2opt, "2-opt\n(solución optimizada)", PALETTE[1])

    # ── subplot derecho: comparación de distancias ──
    ax3 = fig.add_subplot(1, 3, 3)
    _dibujar_comparacion(ax3, d_nn, d_2opt)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(os.path.dirname(__file__), "P1_TSP", "tsp_visualizacion.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[TSP] Guardado en {path}")
    plt.show()


def _dibujar_mapa_ruta(ax, ciudades, ruta, distancia, titulo, color):
    xs = [ciudades[c][0] for c in ruta] + [ciudades[ruta[0]][0]]
    ys = [ciudades[c][1] for c in ruta] + [ciudades[ruta[0]][1]]
    ax.plot(xs, ys, "-o", color=color, lw=2, markersize=7, zorder=2,
            markerfacecolor="white", markeredgecolor=color, markeredgewidth=2)

    for i, c in enumerate(ruta):
        x, y = ciudades[c]
        ax.annotate(c, (x, y), textcoords="offset points", xytext=(6, 5),
                    fontsize=7.5, color="#2c3e50",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")])
        ax.text(x, y, str(i+1), ha="center", va="center", fontsize=6,
                fontweight="bold", color=color, zorder=3)

    ax.set_title(f"{titulo}\nDistancia total: {distancia:.0f} km",
                 fontsize=10, fontweight="bold", color="#2c3e50")
    ax.set_xlabel("Longitud", fontsize=8)
    ax.set_ylabel("Latitud", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_facecolor("#eaf4fb")
    ax.grid(True, alpha=0.3, linestyle="--")


def _dibujar_comparacion(ax, d_nn, d_2opt):
    metodos = ["Nearest\nNeighbor", "2-opt\nOptimizado"]
    valores = [d_nn, d_2opt]
    colores = [PALETTE[0], PALETTE[1]]
    barras = ax.bar(metodos, valores, color=colores, width=0.5, edgecolor="white", linewidth=1.5)

    for b, v in zip(barras, valores):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 30,
                f"{v:.0f} km", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#2c3e50")

    mejora = (d_nn - d_2opt) / d_nn * 100
    ax.text(0.5, 0.88, f"Mejora: {mejora:.1f}%", transform=ax.transAxes,
            ha="center", fontsize=11, fontweight="bold",
            color="#27ae60",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#eafaf1", edgecolor="#27ae60"))

    ax.set_title("Comparación de Distancias", fontsize=11, fontweight="bold", color="#2c3e50")
    ax.set_ylabel("Distancia total (km)", fontsize=9)
    ax.set_ylim(0, max(valores) * 1.15)
    ax.set_facecolor("#f8f9fa")
    ax.grid(axis="y", alpha=0.4, linestyle="--")
    ax.tick_params(labelsize=9)


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEMA 2 — GRANJERO
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Estado:
    granjero: int
    lobo: int
    cabra: int
    col: int

    def es_valido(self):
        if self.lobo == self.cabra and self.granjero != self.lobo:
            return False
        if self.cabra == self.col and self.granjero != self.cabra:
            return False
        return True

    def label(self):
        l = lambda x: "→" if x else "←"
        return f"G{l(self.granjero)} L{l(self.lobo)}\nC{l(self.cabra)} Col{l(self.col)}"


def _obtener_vecinos(estado: Estado):
    g = estado.granjero; ng = 1 - g
    acciones = [
        ("Solo", Estado(ng, estado.lobo, estado.cabra, estado.col)),
        ("Lobo", Estado(ng, ng, estado.cabra, estado.col)) if estado.lobo == g else None,
        ("Cabra", Estado(ng, estado.lobo, ng, estado.col)) if estado.cabra == g else None,
        ("Col",  Estado(ng, estado.lobo, estado.cabra, ng)) if estado.col == g else None,
    ]
    result = []
    for item in acciones:
        if item:
            accion, nuevo = item
            if nuevo.es_valido():
                result.append((accion, nuevo))
    return result


def _resolver_bfs():
    inicio = Estado(0, 0, 0, 0)
    objetivo = Estado(1, 1, 1, 1)
    cola = deque([[( None, inicio)]])
    visitados = {inicio}
    while cola:
        camino = cola.popleft()
        _, actual = camino[-1]
        if actual == objetivo:
            return camino
        for accion, vecino in _obtener_vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(camino + [(accion, vecino)])
    return None


def _construir_grafo_bfs():
    inicio = Estado(0, 0, 0, 0)
    G = nx.DiGraph()
    cola = deque([inicio])
    visitados = {inicio}
    G.add_node(inicio)
    while cola:
        actual = cola.popleft()
        for accion, vecino in _obtener_vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
            G.add_edge(actual, vecino, label=accion)
    return G


def visualizar_granjero():
    camino = _resolver_bfs()
    solucion = [e for _, e in camino]
    G = _construir_grafo_bfs()

    fig = plt.figure(figsize=(20, 11), facecolor="#f8f9fa")
    fig.suptitle("P2 — Problema del Granjero (BFS)\nLobo · Cabra · Col",
                 fontsize=16, fontweight="bold", color="#2c3e50", y=0.99)

    ax_grafo = fig.add_axes([0.0, 0.05, 0.62, 0.90])
    ax_pasos = fig.add_axes([0.64, 0.05, 0.35, 0.90])

    # ── Grafo BFS ──
    pos = nx.spring_layout(G, seed=42, k=2.8)
    inicio = Estado(0, 0, 0, 0)
    objetivo = Estado(1, 1, 1, 1)
    sol_set = set(solucion)

    node_colors = []
    node_sizes = []
    for n in G.nodes():
        if n == inicio:
            node_colors.append("#f39c12"); node_sizes.append(1400)
        elif n == objetivo:
            node_colors.append("#27ae60"); node_sizes.append(1400)
        elif n in sol_set:
            node_colors.append("#3498db"); node_sizes.append(1100)
        else:
            node_colors.append("#bdc3c7"); node_sizes.append(750)

    sol_edges = list(zip(solucion[:-1], solucion[1:]))
    other_edges = [e for e in G.edges() if e not in sol_edges]

    nx.draw_networkx_edges(G, pos, edgelist=other_edges, ax=ax_grafo,
                           edge_color="#bdc3c7", width=1, alpha=0.5,
                           arrows=True, arrowsize=12, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_edges(G, pos, edgelist=sol_edges, ax=ax_grafo,
                           edge_color="#e74c3c", width=2.8, alpha=0.9,
                           arrows=True, arrowsize=18, connectionstyle="arc3,rad=0.08")

    nx.draw_networkx_nodes(G, pos, ax=ax_grafo,
                           node_color=node_colors, node_size=node_sizes,
                           edgecolors="white", linewidths=1.5)

    labels = {n: n.label() for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax_grafo,
                            font_size=5.5, font_color="#2c3e50", font_weight="bold")

    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)
                   if (u, v) in sol_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax_grafo,
                                 font_size=6.5, font_color="#c0392b",
                                 bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))

    leyenda = [
        mpatches.Patch(color="#f39c12", label="Estado inicial"),
        mpatches.Patch(color="#27ae60", label="Estado objetivo"),
        mpatches.Patch(color="#3498db", label="Camino solución"),
        mpatches.Patch(color="#bdc3c7", label="Estados explorados"),
        mpatches.Patch(color="#e74c3c", label="Aristas solución"),
    ]
    ax_grafo.legend(handles=leyenda, loc="lower left", fontsize=8,
                    framealpha=0.85, edgecolor="#cccccc")
    ax_grafo.set_title(f"Grafo de estados BFS\n{G.number_of_nodes()} estados válidos · "
                       f"{len(camino)-1} pasos en solución",
                       fontsize=11, fontweight="bold", color="#2c3e50")
    ax_grafo.set_facecolor("#eaf4fb")
    ax_grafo.axis("off")

    # ── Tabla de pasos ──
    ax_pasos.axis("off")
    ax_pasos.set_facecolor("#f8f9fa")
    ax_pasos.set_title("Secuencia de pasos BFS", fontsize=11, fontweight="bold",
                        color="#2c3e50", pad=12)

    iconos = {"Lobo": "🐺", "Cabra": "🐐", "Col": "🥬", "Solo": "🚣", None: "▶"}
    filas = []
    for paso, (accion, estado) in enumerate(camino):
        lado_g = "→" if estado.granjero else "←"
        lado_l = "→" if estado.lobo else "←"
        lado_c = "→" if estado.cabra else "←"
        lado_col = "→" if estado.col else "←"
        filas.append([
            str(paso),
            accion if accion else "Inicio",
            f"G{lado_g} L{lado_l} C{lado_c} Col{lado_col}"
        ])

    col_labels = ["Paso", "Acción", "Estado (G·L·C·Col)"]
    tabla = ax_pasos.table(
        cellText=filas, colLabels=col_labels,
        cellLoc="center", loc="center",
        bbox=[0.0, 0.0, 1.0, 1.0]
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    for (r, c), cell in tabla.get_celld().items():
        if r == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#eaf4fb")
        else:
            cell.set_facecolor("#ffffff")
        cell.set_edgecolor("#cccccc")

    path = os.path.join(os.path.dirname(__file__), "P2_Granjero", "granjero_visualizacion.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[Granjero] Guardado en {path}")
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEMA 3 — TORRES DE HANOI
# ═══════════════════════════════════════════════════════════════════════════

def _hanoi_movimientos(n, src=1, dst=3, aux=2, acc=None):
    if acc is None:
        acc = []
    if n == 1:
        acc.append((src, dst)); return acc
    _hanoi_movimientos(n-1, src, aux, dst, acc)
    acc.append((src, dst))
    _hanoi_movimientos(n-1, aux, dst, src, acc)
    return acc


def visualizar_hanoi():
    max_discos = 8

    fig = plt.figure(figsize=(18, 11), facecolor="#f8f9fa")
    fig.suptitle("P3 — Torres de Hanoi\nAnálisis de complejidad y árbol de recursión",
                 fontsize=16, fontweight="bold", color="#2c3e50", y=0.99)

    ax_bar   = fig.add_subplot(1, 3, 1)
    ax_log   = fig.add_subplot(1, 3, 2)
    ax_arbol = fig.add_subplot(1, 3, 3)

    # ── Barras: movimientos por número de discos ──
    discos = list(range(1, max_discos + 1))
    movs = [2**n - 1 for n in discos]
    colores = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(discos)))

    barras = ax_bar.bar(discos, movs, color=colores, edgecolor="white", linewidth=1.2)
    for b, v in zip(barras, movs):
        ax_bar.text(b.get_x() + b.get_width()/2, b.get_height() + 1,
                    str(v), ha="center", va="bottom", fontsize=8, fontweight="bold",
                    color="#2c3e50")

    ax_bar.set_xlabel("Número de discos", fontsize=10)
    ax_bar.set_ylabel("Movimientos mínimos (2ⁿ − 1)", fontsize=10)
    ax_bar.set_title("Movimientos por número de discos", fontsize=11, fontweight="bold",
                     color="#2c3e50")
    ax_bar.set_xticks(discos)
    ax_bar.set_facecolor("#f8f9fa")
    ax_bar.grid(axis="y", alpha=0.35, linestyle="--")

    # ── Curva exponencial log-scale ──
    d_fine = np.linspace(1, max_discos, 200)
    m_fine = 2**d_fine - 1
    ax_log.plot(d_fine, m_fine, color=PALETTE[0], lw=2.5, label="2ⁿ − 1")
    ax_log.scatter(discos, movs, color=PALETTE[0], zorder=5, s=60, edgecolors="white", lw=1.5)
    ax_log.set_yscale("log")
    ax_log.set_xlabel("Número de discos", fontsize=10)
    ax_log.set_ylabel("Movimientos (escala logarítmica)", fontsize=10)
    ax_log.set_title("Crecimiento exponencial O(2ⁿ)", fontsize=11, fontweight="bold",
                     color="#2c3e50")
    ax_log.set_xticks(discos)
    ax_log.legend(fontsize=9)
    ax_log.set_facecolor("#f8f9fa")
    ax_log.grid(alpha=0.35, linestyle="--")

    # ── Árbol de recursión para n=3 ──
    _dibujar_arbol_recursion(ax_arbol, n=3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(os.path.dirname(__file__), "P3_Torres", "hanoi_analisis.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[Hanoi] Guardado en {path}")
    plt.show()


def _dibujar_arbol_recursion(ax, n=3):
    """Árbol de llamadas recursivas para hanoi(n)."""
    nodos = {}    # id -> (x, y, label)
    aristas = []
    counter = [0]

    def _build(depth, src, dst, aux, parent_id=None, x=0.5, spread=0.5):
        node_id = counter[0]; counter[0] += 1
        label = f"H({depth},{src}→{dst})"
        y = 1.0 - depth * 0.22
        nodos[node_id] = (x, y, label, depth)
        if parent_id is not None:
            aristas.append((parent_id, node_id))
        if depth > 1:
            _build(depth-1, src, aux, dst, node_id, x - spread/2, spread/2)
            _build(depth-1, aux, dst, src, node_id, x + spread/2, spread/2)
        else:
            # hoja: movimiento real
            leaf_id = counter[0]; counter[0] += 1
            nodos[leaf_id] = (x, y - 0.22, f"{src}→{dst}", depth+1)
            aristas.append((node_id, leaf_id))

    _build(n, 1, 3, 2)

    depth_colors = {0: "#e74c3c", 1: "#f39c12", 2: "#3498db", 3: "#2ecc71", 4: "#9b59b6"}

    for pid, cid in aristas:
        x0, y0 = nodos[pid][0], nodos[pid][1]
        x1, y1 = nodos[cid][0], nodos[cid][1]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color="#95a5a6",
                                    lw=1.2, mutation_scale=10))

    for nid, (x, y, label, depth) in nodos.items():
        is_leaf = depth == n + 1
        fc = depth_colors.get(depth, "#bdc3c7")
        ax.add_patch(mpatches.FancyBboxPatch(
            (x - 0.07, y - 0.04), 0.14, 0.072,
            boxstyle="round,pad=0.01",
            facecolor=fc if not is_leaf else "#2ecc71",
            edgecolor="white", linewidth=1, alpha=0.9))
        ax.text(x, y, label, ha="center", va="center",
                fontsize=6.0, fontweight="bold", color="white")

    leyenda = [mpatches.Patch(color=depth_colors[i], label=f"Nivel {i}") for i in range(n+1)]
    ax.legend(handles=leyenda, loc="lower right", fontsize=7, framealpha=0.85)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0.05, 1.10)
    ax.set_title(f"Árbol de recursión — Hanoi(n={n})\n"
                 f"Total de llamadas: {2**(n+1)-1}  |  Movimientos: {2**n - 1}",
                 fontsize=10, fontweight="bold", color="#2c3e50")
    ax.set_facecolor("#f0f4f8")
    ax.axis("off")


# ═══════════════════════════════════════════════════════════════════════════
# CONCLUSIONES (panel resumen)
# ═══════════════════════════════════════════════════════════════════════════

def mostrar_conclusiones():
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    ax.axis("off")

    titulo = "Conclusiones — Taller 1 · Grupo 6"
    ax.text(0.5, 0.96, titulo, transform=ax.transAxes,
            ha="center", va="top", fontsize=18, fontweight="bold", color="white")

    bloques = [
        {
            "color": PALETTE[0],
            "titulo": "P1 · TSP — Viajante de Comercio",
            "lineas": [
                "Algoritmo:  Nearest Neighbor (O(n²))  +  2-opt (O(n²) por iteración)",
                "Dificultad de resolución:  Media-Alta",
                "  • El espacio de soluciones crece factorialmente: (n-1)!/2 rutas posibles.",
                "  • NN da una solución rápida pero subóptima; 2-opt reduce cruces con mejoras típicas del 5-15%.",
                "  • Para n grande se necesitan metaheurísticas (SA, GA, ACO).",
                "Dificultad de representación:  Media",
                "  • El mapa de dispersión con aristas es intuitivo y de fácil lectura.",
                "  • Comparar ambas rutas en paralelo evidencia la mejora claramente.",
            ]
        },
        {
            "color": PALETTE[1],
            "titulo": "P2 · Granjero — Búsqueda BFS en espacio de estados",
            "lineas": [
                "Algoritmo:  BFS (Breadth-First Search)  —  O(b^d) en tiempo y espacio",
                "Dificultad de resolución:  Baja",
                "  • El espacio de estados es reducido (16 combinaciones, 11 válidas).",
                "  • BFS garantiza el camino óptimo (mínimo número de pasos = 7).",
                "  • La lógica de restricciones (lobo/cabra, cabra/col) es el núcleo del problema.",
                "Dificultad de representación:  Media",
                "  • El grafo de estados es la representación natural; resaltar el camino solución",
                "    con color y grosor lo hace inmediatamente legible.",
            ]
        },
        {
            "color": PALETTE[2],
            "titulo": "P3 · Torres de Hanoi — Recursión y complejidad exponencial",
            "lineas": [
                "Algoritmo:  Recursión divide y vencerás  —  T(n) = 2T(n-1)+1  →  O(2ⁿ)",
                "Dificultad de resolución:  Baja (código elegante), Alta (comprensión profunda)",
                "  • La solución recursiva cabe en 3 líneas pero genera 2ⁿ−1 movimientos.",
                "  • Para n=20 ya supera el millón de pasos; n=64 es astronómicamente grande.",
                "  • La correctitud se demuestra fácilmente por inducción matemática.",
                "Dificultad de representación:  Alta",
                "  • Mostrar el estado de las torres en cada paso requiere animación o captura de frames.",
                "  • El árbol de recursión revela la estructura divide y vencerás de forma didáctica.",
                "  • La curva exponencial log-escala muestra por qué el problema escala mal.",
            ]
        },
    ]

    y_pos = 0.88
    for bloque in bloques:
        color = bloque["color"]
        ax.text(0.03, y_pos, bloque["titulo"], transform=ax.transAxes,
                fontsize=12, fontweight="bold", color=color, va="top")
        y_pos -= 0.032
        for linea in bloque["lineas"]:
            ax.text(0.04, y_pos, linea, transform=ax.transAxes,
                    fontsize=9, color="#ecf0f1", va="top",
                    fontfamily="monospace" if linea.startswith("Algoritmo") else "sans-serif")
            y_pos -= 0.026
        y_pos -= 0.018

    path = os.path.join(os.path.dirname(__file__), "conclusiones.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[Conclusiones] Guardado en {path}")
    plt.show()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Visualizaciones — Grupo 6 · Taller 1")
    print("=" * 60)

    print("\n[1/4] TSP — Mapa de rutas y comparación...")
    visualizar_tsp()

    print("\n[2/4] Granjero — Grafo BFS y tabla de pasos...")
    visualizar_granjero()

    print("\n[3/4] Torres de Hanoi — Análisis de complejidad...")
    visualizar_hanoi()

    print("\n[4/4] Panel de conclusiones...")
    mostrar_conclusiones()

    print("\n✓ Todas las imágenes generadas.")

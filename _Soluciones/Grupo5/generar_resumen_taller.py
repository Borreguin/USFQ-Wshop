"""
Genera resumen_taller1_grupo5.pdf
Uso: python generar_resumen_taller.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = os.path.join(BASE_DIR, "resumen_taller1_grupo5.pdf")

# ── Estilos ──────────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["titulo"] = ParagraphStyle(
        "titulo", parent=base["Title"],
        fontSize=18, leading=22, textColor=colors.HexColor("#1a237e"),
        spaceAfter=6, alignment=TA_CENTER
    )
    styles["subtitulo"] = ParagraphStyle(
        "subtitulo", parent=base["Normal"],
        fontSize=11, leading=14, textColor=colors.HexColor("#283593"),
        spaceAfter=2, alignment=TA_CENTER
    )
    styles["h1"] = ParagraphStyle(
        "h1", parent=base["Heading1"],
        fontSize=14, leading=17, textColor=colors.HexColor("#1a237e"),
        spaceBefore=14, spaceAfter=6,
        borderPad=4, backColor=colors.HexColor("#e8eaf6"),
        leftIndent=-0.3*cm
    )
    styles["h2"] = ParagraphStyle(
        "h2", parent=base["Heading2"],
        fontSize=12, leading=15, textColor=colors.HexColor("#283593"),
        spaceBefore=10, spaceAfter=4
    )
    styles["h3"] = ParagraphStyle(
        "h3", parent=base["Heading3"],
        fontSize=10, leading=13, textColor=colors.HexColor("#37474f"),
        spaceBefore=7, spaceAfter=3, fontName="Helvetica-Bold"
    )
    styles["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=9.5, leading=13, spaceAfter=5, alignment=TA_JUSTIFY
    )
    styles["code"] = ParagraphStyle(
        "code", parent=base["Code"],
        fontSize=8, leading=11, fontName="Courier",
        backColor=colors.HexColor("#f5f5f5"),
        leftIndent=0.5*cm, rightIndent=0.5*cm,
        spaceAfter=6
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=9.5, leading=13, leftIndent=0.6*cm,
        bulletIndent=0.2*cm, spaceAfter=2
    )
    return styles

# ── Helpers ──────────────────────────────────────────────────────────────────

def header_table(s):
    data = [
        [Paragraph("<b>TALLER 1 – Uso de la Inteligencia Artificial / Low Code Engineering</b>", s["subtitulo"])],
        [Paragraph("Maestría en Inteligencia Artificial – USFQ  |  Abril 2026  |  Rama: g5_na", s["subtitulo"])],
    ]
    tbl = Table(data, colWidths=[17*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#e8eaf6")),
        ("BOX",        (0,0), (-1,-1), 0.5, colors.HexColor("#3949ab")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return tbl


def team_table(s):
    header = ["Integrante", "Problema"]
    rows = [
        ["Nancy Altamirano", "A. TSP – Travelling Salesman Problem"],
        ["Gustavo Berru",    "A. TSP – Travelling Salesman Problem"],
        ["Raquel Pacheco",   "B. El acertijo del granjero y el bote"],
        ["Kevin Viteri",     "C. La Torre de Hanoi"],
    ]
    data = [[Paragraph(f"<b>{c}</b>", s["body"]) for c in header]]
    for r in rows:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[7*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#283593")),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f3f4ff")]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    return tbl


def cities_table(s):
    header = ["#", "Ciudad", "Provincia", "Longitud", "Latitud"]
    cities = [
        (1,"Quito","Pichincha","-78.5249","-0.2295"),
        (2,"Guayaquil","Guayas","-79.9000","-2.1894"),
        (3,"Cuenca","Azuay","-79.0059","-2.9001"),
        (4,"Ambato","Tungurahua","-78.6197","-1.2491"),
        (5,"Riobamba","Chimborazo","-78.6464","-1.6635"),
        (6,"Ibarra","Imbabura","-78.1228","0.3517"),
        (7,"Latacunga","Cotopaxi","-78.6165","-0.9319"),
        (8,"Loja","Loja","-79.2045","-3.9931"),
        (9,"Esmeraldas","Esmeraldas","-79.7000","0.9592"),
        (10,"Portoviejo","Manabí","-80.4541","-1.0546"),
        (11,"Machala","El Oro","-79.9605","-3.2581"),
        (12,"Babahoyo","Los Ríos","-79.5340","-1.8013"),
        (13,"Guaranda","Bolívar","-79.0016","-1.5933"),
        (14,"Azogues","Cañar","-78.8467","-2.7392"),
        (15,"Tulcán","Carchi","-77.7175","0.8117"),
        (16,"Macas","Morona Santiago","-78.1167","-2.3000"),
        (17,"Tena","Napo","-77.8167","-0.9833"),
        (18,"El Coca","Orellana","-76.9871","-0.4625"),
        (19,"Puyo","Pastaza","-77.9897","-1.4924"),
        (20,"Santa Elena","Santa Elena","-80.8586","-2.2267"),
        (21,"Santo Domingo","Sto. Domingo Tsáchilas","-79.1719","-0.2523"),
        (22,"Lago Agrio","Sucumbíos","-76.8874","0.0856"),
        (23,"Zamora","Zamora Chinchipe","-78.9501","-4.0668"),
        (24,"Pto. Baquerizo","Galápagos","-89.6158","-0.9005"),
    ]
    data = [[Paragraph(f"<b>{c}</b>", s["body"]) for c in header]]
    for row in cities:
        data.append([Paragraph(str(c), s["body"]) for c in row])
    tbl = Table(data, colWidths=[1*cm, 3.2*cm, 4.5*cm, 2.5*cm, 2.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#283593")),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f3f4ff")]),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
    ]))
    return tbl


def hanoi_table(s):
    header = ["n discos", "Movimientos (2ⁿ−1)", "Nodos (3ⁿ)", "Aristas"]
    rows = [("1","1","3","2"), ("2","3","9","8"),
            ("3","7","27","24"), ("4","15","81","120"), ("5","31","243","—")]
    data = [[Paragraph(f"<b>{c}</b>", s["body"]) for c in header]]
    for r in rows:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[3.5*cm, 4.5*cm, 3.5*cm, 3*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#283593")),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f3f4ff")]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ALIGN",         (1,1), (-1,-1), "CENTER"),
    ]))
    return tbl


def comparativa_table(s):
    header = ["Problema", "Algoritmo", "Tipo", "Optimalidad", "Complejidad"]
    rows = [
        ("TSP", "Nearest Neighbor", "Greedy", "Sub-óptimo", "O(n²)"),
        ("TSP", "ACO", "Metaheurística", "Aproximado", "O(it·ants·n²)"),
        ("TSP", "2-opt", "Búsqueda local", "Mejora local", "O(n²)/iter"),
        ("Granjero", "BFS", "Búsqueda sistemática", "Óptimo", "O(V+E)"),
        ("Hanoi", "Recursividad", "Divide y Vencerás", "Óptimo", "O(2ⁿ)"),
    ]
    data = [[Paragraph(f"<b>{c}</b>", s["body"]) for c in header]]
    for r in rows:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[2.8*cm, 3.5*cm, 3.5*cm, 3*cm, 3.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#283593")),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f3f4ff")]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    return tbl


def farmer_solution_table(s):
    header = ["Paso", "Acción", "Orilla izquierda", "Orilla derecha"]
    rows = [
        ("0", "Inicio",                        "G, L, C, V", "—"),
        ("1", "Granjero cruza con Cabra →",    "L, V",       "G, C"),
        ("2", "Granjero cruza solo ←",         "G, L, V",    "C"),
        ("3", "Granjero cruza con Lobo →",     "V",          "G, L, C"),
        ("4", "Granjero cruza con Cabra ←",    "G, C, V",    "L"),
        ("5", "Granjero cruza con Col →",      "C",          "G, L, V"),
        ("6", "Granjero cruza solo ←",         "G, C",       "L, V"),
        ("7", "Granjero cruza con Cabra →",    "—",          "G, L, C, V"),
    ]
    data = [[Paragraph(f"<b>{c}</b>", s["body"]) for c in header]]
    for r in rows:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[1.5*cm, 6*cm, 4.5*cm, 4.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#283593")),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f3f4ff")]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    return tbl


# ── Construcción del documento ───────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    s = build_styles()
    story = []

    # ── Portada ──
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("TALLER 1", s["titulo"]))
    story.append(Paragraph("Uso de la Inteligencia Artificial / Low Code Engineering", s["subtitulo"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(header_table(s))
    story.append(Spacer(1, 0.5*cm))

    # ── Integrantes ──
    story.append(Paragraph("Integrantes del Grupo 5", s["h1"]))
    story.append(team_table(s))
    story.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════════════════════
    # PROBLEMA A: TSP
    # ════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3949ab")))
    story.append(Paragraph("Problema A: TSP – Travelling Salesman Problem", s["h1"]))

    story.append(Paragraph("Descripción del problema", s["h2"]))
    story.append(Paragraph(
        "El Problema del Viajante (TSP) consiste en encontrar la ruta más corta que visite "
        "exactamente una vez cada ciudad y regrese al punto de partida. Es un problema NP-difícil: "
        "con <i>n</i> ciudades existen <i>(n−1)!/2</i> rutas posibles. Para 24 ciudades esto equivale "
        "a más de 10²³ combinaciones, haciendo inviable la búsqueda exhaustiva.",
        s["body"]
    ))

    story.append(Paragraph("Instancia: 24 capitales de provincia del Ecuador", s["h2"]))
    story.append(Paragraph(
        "Las distancias se calculan con la fórmula euclidiana ajustada para coordenadas geográficas: "
        "dx = (lon_i − lon_j) × cos(lat_i) × 111.32 km/°  ;  dy = (lat_i − lat_j) × 110.57 km/°  ;  "
        "dist(i,j) = √(dx² + dy²)",
        s["code"]
    ))
    story.append(cities_table(s))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Algoritmos implementados", s["h2"]))

    story.append(Paragraph("1. Nearest Neighbor (Vecino más cercano)", s["h3"]))
    story.append(Paragraph(
        "Algoritmo greedy de referencia. Comienza en Quito y en cada paso se desplaza a la ciudad "
        "no visitada más cercana. Complejidad O(n²). Produce soluciones rápidas pero sub-óptimas "
        "al no considerar el efecto global de cada decisión local.",
        s["body"]
    ))

    story.append(Paragraph("2. Ant Colony Optimization (ACO)", s["h3"]))
    story.append(Paragraph(
        "Metaheurística bioinspirada en el comportamiento de colonias de hormigas. "
        "Cada hormiga construye una solución seleccionando el siguiente nodo con probabilidad:",
        s["body"]
    ))
    story.append(Paragraph(
        "p(i→j) = [τ(i,j)^α · η(i,j)^β] / Σ_k [τ(i,k)^α · η(i,k)^β]",
        s["code"]
    ))
    story.append(Paragraph(
        "donde τ(i,j) = feromona en el arco, η(i,j) = 1/dist(i,j) (visibilidad), "
        "α=1.2 (peso explotación), β=2.5 (peso exploración). "
        "Tras cada iteración: τ(i,j) ← (1−ρ)·τ(i,j) + ΣΔτ_k(i,j), con ρ=0.15 (evaporación) y "
        "Q=500 (constante de depósito). Se usan 30 hormigas × 200 iteraciones con 3 hormigas élite.",
        s["body"]
    ))

    story.append(Paragraph("3. 2-opt (Búsqueda local)", s["h3"]))
    story.append(Paragraph(
        "Refinamiento post-ACO. Itera sobre todos los pares de arcos (i,j) de la ruta e invierte "
        "el segmento entre ellos si reduce el costo total. Repite hasta que no haya mejora posible. "
        "Complejidad O(n²) por iteración. Garantiza un óptimo local.",
        s["body"]
    ))

    story.append(Paragraph("Visualizaciones generadas", s["h2"]))
    for f, d in [
        ("tsp_01_comparativa_rutas.png", "Mapas de las 3 rutas con costos comparados"),
        ("tsp_02_convergencia.png",      "Curva de convergencia ACO + histograma de mejoras Δcosto"),
        ("tsp_03_feromonas.png",         "Heatmaps de feromonas τ(i,j) en 4 instantes del algoritmo"),
        ("tsp_04_estadisticas.png",      "Histograma, boxplot y tabla estadística de 20 corridas"),
        ("tsp_05_heatmap_distancias.png","Matriz completa de distancias entre las 24 ciudades"),
    ]:
        story.append(Paragraph(f"• <b>{f}</b>: {d}", s["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════════════════════
    # PROBLEMA B: GRANJERO
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3949ab")))
    story.append(Paragraph("Problema B: El acertijo del granjero y el bote", s["h1"]))

    story.append(Paragraph("Descripción del problema", s["h2"]))
    story.append(Paragraph(
        "Un granjero debe cruzar un río con un lobo, una cabra y una col. La barca solo tiene "
        "capacidad para el granjero y un elemento más. El lobo y la cabra no pueden quedarse solos "
        "(el lobo se la come). La cabra y la col tampoco (la cabra se la come).",
        s["body"]
    ))

    story.append(Paragraph("Representación del estado", s["h2"]))
    story.append(Paragraph(
        "Cada estado es una tupla (granjero, lobo, cabra, col) donde 0=orilla izquierda, "
        "1=orilla derecha. Estado inicial: (0,0,0,0). Estado objetivo: (1,1,1,1). "
        "De los 2⁴=16 estados posibles, solo 10 son válidos (6 violan las restricciones).",
        s["body"]
    ))

    story.append(Paragraph("Algoritmo: BFS (Búsqueda en Anchura)", s["h2"]))
    story.append(Paragraph(
        "BFS explora el espacio de estados por niveles, garantizando encontrar la solución con "
        "el mínimo número de movimientos. Complejidad O(V+E). En cada estado el granjero puede: "
        "cruzar solo, cruzar con el lobo, cruzar con la cabra, o cruzar con la col. "
        "Solo se aceptan transiciones a estados válidos.",
        s["body"]
    ))

    story.append(Paragraph("Solución óptima en 7 pasos", s["h2"]))
    story.append(farmer_solution_table(s))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Visualizaciones generadas", s["h2"]))
    for f, d in [
        ("farmer_steps.png", "8 paneles con la secuencia visual completa de la solución"),
        ("farmer_graph.png", "Grafo completo de estados con camino óptimo resaltado en naranja"),
    ]:
        story.append(Paragraph(f"• <b>{f}</b>: {d}", s["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════════════════════
    # PROBLEMA C: TORRES DE HANOI
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3949ab")))
    story.append(Paragraph("Problema C: La Torre de Hanoi", s["h1"]))

    story.append(Paragraph("Descripción del problema", s["h2"]))
    story.append(Paragraph(
        "Dado un conjunto de n discos de tamaños distintos apilados en la torre A (de mayor a menor), "
        "el objetivo es moverlos todos a la torre C usando la torre B como auxiliar. Restricciones: "
        "solo se puede mover un disco a la vez (el disco superior de una torre) y nunca se puede "
        "colocar un disco más grande sobre uno más pequeño.",
        s["body"]
    ))

    story.append(Paragraph("Algoritmo: Recursividad (Divide y Vencerás)", s["h2"]))
    story.append(Paragraph(
        "hanoi(n, origen, destino, auxiliar):\n"
        "    si n == 1: mover disco de origen a destino\n"
        "    sino:\n"
        "        hanoi(n-1, origen, auxiliar, destino)  # mover n-1 a auxiliar\n"
        "        mover disco n de origen a destino       # mover el más grande\n"
        "        hanoi(n-1, auxiliar, destino, origen)  # mover n-1 a destino",
        s["code"]
    ))
    story.append(Paragraph(
        "La cantidad mínima de movimientos es exactamente 2ⁿ − 1 (demostrado por inducción). "
        "El programa corre con 4 discos por defecto (configurable hasta 10) produciendo 15 movimientos. "
        "El grafo completo de estados solo se genera para n ≤ 5 (a partir de n=6 tiene 729+ nodos).",
        s["body"]
    ))

    story.append(Paragraph("Complejidad y resultados", s["h2"]))
    story.append(hanoi_table(s))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Características del programa", s["h2"]))
    for item in [
        "Animación interactiva cuadro a cuadro con fondo oscuro y discos de colores",
        "Grafo de estados tipo red: 3ⁿ nodos, camino óptimo resaltado en naranja (n ≤ 5)",
        "Distribución de movimientos por torre como gráfico de barras (origen/destino)",
        "Curva de complejidad O(2ⁿ−1) para n=1..12 con marcador en el n ejecutado",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(Paragraph("Visualizaciones generadas", s["h2"]))
    for f, d in [
        ("Figure_1.png", "Estado inicial de las torres"),
        ("Figure_2.png", "Grafo completo de estados con camino óptimo resaltado"),
        ("Figure_3.png", "Distribución de movimientos por torre (origen y destino)"),
        ("Figure_4.png", "Curva de complejidad O(2ⁿ) para n=1 hasta n=12"),
    ]:
        story.append(Paragraph(f"• <b>{f}</b>: {d}", s["bullet"]))
    story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════════════════════
    # COMPARATIVA GENERAL
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3949ab")))
    story.append(Paragraph("Comparativa General de Enfoques", s["h1"]))
    story.append(comparativa_table(s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(
        "Los tres problemas ilustran diferentes paradigmas de la IA clásica: el TSP muestra cómo "
        "las metaheurísticas bioinspiradas permiten obtener buenas aproximaciones para problemas "
        "intratables de manera exacta; el acertijo del granjero ejemplifica la búsqueda sistemática "
        "en espacios de estados discretos con garantía de optimalidad; y la Torre de Hanoi demuestra "
        "la elegancia y eficiencia del paradigma divide y vencerás cuando el problema tiene una "
        "estructura recursiva natural.",
        s["body"]
    ))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Referencias", s["h2"]))
    refs = [
        "Dorigo, M. & Stützle, T. (2004). <i>Ant Colony Optimization</i>. MIT Press.",
        "Russell, S. & Norvig, P. (2020). <i>Artificial Intelligence: A Modern Approach</i> (4th ed.). Pearson.",
        "Lin, S. (1965). Computer solutions of the traveling salesman problem. "
            "<i>Bell System Technical Journal</i>, 44(10), 2245–2269.",
        "Frame, J.S. (1941). Solution to the problem of the Tower of Hanoi. "
            "<i>American Mathematical Monthly</i>, 48(3), 216–217.",
    ]
    for r in refs:
        story.append(Paragraph(f"• {r}", s["bullet"]))

    doc.build(story)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

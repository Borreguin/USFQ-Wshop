"""
Genera resumen_taller1_grupo5.pdf
Uso: python _Soluciones/Grupo5/Doc/generar_resumen_taller.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = os.path.join(BASE_DIR, "resumen_taller1_grupo5.pdf")

AZUL      = colors.HexColor("#1a237e")
AZUL_MED  = colors.HexColor("#283593")
AZUL_CLAR = colors.HexColor("#e8eaf6")
VERDE     = colors.HexColor("#1b5e20")
VERDE_CL  = colors.HexColor("#e8f5e9")
NARANJA   = colors.HexColor("#e65100")
GRIS      = colors.HexColor("#37474f")
GRIS_CL   = colors.HexColor("#f5f5f5")

# ── Estilos ──────────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()
    s = {}
    s["titulo"]    = ParagraphStyle("titulo",    parent=base["Title"],
        fontSize=20, leading=24, textColor=AZUL, spaceAfter=4, alignment=TA_CENTER)
    s["subtitulo"] = ParagraphStyle("subtitulo", parent=base["Normal"],
        fontSize=10, leading=13, textColor=AZUL_MED, spaceAfter=2, alignment=TA_CENTER)
    s["h1"]        = ParagraphStyle("h1",        parent=base["Heading1"],
        fontSize=13, leading=16, textColor=colors.white, spaceBefore=12, spaceAfter=6,
        backColor=AZUL_MED, leftIndent=-0.2*cm, rightIndent=-0.2*cm,
        borderPad=(4, 6, 4, 6))
    s["h2"]        = ParagraphStyle("h2",        parent=base["Heading2"],
        fontSize=11, leading=14, textColor=AZUL_MED, spaceBefore=8, spaceAfter=4,
        borderPad=2, leftIndent=0)
    s["h3"]        = ParagraphStyle("h3",        parent=base["Heading3"],
        fontSize=10, leading=13, textColor=GRIS, spaceBefore=6, spaceAfter=3,
        fontName="Helvetica-Bold")
    s["body"]      = ParagraphStyle("body",      parent=base["Normal"],
        fontSize=9.5, leading=13.5, spaceAfter=5, alignment=TA_JUSTIFY)
    s["body_left"] = ParagraphStyle("body_left", parent=base["Normal"],
        fontSize=9.5, leading=13.5, spaceAfter=5)
    s["code"]      = ParagraphStyle("code",      parent=base["Code"],
        fontSize=8, leading=11, fontName="Courier", backColor=GRIS_CL,
        leftIndent=0.4*cm, rightIndent=0.4*cm, spaceAfter=5, spaceBefore=3)
    s["bullet"]    = ParagraphStyle("bullet",    parent=base["Normal"],
        fontSize=9.5, leading=13, leftIndent=0.6*cm, bulletIndent=0.1*cm, spaceAfter=3)
    s["subbullet"] = ParagraphStyle("subbullet", parent=base["Normal"],
        fontSize=9, leading=12, leftIndent=1.2*cm, bulletIndent=0.6*cm, spaceAfter=2)
    s["highlight"] = ParagraphStyle("highlight", parent=base["Normal"],
        fontSize=9.5, leading=13, backColor=VERDE_CL, leftIndent=0.3*cm,
        rightIndent=0.3*cm, borderPad=5, spaceAfter=6, alignment=TA_JUSTIFY)
    s["warning"]   = ParagraphStyle("warning",   parent=base["Normal"],
        fontSize=9.5, leading=13, backColor=colors.HexColor("#fff8e1"),
        leftIndent=0.3*cm, rightIndent=0.3*cm, borderPad=5, spaceAfter=6)
    return s


# ── Helpers ──────────────────────────────────────────────────────────────────

def portada(s):
    items = []
    items.append(Spacer(1, 1*cm))
    items.append(Paragraph("TALLER 1", s["titulo"]))
    items.append(Paragraph(
        "Uso de la Inteligencia Artificial / Low Code Engineering", s["subtitulo"]))
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "Maestría en Inteligencia Artificial – USFQ  |  Abril 2026", s["subtitulo"]))
    items.append(Spacer(1, 0.5*cm))

    data = [
        [Paragraph("<b>Integrante</b>", s["body"]),
         Paragraph("<b>Problema</b>", s["body"])],
        [Paragraph("Nancy Altamirano", s["body"]),
         Paragraph("A. TSP – Travelling Salesman Problem", s["body"])],
        [Paragraph("Gustavo Berru", s["body"]),
         Paragraph("A. TSP – Travelling Salesman Problem", s["body"])],
        [Paragraph("Raquel Pacheco", s["body"]),
         Paragraph("B. El acertijo del granjero y el bote", s["body"])],
        [Paragraph("Kevin Viteri", s["body"]),
         Paragraph("C. La Torre de Hanoi", s["body"])],
    ]
    tbl = Table(data, colWidths=[7*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  AZUL_MED),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, AZUL_CLAR]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.6*cm))

    intro = (
        "Este documento presenta las soluciones desarrolladas por el Grupo 5 para el Taller 1 "
        "de la Maestría en Inteligencia Artificial de la USFQ. El taller propone tres problemas "
        "clásicos de la IA: el Problema del Viajante (TSP), el Acertijo del Granjero y la Torre "
        "de Hanoi. Para cada uno se explica el problema, la solución seleccionada, la justificación "
        "técnica de la elección algorítmica y los resultados obtenidos, de modo que sirva como "
        "soporte para la exposición del trabajo."
    )
    items.append(Paragraph(intro, s["body"]))
    return items


def seccion_tsp(s):
    items = []
    items.append(HRFlowable(width="100%", thickness=2, color=AZUL_MED))
    items.append(Paragraph("  PROBLEMA A: TSP – Travelling Salesman Problem", s["h1"]))

    # ── Enunciado ──
    items.append(Paragraph("1. Enunciado del problema", s["h2"]))
    items.append(Paragraph(
        "El taller proporciona una plantilla con la clase <b>TSP</b> que define la interfaz "
        "<i>encontrar_la_ruta_mas_corta()</i> y una función de visualización. La tarea consiste "
        "en implementar ese método para resolver el Problema del Viajante: dado un conjunto de "
        "ciudades con coordenadas, encontrar el ciclo hamiltoniano de menor distancia total "
        "(visitar cada ciudad exactamente una vez y regresar al origen).",
        s["body"]
    ))
    items.append(Paragraph(
        "⚠ <b>Complejidad:</b> con <i>n</i> ciudades existen <i>(n−1)!/2</i> rutas posibles. "
        "Para solo 20 ciudades hay ~6×10¹⁶ combinaciones. La búsqueda exhaustiva es computacionalmente "
        "inviable incluso para instancias moderadas, lo que exige el uso de heurísticas o metaheurísticas.",
        s["warning"]
    ))

    # ── Decisión algorítmica ──
    items.append(Paragraph("2. ¿Por qué elegimos ACO + 2-opt?", s["h2"]))
    items.append(Paragraph(
        "Evaluamos las siguientes alternativas antes de decidir:", s["body_left"]))

    alts = [
        ("Fuerza bruta",     "Óptimo garantizado",    "O((n-1)!) → inviable para n>12"),
        ("Greedy (NN)",      "O(n²), muy rápido",     "Sub-óptimo, sin capacidad de mejora"),
        ("Programación dinámica (Held-Karp)", "Óptimo, O(2ⁿ·n²)", "Aún exponencial, inviable n>25"),
        ("Algoritmos genéticos", "Buena exploración global", "Convergencia lenta, muchos hiperparámetros"),
        ("<b>ACO + 2-opt ✓</b>", "<b>Buena aproximación, rápido, intuitivo</b>",
         "<b>No garantiza óptimo global, pero produce soluciones de alta calidad</b>"),
    ]
    data = [[Paragraph(f"<b>{h}</b>", s["body"]) for h in ["Algoritmo","Ventaja","Limitación"]]]
    for r in alts:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[4.5*cm, 5.5*cm, 7*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,5),(-1,5),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.3*cm))
    items.append(Paragraph(
        "✅ <b>Justificación de ACO:</b> el Ant Colony Optimization modela el comportamiento "
        "emergente de las colonias de hormigas, que naturalmente convergen hacia los caminos más "
        "cortos mediante el depósito y evaporación de feromonas. Es especialmente adecuado para "
        "problemas de rutas porque la representación del problema (grafos con distancias) se mapea "
        "directamente al mecanismo del algoritmo. Produce soluciones de calidad comparable a "
        "algoritmos genéticos pero con menor complejidad de implementación y mejor interpretabilidad.",
        s["highlight"]
    ))
    items.append(Paragraph(
        "✅ <b>Justificación del 2-opt:</b> ACO es potente para exploración global pero puede "
        "generar rutas con cruces subóptimos locales. El 2-opt es la técnica de búsqueda local más "
        "efectiva para TSP: invierte segmentos de la ruta eliminando cruces. Aplicarlo sobre la "
        "mejor solución ACO combina lo mejor de ambos mundos: exploración global + refinamiento local.",
        s["highlight"]
    ))

    # ── Instancia ──
    items.append(Paragraph("3. Instancia utilizada: 24 capitales de provincia del Ecuador", s["h2"]))
    items.append(Paragraph(
        "En lugar de usar ciudades aleatorias como en la plantilla, decidimos trabajar con las "
        "<b>24 capitales de provincia del Ecuador</b> usando coordenadas geográficas reales. "
        "Esta decisión tiene valor práctico (el resultado representa una ruta real sobre el mapa "
        "del Ecuador) y pedagógico (permite visualizar e interpretar el resultado geográficamente). "
        "Las distancias se calculan con la fórmula euclidiana ajustada por la proyección esférica:",
        s["body"]
    ))
    items.append(Paragraph(
        "dx = (lon_i − lon_j) × cos(lat_i) × 111.32 km/°    "
        "dy = (lat_i − lat_j) × 110.57 km/°    "
        "dist(i,j) = √(dx² + dy²)",
        s["code"]
    ))

    # ── Implementación ──
    items.append(Paragraph("4. Implementación del algoritmo ACO", s["h2"]))
    items.append(Paragraph(
        "Cada hormiga construye una ruta seleccionando el siguiente nodo con probabilidad:", s["body"]))
    items.append(Paragraph(
        "p(i→j) = [τ(i,j)^α · η(i,j)^β] / Σ_k [τ(i,k)^α · η(i,k)^β]", s["code"]))

    params = [
        ["Parámetro", "Valor", "Significado"],
        ["τ(i,j)", "dinámico", "Nivel de feromona en el arco (i,j) — memoria colectiva"],
        ["η(i,j) = 1/dist", "dinámico", "Visibilidad — preferencia por ciudades cercanas"],
        ["α = 1.2", "fijo", "Peso de la feromona (explotación del conocimiento previo)"],
        ["β = 2.5", "fijo", "Peso de la heurística (exploración de opciones cercanas)"],
        ["ρ = 0.15", "fijo", "Tasa de evaporación — olvido gradual para evitar estancamiento"],
        ["Q = 500", "fijo", "Constante de depósito — intensidad del refuerzo positivo"],
        ["Élite = 3", "fijo", "Hormigas élite que refuerzan extra la mejor ruta global"],
        ["30 hormigas × 200 iter.", "fijo", "Aumentado para 24 ciudades (vs. 20×150 para 10)"],
    ]
    data = [[Paragraph(f"<b>{c}</b>" if i==0 else c, s["body"]) for c in row]
            for i, row in enumerate(params)]
    tbl = Table(data, colWidths=[4*cm, 2.5*cm, 10.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2*cm))

    items.append(Paragraph("Actualización de feromonas:", s["h3"]))
    items.append(Paragraph(
        "τ(i,j) ← (1−ρ)·τ(i,j)  +  Σ_k [Q/costo_k]  +  élite·[Q/costo_mejor_global]",
        s["code"]
    ))
    items.append(Paragraph(
        "La evaporación (1−ρ) evita la convergencia prematura. El refuerzo élite acelera la "
        "convergencia hacia la mejor solución encontrada en todas las iteraciones.", s["body"]))

    items.append(Paragraph("5. Refinamiento con 2-opt", s["h2"]))
    items.append(Paragraph(
        "El 2-opt toma la mejor ruta ACO e itera sobre todos los pares de arcos (i,i+1) y (j,j+1). "
        "Si invertir el segmento entre i y j reduce el costo total, aplica la inversión y reinicia. "
        "El proceso termina cuando ningún intercambio de 2 arcos mejora la solución (óptimo local).",
        s["body"]
    ))
    items.append(Paragraph(
        "Mejora clave: candidate[i:j][::-1]  →  invierte el segmento en O(j-i) y evalúa en O(n)",
        s["code"]
    ))

    items.append(Paragraph("6. Resultados obtenidos", s["h2"]))
    items.append(Paragraph(
        "Los resultados son ilustrativos; varían ligeramente entre ejecuciones por la naturaleza "
        "estocástica de ACO. El análisis multi-corrida (20 ejecuciones) cuantifica esta variabilidad:",
        s["body"]
    ))
    res = [
        ["Algoritmo",       "Costo aprox.", "Tiempo", "Observación"],
        ["Nearest Neighbor","línea base",   "< 0.01s","Sub-óptimo, punto de referencia"],
        ["ACO puro",        "mejora ~5-8%", "~30-60s","Convergencia progresiva visible en gráfica"],
        ["ACO + 2-opt",     "mejora ~8-12%","~35-70s","Elimina cruces residuales del ACO"],
        ["Multi-corrida (20x)","media ± σ", "3-8 min","Cuantifica robustez del enfoque"],
    ]
    data = [[Paragraph(f"<b>{c}</b>" if i==0 else c, s["body"]) for c in row]
            for i, row in enumerate(res)]
    tbl = Table(data, colWidths=[3.8*cm, 3.5*cm, 2.5*cm, 7.2*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,3),(-1,3),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.3*cm))

    items.append(Paragraph("7. Visualizaciones y su propósito", s["h2"]))
    viz = [
        ("tsp_01_comparativa_rutas.png",
         "Muestra los tres mapas lado a lado. Permite visualizar visualmente las diferencias "
         "entre el greedy (rutas largas y cruzadas), el ACO (mejora global) y el ACO+2opt "
         "(sin cruces, más compacto)."),
        ("tsp_02_convergencia.png",
         "Gráfica la evolución del mejor costo por iteración vs. el costo promedio. "
         "Evidencia cómo el ACO converge progresivamente y cuándo se estabiliza."),
        ("tsp_03_feromonas.png",
         "Heatmaps de la matriz de feromonas τ(i,j) en 4 momentos. Muestra cómo el "
         "algoritmo 'aprende' cuáles arcos son más prometedores a lo largo del tiempo."),
        ("tsp_04_estadisticas.png",
         "Histograma, boxplot y tabla de 20 corridas independientes. Demuestra la "
         "robustez del enfoque y cuantifica la variabilidad entre ejecuciones."),
        ("tsp_05_heatmap_distancias.png",
         "Matriz completa de distancias entre las 24 ciudades. Evidencia por qué "
         "Galápagos genera el arco más largo y cuáles ciudades están más cercanas entre sí."),
    ]
    for nombre, desc in viz:
        items.append(Paragraph(f"• <b>{nombre}:</b> {desc}", s["bullet"]))
    return items


def seccion_granjero(s):
    items = []
    items.append(PageBreak())
    items.append(HRFlowable(width="100%", thickness=2, color=AZUL_MED))
    items.append(Paragraph("  PROBLEMA B: El acertijo del granjero y el bote", s["h1"]))

    items.append(Paragraph("1. Enunciado del problema", s["h2"]))
    items.append(Paragraph(
        "El taller proporciona una plantilla vacía. El problema clásico: un granjero debe cruzar "
        "un río con un lobo, una cabra y una col. La barca solo lleva al granjero más un elemento. "
        "Si el granjero los deja solos: el lobo come a la cabra, o la cabra come la col. "
        "¿Cómo cruzar todos sin pérdidas?",
        s["body"]
    ))

    items.append(Paragraph("2. Modelado como problema de búsqueda en espacio de estados", s["h2"]))
    items.append(Paragraph(
        "El primer paso fue formalizar el problema como un espacio de estados para aplicar "
        "algoritmos de búsqueda. Representamos cada configuración como una tupla de 4 valores "
        "binarios (0=orilla izquierda, 1=orilla derecha):", s["body"]))
    items.append(Paragraph(
        "estado = (granjero, lobo, cabra, col)\n"
        "inicio  = (0, 0, 0, 0)    →    objetivo = (1, 1, 1, 1)",
        s["code"]
    ))
    items.append(Paragraph(
        "De los 2⁴ = 16 estados posibles, solo <b>10 son válidos</b>. Los 6 ilegales violan "
        "las restricciones (lobo+cabra solos, o cabra+col solos sin el granjero). "
        "El espacio es pequeño, discreto y perfectamente conocido.", s["body"]))

    items.append(Paragraph("3. ¿Por qué elegimos BFS?", s["h2"]))
    items.append(Paragraph(
        "Con el problema modelado como búsqueda en grafos, evaluamos los algoritmos disponibles:",
        s["body_left"]))

    alts = [
        ["DFS (búsqueda en profundidad)", "Simple de implementar",
         "Puede encontrar solución no óptima; puede ciclar sin control"],
        ["A* (búsqueda informada)",       "Óptimo con heurística admisible",
         "Overkill: el espacio es tan pequeño que la heurística no aporta ventaja"],
        ["Backtracking",                  "Explora todas las opciones",
         "Más complejo que BFS para este tamaño de problema"],
        ["<b>BFS ✓</b>",
         "<b>Garantiza solución óptima (mínimo de movimientos), simple y correcto</b>",
         "<b>No hay desventaja relevante para este tamaño de problema</b>"],
    ]
    data = [[Paragraph(f"<b>{h}</b>", s["body"]) for h in ["Algoritmo","Ventaja","Limitación"]]]
    for r in alts:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[4.5*cm, 6*cm, 6.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,4),(-1,4),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "✅ <b>BFS garantiza optimalidad</b> porque explora el espacio de estados por niveles "
        "(primero todos los estados a distancia 1, luego a distancia 2, etc.). El primer estado "
        "objetivo que encuentre estará necesariamente en el nivel más bajo posible, es decir, "
        "con el mínimo número de movimientos. Para este problema, la solución óptima tiene "
        "<b>7 pasos</b> (existen dos soluciones simétricas equivalentes, ambas de 7 pasos).",
        s["highlight"]
    ))

    items.append(Paragraph("4. Implementación del BFS", s["h2"]))
    items.append(Paragraph(
        "El algoritmo mantiene una cola (deque) de estados por explorar y un conjunto de estados "
        "visitados para evitar ciclos. Cada elemento de la cola lleva el estado actual, el "
        "camino recorrido y las acciones realizadas:", s["body"]))
    items.append(Paragraph(
        "queue = [(estado, camino, acciones)]\n"
        "visited = {estado_inicial}\n"
        "while queue:\n"
        "    estado, camino, acciones = queue.popleft()\n"
        "    if estado == objetivo: return camino, acciones\n"
        "    for (siguiente, accion) in successors(estado):\n"
        "        if siguiente not in visited:\n"
        "            visited.add(siguiente)\n"
        "            queue.append((siguiente, camino+[siguiente], acciones+[accion]))",
        s["code"]
    ))
    items.append(Paragraph(
        "La función <i>successors(estado)</i> genera hasta 4 estados vecinos (granjero cruza "
        "solo, o con lobo, cabra o col) y filtra los ilegales con <i>is_valid(estado)</i>.",
        s["body"]
    ))

    items.append(Paragraph("5. Solución encontrada: 7 pasos (óptima)", s["h2"]))
    pasos = [
        ["0","Inicio","G, L, C, V","—"],
        ["1","Granjero cruza con Cabra →","L, V","G, C"],
        ["2","Granjero cruza solo ←","G, L, V","C"],
        ["3","Granjero cruza con Lobo →","V","G, L, C"],
        ["4","Granjero cruza con Cabra ←","G, C, V","L"],
        ["5","Granjero cruza con Col →","C","G, L, V"],
        ["6","Granjero cruza solo ←","G, C","L, V"],
        ["7","Granjero cruza con Cabra →","—","G, L, C, V ✓"],
    ]
    data = [[Paragraph(f"<b>{h}</b>", s["body"])
             for h in ["Paso","Acción","Orilla izquierda","Orilla derecha"]]]
    for r in pasos:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[1.3*cm, 6*cm, 4.5*cm, 5.2*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,8),(-1,8),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "Clave del paso 4: el granjero <b>regresa con la cabra</b> para evitar que la cabra "
        "quede sola con el lobo mientras lleva la col. Este movimiento contraintuitivo es el "
        "núcleo de la solución y solo BFS lo encuentra de forma sistemática y garantizada.",
        s["body"]
    ))

    items.append(Paragraph("6. Visualizaciones y su propósito", s["h2"]))
    for nombre, desc in [
        ("farmer_steps.png",
         "8 paneles que muestran el estado de ambas orillas en cada paso. Permite seguir "
         "visualmente el razonamiento y verificar que nunca se violan las restricciones."),
        ("farmer_graph.png",
         "Grafo dirigido de todos los 10 estados válidos con sus transiciones. El camino "
         "solución aparece resaltado en naranja, mostrando la estructura del espacio de búsqueda "
         "y por qué BFS lo recorre en el orden correcto."),
    ]:
        items.append(Paragraph(f"• <b>{nombre}:</b> {desc}", s["bullet"]))
    return items


def seccion_hanoi(s):
    items = []
    items.append(PageBreak())
    items.append(HRFlowable(width="100%", thickness=2, color=AZUL_MED))
    items.append(Paragraph("  PROBLEMA C: La Torre de Hanoi", s["h1"]))

    items.append(Paragraph("1. Enunciado del problema", s["h2"]))
    items.append(Paragraph(
        "El taller proporciona una plantilla vacía. El problema clásico: n discos de tamaños "
        "distintos apilados en la torre A (el mayor abajo). Moverlos todos a la torre C usando "
        "B como auxiliar, respetando: (1) solo se mueve el disco superior de cada torre, "
        "(2) nunca se coloca un disco más grande sobre uno más pequeño.",
        s["body"]
    ))

    items.append(Paragraph("2. ¿Por qué elegimos la solución recursiva?", s["h2"]))
    items.append(Paragraph(
        "La Torre de Hanoi tiene una propiedad matemática fundamental: existe una solución "
        "recursiva <b>exacta y óptima</b> que produce el mínimo posible de movimientos (2ⁿ−1). "
        "Esta propiedad hace que sea uno de los ejemplos más claros del paradigma "
        "<b>Divide y Vencerás</b>.", s["body"]))

    alts = [
        ["Iterativa (con pila)",     "No usa pila de llamadas del SO","Más compleja, menos legible"],
        ["BFS sobre grafo de estados","Encuentra mínimo garantizado",
         "O(3ⁿ) nodos — inviable para n>10; redundante porque la recursión ya es óptima"],
        ["Heurística (greedy)",       "Simple","No siempre óptima sin conocimiento del problema"],
        ["<b>Recursividad ✓</b>",
         "<b>Óptima (2ⁿ−1 movimientos), elegante, demostrable por inducción</b>",
         "<b>Stack overflow teórico para n muy grande (no relevante para n≤30)</b>"],
    ]
    data = [[Paragraph(f"<b>{h}</b>", s["body"]) for h in ["Enfoque","Ventaja","Limitación"]]]
    for r in alts:
        data.append([Paragraph(c, s["body"]) for c in r])
    tbl = Table(data, colWidths=[4.5*cm, 6.5*cm, 6*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,4),(-1,4),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2*cm))
    items.append(Paragraph(
        "✅ <b>Demostración de optimalidad por inducción:</b> para n=1, 1 movimiento = 2¹−1 ✓. "
        "Asumiendo que mover k discos requiere 2ᵏ−1 movimientos (hipótesis), mover k+1 discos "
        "requiere (2ᵏ−1) + 1 + (2ᵏ−1) = 2ᵏ⁺¹−1 movimientos ✓. "
        "Ningún algoritmo puede hacerlo con menos movimientos.",
        s["highlight"]
    ))

    items.append(Paragraph("3. Implementación recursiva", s["h2"]))
    items.append(Paragraph(
        "hanoi(n, origen, destino, auxiliar):\n"
        "    caso base:  si n == 1 → mover(origen, destino)\n"
        "    caso rec.:  hanoi(n-1, origen, auxiliar, destino)  # paso 1\n"
        "                mover(origen, destino)                   # paso 2\n"
        "                hanoi(n-1, auxiliar, destino, origen)   # paso 3",
        s["code"]
    ))
    items.append(Paragraph(
        "Los tres pasos son: mover los n−1 discos superiores a la torre auxiliar, mover el "
        "disco más grande a la torre destino, y mover los n−1 discos desde la auxiliar al destino. "
        "Cada llamada recursiva garantiza que el disco más grande siempre se mueve a una torre vacía "
        "o a una torre que solo tiene discos más grandes.", s["body"]))

    items.append(Paragraph("4. Construcción de estados y visualización", s["h2"]))
    items.append(Paragraph(
        "Adicionalmente, implementamos la construcción de todos los estados intermedios para "
        "habilitar la animación y el análisis:", s["body"]))
    for item in [
        "build_states(): simula el movimiento de discos aplicando cada movimiento sobre un diccionario "
        "de torres, guardando una copia del estado tras cada paso.",
        "mostrar_animacion(): usa matplotlib.animation.FuncAnimation para animar los 2ⁿ−1 estados.",
        "build_full_state_graph(): construye el grafo completo de 3ⁿ estados posibles usando "
        "product(['A','B','C'], repeat=n) y conecta los estados con movimientos legales.",
        "draw_hanoi_graph_bonito(): visualiza el grafo tipo red con el camino óptimo resaltado "
        "(disponible para n≤5 para evitar grafos con cientos de nodos).",
    ]:
        items.append(Paragraph(f"• {item}", s["bullet"]))

    items.append(Paragraph("5. Complejidad y resultados", s["h2"]))
    hanoi_data = [
        ["n discos", "Movimientos (2ⁿ−1)", "Nodos en grafo (3ⁿ)", "Tiempo estimado"],
        ["1", "1", "3", "< 0.001s"],
        ["2", "3", "9", "< 0.001s"],
        ["3", "7", "27", "< 0.01s"],
        ["4 (default)", "15", "81", "< 0.1s"],
        ["5", "31", "243", "~ 0.5s"],
        ["10", "1.023", "59.049", "~ 1s (sin grafo)"],
        ["20", "1.048.575", "3.486.784.401", "~ 1s (sin grafo)"],
    ]
    data = [[Paragraph(f"<b>{c}</b>" if i==0 else c, s["body"]) for c in row]
            for i, row in enumerate(hanoi_data)]
    tbl = Table(data, colWidths=[3*cm, 4.5*cm, 4.5*cm, 5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("BACKGROUND",    (0,4),(-1,4),  VERDE_CL),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.2*cm))

    items.append(Paragraph("6. Visualizaciones y su propósito", s["h2"]))
    for nombre, desc in [
        ("Torre_1.png", "Estado inicial con los n discos en la torre A ordenados de mayor a menor."),
        ("Torre_2.png",
         "Grafo completo de estados posibles (3ⁿ nodos). Cada nodo es una configuración válida "
         "de discos. Las aristas son movimientos legales. El camino óptimo se resalta en naranja, "
         "demostrando visualmente que la recursión encuentra la ruta más corta en el grafo."),
        ("Torre_3.png",
         "Barras de frecuencia de uso de cada torre como origen y como destino. Confirma que "
         "la torre A es la mayor fuente y la torre C el mayor destino, con B como intermediaria equilibrada."),
        ("Torre_4.png",
         "Curva O(2ⁿ−1) para n=1..12 con el valor del n ejecutado marcado. Ilustra el crecimiento "
         "exponencial y por qué para n>20 la visualización animada ya no es práctica."),
    ]:
        items.append(Paragraph(f"• <b>{nombre}:</b> {desc}", s["bullet"]))
    return items


def seccion_conclusiones(s):
    items = []
    items.append(PageBreak())
    items.append(HRFlowable(width="100%", thickness=2, color=AZUL_MED))
    items.append(Paragraph("  COMPARATIVA Y CONCLUSIONES", s["h1"]))

    items.append(Paragraph("Comparativa de enfoques algorítmicos", s["h2"]))
    comp = [
        ["Problema","Algoritmo","Paradigma","Optimalidad","Complejidad","Uso en IA"],
        ["TSP","Nearest Neighbor","Greedy","Sub-óptimo","O(n²)","Baseline"],
        ["TSP","ACO","Metaheurística","Aprox. ≈opt","O(it·m·n²)","Optimización combinatoria"],
        ["TSP","2-opt","Búsqueda local","Óptimo local","O(n²)/iter","Post-proceso clásico"],
        ["Granjero","BFS","Búsq. sistemática","Óptimo global","O(V+E)","Planificación"],
        ["Hanoi","Recursividad","Divide y Vencerás","Óptimo global","O(2ⁿ)","Razonamiento formal"],
    ]
    data = [[Paragraph(f"<b>{c}</b>" if i==0 else c, s["body"]) for c in row]
            for i, row in enumerate(comp)]
    tbl = Table(data, colWidths=[2.5*cm, 3.3*cm, 3.3*cm, 2.8*cm, 2.5*cm, 3.6*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  AZUL_MED), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, AZUL_CLAR]),
        ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 4), ("FONTSIZE",(0,0),(-1,-1),8.5),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 0.4*cm))

    items.append(Paragraph("Conclusiones", s["h2"]))
    conclusiones = [
        ("<b>TSP – Metaheurísticas para NP-difíciles:</b> cuando la búsqueda exacta es "
         "computacionalmente imposible, las metaheurísticas como ACO ofrecen un balance "
         "excelente entre calidad de solución y tiempo de cómputo. La combinación con 2-opt "
         "demuestra que los enfoques híbridos superan a cualquier algoritmo aislado."),
        ("<b>Granjero – Búsqueda en espacio de estados:</b> problemas de planificación con "
         "restricciones se resuelven elegantemente modelándolos como grafos de estados. BFS "
         "es la elección natural cuando el espacio es pequeño y se requiere optimalidad. "
         "El mismo enfoque escala a sistemas de planificación más complejos."),
        ("<b>Hanoi – Divide y Vencerás:</b> algunos problemas tienen una estructura "
         "matemática que permite soluciones exactas y óptimas por razonamiento inductivo. "
         "La recursión no es solo una técnica de programación; es la expresión directa de "
         "la solución matemática. El grafo de estados demuestra que la solución recursiva "
         "navega el camino más corto en el espacio de 3ⁿ configuraciones posibles."),
        ("<b>Aporte del grupo:</b> todos los problemas fueron desarrollados desde cero, "
         "superando las plantillas del taller con implementaciones completas, visualizaciones "
         "detalladas, análisis estadístico multi-corrida (TSP) y trabajo con datos reales "
         "(capitales del Ecuador). El código está documentado, modular y ejecutable."),
    ]
    for c in conclusiones:
        items.append(Paragraph(f"• {c}", s["bullet"]))
        items.append(Spacer(1, 0.1*cm))

    items.append(Spacer(1, 0.4*cm))
    items.append(Paragraph("Referencias", s["h2"]))
    refs = [
        "Dorigo, M. & Stützle, T. (2004). <i>Ant Colony Optimization</i>. MIT Press.",
        "Russell, S. & Norvig, P. (2020). <i>Artificial Intelligence: A Modern Approach</i> "
            "(4th ed.). Pearson.",
        "Lin, S. (1965). Computer solutions of the traveling salesman problem. "
            "<i>Bell System Technical Journal</i>, 44(10), 2245–2269.",
        "Frame, J.S. (1941). Solution to the problem of the Tower of Hanoi. "
            "<i>American Mathematical Monthly</i>, 48(3), 216–217.",
        "Cormen, T. et al. (2022). <i>Introduction to Algorithms</i> (4th ed.). MIT Press.",
    ]
    for r in refs:
        items.append(Paragraph(f"• {r}", s["bullet"]))
    return items


# ── Main ──────────────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    s = build_styles()
    story = []
    story += portada(s)
    story += seccion_tsp(s)
    story += seccion_granjero(s)
    story += seccion_hanoi(s)
    story += seccion_conclusiones(s)
    doc.build(story)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

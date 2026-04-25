"""
Genera el PDF resumen del Taller 1 con imágenes embebidas.
Uso: python _Soluciones/Grupo5/generar_resumen_taller.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Image, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT

BASE    = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE, "images")
OUTPUT  = os.path.join(BASE, "resumen_taller1_grupo5.pdf")

W, H = A4

# ── Paleta ───────────────────────────────────────────────────────────────────
C_PRIMARY   = colors.HexColor("#1a237e")
C_SECONDARY = colors.HexColor("#3949ab")
C_ACCENT    = colors.HexColor("#e53935")
C_LIGHT     = colors.HexColor("#e8eaf6")
C_DARK      = colors.HexColor("#0d1b5e")
C_GRAY      = colors.HexColor("#757575")
C_GREEN     = colors.HexColor("#2e7d32")

# ── Estilos ──────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle("CT", parent=base["Title"],
            fontSize=22, leading=30, textColor=C_PRIMARY,
            alignment=TA_CENTER, spaceAfter=6),
        "cover_sub": ParagraphStyle("CS", parent=base["Normal"],
            fontSize=13, leading=20, textColor=C_SECONDARY,
            alignment=TA_CENTER, spaceAfter=4),
        "cover_meta": ParagraphStyle("CM", parent=base["Normal"],
            fontSize=10, textColor=C_GRAY, alignment=TA_CENTER),
        "section": ParagraphStyle("SEC", parent=base["Heading1"],
            fontSize=15, leading=20, textColor=C_PRIMARY,
            spaceBefore=18, spaceAfter=8,
            borderPad=4, borderWidth=0),
        "subsection": ParagraphStyle("SUB", parent=base["Heading2"],
            fontSize=12, leading=16, textColor=C_SECONDARY,
            spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("BODY", parent=base["Normal"],
            fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=6),
        "bullet": ParagraphStyle("BULL", parent=base["Normal"],
            fontSize=10, leading=15, leftIndent=16,
            bulletIndent=6, spaceAfter=3),
        "code": ParagraphStyle("CODE", parent=base["Code"],
            fontSize=8, leading=12, backColor=colors.HexColor("#f5f5f5"),
            leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4),
        "caption": ParagraphStyle("CAP", parent=base["Normal"],
            fontSize=8, textColor=C_GRAY, alignment=TA_CENTER,
            spaceAfter=10),
        "conclusion": ParagraphStyle("CONC", parent=base["Normal"],
            fontSize=10, leading=15, alignment=TA_JUSTIFY,
            leftIndent=12, rightIndent=12, spaceAfter=5,
            backColor=C_LIGHT, borderPad=8),
        "member": ParagraphStyle("MEM", parent=base["Normal"],
            fontSize=11, textColor=C_SECONDARY, alignment=TA_CENTER,
            spaceAfter=2),
    }


def img(fname, width=None, height=None):
    path = os.path.join(IMG_DIR, fname)
    if not os.path.exists(path):
        return Spacer(1, 0.1*cm)
    i = Image(path)
    if width:
        ratio = i.imageHeight / i.imageWidth
        i.drawWidth  = width
        i.drawHeight = width * ratio
    elif height:
        ratio = i.imageWidth / i.imageHeight
        i.drawHeight = height
        i.drawWidth  = height * ratio
    return i


def divider(color=C_SECONDARY, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=6)


def section_header(text, s):
    return KeepTogether([
        Paragraph(text, s["section"]),
        divider(C_PRIMARY, 2),
    ])


def build_pdf():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
        rightMargin=2.2*cm, leftMargin=2.2*cm,
        topMargin=2.5*cm, bottomMargin=2.2*cm)
    s = make_styles()
    story = []
    full_w = W - 4.4*cm

    # ════════════════════════════════════════════════════════════
    # PORTADA
    # ════════════════════════════════════════════════════════════
    story += [
        Spacer(1, 1.2*cm),
        Paragraph("TALLER 1", s["cover_sub"]),
        Paragraph("Uso de la Inteligencia Artificial", s["cover_title"]),
        Paragraph("Low Code Engineering", s["cover_title"]),
        Spacer(1, 0.4*cm),
        divider(C_PRIMARY, 3),
        Spacer(1, 0.3*cm),
        Paragraph("Maestría en Inteligencia Artificial · USFQ", s["cover_meta"]),
        Paragraph("Abril 2025", s["cover_meta"]),
        Spacer(1, 0.8*cm),
    ]

    # Logo si existe
    logo = os.path.join(BASE, "usfq-red.png")
    if os.path.exists(logo):
        story.append(Image(logo, width=4*cm, height=4*cm))
        story.append(Spacer(1, 0.6*cm))

    # Integrantes
    story.append(Paragraph("Integrantes – Grupo 5", s["cover_sub"]))
    story.append(Spacer(1, 0.2*cm))
    members = [
        ("Nancy Altamirano",  "A. TSP – Travelling Salesman Problem"),
        ("Gustavo Berru",     "A. TSP – Travelling Salesman Problem"),
        ("Raquel Pacheco",    "B. El acertijo del granjero y el bote"),
        ("Kevin Viteri",      "C. La Torre de Hanoi"),
    ]
    tbl_data = [["Integrante", "Problema asignado"]] + members
    tbl = Table(tbl_data, colWidths=[full_w*0.45, full_w*0.55])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), C_PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_LIGHT, colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#9fa8da")),
        ("ALIGN",         (0,0), (-1,-1), "LEFT"),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [tbl, Spacer(1, 1*cm)]

    # Índice rápido
    story.append(Paragraph("Contenido", s["subsection"]))
    toc = [
        "1. Problema A — TSP (Travelling Salesman Problem)",
        "2. Problema B — El acertijo del granjero y el bote",
        "3. Problema C — La Torre de Hanoi",
        "4. Conclusiones generales",
    ]
    for t in toc:
        story.append(Paragraph(f"&#8226; {t}", s["bullet"]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # PROBLEMA A — TSP
    # ════════════════════════════════════════════════════════════
    story.append(section_header("A. TSP — Travelling Salesman Problem", s))

    story.append(Paragraph("Descripción del problema", s["subsection"]))
    story.append(Paragraph(
        "Dada una lista de ciudades y las distancias entre cada par de ellas, ¿cuál es la ruta "
        "más corta posible que visita cada ciudad exactamente una vez y regresa al origen? "
        "Se trabajó con 10 ciudades del Ecuador: Quito, Guayaquil, Cuenca, Manta, Ambato, "
        "Loja, Esmeraldas, Riobamba, Ibarra y Latacunga.", s["body"]))

    story.append(Paragraph("Representación del problema", s["subsection"]))
    story.append(Paragraph(
        "El TSP se representa como un <b>grafo completo ponderado</b> G = (V, E) donde V son las "
        "ciudades y cada arista (i,j) ∈ E tiene peso igual a la distancia en km. "
        "El objetivo es encontrar el ciclo hamiltoniano de menor peso total.", s["body"]))

    story.append(Paragraph("Algoritmos implementados", s["subsection"]))
    algo_data = [
        ["Algoritmo", "Descripción", "Complejidad"],
        ["Nearest Neighbor", "Greedy: parte de Quito y siempre salta al vecino más cercano no visitado.", "O(n²)"],
        ["ACO", "Colonia de hormigas: 25 hormigas × 150 iteraciones con feromonas, evaporación ρ=0.15 y élite.", "O(iter·n²)"],
        ["2-opt", "Post-proceso: invierte segmentos de la ruta ACO hasta que no haya mejora posible.", "O(n²)/iter"],
    ]
    tbl2 = Table(algo_data, colWidths=[full_w*0.22, full_w*0.56, full_w*0.22])
    tbl2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), C_SECONDARY),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_LIGHT, colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#9fa8da")),
        ("ALIGN",         (0,0), (-1,-1), "LEFT"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [tbl2, Spacer(1, 0.4*cm)]

    story.append(Paragraph("Fórmula de transición ACO", s["subsection"]))
    story.append(Paragraph(
        "Cada hormiga elige el siguiente nodo j desde el nodo i con probabilidad:", s["body"]))
    story.append(Paragraph(
        "p(i→j) = [ τ(i,j)^α · η(i,j)^β ] / Σk [ τ(i,k)^α · η(i,k)^β ]", s["code"]))
    story.append(Paragraph(
        "donde τ son las feromonas (memoria colectiva), η = 1/dist (heurística de distancia), "
        "α=1.2 pondera la explotación y β=2.5 la exploración. Tras cada iteración se evapora: "
        "τ ← (1−ρ)·τ y las 3 hormigas élite refuerzan la mejor ruta global.", s["body"]))

    story.append(Paragraph("Visualizaciones — TSP", s["subsection"]))

    # Fig 1 – comparativa rutas (ancho completo)
    story.append(img("tsp_01_comparativa_rutas.png", width=full_w))
    story.append(Paragraph(
        "Fig. 1 — Comparativa de rutas: Nearest Neighbor (rojo, ★=inicio) vs ACO (azul) "
        "vs ACO+2opt (verde). La mejora sobre el baseline greedy es del 5.2%.", s["caption"]))

    # Fig 2 y 3 en dos columnas
    w2 = full_w * 0.495
    row = Table([[img("tsp_02_convergencia.png", width=w2),
                  img("tsp_03_feromonas.png",    width=w2)]],
                colWidths=[w2, w2])
    row.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                              ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(row)
    story.append(Paragraph(
        "Fig. 2 (izq.) — Convergencia: mejor global y promedio por iteración. "
        "Fig. 3 (der.) — Feromonas τ(i,j) en escala logarítmica en 4 momentos del algoritmo "
        "(el algoritmo aprende qué arcos son buenos).", s["caption"]))

    # Fig 4 y 5 en dos columnas
    row2 = Table([[img("tsp_04_estadisticas.png",      width=w2),
                   img("tsp_05_heatmap_distancias.png", width=w2)]],
                 colWidths=[w2, w2])
    row2.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(row2)
    story.append(Paragraph(
        "Fig. 4 (izq.) — Análisis estadístico de 20 ejecuciones independientes: "
        "media=1307.93 km, desv.est.=0 (el algoritmo converge siempre al mismo óptimo). "
        "Fig. 5 (der.) — Mapa de calor de distancias entre ciudades.", s["caption"]))

    story.append(Paragraph("Conclusión — TSP", s["subsection"]))
    story.append(Paragraph(
        "El TSP es el problema más complejo del taller: es NP-difícil, sin solución exacta "
        "eficiente para n grande. ACO lo resuelve como metaheurística bioinspirada, "
        "combinando memoria colectiva (feromonas) con exploración local (2-opt). "
        "La desviación estándar de 0 en 20 corridas demuestra que la instancia de 10 ciudades "
        "tiene un óptimo muy bien definido y ACO lo encuentra de forma consistente.", s["conclusion"]))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # PROBLEMA B — GRANJERO
    # ════════════════════════════════════════════════════════════
    story.append(section_header("B. El acertijo del granjero y el bote", s))

    story.append(Paragraph("Descripción del problema", s["subsection"]))
    story.append(Paragraph(
        "Un granjero debe cruzar un río con un lobo, una cabra y una col. "
        "La barca solo admite al granjero y un ítem. "
        "Restricciones: lobo y cabra no pueden quedarse solos (el lobo come la cabra), "
        "ni cabra y col (la cabra come la col).", s["body"]))

    story.append(Paragraph("Representación como espacio de estados", s["subsection"]))
    story.append(Paragraph(
        "Cada situación se codifica como una tupla de 4 bits:", s["body"]))
    story.append(Paragraph(
        "estado = (granjero, lobo, cabra, col)   donde 0 = orilla izquierda, 1 = derecha", s["code"]))
    story.append(Paragraph(
        "Estado inicial: (0,0,0,0)  →  Estado objetivo: (1,1,1,1) "
        "El espacio total tiene 2⁴=16 estados posibles; solo 10 son válidos tras descartar "
        "los que violan las restricciones.", s["body"]))

    story.append(Paragraph("Algoritmo: BFS (Búsqueda en Anchura)", s["subsection"]))
    story.append(Paragraph(
        "BFS explora el grafo de estados nivel por nivel, garantizando encontrar "
        "la solución con el menor número de pasos. Desde cada estado, el granjero "
        "puede cruzar solo o llevando uno de los tres ítems que estén en su mismo lado; "
        "solo se encolan los estados válidos.", s["body"]))

    story.append(Paragraph("Visualizaciones — Granjero", s["subsection"]))

    story.append(img("granjero_01_pasos.png", width=full_w))
    story.append(Paragraph(
        "Fig. 6 — Secuencia completa de 7 pasos de la solución óptima. "
        "Cada panel muestra las dos orillas, la posición de cada elemento y la barca. "
        "Solución: llevar cabra | regresar solo | llevar lobo | regresar con cabra | "
        "llevar col | regresar solo | llevar cabra.", s["caption"]))

    story.append(img("granjero_02_grafo.png", width=full_w))
    story.append(Paragraph(
        "Fig. 7 — Grafo completo de transiciones de estados. "
        "Verde = estado inicial, rojo = estado objetivo, azul = nodos en la solución, "
        "gris = estados explorados pero no usados. La ruta óptima se resalta en naranja.", s["caption"]))

    story.append(Paragraph("Conclusión — Granjero", s["subsection"]))
    story.append(Paragraph(
        "El acertijo del granjero es el problema más elegante del taller para ilustrar "
        "búsqueda en espacios de estados. Con solo 10 estados válidos, BFS garantiza "
        "la solución óptima en exactamente 7 movimientos. La clave del modelado es "
        "definir correctamente la función de validez del estado, que descarta "
        "situaciones peligrosas antes de encolarlas.", s["conclusion"]))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # PROBLEMA C — HANOI
    # ════════════════════════════════════════════════════════════
    story.append(section_header("C. La Torre de Hanoi", s))

    story.append(Paragraph("Descripción del problema", s["subsection"]))
    story.append(Paragraph(
        "Mover n discos de la Torre A a la Torre C usando B como auxiliar, "
        "sin colocar nunca un disco más grande sobre uno más pequeño, moviendo un disco a la vez.", s["body"]))

    story.append(Paragraph("Solución recursiva", s["subsection"]))
    story.append(Paragraph(
        "La recursión se basa en una observación fundamental: para mover n discos de A a C:", s["body"]))
    for paso in [
        "1. Mover los n−1 discos superiores de A a B (usando C como auxiliar)",
        "2. Mover el disco más grande de A a C",
        "3. Mover los n−1 discos de B a C (usando A como auxiliar)",
    ]:
        story.append(Paragraph(f"&#8226; {paso}", s["bullet"]))
    story.append(Paragraph(
        "El caso base es n=1: mover directamente de origen a destino. "
        "La solución siempre requiere exactamente <b>2ⁿ − 1 movimientos</b>, "
        "que es también el mínimo posible.", s["body"]))
    story.append(Paragraph(
        "hanoi(n, origen, destino, auxiliar):\n"
        "    if n == 1: mover origen -> destino\n"
        "    else:\n"
        "        hanoi(n-1, origen, auxiliar, destino)\n"
        "        mover origen -> destino\n"
        "        hanoi(n-1, auxiliar, destino, origen)", s["code"]))

    story.append(Paragraph("Visualizaciones — Hanoi", s["subsection"]))

    w3 = full_w * 0.38
    w4 = full_w * 0.59
    row3 = Table([[img("hanoi_01_estado_final.png", width=w3),
                   img("hanoi_02_movimientos.png",  width=w4)]],
                 colWidths=[w3, w4])
    row3.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(row3)
    story.append(Paragraph(
        "Fig. 8 (izq.) — Estado final con 4 discos: todos apilados en Torre C en orden correcto. "
        "Fig. 9 (der.) — Distribución de movimientos: Torre A (origen) genera 8 salidas, "
        "Torre C (destino) recibe 8 entradas, Torre B (auxiliar) equilibra el tráfico.", s["caption"]))

    story.append(img("hanoi_03_complejidad.png", width=full_w * 0.7))
    story.append(Paragraph(
        "Fig. 10 — Curva de complejidad O(2ⁿ − 1). Con 4 discos se necesitan 15 movimientos; "
        "con 10 discos serían 1023; con 20 discos más de 1 millón.", s["caption"]))

    story.append(Paragraph("Conclusión — Hanoi", s["subsection"]))
    story.append(Paragraph(
        "La Torre de Hanoi es el ejemplo más claro de recursión óptima: el algoritmo no solo "
        "encuentra una solución, sino que demuestra formalmente que no puede existir una "
        "solución más corta que 2ⁿ−1 movimientos. La dificultad no está en programarlo "
        "sino en visualizar los 2ⁿ−1 estados y entender por qué la recursión cubre todos "
        "los casos sin solapamiento ni omisión.", s["conclusion"]))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # CONCLUSIONES GENERALES
    # ════════════════════════════════════════════════════════════
    story.append(section_header("4. Conclusiones Generales", s))

    conclusiones = [
        ("<b>Representación es clave:</b> La dificultad de cada problema no radica en la implementación "
         "sino en elegir la representación correcta. El TSP como grafo ponderado, el Granjero "
         "como espacio de estados y Hanoi como árbol de recursión permiten aplicar algoritmos "
         "estándar directamente."),
        ("<b>La IA aprovecha estructura:</b> ACO no resuelve el TSP por fuerza bruta sino "
         "explotando la estructura del problema: las feromonas acumulan experiencia colectiva "
         "y la heurística de distancia guía la exploración. Esto es central en IA: usar "
         "conocimiento del dominio para reducir el espacio de búsqueda."),
        ("<b>Visualización como diagnóstico:</b> Los mapas de feromonas revelan qué aprendió "
         "el algoritmo; la curva de convergencia muestra cuándo dejó de mejorar; el grafo "
         "de estados del Granjero hace visible por qué algunas rutas son inválidas. "
         "Visualizar no es decoración, es comprensión."),
        ("<b>Complejidad vs. exactitud:</b> TSP es NP-difícil (no hay solución exacta eficiente), "
         "Granjero tiene 16 estados (BFS exacto en ms) y Hanoi tiene solución matemática cerrada. "
         "La IA escoge el algoritmo según la naturaleza del problema, no un único enfoque universal."),
        ("<b>Herramientas Low-Code:</b> La IA generativa (Claude, ChatGPT, Copilot) permite "
         "desarrollar soluciones de calidad académica con ciclos rápidos de prototipado, "
         "pero el analista debe validar los resultados, comprender los algoritmos y ajustar "
         "los parámetros según el contexto del problema."),
    ]
    for c in conclusiones:
        story.append(Paragraph(f"&#8226;  {c}", s["body"]))
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(divider(C_PRIMARY, 2))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Ver también: <b>ensayo_chips_analogicos.pdf</b> — "
        "La Evolución de la IA con Chips Analógicos (Grupo 5, Abril 2025)",
        s["cover_meta"]))

    doc.build(story)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()

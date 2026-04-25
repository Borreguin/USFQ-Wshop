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

BASE         = os.path.dirname(__file__)
TSP_DIR      = os.path.join(BASE, "P1_TSP",      "imagenes")
GRANJERO_DIR = os.path.join(BASE, "P2_Granjero", "imagenes")
HANOI_DIR    = os.path.join(BASE, "P3_Torres",   "imagenes")
OUTPUT       = os.path.join(BASE, "resumen_taller1_grupo5.pdf")

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
    # Busca la imagen en la carpeta del problema correspondiente
    if fname.startswith("tsp_"):
        base_dir = TSP_DIR
    elif fname.startswith("granjero_"):
        base_dir = GRANJERO_DIR
    else:
        base_dir = HANOI_DIR
    path = os.path.join(base_dir, fname)
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
        "El <b>Problema del Viajante de Comercio (TSP)</b> es uno de los problemas de optimización "
        "combinatoria más estudiados en Ciencias de la Computación e Inteligencia Artificial. "
        "Dado un conjunto de ciudades y las distancias entre cada par, el objetivo es encontrar "
        "la ruta más corta que visite cada ciudad exactamente una vez y regrese al origen. "
        "Es formalmente <b>NP-difícil</b>: no existe ningún algoritmo conocido que lo resuelva "
        "de forma exacta en tiempo polinomial para instancias grandes. Para este taller se trabajó "
        "con las <b>24 capitales de provincia del Ecuador</b>, desde Quito hasta Galápagos, "
        "utilizando distancias en kilómetros entre coordenadas geográficas reales.", s["body"]))

    story.append(Paragraph("Paso 1 — Modelado del problema", s["subsection"]))
    story.append(Paragraph(
        "El TSP se representó como un <b>grafo completo ponderado G = (V, E)</b>, donde:", s["body"]))
    for item in [
        "<b>V</b> = conjunto de 24 ciudades (nodos), cada una con nombre, latitud y longitud.",
        "<b>E</b> = aristas que conectan cada par de ciudades; su peso es la distancia en km "
        "calculada con la fórmula de Haversine (distancia sobre la esfera terrestre).",
        "<b>Objetivo:</b> encontrar el ciclo hamiltoniano (recorrido que visita todos los nodos "
        "exactamente una vez y cierra el ciclo) de menor peso total.",
    ]:
        story.append(Paragraph(f"&#8226; {item}", s["bullet"]))
    story.append(Paragraph(
        "Se implementó la clase <b>DistanceMatrix</b> que precalcula y almacena en memoria las "
        "24×24 = 576 distancias, y la clase <b>Route</b> que calcula su costo total como propiedad "
        "con acceso O(1). Este diseño evita recalcular distancias en cada iteración del ACO.", s["body"]))

    story.append(Paragraph("Paso 2 — Vecino más cercano (solución inicial)", s["subsection"]))
    story.append(Paragraph(
        "El algoritmo <b>Nearest Neighbor (NN)</b> construye una ruta greedy como punto de partida. "
        "Su lógica paso a paso:", s["body"]))
    for p in [
        "Comenzar en Quito (ciudad 0). Marcarla como visitada.",
        "En cada paso: de la ciudad actual, saltar a la ciudad no visitada más cercana "
        "(menor distancia en la DistanceMatrix).",
        "Repetir hasta haber visitado las 24 ciudades.",
        "Cerrar el ciclo regresando a Quito.",
    ]:
        story.append(Paragraph(f"&#8226; {p}", s["bullet"]))
    story.append(Paragraph(
        "NN es O(n²) y produce una solución de calidad razonable en microsegundos, "
        "pero no es óptima: puede quedar atrapada eligiendo decisiones localmente buenas "
        "que resultan globalmente malas (el conocido problema del 'pasado nocivo').", s["body"]))

    story.append(Paragraph("Paso 3 — Optimización con Colonia de Hormigas (ACO)", s["subsection"]))
    story.append(Paragraph(
        "El <b>Ant Colony Optimization (ACO)</b> es un algoritmo metaheurístico bioinspirado "
        "en el comportamiento de las hormigas reales al buscar caminos al alimento: depositan "
        "feromonas en los caminos que recorren, y las demás hormigas prefieren seguir caminos "
        "con más feromonas, creando un ciclo de retroalimentación positiva. Se ejecutaron "
        "<b>25 hormigas × 150 iteraciones</b>, más 3 hormigas élite que refuerzan la mejor "
        "ruta global.", s["body"]))
    story.append(Paragraph("El proceso por iteración sigue estos pasos:", s["body"]))
    for p in [
        "<b>Inicialización:</b> matriz de feromonas τ(i,j) = 1.0 para todos los pares; "
        "heurística η(i,j) = 1 / dist(i,j).",
        "<b>Construcción de rutas:</b> cada hormiga parte de una ciudad aleatoria y elige "
        "el siguiente destino j con probabilidad probabilística (ruleta sesgada):",
        "<b>Actualización de feromonas:</b> evaporación global τ ← (1−ρ)·τ con ρ=0.15; "
        "luego cada hormiga deposita Δτ = Q/longitud_ruta sobre los arcos que recorrió.",
        "<b>Hormigas élite:</b> la mejor ruta global recibe un depósito adicional de "
        "feromonas multiplicado por 3, lo que acelera la convergencia.",
        "<b>Registro:</b> se guarda el mejor costo de la iteración para graficar la "
        "curva de convergencia.",
    ]:
        story.append(Paragraph(f"&#8226; {p}", s["bullet"]))
    story.append(Paragraph(
        "p(i→j) = [ τ(i,j)^α · η(i,j)^β ] / Σk∈no_visitados [ τ(i,k)^α · η(i,k)^β ]", s["code"]))
    story.append(Paragraph(
        "donde <b>α=1.2</b> controla cuánto pesan las feromonas (explotación de la memoria "
        "colectiva) y <b>β=2.5</b> controla cuánto pesa la heurística de distancia (exploración "
        "de caminos cortos). El balance α/β determina si el algoritmo explora o explota.", s["body"]))

    story.append(Paragraph("Paso 4 — Mejora local con 2-opt", s["subsection"]))
    story.append(Paragraph(
        "Tras cada ejecución del ACO se aplica <b>2-opt</b> como post-proceso de refinamiento local. "
        "El algoritmo examina todos los pares de aristas (i,i+1) y (j,j+1) en la ruta: si "
        "invertir el segmento entre i+1 y j reduce la longitud total, se acepta el intercambio. "
        "Se repite hasta que no haya más mejoras posibles (convergencia local). "
        "2-opt es O(n²) por pasada y típicamente reduce la ruta del ACO entre un 2% y 8%.", s["body"]))

    story.append(Paragraph("Paso 5 — Análisis estadístico (20 ejecuciones)", s["subsection"]))
    story.append(Paragraph(
        "Para medir la robustez del algoritmo se ejecutaron <b>20 corridas independientes</b>, "
        "cada una con semillas aleatorias distintas. Se calcularon: media, desviación estándar, "
        "mínimo y máximo de la longitud óptima encontrada. Una desviación estándar baja indica "
        "que ACO+2opt converge de forma consistente al mismo óptimo, demostrando estabilidad "
        "del método para esta instancia.", s["body"]))

    story.append(Paragraph("Diseño OOP — clases implementadas", s["subsection"]))
    tsp_oop = [
        ["Clase", "Responsabilidad"],
        ["City", "Entidad ciudad: nombre, lat, lon. Método distance_to() con Haversine."],
        ["DistanceMatrix", "Matriz precalculada n×n de distancias. Acceso O(1)."],
        ["Route", "Lista de ciudades con propiedad cost (costo total del ciclo)."],
        ["NearestNeighborSolver", "Construye la ruta greedy como solución inicial."],
        ["AntColonyOptimizer", "ACO: 25 hormigas × 150 iter, feromonas, élite, evaporación."],
        ["TwoOptSolver", "Post-proceso local: invierte segmentos hasta convergencia."],
        ["TSPVisualizer", "Genera las 5 figuras: rutas, convergencia, feromonas, stats, heatmap."],
        ["TSPSolver", "Orquestador: corre n_runs, compara algoritmos, llama visualizador."],
    ]
    tsp_tbl = Table(tsp_oop, colWidths=[full_w*0.30, full_w*0.70])
    tsp_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), C_SECONDARY),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, C_LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.5, C_GRAY),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [tsp_tbl, Spacer(1, 0.3*cm)]

    story.append(Paragraph("Visualizaciones — TSP", s["subsection"]))

    # Fig 1 – comparativa rutas (ancho completo)
    story.append(img("tsp_01_comparativa_rutas.png", width=full_w))
    story.append(Paragraph(
        "Fig. 1 — Comparativa de rutas para las 24 capitales provinciales del Ecuador: "
        "Nearest Neighbor (rojo, ★=Quito) = 2146.62 km vs ACO+2opt (verde) = 2003.89 km. "
        "Mejora del 6.6% sobre el baseline greedy. "
        "Ruta óptima: Ibarra → Tulcán → Nueva Loja → Orellana → Tena → Puyo → Latacunga "
        "→ Ambato → Guaranda → Riobamba → Macas → Azogues → Cuenca → Zamora → Loja "
        "→ Santa Rosa → Machala → Guayaquil → Babahoyo → Portoviejo → Manta "
        "→ Esmeraldas → Sto. Domingo → Quito → Ibarra.", s["caption"]))

    # Fig 2 y 3 en dos columnas
    w2 = full_w * 0.495
    row = Table([[img("tsp_02_convergencia.png", width=w2),
                  img("tsp_03_feromonas.png",    width=w2)]],
                colWidths=[w2, w2])
    row.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                              ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(row)
    story.append(Paragraph(
        "Fig. 2 (izq.) — Curva de convergencia: mejor ruta global y promedio por iteración. "
        "La brecha se reduce conforme las feromonas concentran el comportamiento colectivo. "
        "Fig. 3 (der.) — Evolución de feromonas τ(i,j) en escala logarítmica en 4 momentos "
        "(iter. 1, 50, 100, 150): el algoritmo aprende cuáles arcos son más prometedores.", s["caption"]))

    # Fig 4 y 5 en dos columnas
    row2 = Table([[img("tsp_04_estadisticas.png",      width=w2),
                   img("tsp_05_heatmap_distancias.png", width=w2)]],
                 colWidths=[w2, w2])
    row2.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(row2)
    story.append(Paragraph(
        "Fig. 4 (izq.) — Análisis estadístico de 20 ejecuciones independientes sobre las "
        "24 capitales provinciales: media = 2010.50 km, desv.est. = 10.73 km. "
        "La baja dispersión confirma que ACO+2opt converge de forma consistente. "
        "Fig. 5 (der.) — Mapa de calor de la matriz de distancias Haversine entre las 24 ciudades; "
        "los bloques de baja distancia revelan la agrupación geográfica regional del Ecuador.", s["caption"]))

    story.append(Paragraph("Conclusión — TSP", s["subsection"]))
    story.append(Paragraph(
        "El TSP es NP-difícil: no existe solución exacta eficiente para n grande. "
        "La estrategia de tres capas —Nearest Neighbor como solución inicial, ACO como "
        "exploración metaheurística bioinspirada y 2-opt como refinamiento local— permite "
        "obtener soluciones de alta calidad en segundos. Las feromonas acumulan la experiencia "
        "colectiva de 25 hormigas iteración a iteración, lo que hace que el algoritmo aprenda "
        "progresivamente qué rutas son buenas, sin explorar los (n−1)!/2 ≈ 10²³ circuitos "
        "posibles de las 24 ciudades.", s["conclusion"]))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # PROBLEMA B — GRANJERO
    # ════════════════════════════════════════════════════════════
    story.append(section_header("B. El acertijo del granjero y el bote", s))

    story.append(Paragraph("Descripción del problema", s["subsection"]))
    story.append(Paragraph(
        "Un granjero debe cruzar un río con un lobo, una cabra y una col. "
        "Su barca solo tiene capacidad para él y un ítem a la vez. "
        "El problema impone dos restricciones de seguridad: (1) el lobo y la cabra "
        "no pueden quedarse solos en la misma orilla sin el granjero (el lobo devora la cabra); "
        "(2) la cabra y la col tampoco pueden quedarse solos (la cabra come la col). "
        "¿En qué orden debe cruzar el granjero para llevar todo al otro lado sin pérdidas?", s["body"]))

    story.append(Paragraph("Paso 1 — Modelado como espacio de estados", s["subsection"]))
    story.append(Paragraph(
        "El problema fue modelado como un <b>problema de búsqueda en el espacio de estados</b>, "
        "donde cada estado representa de forma unívoca la ubicación del granjero, el lobo, "
        "la cabra y la col en las dos orillas del río. Cada actor se codifica con un bit "
        "(0 = orilla izquierda, 1 = orilla derecha), formando una tupla de 4 elementos:", s["body"]))
    story.append(Paragraph(
        "estado = (granjero, lobo, cabra, col)   con valores en {0, 1}\n"
        "Estado inicial:  (0, 0, 0, 0)  — todos en la orilla izquierda\n"
        "Estado objetivo: (1, 1, 1, 1)  — todos en la orilla derecha", s["code"]))
    story.append(Paragraph(
        "El espacio de estados total contiene <b>2⁴ = 16 combinaciones posibles</b>. "
        "Sin embargo, muchas de ellas son inválidas porque violan las restricciones "
        "de seguridad. Al aplicar la función de validez, solo quedan <b>10 estados "
        "seguros</b> que el algoritmo puede usar.", s["body"]))

    story.append(Paragraph("Paso 2 — Función de validez del estado", s["subsection"]))
    story.append(Paragraph(
        "Antes de encolar cualquier estado nuevo, se verifica que no sea peligroso. "
        "Un estado es <b>inválido</b> si se cumple alguna de estas condiciones:", s["body"]))
    for cond in [
        "El lobo y la cabra están en la misma orilla <b>Y</b> el granjero no está con ellos "
        "(lobo come la cabra).",
        "La cabra y la col están en la misma orilla <b>Y</b> el granjero no está con ellos "
        "(cabra come la col).",
    ]:
        story.append(Paragraph(f"&#8226; {cond}", s["bullet"]))
    story.append(Paragraph(
        "Esta validación se implementó en el método <b>State.is_valid()</b> del dataclass "
        "inmutable (frozen=True). Al ser inmutable y hashable, cada estado puede almacenarse "
        "en un conjunto de visitados sin colisiones, lo que es fundamental para la eficiencia "
        "del BFS.", s["body"]))

    story.append(Paragraph("Paso 3 — Generación de sucesores", s["subsection"]))
    story.append(Paragraph(
        "Desde cualquier estado válido, el granjero puede realizar hasta 4 acciones: "
        "cruzar solo, o llevar consigo el lobo, la cabra o la col (siempre que el ítem "
        "elegido esté en su misma orilla). El método <b>State.successors()</b> genera "
        "todos los estados alcanzables y filtra los inválidos antes de devolverlos:", s["body"]))
    story.append(Paragraph(
        "para cada accion en [solo, lobo, cabra, col]:\n"
        "    si el item esta en el mismo lado que el granjero:\n"
        "        nuevo_estado = mover granjero + item al otro lado\n"
        "        si nuevo_estado.is_valid():\n"
        "            agregar (nuevo_estado, etiqueta_accion) a resultados", s["code"]))

    story.append(Paragraph("Paso 4 — Algoritmo BFS (Búsqueda en Anchura)", s["subsection"]))
    story.append(Paragraph(
        "Para resolver el problema se utilizó el algoritmo <b>BFS (Breadth-First Search — "
        "Búsqueda en Anchura)</b>, un algoritmo fundamental de Inteligencia Artificial que "
        "sirve para explorar todos los posibles estados de un problema <i>nivel por nivel</i>, "
        "garantizando encontrar la solución con el <b>menor número de pasos posible</b> "
        "(solución óptima en longitud de camino).", s["body"]))
    story.append(Paragraph("El funcionamiento paso a paso del BFS es:", s["body"]))
    for p in [
        "<b>Inicializar:</b> encolar el estado inicial (0,0,0,0) con su camino [(inicio, 'Inicio')]. "
        "Crear un conjunto de visitados = {(0,0,0,0)}.",
        "<b>Desencolar:</b> tomar el primer elemento de la cola (FIFO). Si es el estado objetivo "
        "(1,1,1,1), devolver el camino completo — se encontró la solución óptima.",
        "<b>Expandir:</b> llamar a State.successors() para obtener todos los estados válidos "
        "alcanzables desde el estado actual.",
        "<b>Filtrar y encolar:</b> para cada sucesor no visitado: marcarlo como visitado y "
        "encolarlo junto con el camino extendido (camino_actual + [(sucesor, acción)]).",
        "<b>Repetir</b> desde el paso 2 hasta encontrar el objetivo o agotar la cola.",
    ]:
        story.append(Paragraph(f"&#8226; {p}", s["bullet"]))
    story.append(Paragraph(
        "BFS garantiza la optimalidad porque explora todos los caminos de longitud 1 antes "
        "de los de longitud 2, todos los de longitud 2 antes de los de longitud 3, y así "
        "sucesivamente. El primer camino que llega al estado objetivo es necesariamente el "
        "más corto. En este problema, BFS encuentra la solución en <b>exactamente 7 pasos</b>.", s["body"]))

    story.append(Paragraph("Paso 5 — Solución encontrada (7 movimientos óptimos)", s["subsection"]))
    sol_data = [
        ["Paso", "Acción", "Estado (F, L, G, C)"],
        ["0", "Inicio", "(0, 0, 0, 0) — Izq: Granjero, Lobo, Cabra, Col  |  Der: vacía"],
        ["1", "Granjero -> con Cabra", "(1, 0, 1, 0) — Izq: Lobo, Col  |  Der: Granjero, Cabra"],
        ["2", "Granjero <- solo", "(0, 0, 1, 0) — Izq: Granjero, Lobo, Col  |  Der: Cabra"],
        ["3", "Granjero -> con Lobo", "(1, 1, 1, 0) — Izq: Col  |  Der: Granjero, Lobo, Cabra"],
        ["4", "Granjero <- con Cabra *", "(0, 1, 0, 0) — Izq: Granjero, Cabra, Col  |  Der: Lobo"],
        ["5", "Granjero -> con Col", "(1, 1, 0, 1) — Izq: Cabra  |  Der: Granjero, Lobo, Col"],
        ["6", "Granjero <- solo", "(0, 1, 0, 1) — Izq: Granjero, Cabra  |  Der: Lobo, Col"],
        ["7", "Granjero -> con Cabra", "(1, 1, 1, 1) — Izq: vacía  |  Der: Granjero, Lobo, Cabra, Col"],
    ]
    sol_tbl = Table(sol_data, colWidths=[full_w*0.10, full_w*0.35, full_w*0.55])
    sol_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), C_PRIMARY),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND",  (0,7), (-1,7), colors.HexColor("#e8f5e9")),
        ("FONTNAME",    (0,7), (-1,7), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0,8), (-1,8), C_GREEN),
        ("FONTNAME",    (0,8), (-1,8), "Helvetica-Bold"),
        ("BACKGROUND",  (0,8), (-1,8), colors.HexColor("#c8e6c9")),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ALIGN",       (0,0), (0,-1), "CENTER"),
        ("ALIGN",       (1,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,7), [colors.white, C_LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.5, C_GRAY),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(sol_tbl)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "* Paso 4 — movimiento contraintuitivo: tras el paso 3, el estado (1,1,1,0) tiene "
        "a lobo y cabra juntos en la orilla derecha. Si el granjero regresara solo, dejaría "
        "al lobo con la cabra sin supervisión (estado inválido). La única opción válida es "
        "regresar con la cabra, produciendo (0,1,0,0). Hay que 'retroceder' para avanzar.", s["body"]))

    story.append(Paragraph("Diseño OOP — clases implementadas", s["subsection"]))
    farm_oop = [
        ["Función / Módulo", "Responsabilidad", "Detalle"],
        ["is_valid(state)", "Valida que el estado no viole las restricciones.",
         "Descarta lobo+cabra o cabra+col solos."],
        ["successors(state)", "Genera los estados alcanzables desde el estado actual.",
         "Hasta 4 acciones: cruzar solo o con lobo/cabra/col."],
        ["bfs()", "Búsqueda en anchura desde START hasta GOAL.",
         "Cola FIFO; retorna path y actions."],
        ["build_graph()", "Construye el grafo dirigido completo de estados válidos.",
         "Usa NetworkX DiGraph con aristas etiquetadas."],
        ["visualize_steps()", "Genera imagen con los 8 paneles de la secuencia.",
         "Guarda granjero_01_pasos.png (150 dpi)."],
        ["visualize_graph()", "Dibuja el grafo de estados con el camino destacado.",
         "Guarda granjero_02_grafo.png (150 dpi)."],
    ]
    farm_tbl = Table(farm_oop, colWidths=[full_w*0.28, full_w*0.42, full_w*0.30])
    farm_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), C_SECONDARY),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, C_LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.5, C_GRAY),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(farm_tbl)
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Visualizaciones — Granjero", s["subsection"]))

    story.append(img("granjero_01_pasos.png", width=full_w))
    story.append(Paragraph(
        "Fig. 6 — Secuencia de solución BFS: 8 paneles (Paso 0 al Paso 7). "
        "Cada panel muestra la orilla izquierda (verde), el río (azul) y la orilla derecha (verde). "
        "Los elementos se identifican con etiquetas: G-Granjero, L-Lobo, C-Cabra, V-Col. "
        "La barca aparece junto al granjero en cada paso. "
        "El paso 4 (Granjero regresa con Cabra) es el movimiento contraintuitivo "
        "que evita dejar al lobo con la cabra sin supervisión.", s["caption"]))

    story.append(img("granjero_02_grafo.png", width=full_w))
    story.append(Paragraph(
        "Fig. 7 — Grafo de estados del acertijo construido por BFS. "
        "Cada nodo muestra la distribución de actores por orilla (I=izquierda, D=derecha; "
        "Ø=vacía). De los 16 estados matemáticamente posibles, 10 son válidos. "
        "Verde = estado inicial I:G,L,C,V / D:Ø. "
        "Rojo = estado objetivo I:Ø / D:G,L,C,V. "
        "Azul = estados del camino óptimo. Gris = estados válidos no usados. "
        "Naranja = aristas del camino solución de 7 pasos.", s["caption"]))

    story.append(Paragraph("Conclusión — Granjero", s["subsection"]))
    story.append(Paragraph(
        "El acertijo del granjero demuestra cómo un problema que parece informal puede "
        "formalizarse rigurosamente como búsqueda en espacio de estados. El modelado con "
        "una tupla de 4 bits captura completamente la situación; BFS garantiza la solución "
        "óptima de 7 movimientos; y la función is_valid() actúa como filtro que elimina "
        "estados peligrosos antes de explorarlos. Este enfoque es generalizable a cualquier "
        "problema de planificación con restricciones: modelar el estado, definir las "
        "transiciones válidas, y aplicar BFS para encontrar el camino más corto.", s["conclusion"]))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # PROBLEMA C — HANOI
    # ════════════════════════════════════════════════════════════
    story.append(section_header("C. La Torre de Hanoi", s))

    # ── Descripción ──────────────────────────────────────────────────────────
    story.append(Paragraph("Descripción del problema", s["subsection"]))
    story.append(Paragraph(
        "La Torre de Hanoi es un clásico de la informática teórica. Se tienen <b>n discos</b> de "
        "distintos tamaños apilados en la Torre A (el más grande abajo), y dos torres vacías B y C. "
        "El objetivo es trasladar <i>todos</i> los discos a la Torre C siguiendo dos reglas: "
        "(1) solo se mueve un disco a la vez, y (2) nunca se coloca un disco más grande "
        "sobre uno más pequeño. El problema fue formulado por Édouard Lucas en 1883 y sigue "
        "siendo referencia obligatoria en cursos de algoritmos porque exhibe una estructura "
        "recursiva perfectamente simétrica.", s["body"]))

    # ── Divide y Vencerás ────────────────────────────────────────────────────
    story.append(Paragraph("Estrategia: Divide y Vencerás", s["subsection"]))
    story.append(Paragraph(
        "La clave es reconocer que mover n discos de A a C es equivalente a tres subproblemas "
        "independientes. Esta descomposición es posible porque el disco más grande es "
        "completamente independiente de los n−1 discos que están encima de él:", s["body"]))
    for paso in [
        "<b>Paso 1:</b> Mover los n−1 discos superiores de A hacia B, usando C como auxiliar.",
        "<b>Paso 2:</b> Mover el disco más grande (disco n) directamente de A hacia C (un solo movimiento).",
        "<b>Paso 3:</b> Mover los n−1 discos de B hacia C, usando A como auxiliar.",
    ]:
        story.append(Paragraph(f"&#8226; {paso}", s["bullet"]))
    story.append(Paragraph(
        "Los pasos 1 y 3 son instancias del <i>mismo problema</i> con n−1 discos, lo que permite "
        "aplicar la misma estrategia recursivamente. El caso base es trivial: con n=1 disco, "
        "se mueve directamente de origen a destino sin ninguna complejidad.", s["body"]))

    # ── Algoritmo recursivo ──────────────────────────────────────────────────
    story.append(Paragraph("Algoritmo recursivo", s["subsection"]))
    story.append(Paragraph(
        "El pseudocódigo captura la estrategia de manera exacta. La función recibe el número "
        "de discos y los nombres de las tres torres (origen, destino, auxiliar):", s["body"]))
    story.append(Paragraph(
        "def hanoi(n, origen, destino, auxiliar):\n"
        "    # Caso base: mover directamente\n"
        "    if n == 1:\n"
        "        mover disco de origen -> destino\n"
        "        return\n"
        "    # Paso 1: liberar el disco grande\n"
        "    hanoi(n-1, origen, auxiliar, destino)\n"
        "    # Paso 2: mover el disco mas grande\n"
        "    mover disco de origen -> destino\n"
        "    # Paso 3: reconstruir sobre el disco grande\n"
        "    hanoi(n-1, auxiliar, destino, origen)", s["code"]))
    story.append(Paragraph(
        "Obsérvese que los roles de las torres <b>rotan</b> en cada llamada recursiva: "
        "lo que era destino pasa a ser auxiliar y viceversa. Este intercambio es lo que "
        "garantiza que nunca se violen las restricciones del problema.", s["body"]))

    # ── Árbol de recursión ───────────────────────────────────────────────────
    story.append(Paragraph("Árbol de recursión (n = 3)", s["subsection"]))
    story.append(Paragraph(
        "Con n=3, la ejecución genera 7 movimientos. El árbol de llamadas ilustra cómo "
        "se descompone el problema:", s["body"]))
    story.append(Paragraph(
        "hanoi(3, A, C, B)\n"
        "  +--> hanoi(2, A, B, C)\n"
        "  |      +--> hanoi(1, A, C, B)  =>  mueve disco 1: A -> C\n"
        "  |      +--> mover disco 2:          A -> B\n"
        "  |      +--> hanoi(1, C, B, A)  =>  mueve disco 1: C -> B\n"
        "  +--> mover disco 3:                 A -> C\n"
        "  +--> hanoi(2, B, C, A)\n"
        "         +--> hanoi(1, B, A, C)  =>  mueve disco 1: B -> A\n"
        "         +--> mover disco 2:          B -> C\n"
        "         +--> hanoi(1, A, C, B)  =>  mueve disco 1: A -> C", s["code"]))
    story.append(Paragraph(
        "Cada nivel del árbol duplica el trabajo: el nivel 0 tiene 1 llamada, "
        "el nivel 1 tiene 2, el nivel 2 tiene 4, hasta llegar a las 2ⁿ⁻¹ llamadas "
        "base que corresponden a los movimientos reales.", s["body"]))

    # ── Demostración matemática ───────────────────────────────────────────────
    story.append(Paragraph("Demostración matemática de la complejidad", s["subsection"]))
    story.append(Paragraph(
        "Sea T(n) el número de movimientos necesarios para n discos. "
        "La recurrencia se formula directamente desde el algoritmo:", s["body"]))
    story.append(Paragraph(
        "T(1) = 1                        (caso base)\n"
        "T(n) = 2 * T(n-1) + 1          (2 subproblemas de n-1 + 1 movimiento del disco grande)", s["code"]))
    story.append(Paragraph(
        "Desarrollando la recurrencia por sustitución repetida:", s["body"]))
    story.append(Paragraph(
        "T(n) = 2*T(n-1) + 1\n"
        "     = 2*(2*T(n-2) + 1) + 1   =  4*T(n-2) + 3\n"
        "     = 4*(2*T(n-3) + 1) + 3   =  8*T(n-3) + 7\n"
        "     = ...\n"
        "     = 2^(n-1) * T(1) + (2^(n-1) - 1)\n"
        "     = 2^(n-1) + 2^(n-1) - 1\n"
        "     = 2^n - 1", s["code"]))
    story.append(Paragraph(
        "Este resultado es también un <b>mínimo absoluto</b>: se puede demostrar por inducción "
        "que cualquier secuencia válida de movimientos requiere al menos 2ⁿ−1 pasos, "
        "lo que convierte al algoritmo recursivo en óptimo.", s["body"]))

    # ── Tabla de complejidad ─────────────────────────────────────────────────
    story.append(Paragraph("Tabla de complejidad: discos vs movimientos", s["subsection"]))
    tbl_data = [["Discos (n)", "Movimientos (2ⁿ−1)", "Tiempo estimado (1 mov/s)"]]
    tiempos  = ["1 s", "3 s", "7 s", "15 s", "31 s", "1 min 3 s",
                "2 min 7 s", "4 min 15 s", "8 min 31 s",
                "~17 min", "~34 min", "~1.1 h", "~2.3 h", "~4.6 h",
                "~9.1 h", "~18.2 h", "~36.4 h", "~3.0 días",
                "~6.0 días", "~12.0 días"]
    for i in range(1, 21):
        tbl_data.append([str(i), f"{2**i - 1:,}", tiempos[i-1]])
    tbl = Table(tbl_data, colWidths=[full_w*0.28, full_w*0.36, full_w*0.36])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  C_PRIMARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1,-1),  8),
        ("ALIGN",       (0, 0), (-1,-1),  "CENTER"),
        ("VALIGN",      (0, 0), (-1,-1),  "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT]),
        ("GRID",        (0, 0), (-1,-1),  0.5, C_GRAY),
        ("TOPPADDING",  (0, 0), (-1,-1),  3),
        ("BOTTOMPADDING",(0,0), (-1,-1),  3),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.2*cm))

    # ── Diseño OOP ───────────────────────────────────────────────────────────
    story.append(Paragraph("Diseño orientado a objetos (OOP)", s["subsection"]))
    story.append(Paragraph(
        "La solución se implementa con cinco clases que siguen el principio de "
        "<i>responsabilidad única</i>:", s["body"]))
    oop_rows = [
        ["Clase", "Responsabilidad", "Métodos clave"],
        ["Disk", "Entidad: disco con tamaño y color", "color (property)"],
        ["Tower", "Pila de discos; valida restricciones", "push(disk), pop(), top"],
        ["HanoiState", "Instantánea de las tres torres", "snapshot()"],
        ["HanoiSolver", "Ejecuta la recursión y registra movimientos", "_recurse(n, towers, src, dst, aux)"],
        ["HanoiVisualizer", "Genera animación y gráficos de análisis", "animate(), plot_analysis(), save_all()"],
    ]
    oop_tbl = Table(oop_rows, colWidths=[full_w*0.22, full_w*0.44, full_w*0.34])
    oop_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  C_SECONDARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (0, -1),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1,-1),  8),
        ("ALIGN",       (0, 0), (-1,-1),  "LEFT"),
        ("VALIGN",      (0, 0), (-1,-1),  "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT]),
        ("GRID",        (0, 0), (-1,-1),  0.5, C_GRAY),
        ("TOPPADDING",  (0, 0), (-1,-1),  4),
        ("BOTTOMPADDING",(0,0), (-1,-1),  4),
        ("LEFTPADDING", (0, 0), (-1,-1),  6),
    ]))
    story.append(oop_tbl)
    story.append(Paragraph(
        "La clase <b>Tower.push()</b> lanza ValueError si se intenta colocar un disco mayor "
        "sobre uno menor, lo que convierte la restricción del puzzle en una invariante "
        "verificada en tiempo de ejecución. <b>HanoiSolver._recurse()</b> opera directamente "
        "sobre las instancias Tower, mientras que <b>HanoiState</b> captura una copia profunda "
        "de las tres torres en cada paso para permitir la visualización completa.", s["body"]))

    # ── Visualizaciones ──────────────────────────────────────────────────────
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

    # ── Interpretación del espacio de estados ────────────────────────────────
    story.append(Paragraph(
        "El espacio completo de estados de la Torre de Hanoi", s["subsection"]))
    story.append(Paragraph(
        "El problema puede también analizarse desde la perspectiva de teoría de grafos. "
        "Para <b>4 discos</b>, el espacio completo de soluciones se puede representar como "
        "un grafo donde cada nodo es una configuración posible de los discos en las tres "
        "torres y cada arista es un movimiento legal entre dos configuraciones.", s["body"]))
    story.append(Paragraph(
        "Las dimensiones de este grafo son:", s["body"]))
    for item in [
        "<b>81 nodos</b> — corresponden a todas las configuraciones posibles de los 4 discos "
        "en las tres torres. Cada disco puede estar en cualquiera de las 3 torres "
        "independientemente, lo que da 3⁴ = 81 estados totales.",
        "<b>120 aristas</b> — representan los movimientos legales entre configuraciones "
        "(solo se puede mover el disco del tope de una torre al tope de otra, siempre que "
        "sea más pequeño).",
        "<b>Nodo verde</b> = estado inicial: todos los discos apilados en la Torre A "
        "en orden decreciente (disco 4 abajo, disco 1 arriba).",
        "<b>Nodo rojo</b> = estado final: todos los discos apilados en la Torre C "
        "en el mismo orden correcto.",
        "<b>Camino naranja</b> = solución óptima de 15 movimientos generada por el "
        "algoritmo recursivo de divide y vencerás.",
    ]:
        story.append(Paragraph(f"&#8226; {item}", s["bullet"]))
    story.append(Paragraph(
        "Aunque el problema tiene 81 configuraciones posibles y 120 movimientos legales, "
        "el algoritmo recursivo <b>no explora todo el grafo</b>. A diferencia del BFS "
        "(que sí recorre el grafo completo nivel por nivel), la estrategia de "
        "<b>divide y vencerás</b> sigue un camino directo y determinístico: en cada nivel "
        "de recursión sabe exactamente qué disco mover y hacia dónde, sin necesidad de "
        "explorar alternativas. Esto garantiza llegar al objetivo en el <b>mínimo número "
        "de movimientos: 15 para 4 discos</b>, con una profundidad de pila de recursión "
        "de solo n niveles.", s["body"]))

    # Tabla comparativa: BFS vs Recursión para Hanoi
    comp_data = [
        ["Criterio", "BFS sobre el grafo", "Recursión (Divide y vencerás)"],
        ["Nodos visitados", "Hasta 81 (todos alcanzables)", "Solo los 15 del camino óptimo"],
        ["Garantía de óptimo", "Sí (primero en llegar)", "Sí (demostrado matemáticamente)"],
        ["Memoria requerida", "O(3^n) — todos los estados", "O(n) — pila de recursión"],
        ["Tiempo de cómputo", "O(3^n) — explora el grafo", "O(2^n) — solo los movimientos"],
        ["Aplicable a n grande", "No (explosión exponencial)", "Sí (eficiente en memoria)"],
    ]
    comp_tbl = Table(comp_data, colWidths=[full_w*0.32, full_w*0.34, full_w*0.34])
    comp_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), C_SECONDARY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT]),
        ("GRID",        (0, 0), (-1, -1), 0.5, C_GRAY),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(comp_tbl)
    story.append(Spacer(1, 0.2*cm))

    # ── Conclusión ───────────────────────────────────────────────────────────
    story.append(Paragraph("Conclusión — Hanoi", s["subsection"]))
    story.append(Paragraph(
        "La Torre de Hanoi demuestra tres principios fundamentales de la algoritmia: "
        "(1) <b>Recursión óptima</b> — el algoritmo encuentra la solución mínima sin necesidad "
        "de exploración adicional; (2) <b>Complejidad exponencial inevitable</b> — T(n) = 2ⁿ−1 "
        "no es una debilidad del algoritmo sino un límite inferior del problema; y "
        "(3) <b>Separación de responsabilidades en OOP</b> — al distribuir la lógica entre "
        "Disk, Tower, HanoiSolver y HanoiVisualizer, el código es legible, testeable y "
        "extensible (por ejemplo, para 10 discos o para nuevas reglas de movimiento) "
        "sin modificar ninguna clase existente.", s["conclusion"]))

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

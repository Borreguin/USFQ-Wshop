# TALLER 1 – Uso de la Inteligencia Artificial / Low Code Engineering

**Curso:** Maestría en Inteligencia Artificial – USFQ  
**Rama:** `g5_na`  
**Fecha:** Abril 2026

---

## Integrantes del Grupo

| Integrante | Problema |
|---|---|
| Nancy Altamirano | A. TSP – Travelling Salesman Problem |
| Gustavo Berru | A. TSP – Travelling Salesman Problem |
| Raquel Pacheco | B. El acertijo del granjero y el bote |
| Kevin Viteri | C. La Torre de Hanoi |

---

## 1. Problemas Resueltos

---

### A. TSP – Travelling Salesman Problem

**Archivo:** `P1_TSP/TSP.py`

#### Descripción del problema

El Problema del Viajante (TSP) consiste en encontrar la ruta más corta que pase exactamente una vez por cada ciudad y regrese al punto de partida. Es un problema NP-difícil: con *n* ciudades existen *(n-1)!/2* rutas posibles. Para 24 ciudades esto equivale a más de 10²³ combinaciones, haciendo inviable la búsqueda exhaustiva.

#### Instancia utilizada

Se utilizan las **24 capitales de provincia del Ecuador**:

| # | Ciudad | Provincia | Longitud | Latitud |
|---|---|---|---|---|
| 1 | Quito | Pichincha | -78.5249 | -0.2295 |
| 2 | Guayaquil | Guayas | -79.9000 | -2.1894 |
| 3 | Cuenca | Azuay | -79.0059 | -2.9001 |
| 4 | Ambato | Tungurahua | -78.6197 | -1.2491 |
| 5 | Riobamba | Chimborazo | -78.6464 | -1.6635 |
| 6 | Ibarra | Imbabura | -78.1228 | 0.3517 |
| 7 | Latacunga | Cotopaxi | -78.6165 | -0.9319 |
| 8 | Loja | Loja | -79.2045 | -3.9931 |
| 9 | Esmeraldas | Esmeraldas | -79.7000 | 0.9592 |
| 10 | Portoviejo | Manabí | -80.4541 | -1.0546 |
| 11 | Machala | El Oro | -79.9605 | -3.2581 |
| 12 | Babahoyo | Los Ríos | -79.5340 | -1.8013 |
| 13 | Guaranda | Bolívar | -79.0016 | -1.5933 |
| 14 | Azogues | Cañar | -78.8467 | -2.7392 |
| 15 | Tulcán | Carchi | -77.7175 | 0.8117 |
| 16 | Macas | Morona Santiago | -78.1167 | -2.3000 |
| 17 | Tena | Napo | -77.8167 | -0.9833 |
| 18 | El Coca | Orellana | -76.9871 | -0.4625 |
| 19 | Puyo | Pastaza | -77.9897 | -1.4924 |
| 20 | Santa Elena | Santa Elena | -80.8586 | -2.2267 |
| 21 | Santo Domingo | Sto. Domingo de los Tsáchilas | -79.1719 | -0.2523 |
| 22 | Lago Agrio | Sucumbíos | -76.8874 | 0.0856 |
| 23 | Zamora | Zamora Chinchipe | -78.9501 | -4.0668 |
| 24 | Pto. Baquerizo | Galápagos | -89.6158 | -0.9005 |

Las distancias se calculan con la fórmula de distancia euclidiana ajustada para coordenadas geográficas:

```
dx = (lon_i - lon_j) × cos(lat_i) × 111.32 km/°
dy = (lat_i - lat_j) × 110.57 km/°
dist(i,j) = √(dx² + dy²)
```

#### Algoritmos implementados

**1. Nearest Neighbor (Vecino más cercano)**

Algoritmo greedy de referencia. Comienza en Quito y en cada paso se desplaza a la ciudad no visitada más cercana. Complejidad O(n²). Produce soluciones rápidas pero sub-óptimas.

**2. Ant Colony Optimization (ACO)**

Metaheurística bioinspirada en el comportamiento de colonias de hormigas. Cada hormiga construye una solución seleccionando el siguiente nodo con probabilidad:

```
p(i→j) = [τ(i,j)^α · η(i,j)^β] / Σ_k [τ(i,k)^α · η(i,k)^β]
```

donde τ(i,j) = feromona, η(i,j) = 1/dist (visibilidad), α=1.2, β=2.5.  
Evaporación: τ(i,j) ← (1−ρ)·τ(i,j) + ΣΔτ, con ρ=0.15, Q=500.  
Parámetros: **30 hormigas × 200 iteraciones**, 3 hormigas élite.

**3. 2-opt (Búsqueda local)**

Refinamiento post-ACO. Itera sobre pares de arcos e invierte el segmento si reduce el costo. Repite hasta no encontrar mejora. Garantiza un óptimo local.

#### Visualizaciones generadas

| Archivo | Descripción |
|---|---|
| `Imágenes/tsp_01_comparativa_rutas.png` | Mapas de las 3 rutas con costos |
| `Imágenes/tsp_02_convergencia.png` | Curva de convergencia ACO + histograma de mejoras |
| `Imágenes/tsp_03_feromonas.png` | Heatmaps de feromonas τ(i,j) en 4 momentos |
| `Imágenes/tsp_04_estadisticas.png` | Análisis estadístico de 20 corridas |
| `Imágenes/tsp_05_heatmap_distancias.png` | Matriz de distancias entre las 24 ciudades |

---

### B. El acertijo del granjero y el bote

**Archivo:** `P2_Granjero/Acertijo.py`

#### Descripción del problema

Un granjero debe cruzar un río con un lobo, una cabra y una col. La barca solo tiene capacidad para el granjero y un elemento más. Restricciones:
- El lobo y la cabra no pueden quedarse solos (el lobo se come la cabra).
- La cabra y la col no pueden quedarse solos (la cabra se come la col).

#### Representación del estado

Cada estado es una tupla `(granjero, lobo, cabra, col)` donde `0` = orilla izquierda y `1` = orilla derecha:

- **Estado inicial:** `(0, 0, 0, 0)` — todos en la orilla izquierda
- **Estado objetivo:** `(1, 1, 1, 1)` — todos en la orilla derecha
- **Estados posibles:** 2⁴ = **16**
- **Estados válidos:** **10** (6 son ilegales por las restricciones)

#### Algoritmo: BFS (Búsqueda en Anchura)

BFS explora el espacio de estados por niveles, garantizando encontrar la solución con el **mínimo número de movimientos**. Complejidad O(V + E).

#### Solución encontrada: 7 pasos

| Paso | Acción | Orilla izquierda | Orilla derecha |
|---|---|---|---|
| 0 | Inicio | G, L, C, V | — |
| 1 | Granjero cruza con Cabra → | L, V | G, C |
| 2 | Granjero cruza solo ← | G, L, V | C |
| 3 | Granjero cruza con Lobo → | V | G, L, C |
| 4 | Granjero cruza con Cabra ← | G, C, V | L |
| 5 | Granjero cruza con Col → | C | G, L, V |
| 6 | Granjero cruza solo ← | G, C | L, V |
| 7 | Granjero cruza con Cabra → | — | G, L, C, V |

#### Visualizaciones generadas

| Archivo | Descripción |
|---|---|
| `Imágenes/farmer_steps.png` | Paneles con la secuencia completa de solución |
| `Imágenes/farmer_graph.png` | Grafo de transiciones con camino óptimo en naranja |

---

### C. La Torre de Hanoi

**Archivo:** `P3_Torres/Torres.py`

#### Descripción del problema

Dado un conjunto de *n* discos apilados en la torre A (de mayor a menor), moverlos todos a la torre C usando B como auxiliar. Restricciones: solo se mueve un disco a la vez (el superior), nunca un disco más grande sobre uno más pequeño.

#### Algoritmo: Recursividad (Divide y Vencerás)

```
hanoi(n, origen, destino, auxiliar):
    if n == 1:
        mover disco de origen a destino
    else:
        hanoi(n-1, origen, auxiliar, destino)   # mover n-1 a auxiliar
        mover disco n de origen a destino        # mover el más grande
        hanoi(n-1, auxiliar, destino, origen)   # mover n-1 a destino
```

#### Complejidad: 2ⁿ − 1 movimientos (mínimo demostrado)

| n discos | Movimientos | Nodos en grafo | Aristas |
|---|---|---|---|
| 1 | 1 | 3 | 2 |
| 2 | 3 | 9 | 8 |
| 3 | 7 | 27 | 24 |
| 4 | 15 | 81 | 120 |
| 5 | 31 | 243 | — |

Programa ejecutado con **4 discos** → 15 movimientos. Grafo disponible para n ≤ 5.

#### Visualizaciones generadas

| Archivo | Descripción |
|---|---|
| `Imágenes/Torre_1.png` | Estado inicial de las torres |
| `Imágenes/Torre_2.png` | Grafo completo de estados con camino óptimo |
| `Imágenes/Torre_3.png` | Distribución de movimientos por torre |
| `Imágenes/Torre_4.png` | Curva de complejidad O(2ⁿ) para n=1..12 |

---

## 2. Comparativa de Enfoques

| Problema | Algoritmo | Tipo | Optimalidad | Complejidad |
|---|---|---|---|---|
| TSP | Nearest Neighbor | Greedy | Sub-óptimo | O(n²) |
| TSP | ACO | Metaheurística | Aproximado | O(iter × ants × n²) |
| TSP | 2-opt | Búsqueda local | Mejora local | O(n²) por iteración |
| Granjero | BFS | Búsqueda sistemática | **Óptimo** | O(V + E) |
| Hanoi | Recursividad | Divide y Vencerás | **Óptimo** | O(2ⁿ) |

---

## 3. Uso de la IA – Planeamiento de Tareas

El taller requiere usar herramientas de IA para el planeamiento y gestión de las actividades. El Grupo 5 utilizó **Notion** como plataforma de planificación colaborativa asistida por IA.

### ¿Cómo se aplicó la IA en el planeamiento?

1. **Definición de tareas con IA:** Se utilizó Claude (Anthropic) para desglosar cada problema del taller (TSP, Granjero, Hanoi) en subtareas concretas: investigación del algoritmo, implementación, generación de visualizaciones, documentación y presentación.

2. **Estructura del tablero en Notion:** Se creó un proyecto con las siguientes columnas de seguimiento:
   - **Por hacer** – tareas identificadas pero no iniciadas
   - **En progreso** – tareas activas con responsable asignado
   - **En revisión** – tareas completadas pendientes de validación del grupo
   - **Completado** – entregables finalizados

3. **Distribución de responsabilidades:**

| Integrante | Tarea principal | Tareas de soporte |
|---|---|---|
| Nancy Altamirano | TSP – Implementación ACO + 2-opt | Coordinación general, README |
| Gustavo Berru | TSP – Visualizaciones y análisis estadístico | Revisión de parámetros ACO |
| Raquel Pacheco | Granjero – BFS + visualizaciones | Documentación del algoritmo |
| Kevin Viteri | Hanoi – Recursividad + grafo de estados | Animaciones y gráficas |

4. **Hitos del proyecto:**

| Hito | Fecha límite | Estado |
|---|---|---|
| Implementación TSP base | Semana 1 | ✅ Completado |
| Implementación Granjero y Hanoi | Semana 1 | ✅ Completado |
| Visualizaciones y gráficas | Semana 2 | ✅ Completado |
| README y documentación técnica | Semana 2 | ✅ Completado |
| PDF resumen del taller | Semana 2 | ✅ Completado |
| Ensayo chips analógicos | Semana 2 | ✅ Completado |
| Revisión final y commit | Semana 2 | ✅ Completado |

5. **Uso de IA para generar código:** Todo el desarrollo fue asistido por Claude Code (CLI), que generó, revisó y corrigió el código de cada problema, sugirió los parámetros óptimos para ACO, y ayudó a estructurar las visualizaciones con matplotlib y networkx.

### Enlace al proyecto de planificación

[Proyecto de Planificación – Taller 1 IA Grupo 5](https://www.notion.so/Proyecto-de-planificaci-n-Taller-1-IA-Grupo-5-9fe3570dff2d48359703271a0cc9b6d4?source=copy_link)

---

## 4. La Evolución de la IA – Ensayo sobre Chips Analógicos

**Archivo:** `Doc/ensayo_chips_analogicos.pdf`

### Descripción del ensayo

El ensayo aborda la pregunta: **¿cuáles son los últimos avances en inteligencia artificial impulsados por chips analógicos?** El análisis parte de las transcripciones y contenido de tres videos del taller y se desarrolla en torno a cuatro ejes temáticos.

### Videos de referencia

Los tres videos analizados para el ensayo son:

| # | URL | Tema central |
|---|---|---|
| 1 | https://www.youtube.com/watch?v=GVsUOuSjvcg | Computación analógica y el futuro del hardware para IA |
| 2 | https://www.youtube.com/watch?v=6Y6FJVqzivc | Memristores y redes neuronales analógicas |
| 3 | https://www.youtube.com/watch?v=trPFX6yAC3E | Procesadores neuromórficos y eficiencia energética |

### Estructura del ensayo

**1. El límite de la computación digital para IA**

Los modelos de IA modernos (GPT-4, LLaMA, Gemini) requieren centros de datos que consumen entre 10 y 100 MW de energía. La arquitectura digital von Neumann enfrenta el "memory wall": el cuello de botella entre CPU/GPU y la memoria principal limita el rendimiento. Los chips digitales realizan operaciones exactas de 32/64 bits cuando las redes neuronales solo necesitan precisión reducida (FP8, INT4), desperdiciando transistores y energía.

**2. Computación analógica: operar en el dominio físico**

Los chips analógicos realizan operaciones matemáticas mediante fenómenos físicos directos:
- **Multiplicación:** la ley de Ohm (V = I·R) calcula productos en hardware sin ciclos de reloj
- **Suma:** la ley de Kirchhoff suma corrientes de múltiples resistencias en paralelo instantáneamente
- **Activación:** transistores en región sub-umbral emulan funciones sigmoides naturalmente

Esto permite implementar la operación de multiplicación-acumulación (MAC) —el núcleo de las redes neuronales— con 10–100× menos energía que con aritmética digital.

**3. Memristores: memoria con cómputo integrado**

El memristor es un componente pasivo cuya resistencia cambia según la corriente que ha pasado por él (memoria). Esto lo convierte en el substrato ideal para el "Computing-in-Memory" (CIM):
- Los pesos de una red neuronal se almacenan como niveles de conductancia del memristor
- La inferencia ocurre físicamente al aplicar voltajes de entrada: la corriente resultante es el producto matricial
- No hay transferencia de datos entre memoria y procesador: el cálculo ocurre donde están los pesos

Empresas como IBM Research, Intel (Loihi), y startups como Mythic AI e Innatera han demostrado chips CIM con memristores operando a <1 mW para inferencia en el borde (edge AI).

**4. Procesadores neuromórficos: inspiración biológica**

Los procesadores neuromórficos (Intel Loihi 2, IBM TrueNorth, BrainScaleS) replican la arquitectura del cerebro:
- **Procesamiento basado en eventos (spiking):** solo procesan cuando hay un cambio, igual que las neuronas biológicas
- **Aprendizaje local (STDP):** los pesos se actualizan localmente sin backpropagation global
- **Masiva paralelización:** millones de núcleos simples en lugar de pocos núcleos potentes

Intel Loihi 2 (2021) tiene 1 millón de neuronas artificiales en 31 mm² y consume 1000× menos energía que una GPU equivalente para tareas de inferencia esparcida.

**5. Perspectivas y desafíos**

La computación analógica enfrenta retos: variabilidad de fabricación, ruido inherente, dificultad para entrenar (los gradientes no se propagan fácilmente en hardware analógico), y menor precisión numérica. Sin embargo, para inferencia en el borde (IoT, wearables, vehículos autónomos), la ventaja energética supera estas limitaciones. El consenso académico apunta a arquitecturas **híbridas digital-analógicas**: entrenamiento en la nube con hardware digital preciso, e inferencia en el borde con chips analógicos ultraeficientes.

### Conclusión del ensayo

La era de la IA estará definida no solo por los algoritmos, sino por el hardware que los ejecuta. Los chips analógicos y neuromórficos representan el siguiente salto evolutivo: pasar de simular la inteligencia en hardware digital genérico a implementarla en substrato físico especializado, reduciendo el consumo energético en órdenes de magnitud. Este cambio habilitará IA ubicua, permanente y eficiente en dispositivos que hoy no tienen capacidad de cómputo.

---

## 5. Estructura del repositorio

```
_Soluciones/Grupo5/
├── Doc/
│   ├── README.md                          # Este archivo
│   ├── ensayo_chips_analogicos.pdf        # Ensayo literal C
│   ├── generar_resumen_taller.py          # Script para regenerar el PDF
│   └── resumen_taller1_grupo5.pdf         # Informe completo del taller
├── Imágenes/                              # Todas las imágenes generadas
│   ├── tsp_01_comparativa_rutas.png
│   ├── tsp_02_convergencia.png
│   ├── tsp_03_feromonas.png
│   ├── tsp_04_estadisticas.png
│   ├── tsp_05_heatmap_distancias.png
│   ├── farmer_steps.png
│   ├── farmer_graph.png
│   ├── Torre_1.png
│   ├── Torre_2.png
│   ├── Torre_3.png
│   └── Torre_4.png
├── P1_TSP/
│   └── TSP.py                             # ACO + 2-opt, 24 capitales de provincia
├── P2_Granjero/
│   ├── Acertijo.py                        # BFS + visualizaciones
│   └── solucion_granjero.txt             # Solución en texto
├── P3_Torres/
│   └── Torres.py                          # Hanoi recursivo + animación + grafo
└── usfq-red.png
```

---

## 6. Instalación y Ejecución

### Dependencias

```bash
pip install numpy matplotlib networkx reportlab
```

### Ejecutar cada problema

```bash
# Desde la raíz del repositorio (USFQ-Wshop/)

# Problema A: TSP con 24 ciudades
python _Soluciones/Grupo5/P1_TSP/TSP.py

# Problema B: Acertijo del granjero
python _Soluciones/Grupo5/P2_Granjero/Acertijo.py

# Problema C: Torre de Hanoi
python _Soluciones/Grupo5/P3_Torres/Torres.py

# Regenerar el PDF resumen
python _Soluciones/Grupo5/Doc/generar_resumen_taller.py
```

### Notas de ejecución

- **TSP:** el análisis de 20 corridas puede tardar 3-8 minutos dependiendo del hardware.
- **Torres:** al ejecutarse solicita el número de discos por consola (recomendado: 3-5). El grafo solo se genera para n ≤ 5.
- **Granjero:** no requiere parámetros; genera las imágenes automáticamente.

---

## 7. Referencias

- Dorigo, M. & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press.
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Lin, S. (1965). Computer solutions of the traveling salesman problem. *Bell System Technical Journal*, 44(10), 2245–2269.
- Frame, J.S. (1941). Solution to the problem of the Tower of Hanoi. *American Mathematical Monthly*, 48(3), 216–217.

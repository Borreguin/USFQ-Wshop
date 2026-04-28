# TALLER 1 – Uso de la Inteligencia Artificial / Low Code Engineering

**Curso:** Maestría en Inteligencia Artificial – USFQ  
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



## 3. Enlace al proyecto de planificación

[Proyecto de Planificación – Taller 1 IA Grupo 5](https://www.notion.so/Proyecto-de-planificaci-n-Taller-1-IA-Grupo-5-9fe3570dff2d48359703271a0cc9b6d4?source=copy_link)



## 4. Estructura del repositorio

```
_Soluciones/Grupo5/
├── Doc/
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
└── README.md
```

---

## 5. Instalación y Ejecución

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


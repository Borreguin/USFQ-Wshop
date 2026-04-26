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

Algoritmo greedy de referencia. Comienza en la ciudad 0 (Quito), y en cada paso se desplaza a la ciudad no visitada más cercana. Tiene complejidad O(n²) y produce soluciones sub-óptimas pero rápidas.

**2. Ant Colony Optimization (ACO)**

Metaheurística bioinspirada en el comportamiento de colonias de hormigas. Cada hormiga construye una solución completa seleccionando el siguiente nodo con probabilidad:

```
p(i→j) = [τ(i,j)^α · η(i,j)^β] / Σ_k [τ(i,k)^α · η(i,k)^β]
```

donde:
- `τ(i,j)` = nivel de feromona en el arco (i,j)
- `η(i,j) = 1/dist(i,j)` = información heurística (visibilidad)
- `α = 1.2` = peso de la feromona (explotación)
- `β = 2.5` = peso de la heurística (exploración)

Tras cada iteración, las feromonas se evaporan y se refuerzan:

```
τ(i,j) ← (1-ρ) · τ(i,j) + Σ Δτ_k(i,j)
Δτ_k(i,j) = Q / costo_ruta_k  (si la ruta k usa el arco (i,j))
```

Parámetros utilizados: 30 hormigas, 200 iteraciones, ρ=0.15, Q=500, 3 hormigas élite.

**3. 2-opt (Búsqueda local)**

Refinamiento post-ACO. Itera sobre todos los pares de arcos (i,j) de la ruta e invierte el segmento entre ellos si reduce el costo total. Repite hasta que no haya mejora posible. Complejidad por iteración: O(n²).

#### Visualizaciones generadas

| Archivo | Descripción |
|---|---|
| `tsp_01_comparativa_rutas.png` | Mapas de las 3 rutas con costos |
| `tsp_02_convergencia.png` | Curva de convergencia ACO + histograma de mejoras |
| `tsp_03_feromonas.png` | Heatmaps de feromonas en 4 momentos del algoritmo |
| `tsp_04_estadisticas.png` | Histograma, boxplot y tabla de 20 corridas |
| `tsp_05_heatmap_distancias.png` | Matriz completa de distancias entre las 24 ciudades |

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

BFS explora el espacio de estados por niveles (profundidad creciente), garantizando encontrar la solución con el **mínimo número de movimientos**. Complejidad: O(V + E) sobre el grafo de estados.

En cada paso, el granjero puede:
1. Cruzar solo
2. Cruzar con el lobo
3. Cruzar con la cabra
4. Cruzar con la col

Solo se aceptan transiciones que lleven a estados válidos.

#### Solución encontrada

BFS encuentra la solución óptima en **7 pasos**:

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
| `P2_Granjero/farmer_steps.png` | 8 paneles con la secuencia visual de la solución |
| `P2_Granjero/farmer_graph.png` | Grafo completo de estados con camino óptimo en naranja |

---

### C. La Torre de Hanoi

**Archivo:** `P3_Torres/Torres.py`

#### Descripción del problema

Dado un conjunto de *n* discos de tamaños distintos apilados en la torre A (de mayor a menor), el objetivo es moverlos todos a la torre C usando la torre B como auxiliar, respetando:
- Solo se puede mover un disco a la vez (el disco superior de una torre).
- Nunca se puede colocar un disco más grande sobre uno más pequeño.

#### Algoritmo: Recursividad (Divide y Vencerás)

La solución recursiva se basa en el siguiente razonamiento:

```
hanoi(n, origen, destino, auxiliar):
    if n == 1:
        mover disco de origen a destino
    else:
        hanoi(n-1, origen, auxiliar, destino)   # mover n-1 discos a auxiliar
        mover disco n de origen a destino        # mover el más grande
        hanoi(n-1, auxiliar, destino, origen)   # mover n-1 discos a destino
```

#### Complejidad y resultados

La cantidad mínima de movimientos es exactamente **2ⁿ − 1** (demostrado por inducción):

| n discos | Movimientos | Nodos en grafo | Aristas |
|---|---|---|---|
| 1 | 1 | 3 | 2 |
| 2 | 3 | 9 | 8 |
| 3 | 7 | 27 | 24 |
| 4 | 15 | 81 | 120 |
| 5 | 31 | 243 | — |

El programa ejecuta el algoritmo con **4 discos por defecto** (configurable hasta 10), produciendo 15 movimientos óptimos. El grafo completo de estados para n=4 tiene 81 nodos (3⁴ posibles combinaciones de posición de discos).

#### Características del programa

- **Animación interactiva:** visualización cuadro a cuadro del proceso de resolución con fondo oscuro y discos de colores
- **Grafo de estados tipo red:** muestra todos los 3ⁿ estados posibles con el camino óptimo resaltado en naranja (solo para n ≤ 5)
- **Análisis de movimientos:** barras con la distribución de movimientos por torre (origen/destino)
- **Curva de complejidad:** gráfico O(2ⁿ−1) para n=1 hasta n=12

#### Visualizaciones generadas

| Archivo | Descripción |
|---|---|
| `P3_Torres/Figure_1.png` | Estado inicial de las torres |
| `P3_Torres/Figure_2.png` | Grafo completo de estados con camino óptimo |
| `P3_Torres/Figure_3.png` | Distribución de movimientos por torre |
| `P3_Torres/Figure_4.png` | Curva de complejidad O(2ⁿ) |

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

## 3. Planeamiento en Notion

[Proyecto de Planificación – Taller 1 IA Grupo 5](https://www.notion.so/Proyecto-de-planificaci-n-Taller-1-IA-Grupo-5-9fe3570dff2d48359703271a0cc9b6d4)

---

## 4. Ensayo: Evolución de la IA con Chips Analógicos

**Archivo:** `ensayo_chips_analogicos.pdf`

Ensayo basado en las transcripciones de los videos del taller sobre computación analógica y su impacto en la IA moderna. Analiza la evolución desde los chips digitales hacia arquitecturas híbridas con memristores, la eficiencia energética de la computación analógica, y el potencial futuro de los procesadores neuromórficos.

---

## 5. Estructura del repositorio

```
_Soluciones/Grupo5/
├── P1_TSP/
│   ├── TSP.py                         # ACO + 2-opt, 24 capitales de provincia
│   ├── imagenes/
│   │   ├── tsp_01_comparativa_rutas.png
│   │   ├── tsp_02_convergencia.png
│   │   ├── tsp_03_feromonas.png
│   │   ├── tsp_04_estadisticas.png
│   │   └── tsp_05_heatmap_distancias.png
│   └── tsp_0[1-5]_*.png               # Copia de imágenes en raíz P1_TSP
├── P2_Granjero/
│   ├── Acertijo.py                    # BFS + visualizaciones
│   ├── farmer_steps.png               # Secuencia de 8 pasos
│   ├── farmer_graph.png               # Grafo de estados
│   └── solucion_granjero.txt          # Solución en texto
├── P3_Torres/
│   ├── Torres.py                      # Hanoi recursivo + animación + grafo
│   ├── Figure_1.png                   # Estado inicial
│   ├── Figure_2.png                   # Grafo de estados
│   ├── Figure_3.png                   # Movimientos por torre
│   └── Figure_4.png                   # Curva de complejidad
├── images/                            # Imágenes adicionales del taller
├── generar_resumen_taller.py          # Script para regenerar el PDF resumen
├── resumen_taller1_grupo5.pdf         # Informe completo del taller
└── ensayo_chips_analogicos.pdf        # Ensayo literal C
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
python _Soluciones/Grupo5/generar_resumen_taller.py
```

### Notas de ejecución

- **TSP:** el análisis de 20 corridas puede tardar 3-8 minutos dependiendo del hardware.
- **Torres:** al ejecutarse sin argumentos, solicita el número de discos por consola (recomendado: 3-5). El grafo completo de estados solo se genera para n ≤ 5.
- **Granjero:** no requiere parámetros; genera las imágenes automáticamente en `P2_Granjero/`.

---

## 7. Referencias

- Dorigo, M. & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press.
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Lin, S. (1965). Computer solutions of the traveling salesman problem. *Bell System Technical Journal*, 44(10), 2245–2269.
- Frame, J.S. (1941). Solution to the problem of the Tower of Hanoi. *American Mathematical Monthly*, 48(3), 216–217.

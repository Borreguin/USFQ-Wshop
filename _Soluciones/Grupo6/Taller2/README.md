# WorkShop-USFQ
## Taller 2 — Uso de Algoritmos de Búsqueda

- **Nombre del grupo**: Grupo 6
- **Integrantes del grupo**:
  * Stan Mora
  * Tais Rodriguez
  * Santiago Bonilla

---

## Descripción

El objetivo es utilizar algoritmos de búsqueda para resolver los laberintos propuestos,
visualizar los resultados y comparar el comportamiento de al menos 2 algoritmos.

> **Nota:** El repositorio original menciona 3 laberintos, sin embargo se encontraron 4 archivos
> (`laberinto1.txt` … `laberinto4.txt`). Se resuelven los **4 laberintos**.

---

## A. Representación del laberinto como grafo

El laberinto se carga desde un archivo `.txt` donde cada celda puede ser:

| Símbolo | Significado |
|---------|-------------|
| `#`     | Pared (no transitable) |
| ` `     | Pasillo libre |
| `E`     | Entrada — nodo inicio |
| `S`     | Salida — nodo destino |

Cada celda transitable (`' '`, `E`, `S`) se convierte en un **nodo** del grafo.
Dos nodos son **vecinos** (arista peso 1) si son adyacentes horizontal o verticalmente y ambos son transitables.
El grafo se representa como un diccionario de adyacencia: `{(fila, col): [(fila', col'), ...]}`

---

## B. Algoritmos de búsqueda

Se implementaron 3 algoritmos en `P1/P1_solvers.py`:

### BFS — Breadth-First Search
Explora por niveles (anchura). Garantiza el **camino más corto** en grafos no ponderados.
- Estructura: Cola (FIFO) — Completitud: Sí — Optimalidad: Sí

### A* (A-estrella)
Búsqueda informada con heurística de **distancia Manhattan** al destino: `f(n) = g(n) + h(n)`.
- Estructura: Cola de prioridad (min-heap) — Completitud: Sí — Optimalidad: Sí

### DFS — Depth-First Search
Explora en profundidad. **No garantiza** el camino más corto.
- Estructura: Pila (LIFO) — Completitud: Sí — Optimalidad: No

---

## Métricas de evaluación

| Métrica | Descripción |
|---------|-------------|
| **Pasos** | Longitud del camino encontrado (celdas − 1) |
| **Nodos explorados** | Cuántos nodos se procesaron antes de encontrar la solución |
| **Tiempo (ms)** | Tiempo de ejecución del algoritmo |

---

## Resultados

### Laberinto 1 — Pequeño (9×11, 43 nodos)

![Laberinto 1](images/laberinto1_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |    14 |              43 |       0.114 |
| A\*       |    14 |              36 |       0.128 |
| DFS       |    30 |              34 |       0.045 |

---

### Laberinto 2 — Mediano (15×29, 201 nodos)

![Laberinto 2](images/laberinto2_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |    44 |             183 |       0.096 |
| A\*       |    44 |             140 |       0.181 |
| DFS       |    72 |              89 |       0.051 |

---

### Laberinto 3 — Grande (23×109, 1270 nodos)

![Laberinto 3](images/laberinto3_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |   344 |             859 |       0.855 |
| A\*       |   344 |             788 |       2.223 |
| DFS       |   558 |             578 |       0.842 |

---

### Laberinto 4 — Grande Extendido (38×109, 2651 nodos)

![Laberinto 4](images/laberinto4_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |   472 |            2410 |       1.750 |
| A\*       |   472 |            2064 |       4.521 |
| DFS       |  1086 |            1535 |       1.634 |

---

## Métricas de evaluación propuestas

Para comparar los algoritmos de forma objetiva se definen tres métricas:

### M1 — Ratio de optimalidad
Mide qué tan corto es el camino encontrado respecto al óptimo (BFS/A\* como referencia).

```
Ratio_optimalidad = pasos_algoritmo / pasos_óptimos
```
Valor ideal: **1.0** (igual al óptimo). Un valor mayor indica un camino más largo.

### M2 — Eficiencia de exploración
Mide qué porcentaje del grafo fue necesario explorar para encontrar la solución.

```
Eficiencia = (nodos_explorados / total_nodos_grafo) × 100 %
```
Valor ideal: **lo más bajo posible**. Menos exploración = algoritmo más dirigido.

### M3 — Tiempo de ejecución (ms)
Tiempo real de cómputo. Depende del hardware, pero sirve para comparar algoritmos en el mismo entorno.

---

## Análisis comparativo con métricas

### M1 — Ratio de optimalidad (pasos encontrados / pasos óptimos)

| Laberinto    | Nodos | BFS  | A\*  | DFS  |
|--------------|------:|-----:|-----:|-----:|
| Laberinto 1  |    43 | 1.00 | 1.00 | **2.14** |
| Laberinto 2  |   201 | 1.00 | 1.00 | **1.64** |
| Laberinto 3  |  1270 | 1.00 | 1.00 | **1.62** |
| Laberinto 4  |  2651 | 1.00 | 1.00 | **2.30** |

BFS y A\* siempre obtienen ratio 1.00 (camino óptimo garantizado).
DFS obtiene entre 1.6× y 2.3× más pasos que el óptimo.

### M2 — Eficiencia de exploración (% del grafo explorado)

| Laberinto    | Total nodos | BFS    | A\*    | DFS    |
|--------------|------------:|-------:|-------:|-------:|
| Laberinto 1  |          43 | 100.0% | 83.7%  | 79.1%  |
| Laberinto 2  |         201 |  91.0% | 69.7%  | 44.3%  |
| Laberinto 3  |        1270 |  67.6% | 62.0%  | 45.5%  |
| Laberinto 4  |        2651 |  90.9% | 77.9%  | 57.9%  |

DFS explora menos nodos, pero a costa de un camino no óptimo.
A\* reduce la exploración respecto a BFS gracias a la heurística, manteniendo optimalidad.

### M3 — Tiempo de ejecución (ms)

| Laberinto    | BFS    | A\*    | DFS    |
|--------------|-------:|-------:|-------:|
| Laberinto 1  |  0.028 |  0.057 |  0.022 |
| Laberinto 2  |  0.092 |  0.252 |  0.141 |
| Laberinto 3  |  0.964 |  1.749 |  1.158 |
| Laberinto 4  |  2.537 |  5.296 |  2.445 |

BFS resulta más rápido en tiempo real porque su estructura (cola simple) tiene menor sobrecarga que el heap de A\*.
En laberintos muy grandes y con heurística más precisa, A\* sería más rápido.

---

## Conclusiones

1. **BFS** garantiza el camino más corto y es el más rápido en tiempo de ejecución, pero explora casi la totalidad del grafo porque no tiene información sobre la ubicación del destino (búsqueda ciega).

2. **A\*** también garantiza el camino óptimo y explora entre un 8% y 22% menos nodos que BFS gracias a la heurística de distancia Manhattan. En laberintos con muchos pasillos rectos y poca ambigüedad estructural la ventaja es menor; en laberintos más complejos o de mayor dimensión la ventaja aumenta. El costo extra de tiempo se debe a la administración del heap de prioridad.

3. **DFS** es el más rápido explorando (menos nodos visitados) pero entrega caminos subóptimos con entre 1.6× y 2.3× más pasos que el óptimo. Es útil únicamente cuando importa encontrar *algún* camino rápidamente y no el más corto.

4. **Métrica recomendada para este problema:** dado que el objetivo es resolver el laberinto (llegar de E a S), la métrica más importante es M1 (optimalidad). Si el tiempo es crítico se añade M3. M2 (eficiencia de exploración) es útil para entender el comportamiento interno del algoritmo pero no afecta directamente al usuario.

5. **Recomendación:** A\* es el algoritmo más adecuado para resolver laberintos cuando se requiere el camino más corto, especialmente a medida que el tamaño del grafo crece.

---

## Estructura del proyecto

```
Taller2/
├── P1/
│   ├── P1.py              # Punto de entrada — ejecutar para resolver todos los laberintos
│   ├── P1_MazeLoader.py   # Carga, grafo y visualización
│   ├── P1_solvers.py      # Algoritmos BFS, A* y DFS
│   ├── P1_util.py         # Colores de celda
│   ├── laberinto1.txt
│   ├── laberinto2.txt
│   ├── laberinto3.txt
│   └── laberinto4.txt
└── images/
    ├── laberinto1_comparacion.png
    ├── laberinto2_comparacion.png
    ├── laberinto3_comparacion.png
    └── laberinto4_comparacion.png
```

## Cómo ejecutar

```bash
cd _Soluciones/Grupo6/Taller2/P1
python P1.py
```
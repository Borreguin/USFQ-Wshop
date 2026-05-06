# WorkShop-USFQ
## Taller 2 — Uso de Algoritmos de Búsqueda

- **Nombre del grupo**: G6
- **Integrantes del grupo**:
  * Estudiante 1
  * Estudiante 2

---

## Descripción

El objetivo es utilizar algoritmos de búsqueda para resolver los 3 laberintos propuestos,
visualizar los resultados y comparar el comportamiento de al menos 2 algoritmos.

---

## A. Representación del laberinto como grafo

El laberinto se carga desde un archivo `.txt` donde cada celda puede ser:

| Símbolo | Significado |
|---------|-------------|
| `#`     | Pared (no transitable) |
| ` `     | Pasillo libre |
| `E`     | Entrada (nodo inicio) |
| `S`     | Salida (nodo destino) |

Cada celda transitable (`' '`, `E`, `S`) se convierte en un **nodo** del grafo.
Dos nodos son **vecinos** (con arista de peso 1) si son adyacentes horizontal o verticalmente y ambos son transitables.
El grafo se representa como un diccionario de adyacencia: `{(fila, col): [(fila', col'), ...]}`

---

## B. Algoritmos de búsqueda

Se implementaron 3 algoritmos en `P1/P1_solvers.py`:

### BFS — Breadth-First Search
Explora por niveles (anchura). Garantiza el **camino más corto** en grafos no ponderados.
- Estructura: Cola (FIFO)
- Completitud: Sí
- Optimalidad: Sí (costo uniforme)

### A* (A-estrella)
Búsqueda informada que usa la heurística de **distancia Manhattan** al destino:
`f(n) = g(n) + h(n)` donde `g` = costo acumulado, `h` = estimación al destino.
- Estructura: Cola de prioridad (min-heap)
- Completitud: Sí
- Optimalidad: Sí (heurística admisible)

### DFS — Depth-First Search
Explora en profundidad. **No garantiza** el camino más corto.
- Estructura: Pila (LIFO)
- Completitud: Sí (grafo finito)
- Optimalidad: No

---

## Métricas de evaluación

| Métrica | Descripción |
|---------|-------------|
| **Pasos** | Longitud del camino encontrado (número de celdas − 1) |
| **Nodos explorados** | Cuántos nodos se procesaron antes de encontrar la solución |
| **Tiempo (ms)** | Tiempo de ejecución del algoritmo |

---

## Resultados

### Laberinto 1 — Pequeño (9×11, 43 nodos)

![Laberinto 1](/Taller2/images/laberinto1_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |    14 |              43 |       0.029 |
| A\*       |    14 |              36 |       0.060 |
| DFS       |    30 |              34 |       0.021 |

### Laberinto 2 — Mediano (15×29, 201 nodos)

![Laberinto 2](/Taller2/images/laberinto2_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |    44 |             183 |       0.263 |
| A\*       |    44 |             140 |       0.343 |
| DFS       |    72 |              89 |       0.108 |

### Laberinto 3 — Grande (23×109, 1270 nodos)

![Laberinto 3](/Taller2/images/laberinto3_comparacion.png)

| Algoritmo | Pasos | Nodos explorados | Tiempo (ms) |
|-----------|------:|----------------:|------------:|
| BFS       |   344 |             859 |       9.605 |
| A\*       |   344 |             788 |       2.928 |
| DFS       |   558 |             578 |       1.472 |

---

## Análisis comparativo

**BFS vs A\*:**
- Ambos encuentran el **camino óptimo** (mismo número de pasos).
- A\* explora **menos nodos** gracias a la heurística Manhattan, lo que reduce el espacio de búsqueda significativamente en laberintos grandes.
- En el laberinto grande, A\* fue ~3× más rápido que BFS.

**BFS/A\* vs DFS:**
- DFS explora incluso menos nodos que A\* pero encuentra un camino **subóptimo** (más pasos).
- En el laberinto grande, DFS usó 558 pasos vs 344 de BFS/A\* (62% más largo).
- DFS es rápido pero no garantiza encontrar el camino más corto.

**Conclusión:** A\* es el mejor balance entre calidad de solución y eficiencia.
Para laberintos grandes donde el camino óptimo importa, A\* supera a BFS reduciendo los nodos explorados mediante la guía heurística.

---

## Estructura del proyecto

```
Taller2/
├── P1/
│   ├── P1.py              # Casos de estudio (punto de entrada)
│   ├── P1_MazeLoader.py   # Carga del laberinto, grafo y visualización
│   ├── P1_solvers.py      # Algoritmos BFS, A* y DFS
│   ├── P1_util.py         # Colores de celda
│   ├── laberinto1.txt
│   ├── laberinto2.txt
│   └── laberinto3.txt
└── images/
    ├── laberinto1_comparacion.png
    ├── laberinto2_comparacion.png
    └── laberinto3_comparacion.png
```

## Cómo ejecutar

```bash
cd Taller2/P1
python P1.py
```

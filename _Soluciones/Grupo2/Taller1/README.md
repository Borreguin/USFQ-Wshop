# Taller 1 — Grupo 2

**Maestría en Inteligencia Artificial — USFQ**

Este taller aborda tres problemas clásicos de Inteligencia Artificial: optimización combinatoria, búsqueda en espacios de estados y resolución recursiva de puzzles. Cada problema fue implementado en Python con visualización interactiva.

---

## Índice

1. [P1 — Problema del Viajante (TSP)](#p1--problema-del-viajante-tsp)
2. [P2 — Acertijo del Granjero](#p2--acertijo-del-granjero)
3. [P3 — Torres de Hanoi](#p3--torres-de-hanoi)
4. [Resumen comparativo](#resumen-comparativo)
5. [Requisitos](#requisitos)

---

## P1 — Problema del Viajante (TSP)

**Directorio:** `P1_TSP/`

### Descripción

Dado un conjunto de ciudades con coordenadas en el plano 2D, encontrar la ruta más corta que visite cada ciudad exactamente una vez y regrese al punto de origen (ciclo hamiltoniano). Es un problema NP-difícil de optimización combinatoria.

### Algoritmo: Vecino Más Cercano + 2-Opt

Se aplica un enfoque híbrido de dos fases:

**Fase 1 — Construcción greedy (Vecino Más Cercano):**
- Desde una ciudad inicial, se selecciona iterativamente la ciudad no visitada más cercana.
- Complejidad: O(n²)
- Produce una solución inicial válida, típicamente dentro del 20–25% del óptimo.

**Fase 2 — Mejora local (2-Opt):**
- Detecta y elimina cruces en la ruta invirtiendo segmentos.
- Itera hasta que no exista ninguna mejora posible (convergencia al óptimo local).
- Complejidad: O(n²) por iteración.

### Archivos

| Archivo | Descripción |
|---|---|
| `TSP.py` | Implementación del algoritmo (vecino más cercano + 2-opt) |
| `util.py` | Generación de ciudades y funciones de visualización |
| `TSP_Notebook.ipynb` | Notebook con ejemplos y comparación de casos |

### Ejecución

```bash
python TSP.py
# o bien:
jupyter notebook TSP_Notebook.ipynb
```

### Resultados de ejemplo

| Ciudades | Distancia total |
|---|---|
| 10 ciudades | ~570 unidades |
| 100 ciudades | Mejora visual notable entre fases |

---

## P2 — Acertijo del Granjero

**Directorio:** `P2_Granjero/`

### Descripción

Un granjero debe cruzar un río con un lobo, una cabra y una col. El bote solo puede llevar al granjero y un elemento más. Restricciones:
- El lobo no puede quedarse solo con la cabra.
- La cabra no puede quedarse sola con la col.

El objetivo es encontrar la secuencia de movimientos válidos para llevar a todos al otro lado.

### Algoritmo: Búsqueda en Anchura (BFS)

BFS garantiza encontrar la solución más corta:

- **Representación de estado:** Tupla `(granjero, lobo, cabra, col)` donde 0 = orilla izquierda, 1 = orilla derecha.
- **Estado inicial:** `(0, 0, 0, 0)`
- **Estado objetivo:** `(1, 1, 1, 1)`
- **Transiciones:** El granjero cruza solo o con uno de los elementos (si es seguro).
- **Validación:** Se verifican los pares peligrosos en cada estado generado.

Complejidad temporal y espacial: O(n) sobre el espacio de estados válidos.

### Archivos

| Archivo | Descripción |
|---|---|
| `Acertijo.py` | Algoritmo BFS e impresión de la solución en consola |
| `visualizador_granjero.py` | Interfaz gráfica interactiva (Tkinter) para recorrer la solución paso a paso |

### Ejecución

```bash
# Solución en consola
python Acertijo.py

# Visualizador interactivo
python visualizador_granjero.py
```

### Solución óptima

La solución requiere **7 movimientos**. El visualizador permite navegar cada paso con botones Anterior / Siguiente sobre una representación gráfica del río.

---

## P3 — Torres de Hanoi

**Directorio:** `P3_Torres/`

### Descripción

Mover una pila de n discos desde la torre origen (A) hasta la torre destino (C), usando la torre auxiliar (B), respetando las reglas:
- Solo se puede mover un disco a la vez.
- Un disco mayor nunca puede colocarse sobre uno menor.

### Algoritmo: Recursión (Divide y Vencerás)

```
hanoi(n, origen, destino, auxiliar):
    si n == 1:
        mover disco de origen → destino
    si no:
        hanoi(n-1, origen, auxiliar, destino)
        mover disco n de origen → destino
        hanoi(n-1, auxiliar, destino, origen)
```

- Complejidad temporal: O(2ⁿ − 1) movimientos totales.
- Profundidad de recursión: O(n).

### Archivos

| Archivo | Descripción |
|---|---|
| `Torres.py` | Algoritmo recursivo, visualización animada con Matplotlib y ejecución principal |

### Ejecución

```bash
python Torres.py
# Ingresar el número de discos cuando se solicite (recomendado: 3–6)
```

### Movimientos según número de discos

| Discos | Movimientos (2ⁿ − 1) |
|---|---|
| 3 | 7 |
| 4 | 15 |
| 5 | 31 |
| 6 | 63 |

---

## Resumen comparativo

| Proyecto | Problema | Algoritmo | Entrada | Complejidad |
|---|---|---|---|---|
| **P1 — TSP** | Optimización de ruta | Vecino Más Cercano + 2-Opt | Número de ciudades n | O(n²) por fase |
| **P2 — Granjero** | Búsqueda con restricciones | BFS (Búsqueda en Anchura) | Espacio de estados fijo | O(estados válidos) |
| **P3 — Torres** | Puzzle recursivo | Divide y Vencerás (recursión) | Número de discos n | O(2ⁿ − 1) |

### Diferencias clave

- **Garantía de óptimo:** BFS (Granjero) y la recursión (Torres) garantizan la solución óptima. El TSP usa heurísticas y encuentra un óptimo local.
- **Estrategia de búsqueda:** El TSP hace mejora local; el Granjero hace búsqueda exhaustiva; las Torres usan descomposición recursiva del problema.
- **Escalabilidad:** TSP escala polinomialmente; Torres crece exponencialmente; el Granjero tiene espacio de estados acotado.

---

## Requisitos

```
Python >= 3.8
matplotlib
tkinter (incluido en la instalación estándar de Python)
jupyter (opcional, para P1_TSP/TSP_Notebook.ipynb)
```

Instalación de dependencias:

```bash
pip install matplotlib jupyter
```

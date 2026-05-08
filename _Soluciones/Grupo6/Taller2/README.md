# Taller 2 — Grupo 6

## Requisitos

```bash
pip install numpy matplotlib
```

Para la GUI interactiva también se necesita `tkinter` (incluido con Python estándar en la mayoría de sistemas).

---

## P1 — Resolución de laberintos (BFS, A\*, DFS)

### Ejecución por consola

Resuelve los 4 laberintos con los tres algoritmos e imprime métricas de pasos, nodos explorados y tiempo. Guarda imágenes comparativas en `images/`.

```bash
cd P1
python P1.py
```

Salida esperada por laberinto:

```
============================================================
  Laberinto 1 (pequeño)  (laberinto1.txt)
============================================================
  Nodos en el grafo : 43
  Inicio (E)        : (fila, col)
  Salida (S)        : (fila, col)

  Algoritmo   Pasos  Nodos exp.  Tiempo (ms)
  --------   -----  ----------  -----------
  BFS           14          43        0.114
  A*            14          36        0.128
  DFS           30          34        0.045
```

Las imágenes se guardan en `Taller2/images/laberintoN_comparacion.png`.

---

### GUI interactiva 

Abre una ventana con los 4 laberintos (3 Clásicos y 1 Cuántico). Permite seleccionar el laberinto y el algoritmo, animar la exploración paso a 
paso, y ver las métricas en tiempo real.

```bash
cd P1/Q
python main.py
```

---

---

## P2 — Ant Colony Optimization (ACO)

### ACO en grilla (pathfinding)

Ejecuta dos casos de estudio en una grilla 10×10 con obstáculos. Guarda gráficos de feromonas y mejor camino.

```bash
cd P2
python P2_ACO.py
```

- **Caso 1** — barrera parcial (3 obstáculos): guarda `caso1_ACO.png`
- **Caso 2** — barrera casi total (4 obstáculos, solo un paso libre): guarda `caso2_ACO.png`

Salida en consola por caso:

```
[Iter  5] Nuevo mejor: 12 pasos → [(0,0), ..., (4,7)]
[Iter 18] Nuevo mejor:  9 pasos → [(0,0), ..., (4,7)]
...
Gráfico guardado como 'caso1_ACO.png'
```

---

### ACO para el Problema del Viajante (TSP)

Resuelve el TSP para 10 ciudades generadas aleatoriamente. Guarda el tour y la curva de convergencia.

```bash
cd P2
python P2_TSP.py
```

Genera el archivo `aco_tsp.png` con dos gráficos:
- El mejor tour encontrado sobre el mapa de ciudades.
- La curva de convergencia (distancia mínima por iteración).

---

### Búsqueda de hiperparámetros (ACO)

Prueba combinaciones de `num_ants`, `evaporation_rate`, `alpha` y `beta` para el Caso 2, e imprime el ranking de configuraciones. Guarda el gráfico en `hyperparam_search.png`.

```bash
cd P2
python hiperparametros.py
```
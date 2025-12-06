# Taller 2

## Inteligencia artificial - Grupo 3

- **Integrantes del grupo**:

|    Integrantes    |
|:-----------------:|
|   Juan Pazmino    |
|   Wilson Lopez    |
| Cristian Calderon | 

---


# Maze Solver - Algoritmos de Búsqueda A* y BFS

Implementación en Python de algoritmos de búsqueda informada (A*) y no informada (BFS) para resolver laberintos, con visualización gráfica mediante Matplotlib.
En este taller se resuelve laberintos representados como archivos de texto utilizando dos estrategias de búsqueda fundamentales en Inteligencia Artificial. El desarrollo sigue una metodología de tres pasos:

1. **Modelado**: Transformar el laberinto en un grafo de adyacencia
2. **Implementación**: Desarrollar A* con heurística Manhattan
3. **Evaluación**: Comparar rendimiento A* vs BFS

---
## Algoritmos de Búsqueda

### Comparativa General

| Algoritmo | Descripción | Pros | Contras |
|-----------|-------------|------|---------|
| **BFS** | Explora nivel por nivel, garantizando el camino más corto en número de pasos | **Óptimo** (encuentra el camino más corto) | Ineficiente en laberintos grandes (mucha memoria) |
| **DFS** | Explora lo más profundo posible antes de retroceder (backtracking) | **Bajo uso de memoria** (utiliza una pila) | No garantiza el camino más corto; puede quedar "atascado" en caminos largos |
| **BDS** | Ejecuta búsqueda simultánea desde Entrada y Salida hasta encontrarse | **Mucho más rápido** que BFS/DFS unilaterales en laberintos grandes | Más complejo de implementar y coordinar |
| **A*** | Búsqueda informada con heurística que guía hacia la meta | **Eficiente** (explora menos nodos) y **óptimo** | Requiere definir una heurística admisible |

---

## A* (A-Star) - Búsqueda Informada

A* combina el costo real con una estimación heurística:

- **g(n)**: Costo real desde el inicio hasta el nodo actual
- **h(n)**: Heurística estimada desde el nodo actual hasta la meta
- **f(n) = g(n) + h(n)**: Función de evaluación total

#### Heurística: Distancia Manhattan

```python
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

Esta heurística es **admisible** (nunca sobreestima) y **consistente**, garantizando optimalidad.

#### Estructuras de Datos

| Estructura | Propósito | Implementación |
|------------|-----------|----------------|
| `open_list` | Cola de prioridad (frontera) | `heapq` - Min-heap por f_score |
| `g_score` | Costo acumulado por nodo | `dict` inicializado en ∞ |
| `came_from` | Rastreo del camino | `dict` nodo → nodo_padre |

---

### BFS (Breadth-First Search) - Búsqueda No Informada

BFS explora el grafo por niveles, garantizando el camino más corto en grafos no ponderados.

#### Estructuras de Datos

| Estructura | Propósito | Implementación |
|------------|-----------|----------------|
| `queue` | Cola FIFO | `collections.deque` |
| `came_from` | Nodos visitados + rastreo | `dict` nodo → nodo_padre |

#### Características

- **Completitud**: Siempre encuentra solución si existe
- **Optimalidad**: Garantizada en grafos no ponderados
- **Estrategia**: Expansión por niveles (Level-Order)

---

## Modelado como Grafo

El laberinto se transforma en un **grafo de adyacencia** donde:

- **Nodos (Vértices)**: Cada celda transitable (`' '`, `'E'`, `'S'`) representada como tupla `(y, x)`
- **Aristas (Conexiones)**: Conexión entre nodos adyacentes (arriba, abajo, izquierda, derecha) si ambos son transitables

```python
# Ejemplo de grafo resultante
graph = {
    (1, 1): [(1, 2), (2, 1)],  # Nodo con 2 vecinos
    (1, 2): [(1, 1), (1, 3)],  # Nodo con 2 vecinos
    ...
}

# Direcciones de movimiento (4-conectividad)
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
#             Derecha  Izquierda Abajo   Arriba
```

---

## Resultados Experimentales

### Laberinto 1 (Simple - 9x11)

| Algoritmo | Tiempo (ms) | Pasos |
|-----------|-------------|-------|
| A* | 0.03 | 14 |
| BFS | 0.01 | 14 |

![L1](/Taller2/images/L1.png) 

### Laberinto 2 (Intermedio - 15x29)

| Algoritmo | Tiempo (ms) | Pasos |
|-----------|-------------|-------|
| A* | 0.12 | 44 |
| BFS | 0.04 | 44 |

![L2](/Taller2/images/L2.png) 

### Laberinto 3 (Complejo - 23x109)

| Algoritmo | Tiempo (ms) | Pasos |
|-----------|-------------|-------|
| A* | 1.48 | 344 |
| BFS | 0.41 | 344 |

![L3](/Taller2/images/L3.png) 

## Conclusiones

- Ambos algoritmos encuentran el **mismo número de pasos**, confirmando que ambos son óptimos en grafos no ponderados
- **BFS es más rápido** en todos los casos de prueba debido a:
  - Menor overhead computacional (cola FIFO vs cola de prioridad)
  - Sin cálculo de heurística por cada nodo
  - Operaciones O(1) en `deque` vs O(log n) en `heapq`

---

## Análisis Comparativo

### ¿Cuándo usar cada algoritmo?

| Escenario | Recomendación |
|-----------|---------------|
| Laberinto con costo uniforme | BFS (menor overhead) |
| Grafo con costos variables | A* (único óptimo de los dos) |
| Espacios de búsqueda muy grandes | A* (heurística reduce exploración) |
| Implementación rápida | BFS (más simple) |

### Complejidad Teórica

| Algoritmo | Tiempo | Espacio |
|-----------|--------|---------|
| A* | O(b^d) reducido por heurística | O(b^d) |
| BFS | O(b^d) | O(b^d) |

Donde `b` = factor de ramificación, `d` = profundidad de la solución.

### ¿Por qué BFS fue más rápido en estos experimentos?

En laberintos con **costo uniforme** (cada paso = 1), BFS tiene ventajas prácticas:

1. **Sin overhead de heurística**: A* calcula `h(n)` para cada nodo expandido
2. **Cola más eficiente**: `deque.popleft()` es O(1), mientras `heapq.heappop()` es O(log n)
3. **Sin duplicados**: BFS marca visitados inmediatamente; A* puede re-procesar nodos

### ¿Cuándo A* supera a BFS?

A* muestra su verdadero potencial cuando:
- El espacio de búsqueda es **muy grande** (la heurística evita explorar zonas irrelevantes)
- Los costos entre nodos son **variables** (BFS ya no garantiza optimalidad)
- La meta está en una **dirección clara** desde el inicio

---

## Estructura de Clases y Funciones

### `MazeLoader` (P1_MazeLoader.py)

| Método | Descripción |
|--------|-------------|
| `load_Maze()` | Parsea archivo .txt a matriz 2D |
| `plot_maze()` | Renderiza laberinto con Matplotlib |
| `get_graph()` | Convierte matriz a grafo de adyacencia |

### Funciones Solver (P1_Solver.py)

| Función | Descripción |
|---------|-------------|
| `heuristic(a, b)` | Calcula distancia Manhattan |
| `solve_maze_astar()` | Implementación de A* |
| `solve_maze_bfs()` | Implementación de BFS |
| `reconstruct_path()` | Reconstruye camino desde `came_from` |

---

# Análisis de Ant Colony Optimization (ACO) para Pathfinding

## Diferencias Principales

| Aspecto | P2_ACO.py `study_case_2()`                         | Col_A.py `run()`                              |
|---------|--------------------------------------|----------------------------------------|
| Almacenamiento de obstáculos | `list` → O(n) por búsqueda           | `set` → O(1) por búsqueda              |
| Validación de caminos | No verifica si llega al destino      | Solo acepta caminos completos          |
| Límite de pasos | Sin límite (riesgo de loop infinito) | `max_steps=200`                        |
| Depósito de feromonas | Puede duplicar en misma celda        | Usa `set(path)` para evitar duplicados |
| Algoritmo adicional | —                                    | Incluye A* para comparación            |

---

## Errores Identificados en P2_ACO.py `study_case_2()`

### 1. Error 1: Selección de Caminos Incompletos
Un camino que se quedó atascado (no llegó al destino) será más corto que uno que completó el recorrido. El algoritmo premia caminos fallidos.


**Código problemático:**
```python
all_paths.sort(key=lambda x: len(x))
best_path = all_paths[0]
```

**Solución en Col_A.py:**
```python
if path[-1] == self.end:
    paths.append(path)  # Solo considera caminos que llegaron al destino
```

### 2. Depósito de Feromonas Redundante

**Código problemático:**
```python
def _deposit_pheromones(self, path):
    for position in path:
        self.pheromones[position[1], position[0]] += 1
```

**Solución:**
```python
for pos in set(path):  # Actualización solo en posiciones únicas
```

### 3. Posible Loop Infinito

Sin límite de pasos, una hormiga podría quedarse en un ciclo indefinido.

**Solución:**
```python
while pos != self.end and len(path) < max_steps:
```

---

## Análisis del Study Case 2

### Pregunta 1: ¿Es suficiente elegir el camino con menor tamaño?

**Respuesta: NO**

La condición faltante es verificar que el camino llegue al destino:
```python
path[-1] == self.end
```

Sin esta validación, caminos atascados de longitud 3-4 son seleccionados sobre caminos completos de longitud 12+.

### Pregunta 2: Ajuste de Parámetros

| Parámetro | Valor Original | Valor Corregido | Justificación                                          |
|-----------|----------------|--------------|--------------------------------------------------------|
| `alpha` | 0.1 | **0.5** | Mayor influencia de feromonas                          |
| `beta` | 15 | **7** | Menos greedy, permite exploración                      |
| `num_ants` | 10 | 10 | Lo mantengo porque mantiene la exploración del espacio |
| `evaporation_rate` | 0.1 | 0.1-0.3 | Es un valor razonable                                  |

**Explicación de `alpha` y `beta`:**
- **Alpha:** Controla influencia de feromonas. Con 0.1, las hormigas ignoran rastros anteriores.
- **Beta:** Controla influencia de la heurística. Con 15, las hormigas van directo al objetivo sin explorar alternativas, chocando contra la barrera.

---

## Comparación Visual de Resultados

### Implementación Incorrecta
- El camino se atasca en la esquina superior
- NO conecta origen con destino
- Feromonas concentradas en zona de "atasco"
- Camino incompleto seleccionado como "mejor"

![ACO01](/Taller2/images/ACO01.png) 

### Implementación Corregida
- El camino rodea la barrera correctamente
- Conecta exitosamente start → end
- Feromonas distribuidas a lo largo del camino válido
- Resultado funcional y óptimo

![ACO02](/Taller2/images/ACO02.png) 

---

## Conclusiones

1. Una correcta validacion es muy importante ya que una solución inválida nunca debe competir con soluciones válidas, sin importar su "costo" aparente.

2. Un correcto balance de los valores de alpha y beta deben permitir tanto explotación (seguir feromonas) como exploración (buscar alternativas).

3. **Estructuras de datos:** Usar `set` para obstáculos mejora significativamente el rendimiento en búsquedas.

4. **Límites de seguridad:** Siempre incluir `max_steps` para prevenir loops infinitos.

---

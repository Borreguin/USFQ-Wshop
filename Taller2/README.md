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
| **A*** | Búsqueda informada con heurística que guía hacia la meta | **Eficiente** (explora menos nodos) y **óptimo** | Requiere definir una heurística admisible |

---

## A* (A-Star) - Búsqueda Informada

A* combina el costo real con una estimación heurística:

- **g(n)**: Costo real desde el inicio hasta el nodo actual
- **h(n)**: Heurística estimada desde el nodo actual hasta la meta
- **f(n) = g(n) + h(n)**: Función de evaluación total

#### Estructuras de Datos

| Estructura  | Propósito                    | Implementación                 |
|-------------|------------------------------|--------------------------------|
| `open_list` | Cola de prioridad (frontera) | `heapq` - Min-heap por f_score |
| `g_score`   | Costo acumulado por nodo     | `dict` inicializado en ∞       |
| `came_from` | Rastreo del camino           | `dict` nodo → nodo_padre       |

---

### BFS (Breadth-First Search) - Búsqueda No Informada

BFS explora el grafo por niveles, garantizando el camino más corto en grafos no ponderados.

#### Estructuras de Datos

| Estructura  | Propósito                 | Implementación            |
|-------------|---------------------------|---------------------------|
| `queue`     | Cola FIFO                 | `collections.deque`       |
| `came_from` | Nodos visitados + rastreo | `dict` nodo → nodo_padre  |

#### Características

- **Completitud**: Siempre encuentra solución si existe
- **Optimalidad**: Garantizada en grafos no ponderados
- **Estrategia**: Expansión por niveles (Level-Order)

---

## Modelado como Grafo

El laberinto se transforma en un **grafo de adyacencia** donde:

- **Nodos (Vértices)**: Cada celda transitable (`' '`, `'E'`, `'S'`) representada como tupla `(y, x)`
- **Aristas (Conexiones)**: Conexión entre nodos adyacentes (arriba, abajo, izquierda, derecha) si ambos son transitables

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

## Descripción de Parámetros del Modelo

### Parámetros de Configuración del Entorno

| Parámetro   | Tipo                 | Descripción                                               |
|-------------|----------------------|-----------------------------------------------------------|
| `start`     | `tuple (x, y)`       | Coordenadas del punto de inicio en la grilla              |
| `end`       | `tuple (x, y)`       | Coordenadas del punto destino/objetivo                    |
| `obstacles` | `list/set`           | Conjunto de coordenadas que representan celdas bloqueadas |
| `grid_size` | `tuple (rows, cols)` | Dimensiones de la grilla de búsqueda                      |

### Parámetros del Algoritmo ACO

| Parámetro          | Tipo    | Default | Rango Típico  |
|--------------------|---------|---------|---------------|
| `num_ants`         | `int`   | 10      | 10 - 100      |
| `evaporation_rate` | `float` | 0.1     | 0.01 - 0.5    |
| `alpha`            | `float` | 0.5     | 0.5 - 2.0     |
| `beta`             | `float` | 7       | 2.0 - 10.0    |
| `iterations`       | `int`   | 150     | 50 - 500      |
| `max_steps`        | `int`   | 200     | grid_size * 2 |

## Propósito de Cada Parámetro

### `num_ants` — Número de Hormigas
Define cuántas hormigas exploran el espacio en cada iteración.

- Más hormigas = mayor exploración del espacio de soluciones
- Menos hormigas = convergencia más rápida pero posible estancamiento en óptimos locales
- **Trade-off:** Calidad de solución vs. tiempo de cómputo

### `evaporation_rate` — Tasa de Evaporación
Controla qué tan rápido se "olvidan" los caminos antiguos.

```python
self.pheromones *= (1 - evaporation_rate)
```

- **Valor alto (0.3-0.5):** Feromonas desaparecen rápido → favorece exploración de nuevas rutas
- **Valor bajo (0.01-0.1):** Feromonas persisten → refuerza caminos conocidos
- **Analogía:** Como el olor de las hormigas reales que se desvanece con el tiempo

### `alpha` — Influencia de Feromonas
**Propósito:** Determina qué tanto peso tienen las feromonas en la decisión de movimiento.

- **`alpha= 0`:** Ignora completamente las feromonas (búsqueda puramente heurística)
- **`alpha -> alto`:** Las hormigas siguen fuertemente los rastros de las anteriores
- **Efecto:** Controla la **explotación** del conocimiento colectivo

### `beta`— Influencia de la Heurística
Determina qué tanto peso tiene la distancia al objetivo en la decisión.

- **`beta = 0`:** Ignora la distancia (movimiento aleatorio guiado solo por feromonas)
- **`beta alto`:** Comportamiento "greedy", siempre intenta acercarse al destino
- **Efecto:** Controla la **explotación** de información heurística

### Balance alpha/beta

| Configuración            | Comportamiento                     | Cuándo Usar                               |
|--------------------------|------------------------------------|-------------------------------------------|
| `alpha bajo, beta alto`  | Muy greedy, poca memoria colectiva | Espacios simples sin obstáculos           |
| `alpha alto, beta bajo`  | Sigue rastros, ignora destino      | Problemas donde la experiencia es crucial |
| `alpha ≈ beta`           | Equilibrado                        | Caso general, recomendado                 |

### `iterations` — Número de Iteraciones
Cuántas veces se repite el ciclo completo de exploración.

- Más iteraciones = mejor convergencia hacia el óptimo
- El algoritmo puede converger antes si encuentra un camino estable
- **Criterio de parada alternativo:** Detectar cuando `best_path` no mejora en N iteraciones

### `max_steps` — Máximo de Pasos por Hormiga
Límite de seguridad para evitar loops infinitos.

- Previene que una hormiga atrapada consuma recursos indefinidamente
- Debe ser mayor que la longitud esperada del camino óptimo
- **Regla práctica:** `max_steps ≥ rows × cols` para garantizar cobertura

---

## Conclusiones

1. Una correcta validacion es muy importante ya que una solución inválida nunca debe competir con soluciones válidas, sin importar su "costo" aparente.
2. Un correcto balance de los valores de alpha y beta deben permitir tanto explotación (seguir feromonas) como exploración (buscar alternativas).
3. **Estructuras de datos:** Usar `set` para obstáculos mejora significativamente el rendimiento en búsquedas.
4. **Límites de seguridad:** Siempre incluir `max_steps` para prevenir loops infinitos.

---

## Pregunta de investigacion - Aplicación de ACO al Travelling Salesman Problem (TSP)

### ¿Es posible utilizar ACO para resolver el TSP?

**Sí.** El algoritmo ACO fue diseñado para resolver el TSP por Marco Dorigo en 1992. El problema de pathfinding en grilla (como el implementado en los archivos analizados) es una adaptación posterior del algoritmo original.

El TSP es un problema de optimización combinatoria donde se busca el recorrido más corto que visite todas las ciudades exactamente una vez y regrese al punto de origen.

### Diferencias: Pathfinding vs TSP

| Aspecto     | Pathfinding (Grilla)             | TSP                                            |
|-------------|----------------------------------|------------------------------------------------|
| Objetivo    | Ir de A a B                      | Visitar todas las ciudades y volver            |
| Grafo       | Grilla regular con vecinos fijos | Grafo completo (todas las ciudades conectadas) |
| Restricción | Evitar obstáculos                | Visitar cada ciudad exactamente una vez        |
| Heurística  | Distancia al destino             | Distancia entre ciudades                       |
| Solución    | Secuencia de celdas              | Permutación de ciudades                        |

### Pasos para Implementar ACO en TSP

1. Representación del Problema 
   - Crear matrices de distancias y feromonas
2. Calcular Matriz de Distancias 
   - Distancia euclidiana entre pares de ciudades
3. Construir Tour 
   - Cada hormiga visita todas las ciudades una vez
4. Selección Probabilística 
   - Elegir siguiente ciudad según feromonas y distancia
5. Calcular Longitud del Tour 
   - Sumar distancias de todas las aristas
6. Actualización de Feromonas 
   - Evaporación + depósito proporcional a calidad del tour
7. Iteración y Convergencia 
   - Repetir hasta encontrar buena solución
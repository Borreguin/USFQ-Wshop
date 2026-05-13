![USFQ-LOGO](/Taller1/images/usfq-red.png)

# WorkShop-USFQ — Grupo 6
## Inteligencia Artificial · M1 Taller 1

---

### Integrantes

| Nombre | |
|---|---|
| Stan Mora | |
| Tais Rodriguez | |
| Oldrin Bonilla | |

---

## Problema A — TSP: Travelling Salesman Problem

**Archivo:** `P1_TSP/TSP.py` · `P1_TSP/app.py` · `P1_TSP/index.html`

**Descripción:**  
Dado un conjunto de ciudades y las distancias entre cada par, encontrar la ruta más corta que visita cada ciudad exactamente una vez y regresa al punto de origen (ciclo cerrado).

**Algoritmo implementado:**
- **Nearest Neighbor (heurística greedy O(n²)):** parte de una ciudad inicial y en cada paso avanza a la ciudad no visitada más cercana. Genera una ruta válida rápidamente, aunque no garantiza el óptimo global.
- **2-opt (mejora local):** toma la ruta generada e invierte segmentos de forma iterativa mientras encuentre intercambios que reduzcan la distancia total. Elimina cruces innecesarios entre aristas.
- El pipeline final es: `Nearest Neighbor → 2-opt`.

**Visualización:**  
Mapa interactivo con ArcGIS (frontend en `index.html`) que dibuja la ruta optimizada sobre un mapa real con las coordenadas de cada ciudad.

---

## Problema B — El acertijo del granjero y el bote

**Archivo:** `P2_Granjero/solver.py` · `P2_Granjero/estado.py` · `P2_Granjero/grafo_rio.py` · `P2_Granjero/index.html`

**Descripción:**  
Un granjero debe cruzar un río con un lobo, una cabra y una col. La barca solo lleva al granjero y un elemento a la vez. Restricciones: lobo y cabra no pueden quedarse solos; cabra y col tampoco.

**Algoritmo implementado:**
- **BFS (Búsqueda en Anchura):** explora el espacio de estados nivel por nivel, garantizando encontrar la solución con el menor número de pasos.
- El estado se representa como `(granjero, lobo, cabra, col)` donde `0 = orilla izquierda` y `1 = orilla derecha`.
- `grafo_rio.py` define las transiciones válidas (vecinos) desde cada estado.
- El algoritmo descarta estados inválidos (peligrosos) y estados ya visitados para evitar ciclos.

**Visualización:**  
`index.html` muestra paso a paso el cruce del río con representación gráfica de cada elemento en cada orilla.

---

## Problema C — Torres de Hanói

**Archivo:** `P3_Torres/Torres.py` · `P3_Torres/Simulacion/simulacion.py`

**Descripción:**  
Mover una pila de `n` discos desde la torre origen (torre 1) hasta la torre destino (torre 3), usando una torre auxiliar (torre 2). Reglas: solo un disco a la vez, nunca un disco mayor sobre uno menor.

**Algoritmo implementado:**
- **Recursión clásica:** para mover `n` discos de A a C usando B como auxiliar:
  1. Mover los `n-1` discos superiores de A → B
  2. Mover el disco más grande de A → C
  3. Mover los `n-1` discos de B → C
- Base case: `n = 0`, no hace nada.
- El número mínimo de movimientos es siempre **2ⁿ − 1**.

**Implementación en dos partes:**
- `Torres.py`: resuelve y visualiza cada estado con **matplotlib**, guardando la imagen final en PNG.
- `Simulacion/simulacion.py`: simulación interactiva con **tkinter** que permite elegir el número de discos (1–7), controlar la velocidad de animación y ver el movimiento disco a disco con resaltado visual.
## Link Notion GRUPO6
https://www.notion.so/MSDS-INTELIGENCIA-ARTIFICIAL-34d7bd998d1780ae948ce20e594d6e9e?source=copy_link
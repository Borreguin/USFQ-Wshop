<img src="/Taller1/images/usfq-red.png" alt="Alt Text" width="400">

# WorkShop-USFQ
## Inteligencia artificial - Grupo 3

- **Integrantes del grupo**:

| Integrante | Ejercicio Resuelto                 | 
|:----:|:-----------------------------------|
|Juan Pazmino| P1 TSP Travelling salesman problem |
|Wilson Lopez|P2 El acertijo del granjero y el bote|
|Cristian Calderon| P3 La torre de Hanoi               |


## Resumen
### Taller 1

### TSP Travelling salesman problem – Problema del vendedor viajante

- **Algoritmo Principal:** 2-OPT.
- **Concepto:** El 2-OPT es un algoritmo de búsqueda local diseñado para optimizar rutas. Funciona mediante intercambios iterativos de aristas, buscando eliminar cruces en la ruta hasta alcanzar una solución localmente óptima (heurística).
- **Desafío del TSP:** Encontrar la ruta más corta (solución globalmente óptima) se vuelve computacionalmente inviable a medida que el número de ciudades aumenta (ej. hasta 100 ciudades), justificando el uso de heurísticas como 2-OPT.
    
    ### Funcionamiento del Algoritmo 2-Opt
    El 2-Opt optimiza rutas a través de **intercambios iterativos**, eliminando cruces y desorden en el camino.

  1.  **Comenzar:** Se inicia con una ruta inicial arbitraria.
  2.  **Buscar Cruces:** Se escanea la ruta en busca de dos segmentos ($A \rightarrow B$ y $C \rightarrow D$) que puedan ser intercambiados.
  3.  **Verificar:** Se comprueba si reemplazar las conexiones por ($A \rightarrow C$ y $B \rightarrow D$) resulta en una distancia total más corta.
  4.  **Invertir:** Si se encuentra una mejora, se **invierte el segmento** del camino entre los dos puntos de intercambio para acortar la ruta.
  5.  **Repetir:** El proceso se repite hasta que no se encuentra ningún intercambio adicional que mejore la ruta, alcanzando un **óptimo local**.

---

### **P2 El acertijo del granjero y el bote**

### 1. Representacion del estado

El acertijo se modela como un problema de búsqueda, donde cada **estado** es una tupla de cuatro elementos:

`(granjero, lobo, cabra, col)`

Cada valor indica la orilla: **'L'** (Izquierda) o **'R'** (Derecha).

* **Inicio:** `('L', 'L', 'L', 'L')` (Todos a la izquierda).
* **Meta:** `('R', 'R', 'R', 'R')` (Todos a la derecha).

### Reglas de Seguridad (`es_estado_valido`)

Un estado es **inválido** (desastre) si:
1.  El lobo y la cabra están juntos, y el granjero no está en esa orilla (`granjero != lobo and lobo == cabra`).
2.  La cabra y la col están juntas, y el granjero no está en esa orilla (`granjero != cabra and cabra == col`).

### 2. El algoritmo BFS

La función `bfs_resolver` utiliza BFS para garantizar que la solución encontrada sea el camino con la menor cantidad de cruces.

### Movimientos Posibles (`vecinos`)
El granjero siempre se mueve. Un movimiento es válido si:
1.  El granjero puede cruzar **solo**.
2.  El granjero puede cruzar **con un único elemento** (lobo, cabra o col), siempre que el elemento esté en su misma orilla.
3.  El estado resultante es **válido** (no hay desastre).

### 3. Solucion optima (7 Cruces)

La secuencia de movimientos más corta para resolver el acertijo es:

| Paso | Movimiento del Granjero | Estado (G, L, C, Col) |
|:----:|:------------------------|:----------------------:|
| 0    | Estado inicial          | **('L', 'L', 'L', 'L')** |
| 1    | Cruza **con la cabra** | **('R', 'L', 'R', 'L')** |
| 2    | Cruza **solo** | **('L', 'L', 'R', 'L')** |
| 3    | Cruza **con el lobo** | **('R', 'R', 'R', 'L')** |
| 4    | Cruza **con la cabra** | **('L', 'R', 'L', 'L')** |
| 5    | Cruza **con la col** | **('R', 'R', 'L', 'R')** |
| 6    | Cruza **solo** | **('L', 'R', 'L', 'R')** |
| 7    | Cruza **con la cabra** | **('R', 'R', 'R', 'R')** (META) |

---

### **P3 La torre de Hanoi**


### Planificación del proyecto

La planificación del proyecto se encuentra siguiendo el [Link a Notion](https://www.notion.so/juanpin/2babb7e62c6e808faae8cf13f1051af5?v=2babb7e62c6e81c0b7c1000c4df51a33&source=copy_link)





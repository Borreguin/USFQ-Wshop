<img src="/Taller1/images/usfq-red.png" alt="Alt Text" width="400">

# WorkShop-USFQ
## Inteligencia artificial - Grupo 3

- **Integrantes del grupo**:

| Integrante | Ejercicio Resuelto                 | Tareas                                                  |
|:----:|:-----------------------------------|:--------------------------------------------------------|
|Juan Pazmino| P1 TSP Travelling salesman problem | Resolucion, resumen funcionamiento, Colaboracion ensayo |
|Wilson Lopez|P2 El acertijo del granjero y el bote| Resolucion, resumen funcionamiento, Colaboracion ensayo |
|Cristian Calderon| P3 La torre de Hanoi | Resolucion, resumen funcionamiento, Colaboracion ensayo |

---

## Resumen
### Taller 1

## TSP Travelling salesman problem – Problema del vendedor viajante

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

## **P2 El acertijo del granjero y el bote**

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

## **P3 La torre de Hanoi**

### 1. Estructura del algoritmo (`torre_de_hanoi`)

La función `torre_de_hanoi(n, origen, auxiliar, destino)` es el núcleo de la solución. La estrategia principal fue dividir el problema en subproblemas más sencillos: para mover una pila de discos de una torre a otra, el algoritmo solo necesita saber la torre de destino, origen y un pivote (auxiliar) para mover discos.

### A. División (3 Pasos)
El **Paso Clave** de cada llamada recursiva se enfoca en el disco más grande ($N$) que está en la pila actual. Para mover $N$ discos de A (Origen) a C (Destino), el proceso es siempre:

1.  **Llamada Recursiva 1:** Mover los $N-1$ discos superiores del Origen (A) al Auxiliar (B).
2.  **Movimiento Directo:** Mover el disco $N$ del Origen (A) al Destino (C).
3.  **Llamada Recursiva 2:** Mover los $N-1$ discos del Auxiliar (B) al Destino (C).

### B. Finalización (Caso Base)
La recursividad se detiene cuando la función detecta que $n = 1$, donde $n$ es el número de discos. En este caso, se realiza un movimiento directo, se incrementa el contador global (`paso_global`), y la rama de ejecución finaliza (`return`).

### 2. Implementacion y visualizacion

### Contador Global
Se utiliza la variable `paso_global` (declarada con `global`) para rastrear y asegurar que todos los movimientos se cuenten de forma secuencial y única, a pesar de las múltiples llamadas recursivas. Esta variable es clave para el desempeño y verificación del algoritmo.

### Visualización
Se implementó una visualización en consola que muestra la secuencia de movimientos final (ej: "Paso 1: Mover disco 1 de A a C"). El caso de estudio por defecto para $N=3$ discos genera $2^3 - 1 = 7$ movimientos, que es la solución óptima.

### 3. Ventajas de recursividad

La metodología recursiva es la forma más eficiente y elegante de resolver la Torre de Hanói por las siguientes razones:

### 1. Simpleza Lógica y Elegancia Matemática
El problema de Hanói es inherentemente recursivo. La única forma de resolver este problema para $N$ discos es asumiendo que ya se sabe resolver para $N-1$ discos. La recursividad permite traducir esta definición matemática directamente al código, sin necesidad de complejos bucles.

### 2. Garantía de Optimización y Eficiencia
El algoritmo recursivo genera la secuencia **mínima** de movimientos garantizada para cualquier número de discos. El número de movimientos es siempre $2^N - 1$. Un enfoque iterativo para este problema sería significativamente más complejo de diseñar y mantener.

### 3. Manejo de Pilas (Stack)
La recursividad utiliza la pila de llamadas del sistema (Call Stack) de Python para gestionar automáticamente las tareas pendientes (los subproblemas). Cuando la función llama a `torre_de_hanoi(n - 1, ...)` en el paso 1, la función de tamaño $N$ se pausa y espera a que el subproblema de tamaño $N-1$ se resuelva. Esto asegura que el subproblema se resuelva antes de hacer el movimiento del disco $N$.



## Planificación del proyecto

La planificación del proyecto se encuentra siguiendo el [Link a Notion](https://www.notion.so/juanpin/2babb7e62c6e808faae8cf13f1051af5?v=2babb7e62c6e81c0b7c1000c4df51a33&source=copy_link)





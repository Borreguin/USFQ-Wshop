# Explicación Detallada del Código `Torres.py`

Este documento analiza línea por línea el código implementado para resolver y animar el problema de las Torres de Hanoi.

## 1. Importación de Librerías

```python
1: import matplotlib.pyplot as plt
2: from matplotlib.animation import FuncAnimation
```
*   **Línea 1**: Importa la librería `matplotlib.pyplot` con el alias `plt`. Esta librería se usa para crear gráficos en Python. Aquí la usaremos para dibujar las torres y los discos.
*   **Línea 2**: Importa `FuncAnimation` de `matplotlib.animation`. Esta herramienta permite crear animaciones actualizando el gráfico repetidamente.

---

## 2. Función Recursiva `hanoi`

```python
4: def hanoi(n, origen, destino, auxiliar, movimientos):
```
*   **Definición**: Función recursiva que calcula los pasos para mover `n` discos.
*   **Parámetros**:
    *   `n`: Número de discos a mover.
    *   `origen`: Poste donde están los discos inicialmente (ej. 0 para 'A').
    *   `destino`: Poste a donde queremos llevarlos (ej. 2 para 'C').
    *   `auxiliar`: Poste que usamos de apoyo (ej. 1 para 'B').
    *   `movimientos`: Una lista vacía `[]` que iremos llenando con los pasos.

```python
9:     if n == 1:
10:         movimientos.append((origen, destino))
11:         return
```
*   **Caso Base**: Si solo hay **1 disco** (`n=1`), simplemente lo movemos del origen al destino.
*   **Ejemplo**: Si llamamos `hanoi(1, 0, 2, 1, lista)`, añade `(0, 2)` a la lista (mover de A a C).

```python
13:     hanoi(n - 1, origen, auxiliar, destino, movimientos)
14:     movimientos.append((origen, destino))
15:     hanoi(n - 1, auxiliar, destino, origen, movimientos)
```
*   **Paso Recursivo**: Si hay más de 1 disco (ej. `n=3`):
    1.  **Línea 13**: Mueve los `n-1` discos (los 2 de arriba) del `origen` al `auxiliar`.
    2.  **Línea 14**: Mueve el disco grande que queda (el disco `n`) del `origen` al `destino`.
    3.  **Línea 15**: Mueve los `n-1` discos que dejamos en `auxiliar` hacia el `destino`.

---

## 3. Generación de Estados `generar_estados`

```python
18: def generar_estados(n, movimientos, origen=0):
```
*   Esta función toma la lista de movimientos calculada arriba y crea una "foto" de cómo se ven las torres en cada paso.

```python
23:     torres = [[], [], []]
24:     torres[origen] = list(range(n, 0, -1))
```
*   **Línea 23**: Crea 3 listas vacías representando los 3 postes: `[[], [], []]`.
*   **Línea 24**: Llena el poste de origen.
    *   **Ejemplo Numérico (`n=3`)**: `range(3, 0, -1)` genera `3, 2, 1`.
    *   `torres` queda así: `[[3, 2, 1], [], []]`.
    *   El `3` es la base (grande), el `1` es la cima (pequeño).

```python
26:     estados = [ [t.copy() for t in torres] ]
```
*   Guarda el estado inicial. Usamos `.copy()` para guardar una copia de la lista en ese momento, no una referencia que cambie después.

```python
28:     for (desde, hasta) in movimientos:
29:         disco = torres[desde].pop()
30:         torres[hasta].append(disco)
31:         estados.append([x.copy() for x in torres])
```
*   **Bucle**: Recorre cada movimiento (ej. `(0, 2)` mover de A a C).
*   **Línea 29**: `.pop()` saca el último elemento (el disco de arriba) de la torre `desde`.
    *   *Ejemplo*: Si torre A es `[3, 2, 1]`, `.pop()` saca el `1`. Torre A queda `[3, 2]`.
*   **Línea 30**: `.append(disco)` pone ese disco en la torre `hasta`.
    *   *Ejemplo*: Si torre C es `[]`, ahora queda `[1]`.
*   **Línea 31**: Guarda la nueva "foto" de las torres en la lista `estados`.

---

## 4. Animación `animar_hanoi`

```python
36: def animar_hanoi(n, estados):
```
*   Función encargada de dibujar.

```python
40:     fig, ax = plt.subplots(figsize=(8, 4))
43:     centros = [0, 6, 12]
```
*   **Línea 40**: Crea una figura de 8x4 pulgadas.
*   **Línea 43**: Define las coordenadas X donde se dibujarán los postes: 0, 6 y 12.

```python
45:     def dibujar_estado(estado):
46:         ax.clear()
49:         ax.set_xlim(-3, 15)
50:         ax.set_ylim(0, n + 1)
```
*   **Línea 46**: Borra lo que había antes en el gráfico.
*   **Líneas 49-50**: Fija los límites del gráfico para que no se mueva la cámara.

```python
53:         for c in centros:
54:             ax.plot([c, c], [0, n + 0.5], linewidth=2)
```
*   Dibuja líneas verticales (los postes) en las posiciones 0, 6 y 12.

```python
57:         for indice_poste, torre in enumerate(estado):
58:             for nivel, disco in enumerate(torre):
60:                 ancho = disco * 1.2
61:                 izquierda = centros[indice_poste] - ancho / 2
62:                 y = nivel + 0.5
63:                 ax.barh(y=y, width=ancho, left=izquierda, height=0.8)
```
*   **Dibuja los discos**:
    *   Recorre cada poste y cada disco dentro del poste.
    *   **Línea 60**: Calcula el ancho. Un disco `3` será más ancho (`3.6`) que un disco `1` (`1.2`).
    *   **Línea 61**: Calcula la posición izquierda para que el disco quede centrado en el poste.
    *   **Línea 63**: `ax.barh` dibuja una barra horizontal (el disco).

```python
70:     def actualizar(cuadro):
71:         dibujar_estado(estados[cuadro])
```
*   Esta función se llama en cada "frame" de la animación. Simplemente dibuja el estado correspondiente al número de cuadro actual.

```python
73:     animacion = FuncAnimation(fig, actualizar, frames=len(estados), interval=700, repeat=False)
74:     plt.show()
```
*   Crea la animación y la muestra en una ventana. `interval=700` significa 700 milisegundos (0.7 segundos) por paso.

---

## 5. Bloque Principal `main`

```python
77: if __name__ == "__main__":
78:     n = 3
81:     movimientos = []
82:     hanoi(n, origen=0, destino=2, auxiliar=1, movimientos=movimientos)
```
*   Define `n=3` discos.
*   Llama a la función recursiva `hanoi` para llenar la lista `movimientos`.
    *   `0` = Poste A
    *   `1` = Poste B
    *   `2` = Poste C

```python
85:     for i, (desde, hasta) in enumerate(movimientos, 1):
86:         print(f"{i}. Mover disco de {['A','B','C'][desde]} a {['A','B','C'][hasta]}")
```
*   Imprime los pasos en texto legible (convierte 0,1,2 a A,B,C).

```python
89:     estados = generar_estados(n, movimientos, origen=0)
90:     animar_hanoi(n, estados)
```
*   Genera las "fotos" de todos los pasos y lanza la animación.

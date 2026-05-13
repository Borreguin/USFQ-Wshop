# Taller 3 — Inteligencia Artificial

- **P1**: Unsupervised Machine Learning
- **P2**: Linear Programming
- **P3**: Algoritmos Genéticos

---

## GLPK package (P2)

The GLPK (GNU Linear Programming Kit) package is intended for solving large-scale linear programming (LP), mixed integer programming (MIP), and other related problems.

| OS | Instalación |
|----|-------------|
| Windows | https://winglpk.sourceforge.net/ |
| Linux | `apt-get install -y -qq glpk-utils` |
| Mac | `brew install glpk` |

---

## P3 — Algoritmos Genéticos

### Objetivo

Generar la frase **`GA Workshop! USFQ`** (17 caracteres) a partir de una población de 100 frases aleatorias usando un Algoritmo Genético. Se implementan 5 casos de estudio que comparan distintas configuraciones.

### Estructura del proyecto

```
Taller3/
└── P3_GA/
    ├── GA.py              # Clase GA + 5 casos de estudio (punto de entrada consola)
    ├── constants.py       # Enums de configuración
    ├── generalSteps.py    # Pasos generales del AG (población, aptitud, nueva generación)
    ├── operation.py       # Operadores: selección, cruce, mutación
    ├── util.py            # Función de distancia de Hamming
    └── GUI/
        ├── app.py         # Ventana principal PyQt5
        ├── worker.py      # Hilo de ejecución del AG (QThread)
        └── panels/
            ├── config_panel.py   # Panel de configuración (casos de estudio)
            ├── run_panel.py      # Panel de salida en tiempo real
            └── stats_panel.py    # Panel de estadísticas y gráficos
```

---

## Requisitos

```
Python >= 3.10
PyQt5 >= 5.15
matplotlib >= 3.7
```

Instalación de dependencias (si no están instaladas):

```bash
pip install PyQt5 matplotlib
```

---

## Cómo ejecutar

> **Directorio de trabajo obligatorio:** todos los comandos deben ejecutarse desde
> `_Soluciones/Grupo6/`  (el nivel que contiene la carpeta `Taller3/`).

```bash
cd _Soluciones/Grupo6
```

---

### Opción A — Consola (modo texto)

Edita la función `main()` al final de `GA.py` y descomenta el caso que quieres ejecutar:

```python
# GA.py  — función main()
if __name__ == "__main__":
    objective = "GA Workshop! USFQ"

    case_study_1(objective)   # Caso 1: coincidencias (DEFAULT)
    # case_study_2(objective) # Caso 2: distancia Hamming corregida
    # case_study_3(objective) # Caso 3: mutation_rate = 0.05
    # case_study_4(objective) # Caso 4: población = 200
    # case_study_5(objective) # Caso 5: combinación óptima (IMPROVED)
```

Luego ejecuta desde la terminal (directorio `_Soluciones/Grupo6/`):

```bash
python3 -m Taller3.P3_GA.GA
```

O bien desde PyCharm: abre `GA.py` y presiona el botón **Run** (el punto de entrada
`if __name__ == "__main__"` ya está configurado).

#### Ejecutar un caso específico directamente desde Python

```python
# Desde _Soluciones/Grupo6/
from Taller3.P3_GA.GA import case_study_1, case_study_5

objective = "GA Workshop! USFQ"
case_study_1(objective)   # ejecuta el Caso 1
case_study_5(objective)   # ejecuta el Caso 5 (convergencia más rápida)
```

---

### Opción B — Interfaz gráfica (GUI)

El lanzador se encuentra en `Taller3/P3_GA/GUI/run_gui.py`. Ejecuta:

```bash
python3 Taller3/P3_GA/GUI/run_gui.py
```

O desde PyCharm: abre `Taller3/P3_GA/GUI/run_gui.py` y presiona **Run**.

#### Pasos dentro de la GUI

1. **Selecciona el caso de estudio** en el menú desplegable superior izquierdo.
   - La descripción del caso aparece automáticamente en el cuadro de texto.
   - Los parámetros (población, mutación, iteraciones) se auto-completan.
2. **Ajusta los parámetros** si deseas experimentar con valores distintos.
3. Presiona **Ejecutar AG** (botón verde).
4. Observa la evolución generación a generación en el **panel central**:
   - Letras en **verde** = coinciden con el objetivo.
   - Letras en **rojo** = aún difieren.
   - La barra de progreso muestra el porcentaje de caracteres correctos.
5. Al finalizar, el **panel derecho** muestra:
   - Gráfico de convergencia (mejor aptitud, media, coincidencias por generación).
   - Tabla con los datos de cada generación.
   - Resumen textual del resultado.
6. Presiona **Detener** en cualquier momento para interrumpir la ejecución.

#### Valores a ingresar por caso de estudio

> Los campos **Expresión objetivo** y **Semilla aleatoria** no cambian en ningún caso.

```
┌─────────────────────────────┬────────────────────────────────────┬────────┬────────┬────────────┬────────┐
│ Caso de estudio             │ Expresión objetivo                 │ Pobl.  │ Mut.   │ Iteraciones│ Semilla│
├─────────────────────────────┼────────────────────────────────────┼────────┼────────┼────────────┼────────┤
│ Caso 1 — Coincidencias      │ GA Workshop! USFQ                  │  100   │ 0.010  │    1000    │  123   │
│ Caso 2 — Distancia Hamming  │ GA Workshop! USFQ                  │  100   │ 0.010  │    1000    │  123   │
│ Caso 3 — Mutación alterada  │ GA Workshop! USFQ                  │  100   │ 0.050  │    1000    │  123   │
│ Caso 4 — Población aumentada│ GA Workshop! USFQ                  │  200   │ 0.010  │    1000    │  123   │
│ Caso 5 — Combinación óptima │ GA Workshop! USFQ                  │  200   │ 0.050  │    1000    │  123   │
└─────────────────────────────┴────────────────────────────────────┴────────┴────────┴────────────┴────────┘
```

> Al seleccionar cada caso en el dropdown, los campos de población, mutación e iteraciones
> se auto-completan con los valores correctos. Solo verifica que la expresión objetivo
> y la semilla sean las indicadas antes de presionar **Ejecutar AG**.

---

## Descripción de los 5 casos de estudio

| Caso | Población | Mutación | Selección | Cruce | Descripción |
|------|-----------|----------|-----------|-------|-------------|
| 1 | 100 | 0.01 | Ruleta | Un punto | DEFAULT — conteo de coincidencias (maximizar) |
| 2 | 100 | 0.01 | Partición aleatoria | Un punto | BY_DISTANCE — distancia de Hamming (minimizar) |
| 3 | 100 | **0.05** | Ruleta | Un punto | Tasa de mutación 5× mayor |
| 4 | **200** | 0.01 | Ruleta | Un punto | Población duplicada |
| 5 | **200** | **0.05** | **Torneo (k=3)** | **Dos puntos** | Combinación óptima + elitismo 10% |

### Respuestas a los ejercicios

**Ej. 1 — Resultados de los casos 1 y 2**
- **Caso 1** converge a la solución en ~200–400 generaciones.
- **Caso 2** (versión original con el bug) no convergía porque `distance()` acumulaba
  diferencias sin valor absoluto: valores positivos y negativos se cancelaban, haciendo
  que individuos muy distintos tuvieran distancia ≈ 0.

**Ej. 2 — Por qué el Caso 2 fallaba**
En `util.py`, la función `distance()` usaba `acc += (e1 - e2)`. Si un carácter tenía
ASCII mayor que el objetivo y el siguiente tenía ASCII menor, los errores se anulaban
entre sí. La aptitud no reflejaba la distancia real, por lo que la selección de padres
no tenía señal útil.

**Ej. 3 — Corrección de `distance()`**
Se reemplazó `(e1 - e2)` por `abs(e1 - e2)`, produciendo la **distancia de Hamming**
real en el espacio ASCII. Ahora la aptitud decrece monotónicamente al acercarse al
objetivo y el Caso 2 converge correctamente.

**Ej. 4 — Mejoras sin alterar `mutation_rate`**
Se implementaron en `operation.py` y `generalSteps.py` (tipo `IMPROVED`):
- **Selección por torneo** (k=3): elige el mejor de 3 individuos al azar → mayor
  presión selectiva que la ruleta sin perder diversidad.
- **Cruce de dos puntos**: intercambia el segmento central → mayor recombinación.
- **Elitismo** (top 10%): los mejores individuos pasan intactos → no se pierde la
  mejor solución encontrada entre generaciones.

**Ej. 5 — Caso 3: tasa de mutación alterada**
Con `mutation_rate = 0.05` la convergencia es menos estable: la mayor mutación
introduce diversidad pero puede destruir caracteres ya correctos. El rango óptimo
para este problema es **0.01 – 0.05**; por encima de 0.1 el AG se comporta como
búsqueda aleatoria.

**Ej. 6 — Caso 4: tamaño de población**
Con 200 individuos la diversidad inicial es mayor, lo que reduce la convergencia
prematura. La convergencia es más suave y confiable, aunque cada generación
tarda el doble en procesarse.

**Ej. 7 — Caso 5: combinación definitiva**
Población 200 + mutación 0.05 + IMPROVED (elitismo + torneo + cruce 2 puntos).
En las pruebas converge en **~25–60 generaciones**, comparado con ~200–400 del Caso 1.

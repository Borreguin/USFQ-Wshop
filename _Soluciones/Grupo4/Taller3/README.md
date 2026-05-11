# Taller 3 de inteligencia artificial

- P1: Unsupervised Machine Learning
- P2: Linear Programming

## GLPK package:
The GLPK (GNU Linear Programming Kit) package is intended for solving large-scale linear programming (LP), mixed integer programming (MIP), and other related problems. It is a set of routines written in ANSI C and organized in the form of a callable library.
This project uses this Linear Programming Kit to solve large-scale problems related to Logistics. 

The installation of this package depends on the Operating System:

Windows: https://winglpk.sourceforge.net/

Linux: apt-get install -y -qq glpk-utils

Mac:  brew install glpk


# Resumen - Algoritmos Genéticos (Taller 3, P3_GA)

## Objetivo del Proyecto
Implementar y optimizar un Algoritmo Genético para generar la frase objetivo: **"GA Workshop! USFQ"** (17 caracteres)
a partir de una población inicial de individuos aleatorios, analizando el impacto de distintos parámetros y operadores evolutivos.

---

## Modificaciones Realizadas

### 1. Corrección de `util.py`
**Problema:** La función `distance()` original sumaba las diferencias ASCII **sin valor absoluto**, lo que provocaba que diferencias positivas y negativas se cancelaran entre sí. Como resultado, cadenas de espacios en blanco obtenían distancia **-869** (el mínimo posible), siendo seleccionadas como los mejores individuos por `MIN_DISTANCE`. El algoritmo evolucionaba en dirección opuesta al objetivo.

```python
# ANTES — con error
acc += (e1 - e2)                          # sin abs(): produce valores negativos

# DESPUÉS — corregida
acc += abs(e1 - e2)                       # Distancia Manhattan: siempre >= 0
return acc + (abs(len(list1) - len(list2)) * 100)  # penaliza diferencia de longitud
```

### 2. Mejoras en `operation.py`
- **Selección por Torneo** (`ParentSelectionType.NEW`): Selecciona al mejor individuo de un subconjunto aleatorio de tamaño `k`. Mantiene presión selectiva constante incluso cuando las aptitudes son similares, eliminando los estancamientos prolongados de la selección por ruleta.
- **Cruce Uniforme** (`CrossoverType.NEW`): Decide gen a gen (probabilidad 50%) de cuál padre hereda cada posición. Permite combinar genes correctos dispersos en distintas posiciones, a diferencia del cruce de un punto que solo recombina dos bloques contiguos.

### 3. Nuevos Tipos en `generalSteps.py`
- **`NewGenerationType.NEW`**: Combina `ParentSelectionType.NEW` (torneo) + `CrossoverType.NEW` (uniforme) para una generación de nueva población con convergencia óptima.

### 4. Casos de Estudio en `GA.py`
- **Caso 1**: `DEFAULT` — coincidencias exactas, línea base
- **Caso 2**: `BY_DISTANCE` — requería corrección en `util.py`
- **Caso 3**: `mutation_rate = 0.05` — evaluación del impacto de mayor mutación
- **Caso 4**: Población = 200 — evaluación del tamaño de población
- **Caso 5**: DEFINITIVO — población 150, `mutation_rate` 0.02, torneo + cruce uniforme

---

## Resultados Obtenidos

| Caso | Población | `mutation_rate` | Selección | Cruce | Generaciones | Resultado |
|:----:|:---------:|:---------------:|:---------:|:-----:|:------------:|:---------:|
| 1: DEFAULT | 100 | 0.01 | Ruleta | Punto único | **982** | ✅ Converge |
| 2: BY_DISTANCE | 100 | 0.01 | Min. Distancia | Punto único | **1000** | ❌ No converge |
| 3: Mutation 0.05 | 100 | 0.05 | Ruleta | Punto único | **1000** | ❌ No converge |
| 4: Población 200 | 200 | 0.01 | Ruleta | Punto único | **507** | ✅ Converge |
| **5: DEFINITIVO** | **150** | **0.02** | **Torneo** | **Uniforme** | **71** | ✅ **Converge** |

---

## Hallazgos Clave

| Componente | Hallazgo |
|------------|----------|
| **Función `distance()`** | Sin `abs()`, produce valores negativos que invierten la presión selectiva. La corrección con distancia Manhattan garantiza que individuos más similares al objetivo tengan siempre distancia menor. |
| **Operador de selección** | Torneo > Ruleta. La ruleta pierde presión selectiva cuando las aptitudes son similares, causando estancamientos de 100–250 generaciones. El torneo los elimina. |
| **Operador de cruce** | Cruce uniforme > Punto único. Permite combinar genes correctos en posiciones no contiguas, acelerando la convergencia. |
| **`mutation_rate`** | Con operadores por defecto, el óptimo es **0.01**. Subir a 0.05 destruye genes correctos con mayor frecuencia que los corrige (no convergió). Con operadores mejorados, **0.02** es beneficioso. |
| **Tamaño de población** | Duplicar de 100 a 200 redujo generaciones de 982 a 507 (~48% menos) con costo computacional total similar (~100K evaluaciones). Óptimo observado: **150 individuos**. |
| **Mejora combinada** | El Caso 5 es **13.8× más rápido** que el Caso 1 (71 vs. 982 generaciones) y ~9× más eficiente en evaluaciones totales (~10,650 vs. ~98,200). |

---

## Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `GA.py` | Clase principal `GA` y definición de los 5 casos de estudio |
| `generalSteps.py` | Generación de población, evaluación de aptitud y generación de nueva población |
| `operation.py` | Operadores evolutivos: selección de padres, cruce y mutación |
| `util.py` | Función `distance()` corregida (distancia Manhattan) |
| `P3_GA_Taller3_Final.ipynb` | Notebook con análisis completo, resultados y conclusiones de los 5 casos |

---

## Conclusión

La configuración definitiva del **Caso 5** — población 150, `mutation_rate` 0.02, selección por torneo (`ParentSelectionType.NEW`) y 
cruce uniforme (`CrossoverType.NEW`) — converge en **71 generaciones**, frente a las 982 del caso base. Las mejoras son sinérgicas: 
a mayor diversidad inicial alimenta al torneo, el torneo garantiza presión selectiva constante, el cruce uniforme combina los mejores genes disponibles, y la corrección de `distance()` asegura que la función de aptitud BY_DISTANCE guíe la evolución en la dirección correcta.
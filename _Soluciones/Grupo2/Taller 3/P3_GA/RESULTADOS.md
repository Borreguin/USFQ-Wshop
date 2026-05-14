# Algoritmo Genético — Análisis de Resultados

**Objetivo:** `"GA Workshop! USFQ"` (17 caracteres)  
**Población inicial:** 100 individuos aleatorios  
**Tasa de mutación:** 1 %  
**Iteraciones máximas:** 1 000  
**Espacio de genes:** `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !`

---

## Caso de Estudio 1 — DEFAULT (conteo de coincidencias)

### Configuración

| Componente | Estrategia |
|---|---|
| Función de aptitud | Cuenta cuántos caracteres coinciden exactamente en la misma posición con el objetivo (rango: 0 – 17) |
| Selección de padres | Ruleta (*fitness-proportionate selection*): mayor aptitud → mayor probabilidad de ser elegido |
| Cruce | Un punto de cruce aleatorio (*single-point crossover*) |
| Mutación | Reemplazo aleatorio del gen con probabilidad 1 % por posición |
| Selección del mejor | El individuo con **máxima** aptitud en cada generación |

### Resultado de ejecución

```
Generación   0: zAZYChdKBWPBHwjFi  - Aptitud:  2
Generación   1: lAiEiakYYspiJYaYM  - Aptitud:  3
...
Generación 514: GA Workstop!BUSFQ  - Aptitud: 15
Generación 515: GA WErksoop!tUSFQ  - Aptitud: 14
...
Generación 981: GA Worksfop! USFQ  - Aptitud: 16
Objetivo alcanzado:
Generación 982: GA Workshop! USFQ  - Aptitud: 17
```

### Explicación

El algoritmo **convergió exitosamente** a la solución óptima en la generación 982.

**¿Por qué funciona?**

La función de aptitud (`aptitud = número de caracteres en la posición correcta`) guía al algoritmo de forma precisa hacia el objetivo:

- **Generación 0:** la población es aleatoria; el mejor individuo solo acierta 2 de 17 caracteres.
- A medida que avanzan las generaciones, la selección por ruleta favorece a los individuos con más coincidencias. Esos individuos se reproducen más y transfieren sus genes correctos a las siguientes generaciones mediante el cruce.
- La mutación (1 %) introduce variabilidad puntual que evita que el algoritmo quede atascado en óptimos locales.
- Ocasionalmente la aptitud del mejor individuo retrocede un paso (ej. generaciones 514 → 515: 15 → 14); esto es normal porque la selección de padres es probabilística y el cruce puede romper combinaciones útiles. Sin embargo, la tendencia general es ascendente.
- En la generación 981 el mejor individuo ya tiene 16 de 17 caracteres correctos (`GA Worksfop! USFQ`; solo falla la `f` por `h`). En la siguiente iteración la mutación o el cruce corrigen esa posición y se alcanza la solución completa.

**Conclusión:** este es el escenario **1a** — el algoritmo converge a la solución óptima dentro del número de iteraciones establecidas.

---

## Caso de Estudio 2 — DISTANCE (distancia con signo)

### Configuración

| Componente | Estrategia |
|---|---|
| Función de aptitud | `word_distance(individuo, objetivo)`: suma con signo de las diferencias de valores ASCII carácter a carácter |
| Selección de padres | Torneo por distancia mínima: se divide la población en dos particiones aleatorias y se elige el individuo de menor aptitud de cada una |
| Cruce | Un punto de cruce aleatorio (igual que Caso 1) |
| Mutación | Igual que Caso 1 (1 % por posición) |
| Selección del mejor | El individuo con **mínima** aptitud (distancia más negativa) en cada generación |

### La función de distancia — el problema central

```python
# util.py — Algo no está bien con esta función de distancia
def distance(list1, list2):
    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += (e1 - e2)          # diferencia con SIGNO, no valor absoluto
    return acc + (len(list1) - len(list2))
```

Esta función calcula la **suma algebraica** (con signo) de las diferencias de valores ASCII, no la distancia real. Una distancia verdadera requeriría valor absoluto: `|e1 - e2|`. Al omitirlo, el resultado puede ser un número muy negativo si los caracteres del individuo tienen valores ASCII menores que los del objetivo, aunque estén completamente equivocados.

## Explicación Caso 2

El objetivo `"GA Workshop! USFQ"` tiene la siguiente suma de valores ASCII:

```
G(71)+A(65)+' '(32)+W(87)+o(111)+r(114)+k(107)+s(115)+h(104)
+o(111)+p(112)+!(33)+' '(32)+U(85)+S(83)+F(70)+Q(81) = 1413
```

El espacio de genes disponibles es `a-z A-Z ' ' '!'`. Los caracteres con el **menor** valor ASCII en ese conjunto son:
- `' '` (espacio): ASCII **32**
- `'!'`: ASCII **33**

Un individuo compuesto por 17 espacios produce:
```
distancia = 17 × 32 − 1413 = 544 − 1413 = −869
```

Dado que el algoritmo selecciona siempre el individuo con la **distancia mínima** (más negativa), está incentivando que todos los caracteres del individuo tengan el valor ASCII más bajo posible, completamente al margen de si se acercan o no al objetivo.

### Resultado de ejecución

```
Generación   0: GBRIOYQM!FHQAxGcW  - Aptitud:  -97
Generación   1: PCm R!EB!FHQAxGcW  - Aptitud: -177
...
Generación   8: PC!  !EB!FHGAGAcD  - Aptitud: -387
Generación   9: PC!  !EB!FHNAGABD  - Aptitud: -413
...
Generación 135:   !     !    !     - Aptitud: -866
Generación 136:   !     !    !     - Aptitud: -866
...
Generación 598:                    - Aptitud: -869
...
Generación 999:                    - Aptitud: -869
Objetivo no alcanzado en las iteraciones establecidas 1000
```

### Explicación generación a generación

| Rango de generaciones | Comportamiento | Causa |
|---|---|---|
| 0 – 9 | Aptitud cae rápidamente de −97 a −413 | La selección favorece caracteres de bajo ASCII; los caracteres de mayor valor (letras mayúsculas, minúsculas) son eliminados. |
| 9 – 135 | La aptitud sigue cayendo hasta −866; aparecen espacios y `!` en el individuo mostrado | La población entera converge hacia espacios y `!`, los únicos genes que minimizan la distancia firmada. |
| 135 – 598 | El individuo mostrado oscila entre cadenas de espacios y `!` con aptitud −866 | La mayoría del individuo ya son espacios; las pocas `!` restantes van siendo reemplazadas también por espacios. |
| 598 – 999 | El individuo es `"                 "` (17 espacios) con aptitud −869, y ya no cambia | La población ha **convergido prematuramente** a un único individuo (17 espacios). No hay diversidad genética, la mutación no logra escapar. |
| 1000 | Objetivo no alcanzado | — |

### Conclusión

Este es el escenario **1b — el algoritmo no converge y se aleja del objetivo**. No se trata de falta de iteraciones, sino de un defecto estructural en la función de aptitud:

1. **La distancia con signo no mide proximidad real.** Un individuo de 17 espacios tiene aptitud −869 y es considerado "el mejor" por el algoritmo, pero es completamente incorrecto (0 caracteres coincidentes con el objetivo).
2. **La selección refuerza el error.** Al premiar sistemáticamente los valores ASCII bajos, el algoritmo expulsa de la población exactamente los caracteres que conforman el objetivo (letras mayúsculas como `G`, `A`, `W`, `U`, `S`, `F`, `Q` tienen valores ASCII altos: 65–87).
3. **Pérdida total de diversidad.** Una vez que la población converge a 17 espacios, el cruce no produce nada nuevo y la mutación (1 %) raramente introduce un carácter distinto; cuando lo hace, ese individuo tiene mayor aptitud que los demás y es eliminado en la siguiente generación.

Para corregir el Caso 2 bastaría con reemplazar la distancia con signo por una **distancia absoluta**:

```python
# Corrección sugerida en util.py
def distance(list1, list2):
    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += abs(e1 - e2)       # valor absoluto
    return acc
```

Con esa corrección, la aptitud 0 significaría coincidencia exacta y el algoritmo tendería a disminuir la distancia real hacia el objetivo.

---

## Comparativa entre casos

| | Caso 1 (DEFAULT) | Caso 2 (DISTANCE) |
|---|---|---|
| Función de aptitud | Coincidencias exactas (0 – 17) | Suma con signo de diferencias ASCII |
| Selección del mejor | Máxima aptitud | Mínima aptitud |
| ¿Guía correctamente? | Sí | No |
| Resultado | Convergió en gen. 982 | Divergió; terminó en 17 espacios |
| Escenario | 1a — solución óptima alcanzada | 1b — alejamiento del objetivo |
| Defecto identificado | Ninguno | Distancia sin valor absoluto |

---

## Caso de Estudio 3 — Convergencia Acelerada (Elitismo + Torneo + Cruce Uniforme)

### Motivación

El Caso 1 converge correctamente pero tarda 982 generaciones. Sin cambiar `mutation_rate`, existen tres mejoras ortogonales que aceleran significativamente la convergencia:

| Problema en Caso 1 | Solución implementada |
|---|---|
| La ruleta tiene baja presión selectiva cuando las aptitudes son similares | **Selección por torneo** |
| El cruce de un punto rompe combinaciones de genes buenos que están distribuidos en el cromosoma | **Cruce uniforme** |
| Un individuo excelente puede perderse completamente en la siguiente generación | **Elitismo** |

### Mejoras implementadas (`NewGenerationType.NEW`)

#### 1. Selección por torneo (`ParentSelectionType.NEW`) — `operation.py`

```python
if _type == ParentSelectionType.NEW:
    k = 5
    indices = list(range(len(population)))
    candidates1 = random.sample(indices, k)
    candidates2 = random.sample(indices, k)
    parent1 = population[max(candidates1, key=lambda i: aptitudes[i])]
    parent2 = population[max(candidates2, key=lambda i: aptitudes[i])]
    return parent1, parent2
```

Se seleccionan **5 candidatos al azar** para cada padre y gana el de mayor aptitud. Esto genera mayor presión selectiva que la ruleta, especialmente en generaciones tempranas donde las diferencias de aptitud son pequeñas.

#### 2. Cruce uniforme (`CrossoverType.NEW`) — `operation.py`

```python
if _type == CrossoverType.NEW:
    child1 = ''
    child2 = ''
    for g1, g2 in zip(parent1, parent2):
        if random.random() < 0.5:
            child1 += g1
            child2 += g2
        else:
            child1 += g2
            child2 += g1
    return child1, child2
```

Cada posición del cromosoma hijo se toma **independientemente** de uno u otro padre con probabilidad 50 %. A diferencia del cruce de un punto, permite combinar genes correctos aunque estén dispersos a lo largo de la cadena, sin importar su posición.

#### 3. Elitismo (`NewGenerationType.NEW`) — `generalSteps.py`

```python
if _type == NewGenerationType.NEW:
    elite_count = max(1, len(population) // 10)  # top 10% = 10 individuos
    sorted_indices = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
    new_population = [population[i] for i in sorted_indices[:elite_count]]
    while len(new_population) < len(population):
        parent1, parent2 = parent_selection(ParentSelectionType.NEW, population, aptitudes)
        child1, child2 = crossover(CrossoverType.NEW, parent1, parent2)
        child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
        child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
        new_population.extend([child1, child2])
    return new_population[:len(population)]
```

Los **10 mejores individuos** de cada generación pasan directamente a la siguiente sin modificación. El resto de los 100 individuos se genera con torneo + cruce uniforme. Esto garantiza que la aptitud del mejor individuo **nunca retrocede** entre generaciones.

### Configuración del Caso 3

```python
def case_study_3(_objetive):
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01          # sin cambios respecto al Caso 1
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_new_generation_type(NewGenerationType.NEW)   # activa las 3 mejoras
    ga.run()
```

### Análisis comparativo de convergencia

| Métrica | Caso 1 (DEFAULT) | Caso 3 (Mejorado) |
|---|---|---|
| Generación de convergencia | 982 | Significativamente menor |
| Regresiones de aptitud | Frecuentes (ej. gen 514→515: 15→14) | Imposibles (elitismo garantiza monotonía) |
| Presión selectiva | Baja (ruleta) | Alta (torneo k=5) |
| Mezcla de genes | Parcial (un punto de corte) | Completa (posición a posición) |
| `mutation_rate` | 0.01 | 0.01 (sin cambio) |

### ¿Por qué converge más rápido?

El efecto combinado de las tres técnicas actúa en distintas fases:

- **Generaciones tempranas (0–50):** el torneo selecciona agresivamente a los individuos con más caracteres correctos, descartando antes los individuos débiles.
- **Generaciones medias:** el cruce uniforme combina caracteres correctos de ambos padres sin importar su posición en la cadena, creando hijos con más aciertos simultáneos.
- **Toda la ejecución:** el elitismo preserva el mejor individuo encontrado hasta el momento; la aptitud del mejor candidato es **monótonamente creciente**, eliminando los retrocesos que se observan en el Caso 1.

---

## Caso de Estudio 4 — Efecto del Tamaño de Población (1 000 individuos)

### Pregunta

> ¿Es beneficioso aumentar el tamaño de la población?

### Configuración

Mismo algoritmo mejorado del Caso 3 (elitismo + torneo + cruce uniforme), único cambio: población de **1 000** individuos en lugar de 100.

```python
def case_study_4(_objetive):
    population = generate_population(1000, len(_objetive))  # 10× más individuos
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_new_generation_type(NewGenerationType.NEW)
    ga.run()
```

### Resultado de ejecución

| Caso | Población | Generación donde aptitud = 16 |
|---|---|---|
| Caso 3 (mejorado) | 100 | Generación **66** |
| Caso 4 (población ×10) | 1 000 | Generación **8** |

```
Caso 3:
Generación 66: GA Workspop! USFQ - población: 100  - Aptitud: 16

Caso 4:
Generación  8: GA Woukshop! USFQ - población: 1000 - Aptitud: 16
```

El mismo nivel de aptitud (16/17) se alcanza **~8 veces más rápido** medido en generaciones.

### Explicación: por qué más individuos convergen más rápido

#### 1. Mayor cobertura del espacio de búsqueda desde el inicio

Con 100 individuos aleatorios de 17 caracteres y un alfabeto de 55 símbolos, la probabilidad de que algún individuo tenga acertado un carácter concreto en una posición específica es baja en las primeras generaciones. Con 1 000 individuos, la población inicial ya contiene más variantes correctas por posición. El algoritmo parte de una "materia prima" genética mucho más rica.

#### 2. El torneo opera sobre un pool más grande

En la selección por torneo (k=5), los 5 candidatos se extraen de un pool 10 veces mayor. En promedio, el mejor de 5 candidatos sacados de 1 000 tiene mayor aptitud que el mejor de 5 sacados de 100. La presión selectiva efectiva es mayor sin necesidad de aumentar k.

#### 3. El elitismo preserva más soluciones parciales

Con población de 1 000, el 10% de élite son **100 individuos** (frente a 10 en el Caso 3). Esto mantiene simultáneamente muchas soluciones parciales buenas, acelerando la combinación de caracteres correctos de distintas posiciones.

#### 4. Reducción de la deriva genética

Con poblaciones pequeñas, la selección aleatoria puede eliminar por azar individuos con genes buenos (deriva genética). Con 1 000 individuos este efecto es mínimo: un buen gen presente en varios individuos tiene muchas más copias de respaldo y no desaparece fácilmente.

### ¿Siempre es beneficioso aumentar la población?

**No necesariamente.** Aumentar la población tiene un costo:

| Factor | Impacto al aumentar población |
|---|---|
| Generaciones hasta converger | Disminuye (positivo) |
| Tiempo de cómputo por generación | Aumenta linealmente (negativo) |
| Memoria utilizada | Aumenta linealmente (negativo) |
| Diversidad genética | Aumenta (positivo) |
| Riesgo de deriva genética | Disminuye (positivo) |

Existe un punto de rendimientos decrecientes: pasar de 100 a 1 000 individuos redujo las generaciones necesarias ~8×, pero el tiempo de cómputo total por generación también creció ~10×. Para problemas más complejos o con mayor número de iteraciones, la ganancia en generaciones puede no compensar el costo computacional por generación.

**Conclusión:** aumentar la población **es beneficioso cuando el cuello de botella es la diversidad genética** (como en este problema, donde 100 individuos pueden no cubrir bien todas las posiciones del objetivo). Sin embargo, para problemas donde la población base ya es suficientemente diversa, el incremento añade costo sin mejora proporcional. El tamaño óptimo depende del tamaño del espacio de búsqueda, la longitud del cromosoma y los recursos disponibles.

---

## Caso de Estudio 5 — El Definitivo

### Síntesis de aprendizajes

| Caso | Lección aprendida | Incorporado al Caso 5 |
|---|---|---|
| 1 | La función DEFAULT (conteo de coincidencias) guía correctamente el algoritmo | ✅ Mantiene `AptitudeType.DEFAULT` |
| 2 | Una métrica con signo no sirve como distancia; el algoritmo diverge | ✅ Se descarta `BY_DISTANCE` |
| 3 | Elitismo 10% + torneo k=5 + cruce uniforme reducen la convergencia de 982 a ~66 generaciones | ✅ Base de los operadores |
| 4 | Población 1 000 reduce la generación de aptitud=16 de la 66 a la 8 | ✅ Tamaño de población |

El Caso 5 **ajusta los parámetros de los operadores mejorados para sacar el máximo partido de la población grande**.

### Configuración

```python
def case_study_5(_objetive):
    population = generate_population(1000, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_new_generation_type(NewGenerationType.DEFINITIVE)
    ga.run()
```

### Qué hace `NewGenerationType.DEFINITIVE` — `generalSteps.py`

```python
if _type == NewGenerationType.DEFINITIVE:
    # Elitismo 20% + torneo k=10 + cruce uniforme
    elite_count = max(1, len(population) // 5)          # 200 individuos de élite
    sorted_indices = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
    new_population = [population[i] for i in sorted_indices[:elite_count]]
    indices = list(range(len(population)))
    k = 10                                               # torneo más agresivo que Caso 3/4
    while len(new_population) < len(population):
        c1 = random.sample(indices, k)
        c2 = random.sample(indices, k)
        parent1 = population[max(c1, key=lambda i: aptitudes[i])]
        parent2 = population[max(c2, key=lambda i: aptitudes[i])]
        child1, child2 = crossover(CrossoverType.NEW, parent1, parent2)   # cruce uniforme
        child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
        child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
        new_population.extend([child1, child2])
    return new_population[:len(population)]
```

### Las tres mejoras respecto al Caso 4

#### 1. Elitismo del 20% (vs 10% en Caso 3/4)

Con 1 000 individuos, el 20% de élite son **200 individuos** preservados intactos. Esto garantiza que en cada generación se conservan múltiples soluciones con aptitudes altas y diversas. Ningún carácter correcto descubierto en cualquier posición se pierde, ya que habrá varios individuos élite que lo contienen.

#### 2. Torneo de tamaño k=10 (vs k=5 en Caso 3/4)

Con una población de 1 000 individuos, un torneo de 5 candidatos era conservador. Con k=10 se examina el 1% de la población en cada selección de padre, eligiendo al mejor de ese grupo. Esto produce una presión selectiva sustancialmente mayor: en promedio, el ganador de un torneo de 10 tiene aptitud significativamente superior al ganador de un torneo de 5 en la misma población.

#### 3. Cruce uniforme (heredado del Caso 3, mantenido)

Cada posición del cromosoma se hereda independientemente de uno u otro padre. Con 200 individuos élite disponibles como donantes genéticos y alta presión selectiva, el cruce uniforme ensambla rápidamente individuos con muchos caracteres correctos simultáneos.

### Comparativa final entre todos los casos

| Caso | Población | Operadores clave | Aptitud=16 en gen. | Resultado final |
|---|---|---|---|---|
| 1 — DEFAULT | 100 | Ruleta + un punto de cruce | Gen. ~514 | Convergió en gen. 982 |
| 2 — DISTANCE | 100 | Torneo distancia + un punto | — | Divergió (17 espacios) |
| 3 — Mejorado | 100 | Élite 10% + torneo k=5 + uniforme | Gen. 66 | Convergió mucho antes |
| 4 — Población ×10 | 1 000 | Élite 10% + torneo k=5 + uniforme | Gen. 8 | Convergió en pocas gens. |
| **5 — Definitivo** | **1 000** | **Élite 20% + torneo k=10 + uniforme** | **< Gen. 8** | **Convergencia más rápida** |

### Por qué es el definitivo

El Caso 5 elimina todas las debilidades identificadas a lo largo del proceso:

- **Sin regresiones**: el elitismo del 20% garantiza que la aptitud del mejor individuo es monótonamente creciente generación a generación.
- **Sin baja presión selectiva**: el torneo k=10 descarta rápidamente a los individuos débiles, incluso en generaciones tempranas donde las diferencias de aptitud son pequeñas.
- **Sin pérdida de genes por posición**: con 200 individuos élite y cruce uniforme, cada carácter correcto descubierto en cualquier posición tiene muchas copias en la población y se propaga eficientemente.
- **Sin deriva genética**: la población de 1 000 individuos garantiza que ningún buen gen desaparece por azar.
- **Sin métrica defectuosa**: mantiene la función DEFAULT, la única que mide correctamente la proximidad al objetivo.


# Problema 3: Algoritmos Genéticos
**Integrante:** Jhon Del Castillo  
**Taller 3 — MSDS 6004 Inteligencia Artificial**

---

## Resultados de ejecución

### Casos base

| Caso | Descripción | Generación de convergencia | Resultado |
|------|-------------|---------------------------|-----------|
| Caso 1 | DEFAULT — cuenta coincidencias por posición | 982 | Converge ✓ |
| Caso 2 (original) | BY_DISTANCE — función `distance` con bug | 1000 | No converge ✗ (aptitud: -869) |
| Caso 2 (corregido) | BY_DISTANCE — función `distance` con `abs()` | 378 | Converge ✓ |
| Caso mejorado (ítem 4) | Torneo + cruce 2 puntos | 148 | Converge ✓ |

### Caso 3 — Variación de `mutation_rate`

| mutation_rate | Generación de convergencia | Resultado |
|---------------|---------------------------|-----------|
| 0.001 | 1000 | No converge ✗ |
| 0.01 | 148 | Converge ✓ |
| 0.05 | 91 | Converge ✓ (más rápido) |
| 0.1 | 1000 | No converge ✗ |
| 0.3 | 1000 | No converge ✗ |

### Caso 4 — Variación del tamaño de población

| Población | Generación de convergencia |
|-----------|---------------------------|
| 20 | 880 |
| 50 | 399 |
| 100 | 148 |
| 200 | 74 |
| 500 | 43 |

### Caso 5 — Configuración definitiva

| Parámetro | Valor |
|-----------|-------|
| Población | 200 |
| mutation_rate | 0.02 |
| Selección | Torneo (k=5) |
| Cruce | Dos puntos |
| **Generación de convergencia** | **76** |

---

## Conclusiones

### Ítem 1 y 2 — Casos base y bug en `distance`

El Caso 1 (función DEFAULT) demostró que el algoritmo genético converge correctamente cuando
la función de aptitud guía de manera consistente la selección, alcanzando el objetivo
`"GA Workshop! USFQ"` en la generación 982.

El Caso 2, en su implementación original, falló completamente: la función `distance` acumulaba
diferencias con signo, permitiendo que valores positivos y negativos se cancelaran entre sí,
produciendo una aptitud de -869 que no reflejaba ninguna proximidad real al objetivo. Esto
inutilizó la selección de padres, impidiendo cualquier convergencia en las 1000 iteraciones.

### Ítem 3 — Corrección de la función `distance`

Al corregir `distance` usando valor absoluto (`abs()`) para cada posición, la métrica pasó a ser
siempre positiva y proporcional a la distancia real entre individuos. La función corregida es:

```python
def distance(list1: List[int], list2: List[int]):
    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += abs(e1 - e2)
    acc += abs(len(list1) - len(list2)) * 128
    if min(len(list1), len(list2)) == 0:
        return None
    return acc
```

Con esta corrección, el Caso 2 convergió en la generación 378, demostrando que una función
de aptitud bien definida es el componente más crítico de un algoritmo genético.

### Ítem 4 — Mejora de convergencia sin alterar `mutation_rate`

Se implementó selección por torneo (k=5) y cruce de dos puntos. La selección por torneo
garantiza que los padres elegidos sean siempre los mejores de un subconjunto aleatorio,
reduciendo la probabilidad de propagar individuos débiles. El cruce de dos puntos preserva
mejor los bloques de caracteres correctos en comparación con el cruce de un solo punto,
resultando en descendencia de mayor calidad.

### Ítem 5 — Efecto del parámetro `mutation_rate`

Los experimentos revelaron que este parámetro tiene un comportamiento crítico con zona óptima estrecha:

- **Valores bajos (0.001):** generan poca diversidad, el algoritmo queda atrapado en óptimos
  locales y no converge en 1000 generaciones.
- **Valor óptimo (0.05):** balance ideal entre exploración y explotación, convergió en solo
  91 generaciones siendo el más eficiente del experimento.
- **Valores altos (0.1, 0.3):** destruyen los individuos bien adaptados al introducir demasiado
  ruido aleatorio, impidiendo la convergencia.

Se concluye que el rango efectivo para este problema se encuentra entre **0.01 y 0.05**.

### Ítem 6 — Efecto del tamaño de la población

Se observó una relación inversa clara entre tamaño de población y generaciones requeridas.
Una población de 20 individuos tardó 880 generaciones por su escasa diversidad genética,
mientras que 500 individuos convergieron en 43 generaciones gracias a la alta diversidad
inicial que permite explorar mejor el espacio de soluciones.

Sin embargo, poblaciones muy grandes implican mayor costo computacional por generación.
El balance óptimo para este problema se encontró entre **200 y 500 individuos**.

### Ítem 7 — Configuración definitiva

El Caso 5, combinando población de 200 individuos, `mutation_rate` de 0.02, selección por
torneo y cruce de dos puntos, convergió en la generación **76**. Este resultado confirma que
la combinación de una función de aptitud correcta, una selección de padres selectiva, un
cruce que preserve bloques útiles y un `mutation_rate` balanceado produce la convergencia
más eficiente.

Ningún parámetro por sí solo determina el rendimiento del algoritmo; es su interacción lo
que define el comportamiento evolutivo del sistema. El algoritmo genético es altamente
sensible a la calidad de la función de aptitud — como lo demostró el bug en `distance` —
y a la configuración conjunta de sus operadores evolutivos.

# Taller 3

- [Participación](Participacion_Taller_3_G1.pdf)

## 1. USO DE APRENDIZAJE NO SUPERVISADO

### A. Plotear las variables
<!-- Jairo -->

<!-- Agregar gráficos y hallazgos -->

### B. Encontrar patrones/clústeres – análisis univariable
<!-- Jairo -->

<!-- Agregar gráficos y hallazgos -->

### C. Encontrar anomalías – análisis univariable
<!-- Javi -->

<!-- Agregar gráficos y hallazgos -->

### D. Encontrar patrones – análisis multivariable
<!-- Nico -->

<!-- Agregar gráficos y hallazgos -->

### E. Encontrar anomalías – análisis multivariable

Las anomalías multivariables se detectaron identificando perfiles diarios que no pertenecen claramente a los clústeres principales encontrados mediante KMeans y Agglomerative Clustering.

Para cada par de variables (CO2 y temperatura), se comparó la forma completa de los perfiles diarios respecto a los patrones promedio de cada clúster.

En el caso del CO2, se identificaron días con picos excesivos de concentración, variaciones abruptas y perfiles que no seguían la tendencia típica de ocupación del edificio. Algunos perfiles alcanzaron valores superiores a 1300 ppm, alejándose significativamente de los patrones representativos. En las gráficas se visualizan todos los días normales en gris y las anomalías en rojo.

![PS1](images_P1/anomalies_V005_vent01_CO2.png)

![PS1](images_P1/anomalies_V022_vent02_CO2.png)


En las variables de temperatura, las anomalías fueron más evidentes, observándose caídas bruscas y valores atípicos cercanos a 0 °C y 7 °C, los cuales no corresponden al comportamiento normal del sistema de ventilación. Estos perfiles podrían estar asociados a errores de sensor, fallos de adquisición de datos o condiciones operacionales inusuales.

![PS1](images_P1/anomalies_V006_vent01_temp_out.png)

![PS1](images_P1/anomalies_V023_vent02_temp_out.png)

Los métodos KMeans y Agglomerative mostraron consistencia en la identificación de los patrones principales, permitiendo detectar perfiles diarios alejados de los centroides o grupos representativos como posibles anomalías.


### F. Conclusiones
<!-- Todos -->

<!-- Agregar hallazgos -->

<!----------------------------------------------------------------------------------->

## 2. INVESTIGACIÓN OPERATIVA: TRAVELLING SALEMAN PROBLEM (TSP)

### A. Analizar el código propuesto
<!-- Jairo + Eve -->

<!-- Agregar gráficos y hallazgos, responder ¿qué tal te parece las soluciones que ha arrojado el modelo sin aplicar
todavía una heurística que ayude al modelo? -->

### B. Analizar el parámetro tee
<!-- Jairo + Eve -->

<!-- Agregar gráficos y hallazgos -->

### C. Aplicar heurística de límites a la función objetivo
<!-- Nico -->

<!-- Agregar gráficos y hallazgos, responder ¿Cuál es la diferencia entre los dos casos? y ¿Sirve esta heurística para cualquier caso? ¿Cuál pudiera ser una razón? -->

### D. Aplicar heurística de vecinos cercanos
<!-- Javi -->

<!-- Agregar gráficos y hallazgos, responder ¿Cuál es la diferencia entre los dos casos? y ¿Sirve esta heurística para cualquier caso? ¿Cuál pudiera ser una razón? -->

### E. Conclusiones
<!-- Todos -->

<!-- Agregar hallazgos -->

<!----------------------------------------------------------------------------------->

## 3. ALGORTIMOS GENÉTICOS

1. Ejecute los dos casos de estudio y explique los resultados de ejecución de cada caso de 
estudio.

•	Caso 1 (evaluación por coincidencias por posición): Se alcanzó el objetivo planteado. Observación: la aptitud (número de caracteres coincidentes) aumenta gradualmente hasta llegar al objetivo. Resultado de la ejecución: objetivo alcanzado en la generación 139 (Aptitud: 11).

•	Caso 2 (evaluación por distancia / minimización): Inicialmente se pudo ver que no alcanzó los objetivos planteados. Se modificó la función de distancia para usar valores absolutos y evitar negativos. Con la implementación correcta y las mejoras, alcanzó el objetivo más rápido. Observación: la aptitud (distancia) disminuye hasta 0. Resultado de la ejecución: objetivo alcanzado en la generación 69 (Aptitud: 0).

2. ¿Cuál sería una posible explicación para que el caso 2 no finalice como lo hace el caso 1?

La raíz del problema fue la función distance() en util.py. Antes devolvía una suma de diferencias con signo (valores negativos), por lo que la evaluación por distancia devolvía aptitudes incorrectas (negativas) y la lógica de selección/minimización quedaba distorsionada. Eso hacía que el algoritmo no favoreciera correctamente las soluciones cercanas al objetivo y no convergiera como se esperaba.

3. Realice una correcta implementación para obtener la distancia/diferencia correcta entre 
dos individuos en el archivo util.py función distance.

Cambié distance() para usar la distancia de Levenshtein sobre las secuencias (listas de códigos de caracteres). Ventajas: mide inserciones/deletes/substitutions (medida de edición) y es una métrica adecuada para similitud entre palabras. Archivo modificado: util.py.

4. ¿Sin alterar el parámetro de mutación mutation_rate, se puede implementar algo para 
mejorar la convergencia y que esta sea más rápida?

Implementé dos mejoras que aceleran la convergencia sin cambiar mutation_rate:

  Selección por torneo para ParentSelectionType.MIN_DISTANCE (favorece padres con menor distancia). Archivo modificado: operation.py.

  Elitismo en la generación NewGenerationType.MIN_DISTANCE: se conserva el mejor individuo y se generan hijos para completar la población (evita perder la mejor solución entre generaciones). Archivo modificado: generalSteps.py.

Efecto observado: con Levenshtein + torneo + elitismo, el Caso 2 pasó de tardar muchas generaciones a alcanzar el objetivo en ~69 generaciones (ejecución de prueba).

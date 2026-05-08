# Taller 2

## 1. USO DE ALGORITMOS DE BÚSQUEDA

### A. Leer el laberinto y representarlo como un grafo
Completar con conclusiones sobre parte A

### B. Aplicar algoritmos de búsqueda
Completar con conclusiones sobre parte B, responder:
¿Se puede establecer alguna métrica para evaluar los algoritmos en este problema?

Recordar agregar la solución a los laberintos como una imagen en el readme

## 2. OPTIMIZACIÓN DE COLONIAS DE HORMIGAS

### A. Correr la implementación planteada
A través del análisis de esta implementación de Colonia de Hormigas, se observó cómo el algoritmo combina eficientemente dos mecanismos clave: la explotación de rutas prometedoras mediante el depósito de feromonas y la exploración de nuevas posibilidades a través de la evaporación. Los parámetros alpha y beta juegan un papel crucial en el balance entre seguir rastros conocidos versus dirigirse hacia el objetivo final; en este caso, beta tiene un valor mucho mayor (15 versus 0.1), lo que indica que la cercanía al destino es más influyente que el historial de feromonas. Comparando los dos casos de estudio, vimos que la configuración de obstáculos afecta significativamente la convergencia del algoritmo, donde obstáculos que obligan a alejarse un poco de la meta o desviarse mucho del camino más corto sin obstáculos puede provocar errores debido a que los parámetros priorizan reducir la distancia a la meta. Sin embargo, identificamos una limitación importante en la lógica actual: el código selecciona el camino más corto sin verificar si realmente alcanza el destino, lo que podría resultar en soluciones incompletas como se obtuvo en el caso 2. Esta observación nos mostró la importancia de validar correctamente las soluciones en problemas de búsqueda de caminos.

Así mismo, se agregaron comentarios al código indicando lo que hace cada bloque identificado durante el análisis

### B. ¿Qué ocurre con el segundo caso de estudio?
En el segundo caso de estudio, nos enfrentamos a una barrera continua de obstáculos que bloquea gran parte del camino directo del inicio hacia el destino. El problema original residía en que el algoritmo seleccionaba el camino más corto sin verificar si realmente alcanzaba el destino, lo que era especialmente problemático en este escenario donde muchas hormigas quedarían atrapadas sin poder llegar. La solución implementada añade una condición crítica: filtrar únicamente los caminos que terminen en el destino (`path[-1] == self.end`) antes de seleccionar el más corto. Esto asegura que solo se refuercen con feromonas las rutas exitosas.

Además, para superar la dificultad adicional que representa la barrera continua, ajustamos los parámetros del algoritmo: aumentamos el número de hormigas a 30 para explorar más posibilidades en paralelo, redujimos la tasa de evaporación a 0.05 para mantener los rastros de feromona más tiempo (permitiendo que las soluciones se consoliden mejor), incrementamos alpha a 0.5 para confiar más en el historial de feromonas acumuladas, y aumentamos el número de iteraciones a 200 para dar más tiempo al algoritmo para converger. Estos cambios permiten que el algoritmo explore caminos alternativos alrededor de la barrera y refuerce gradualmente la ruta viable, demostrando cómo la sintonización de parámetros es esencial para adaptar el algoritmo a diferentes configuraciones del problema.

### C. Describir los parámetros del modelo
En este modelo, los parámetros controlan directamente cómo se comporta la colonia de hormigas al momento de buscar una ruta. `num_ants` define cuántas hormigas exploran el mapa en cada iteración, por lo que un valor más alto aumenta la exploración, aunque también eleva el costo computacional. `evaporation_rate` indica qué tan rápido desaparece la feromona acumulada; si es muy baja, el algoritmo puede aferrarse demasiado a caminos antiguos, y si es muy alta, pierde memoria de las rutas buenas demasiado rápido. `alpha` determina cuánto peso tiene la feromona en la decisión de movimiento, mientras que `beta` controla la influencia de la heurística, es decir, la cercanía al objetivo (la inversa de la distancia con norma euclideana). Los parámetros permiten balancear la búsqueda entre seguir experiencias previas y acercarse de forma más directa a la meta, al igual que permiten controlar qué tanto puede explorar nuevos caminos o mantenerse en los ya explorados.

### D. ¿Qué es Random Search y Grid Search? ¿Cómo aplicarlos para esta heurística?
Responder: Qué búsqueda de parámetros es la más adecuada para este ejercicio
Conclusiones sobre implementación de uno de los métodos de optimización de hiperparametros 

### E. Pregunta de investigación:
Responder: ¿Será que se puede utilizar este algoritmo para resolver el Travelling Salesman Problema (TSP)? ¿Cuáles serían los pasos de su implementación?

## 3. ENSAYO - Modelos de lenguaje y algoritmos de búsqueda: análisis, comparaciones y diferencias

- [Ensayo](Ensayo_G1_T2.pdf)


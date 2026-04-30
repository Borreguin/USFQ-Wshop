## Conclusiones a los problemas planteados
### P1: TSP – Travelling Salesman Problem – Problema del vendedor viajante

El problema consiste en encontrar un ciclo Hamiltoniano de costo mínimo: visitar cada ciudad exactamente una vez y volver al origen. Es un problema clásico de optimización combinatoria donde la calidad de la ruta depende de equilibrar exploración global y mejora local. En la práctica, para tamaños medianos y grandes, lo más útil no es garantizar óptimo exacto sino obtener soluciones muy buenas en poco tiempo.

Encontrar la solución exacta del TSP no escala bien, ya que la cantidad de recorridos posibles aumenta de forma factorial ($\sim n!$), motivo por el cual se clasifica como un problema NP-hard. Para instancias pequeñas puede resolverse exactamente, pero al incrementar $n$ el tiempo de cómputo se vuelve demasiado alto. Por eso, la estrategia heurística aplicada (vecino más cercano con multiarranque + 2-opt) resulta práctica: no garantiza el óptimo global, aunque suele entregar rutas de muy buena calidad en tiempos aceptables.

El TSP se modela naturalmente como un grafo completo ponderado donde cada nodo representa una ciudad y cada arista codifica la distancia entre pares de ciudades. Desde el punto de vista computacional, trabajar con coordenadas cartesianas y calcular distancias euclidianas agiliza la generación de la matriz de costos. Desde la perspectiva visual, plasmar las ciudades como puntos en un plano bidimensional y conectarlas mediante una línea cerrada permite analizar fácilmente la ruta obtenida e identificar patrones subóptimos como intersecciones innecesarias que algoritmos como 2-opt pueden corregir.

### P2: El acertijo del granjero y el bote

Se trata de una búsqueda en un espacio de estados con reglas de seguridad, no únicamente de desplazamiento. El punto central es definir correctamente las condiciones, ya que algunos estados, aunque parezcan próximos a la meta, no son válidos. Distinguir entre estado, creación de movimientos y verificación permite una solución ordenada, comprobable y reutilizable.

Para este caso concreto, la dificultad computacional es baja porque el espacio total es pequeño: $2^4 = 16$ estados posibles. Sin embargo, la dificultad real es de modelado lógico: definir correctamente qué estados son seguros y evitar ciclos. BFS es una elección muy sólida porque garantiza encontrar una solución mínima en número de cruces cuando todas las acciones tienen costo uniforme. Enumerar todas las soluciones también es manejable aquí, pero en variantes con más elementos el crecimiento combinatorio vuelve más costosa la exploración.

Representarlo como grafo es natural y didáctico, ya que los nodos corresponden a estados válidos y las aristas a movimientos permitidos. Además, la visualización por capas (distancia BFS) facilita la lectura del progreso desde el inicio hasta la meta. El reto principal no es matemático, sino de legibilidad: etiquetar estados y aristas sin saturar el diagrama. Por ello, combinar una salida textual paso a paso con un grafo visual resulta una estrategia muy efectiva, porque integra precisión lógica e interpretación humana.

### P3: La torre de Hanoi

Es un problema clásico de descomposición recursiva: mover $n$ discos se reduce a resolver dos veces el caso de $n-1$ con un movimiento central obligatorio. Tiene una estructura determinista y elegante, ya que al seguir las reglas la secuencia óptima queda totalmente definida. La implementación refleja bien esa naturaleza al separar la visualización del estado y la lógica recursiva de los movimientos.

Conceptualmente, la dificultad está en entender la recursión (caso base + llamada recursiva doble), no en encontrar “muchas alternativas”. Matemáticamente, la solución óptima tiene tamaño exacto $2^n - 1$, por lo que el tiempo crece exponencialmente con $n$. Esto implica que para valores pequeños o medianos es manejable, pero para $n$ grande el número de pasos crece muy rápido.

Representarlo como tres pilas (A, B, C) es muy natural porque coincide con la regla física de “apilar discos”, y la visualización paso a paso resulta didáctica al permitir verificar fácilmente que nunca se coloca un disco grande sobre uno pequeño. El principal reto aparece cuando $n$ crece, ya que se generan demasiados estados intermedios y la salida en consola se vuelve extensa. Como complemento, también puede representarse como árbol de recursión o grafo de estados, aunque para una enseñanza inicial la forma actual es clara y suficiente.


## Planificación de tareas - Notion
- [Enlace notion](https://www.notion.so/P3-Torre-de-Hanoi-cbe6d05ac39d486aabd2c87960644a3d?source=copy_link)

## Ensayo - Cuáles son los últimos avances en IA con chips analógicos
- [Ensayo](Ensayo_G1.pdf)
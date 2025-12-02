# WorkShop-USFQ
## Taller 2 de inteligencia artificial

- **Nombre del grupo**: Grupo 2
- **Integrantes del grupo**:

    • Daniel Grijalva

    • Sebastian Jacome

    • Danny Plaza

    • Jorge Sosa

1. USO DE ALGORITMOS DE BÚSQUEDA
    El objetivo de esta tarea es utilizar cualquier algoritmo de búsqueda para resolver los 3
    laberintos propuestos, el reto es poder visualizar/representar los resultados,
    adicionalmente poder comparar al menos 2 algoritmos de búsqueda y mirar cómo se
    comportan para cada laberinto.

    A. Leer	el	laberinto	y	representarlo	como	un	grafo
        Implementar	una	función	que	permita	transformar	la	información	del	laberinto	en	un	
        grafo,	buscar	la	mejor	manera	de	representar	la	información	del	laberinto.
    B. Aplicar	algoritmos	de	búsqueda	
        Una	vez	obtenido	el	grafo,	aplicar	al	menos	dos	algoritmos	de	búsqueda	para	comparar	
        su	 comportamiento,	efectividad	 y	 rapidez. ¿Se	 puede	establecer	alguna	métrica	 para	
        evaluar	los	algoritmos	en	este	problema?

2. OPTIMIZACIÓN	DE	COLONIAS	DE	HORMIGAS
Ant	 Colony	 Optimization	 (ACO)	 es una técnica de optimización inspirada en el
comportamiento de las hormigas reales cuando buscan recursos para su colonia. El propósito de este algoritmo en el campo de la IA es el de simular el comportamiento de las hormigas para encontrar el mejor camino desde el nido de la colonia a la fuente de recursos.
    A. Correr	la	implementación	planteada
        En	el	repositorio,	en	la	carpeta	Taller2/P2/P2_ACO.py	se	plantea	un	ejemplo	de	este	
        algoritmo,	ejecutar	el	caso	de	estudio	1.	Analizar	el	código.
    B. ¿Qué	ocurre	con	el	segundo	caso	de	estudio?
        Se	plantea	el	caso	de	estudio	2,	sin	embargo,	algo	está	mal	en	la	selección	del	camino,	
        ¿puedes	arreglarlo?	Pistas:	
           1. Al	escoger	el	mejor	camino	una	condición	está	faltando,	¿es	suficiente	elegir	
           el	camino	con	el	menor	tamaño?
           2. Cambiar	el	número	de	hormigas,	cambiar	los	parámetros:	taza	de	
           evaporación,	Alpha,	Beta.
    C. Describir	los	parámetros	del	modelo
        ¿Qué	propósito	tiene	cada	parámetro	en	el	modelo?	
    D. Pregunta	de	investigación:
        ¿Será	que	se	puede	utilizar	este	algoritmo	para	resolver	el	Travelling	Salesman	
        Problema	(TSP)?	¿Cuáles	serían	los	pasos	de	su	implementación?
![Maze1](/Taller2/images/maze1.jpg) 

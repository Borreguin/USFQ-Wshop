# Resolución del TSP mediante Algoritmos Genéticos

Proyecto final de Inteligencia Artificial / Ciencia de Datos.

## Objetivo
Diseñar, implementar y analizar un Algoritmo Genético para resolver instancias del Traveling Salesman Problem (TSP), evaluando la calidad de las soluciones y el comportamiento del algoritmo mediante fitness, diversidad, comparación contra una heurística y análisis experimental de parámetros.

## Estructura del paquete

```text
tsp_ga_project/
├── code/
│   └── tsp_ga_analysis.py
├── data/
│   └── cities_100_*.csv
├── figures/
│   ├── *_convergencia.png
│   ├── *_diversidad.png
│   ├── *_ruta.png
│   ├── parametros_distancia.png
│   └── parametros_diversidad_unica.png
├── results/
│   ├── summary_all_datasets.csv
│   ├── parameter_experiment_largest_dataset.csv
│   ├── *_history.csv
│   └── *_best_route.csv
└── report/
    ├── informe_tsp_algoritmos_geneticos.docx
    └── informe_tsp_algoritmos_geneticos.pdf
```

## Datos
Los CSV tienen columnas `city`, `x`, `y`. Aunque el enunciado original menciona instancias de más de 100 ciudades, los archivos entregados contienen entre 80 y 88 ciudades. El proyecto trabaja con cada dataset real sin agregar ciudades artificiales.

## Configuración principal del AG
- Representación: permutación de índices de ciudades.
- Fitness: distancia total del tour cerrado; menor es mejor.
- Selección: torneo k=3.
- Crossover base: OX.
- Crossover experimental: PMX.
- Mutación: inversión.
- Elitismo: 3 individuos.
- Comparación: Nearest Neighbor y Nearest Neighbor + 2-opt.
- Métricas de diversidad: porcentaje de individuos únicos y distancia Hamming promedio.

## Ejecución
Desde la carpeta raíz del proyecto:

```bash
python code/tsp_ga_analysis.py
```

El script genera archivos CSV de resultados y figuras PNG. El informe principal ya resume los resultados obtenidos para los diez datasets.

## Resultado general
En los resultados generados, el AG + 2-opt produjo soluciones válidas en todos los datasets y redujo la distancia promedio frente a Nearest Neighbor aproximadamente en 7.84%.

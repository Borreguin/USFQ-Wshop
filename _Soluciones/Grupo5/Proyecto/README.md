# Proyecto Final IA - Resolución del TSP mediante Algoritmos Genéticos

Grupo 5: Nancy Altamirano, Gustavo Berru, Raquel Pacheco, Kevin Viteri.

## Contenido

- `data/`: datasets CSV originales con columnas `city`, `x`, `y`.
- `code/tsp_ga_project.py`: implementación del Algoritmo Genético Generacional Elitista para TSP.
- `code/generate_extra_figures_v5.py`: generación de gráficas complementarias para el informe v5.
- `code/generate_report_v5.py`: generación del informe profesional en Word.
- `results/`: históricos por generación, rutas finales, resumen global, validación de permutaciones y experimento de parámetros.
- `figures/`: gráficas de fitness, convergencia, diversidad, comparación con heurística y parámetros.
- `report/`: informe final en Word y PDF.

## Algoritmo utilizado

Algoritmo Genético Generacional Elitista con:

- Representación por permutaciones de ciudades.
- Selección por torneo.
- Crossover OX, válido para permutaciones.
- Mutación por inversión.
- Elitismo de 2 individuos.
- Refinamiento final 2-opt.

OX no es un algoritmo alternativo al AG elitista; es el operador de crossover utilizado dentro del AG para recombinar rutas sin generar ciudades repetidas ni faltantes.

## Ejecución

Desde la raíz del proyecto:

```bash
python code/tsp_ga_project.py
python code/generate_extra_figures_v5.py
python code/generate_report_v5.py
```

El informe final responde explícitamente los literales a) a f), incluye tablas, gráficas y sustentación técnica para exposición.

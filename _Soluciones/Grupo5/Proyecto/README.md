# Proyecto final de IA - Resolucion del TSP mediante Algoritmos Geneticos

**Grupo 5:** Nancy Altamirano, Gustavo Berru, Raquel Pacheco y Kevin Viteri.

Este paquete contiene el informe profesional, codigo reproducible, datasets, resultados y graficas del proyecto **Resolucion del TSP mediante Algoritmos Geneticos**.

## Algoritmo usado

Se implementa un **Algoritmo Genetico Generacional Elitista** adaptado al TSP:

- Representacion: permutacion valida de ciudades.
- Seleccion: torneo de tamano 3.
- Crossover principal: OX (Order Crossover), valido para permutaciones.
- Mutacion: inversion de segmento.
- Elitismo: conserva los 2 mejores individuos por generacion.
- Fitness: `fitness = 1 / distancia_total`.
- Comparacion: heuristica Nearest Neighbor.
- Refinamiento final: 2-opt.

## Estructura del paquete

- `data/`: archivos CSV originales con columnas `city`, `x`, `y`.
- `code/tsp_ga_project.py`: implementacion completa del algoritmo, comparacion y experimentos.
- `results/`: historiales por generacion, rutas finales, tabla resumen, validacion y parametros.
- `figures/`: graficas de fitness, diversidad, comparacion y parametros.
- `report/`: informe profesional en DOCX y PDF.

## Como ejecutar

Desde la carpeta raiz del paquete:

```bash
python code/tsp_ga_project.py
```

El script regenerara los archivos de `results/` y `figures/` usando una semilla fija para reproducibilidad.

## Resultados principales

En los 10 datasets cargados se generaron rutas validas sin ciudades repetidas ni faltantes. El AG elitista + 2-opt obtuvo, en promedio, una mejora relativa de aproximadamente 7.83% frente a Nearest Neighbor. Como los datasets no incluyen optimos certificados, el error relativo se reporta con respecto a la heuristica de referencia.

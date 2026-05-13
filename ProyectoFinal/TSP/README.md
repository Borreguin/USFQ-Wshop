# ProyectoFinal — TSP con Algoritmo Genético

**Curso:** MSDS 6004 — Inteligencia Artificial — USFQ  
**Grupo 5:** Kevin Vitery · Raquel Pacheco · Gustavo Baru · Nancy Altamirano

---

## Descripción del problema

El **Problema del Viajante (TSP)** consiste en encontrar la ruta más corta posible que:
- Visite todas las ciudades **exactamente una vez**.
- Regrese al punto de inicio.
- Minimice la **distancia total recorrida**.

Es un problema NP-difícil: para `n` ciudades existen `(n-1)!/2` rutas posibles (para 82 ciudades ≈ 3×10¹²²).

---

## Estructura del proyecto

```
ProyectoFinal/TSP/
├── dataset/                      # Datasets de ciudades
│   ├── cities_100_123.csv        # 82 ciudades, semilla 123 (dataset principal)
│   ├── cities_100_456.csv        # instancias alternativas
│   └── ...
├── ga_tsp/                       # Módulos del Algoritmo Genético
│   ├── distances.py              # Carga de datos y matriz de distancias
│   ├── selection.py              # Selección por torneo
│   ├── crossover.py              # Cruce OX (Order Crossover)
│   ├── mutation.py               # Mutación swap, inversión y combinada
│   ├── elitism.py                # Elitismo
│   ├── nearest_neighbor.py       # Heurística Vecino Cercano (baseline)
│   ├── local_search.py           # Post-procesamiento 2-opt
│   └── ga.py                     # Clase principal GeneticAlgorithmTSP
├── plots/                        # Scripts de visualización
│   ├── fitness_plot.py           # Evolución del fitness por generación
│   ├── diversity_plot.py         # Diversidad poblacional
│   └── route_plot.py             # Visualización de rutas y comparativa
├── results/                      # Resultados generados (creado al ejecutar)
│   ├── fitness_evolution.png
│   ├── diversity.png
│   ├── route_comparison.png
│   ├── summary.csv
│   └── experiments/
├── main.py                       # Punto de entrada principal
├── experiments.py                # Experimentos de parámetros
└── requirements.txt
```

---

## Instalación y ejecución

```bash
pip install -r requirements.txt

# Ejecutar el pipeline completo (GA + comparativa + gráficas)
python main.py

# Ejecutar experimentos de parámetros
python experiments.py
```

---

## Diseño del Algoritmo Genético

### Representación
Cada individuo es una **permutación** de índices de ciudades `[0..n-1]`.  
Esto garantiza que toda solución sea válida (sin ciudades repetidas ni faltantes).

### Función de fitness
```
fitness(tour) = 1 / distancia_total(tour)
```
Mayor fitness = ruta más corta. La distancia usa la norma Euclídea.

### Operadores genéticos

| Operador | Tipo | Descripción |
|---|---|---|
| **Selección** | Torneo k=5 | Se eligen 5 candidatos al azar; gana el de mayor fitness |
| **Cruce** | OX (Order Crossover) | Preserva el orden relativo de ciudades del padre; no genera duplicados |
| **Mutación** | Combinada (swap + inversión) | Swap: intercambia 2 posiciones. Inversión: invierte un segmento |
| **Elitismo** | Top 5 | Los 5 mejores individuos pasan sin cambios a la siguiente generación |

### Order Crossover (OX)
```
Padre 1: [A B C | D E F | G H]
Padre 2: [C A H | B D G | F E]

Segmento heredado de P1: [D E F] (posiciones 3-5)
Hijo: [_ _ _ D E F _ _]
Completar con P2 (en orden, saltando D E F):
Hijo: [C A H D E F G B]   ← permutación válida
```

### Post-procesamiento 2-opt
Después del GA se aplica **2-opt** sobre la mejor solución encontrada.  
Elimina cruces de aristas invirtiendo segmentos → mejora adicional de ~7%.

---

## Resultados principales

| Método | Distancia | Tiempo | Mejora vs NN |
|---|---|---|---|
| Vecino Cercano (NN) | 1850.11 | 0.002 s | — |
| Algoritmo Genético | 1723.68 | 18.3 s | **+6.83%** |
| GA + 2-opt | 1592.43 | 0.5 s | **+13.93%** |

_Dataset: `cities_100_123.csv` (82 ciudades), configuración: pop=150, mut=0.02, gen=1000, torneo k=5._

---

## Análisis de experimentos

### Tamaño de población
Mayor población = más diversidad genética = mejores soluciones, con rendimientos decrecientes >200.

### Tasa de mutación
Rango óptimo: **0.02–0.05**. Muy baja → estancamiento local. Muy alta → destruye soluciones buenas.

### Tipo de mutación
**Inversión** supera a swap porque equivale a deshacer cruces (operación 2-opt), produciendo soluciones más cortas.

### Tamaño del torneo
Torneo k=3 o k=7 da mejor balance presión selectiva/diversidad que k=2 (poca presión) o k=10 (convergencia prematura).

---

## Gráficas generadas

- **`fitness_evolution.png`**: mejor fitness, fitness promedio y peor fitness por generación + distancia del mejor individuo.
- **`diversity.png`**: porcentaje de individuos únicos en la población + correlación diversidad vs calidad.
- **`route_comparison.png`**: mapa comparativo ruta NN (izq.) vs ruta GA+2-opt (der.).
- **`experiments/experiments_comparison.png`**: curvas de convergencia para los 4 experimentos.

# TALLER 1 – Uso de la Inteligencia Artificial / Low Code Engineering

**Curso:** Maestría en Inteligencia Artificial – USFQ
**Rama:** `g5_na`

---

## Integrantes del Grupo

| Integrante | Problema |
|---|---|
| Nancy Altamirano | A. TSP – Travelling Salesman Problem |
| Gustavo Berru | A. TSP – Travelling Salesman Problem |
| Raquel Pacheco | B. El acertijo del granjero y el bote |
| Kevin Viteri | C. La Torre de Hanoi |

---

## 1. Problemas Resueltos

### A. TSP – Travelling Salesman Problem
**Archivo:** `P1_TSP/TSP.py`

Solución con tres algoritmos en cadena:
1. **Nearest Neighbor** – baseline greedy (referencia)
2. **Ant Colony Optimization (ACO)** – metaheurística bioinspirada con feromonas, evaporación y hormigas élite
3. **2-opt** – refinamiento local sobre la mejor solución ACO

**Visualizaciones:**
- Comparativa de rutas: NN vs ACO vs ACO+2opt
- Curva de convergencia y mejoras por iteración (Δcosto)
- Evolución de feromonas τ(i,j) en heatmaps logarítmicos
- Análisis estadístico de 20 corridas independientes (histograma, boxplot, métricas)
- Mapa de calor de distancias entre ciudades ecuatorianas

### B. El acertijo del granjero y el bote
**Archivo:** `P2_Granjero/Acertijo.py`

Solución con **BFS (Búsqueda en Anchura)** sobre espacio de estados.
Estado: `(granjero, lobo, cabra, col)` donde 0=izquierda, 1=derecha.

**Visualizaciones:**
- Panel de 8 pasos con íconos mostrando cada orilla y la barca
- Grafo completo de transiciones de estados con la solución resaltada

### C. La Torre de Hanoi
**Archivo:** `P3_Torres/Torres.py`

Solución **recursiva** exacta. Para n discos: mueve n-1 a auxiliar, mueve el mayor al destino, mueve n-1 del auxiliar al destino. Siempre requiere 2ⁿ − 1 movimientos.

**Visualizaciones:**
- Animación de cada movimiento sobre fondo oscuro
- Barras de movimientos por torre (origen y destino)
- Curva de complejidad O(2ⁿ) para n=1..12

---

## 2. Planeamiento en Notion
[Enlace al proyecto de planificación en Notion](#)

---

## 3. Ensayo: Evolución de la IA con Chips Analógicos
**Archivo:** `ensayo_chips_analogicos.pdf`

Ensayo basado en las transcripciones de los videos sobre computación analógica y su impacto
en la IA moderna: chips de memristores, eficiencia energética, futuro híbrido digital+analógico.

---

## Ejecución

```bash
pip install numpy matplotlib networkx

python Taller1/P1_TSP/TSP.py
python Taller1/P2_Granjero/Acertijo.py
python Taller1/P3_Torres/Torres.py
```

## Notion Link:
https://www.notion.so/Proyecto-de-planificaci-n-Taller-1-IA-Grupo-5-9fe3570dff2d48359703271a0cc9b6d4
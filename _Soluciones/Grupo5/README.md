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
**Archivos:** `P1_TSP/TSP.py` · `src/tsp.py` (OOP)

Solución con tres algoritmos en cadena aplicados a las **24 capitales de provincia del Ecuador**:
1. **Nearest Neighbor** – baseline greedy (2146.62 km)
2. **Ant Colony Optimization (ACO)** – metaheurística bioinspirada; 25 hormigas × 150 iteraciones, feromonas, evaporación ρ=0.15, hormigas élite
3. **2-opt** – refinamiento local sobre la mejor solución ACO (2003.89 km, mejora 6.6%)

**Visualizaciones generadas:**
- `tsp_01_comparativa_rutas.png` – Comparativa NN vs ACO vs ACO+2opt
- `tsp_02_convergencia.png` – Curva de convergencia por iteración
- `tsp_03_feromonas.png` – Evolución de feromonas τ(i,j) en 4 momentos
- `tsp_04_estadisticas.png` – Análisis de 20 corridas (media=2010.50 km ±10.73 km)
- `tsp_05_heatmap_distancias.png` – Mapa de calor de distancias Haversine

### B. El acertijo del granjero y el bote
**Archivos:** `P2_Granjero/Acertijo.py` · `src/granjero.py` (OOP)

Solución con **BFS (Búsqueda en Anchura)** sobre espacio de estados.
Estado: `(granjero, lobo, cabra, col)` donde `0`=orilla izquierda, `1`=orilla derecha.
De 16 estados posibles, 10 son válidos. BFS encuentra la solución óptima en **7 pasos**.

**Visualizaciones generadas:**
- `granjero_01_pasos.png` – 8 paneles con la secuencia completa de solución
- `granjero_02_grafo.png` – Grafo de transiciones de estados con camino óptimo en naranja

### C. La Torre de Hanoi
**Archivos:** `P3_Torres/Torres.py` · `src/hanoi.py` (OOP)

Solución **recursiva** exacta con estrategia divide y vencerás.
Para n discos: mueve n-1 a auxiliar → mueve el mayor al destino → mueve n-1 del auxiliar al destino.
Siempre requiere exactamente **2ⁿ − 1 movimientos** (mínimo demostrado).
Con 4 discos: **15 movimientos**. Espacio de estados: 3⁴ = **81 nodos**, 120 aristas.

**Visualizaciones generadas:**
- `hanoi_01_estado_final.png` – Estado final con 4 discos en Torre C
- `hanoi_02_movimientos.png` – Distribución de movimientos por torre
- `hanoi_03_complejidad.png` – Curva de complejidad O(2ⁿ) para n=1..12

---

## 2. Planeamiento en Notion

[Proyecto de Planificación – Taller 1 IA Grupo 5](https://www.notion.so/Proyecto-de-planificaci-n-Taller-1-IA-Grupo-5-9fe3570dff2d48359703271a0cc9b6d4)

---

## 3. Ensayo: Evolución de la IA con Chips Analógicos
**Archivo:** `ensayo_chips_analogicos.pdf`

Ensayo basado en las transcripciones de los videos sobre computación analógica y su impacto
en la IA moderna: chips de memristores, eficiencia energética, futuro híbrido digital+analógico.

---

## Archivos del repositorio

```
_Soluciones/Grupo5/
├── P1_TSP/
│   ├── TSP.py                     # Entrada: corre TSP con 24 ciudades
│   └── imagenes/                  # 5 PNG: comparativa, convergencia, feromonas, estadísticas, heatmap
├── P2_Granjero/
│   ├── Acertijo.py                # Entrada: BFS + visualizaciones
│   ├── solucion_granjero.txt      # Solución impresa con estados
│   └── imagenes/                  # 2 PNG: pasos de solución, grafo de transiciones
├── P3_Torres/
│   ├── Torres.py                  # Entrada: Hanoi recursivo
│   └── imagenes/                  # 3 PNG: estado final, movimientos, curva de complejidad
├── src/
│   ├── tsp.py                     # OOP: City, ACO, TSPVisualizer…
│   ├── granjero.py                # OOP: State, FarmerPuzzle…
│   └── hanoi.py                   # OOP: Disk, Tower, HanoiSolver…
├── generar_imagenes.py            # Regenera las 10 imágenes (headless)
├── generar_resumen_taller.py      # Regenera el PDF resumen
├── resumen_taller1_grupo5.pdf     # Informe completo del taller
└── ensayo_chips_analogicos.pdf    # Ensayo literal C
```

## Ejecución

```bash
# Instalar dependencias
pip install numpy matplotlib networkx reportlab

# Desde la raíz del repositorio (USFQ-Wshop/)
python _Soluciones/Grupo5/P1_TSP/TSP.py
python _Soluciones/Grupo5/P2_Granjero/Acertijo.py
python _Soluciones/Grupo5/P3_Torres/Torres.py

# Regenerar todas las imágenes y el PDF resumen
python _Soluciones/Grupo5/generar_imagenes.py
python _Soluciones/Grupo5/generar_resumen_taller.py
```

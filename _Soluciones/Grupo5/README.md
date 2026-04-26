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

Solución con tres algoritmos en cadena aplicados a **10 ciudades ecuatorianas** (Quito, Guayaquil, Cuenca, Manta, Ambato, Loja, Esmeraldas, Riobamba, Ibarra, Latacunga):
1. **Nearest Neighbor** – baseline greedy
2. **Ant Colony Optimization (ACO)** – metaheurística bioinspirada; 25 hormigas × 150 iteraciones, feromonas, evaporación ρ=0.15, hormigas élite
3. **2-opt** – refinamiento local sobre la mejor solución ACO

**Visualizaciones generadas:**
- `P1_TSP/imagenes/tsp_01_comparativa_rutas.png` – Comparativa NN vs ACO vs ACO+2opt
- `P1_TSP/imagenes/tsp_02_convergencia.png` – Curva de convergencia por iteración
- `P1_TSP/imagenes/tsp_03_feromonas.png` – Evolución de feromonas τ(i,j) en 4 momentos
- `P1_TSP/imagenes/tsp_04_estadisticas.png` – Análisis estadístico de 20 corridas
- `P1_TSP/imagenes/tsp_05_heatmap_distancias.png` – Mapa de calor de distancias

### B. El acertijo del granjero y el bote
**Archivo:** `P2_Granjero/Acertijo.py`

Solución con **BFS (Búsqueda en Anchura)** sobre espacio de estados.
Estado: `(granjero, lobo, cabra, col)` donde `0`=orilla izquierda, `1`=orilla derecha.
De 16 estados posibles, 10 son válidos. BFS encuentra la solución óptima en **7 pasos**.

**Visualizaciones generadas:**
- `P2_Granjero/farmer_steps.png` – Paneles con la secuencia completa de solución
- `P2_Granjero/farmer_graph.png` – Grafo de transiciones de estados con camino óptimo en naranja

### C. La Torre de Hanoi
**Archivo:** `P3_Torres/Torres.py`

Solución **recursiva** exacta con estrategia divide y vencerás.
Para n discos: mueve n-1 a auxiliar → mueve el mayor al destino → mueve n-1 del auxiliar al destino.
Siempre requiere exactamente **2ⁿ − 1 movimientos** (mínimo demostrado).
Con 4 discos: **15 movimientos**. Espacio de estados: 3⁴ = **81 nodos**, 120 aristas.

**Visualizaciones generadas:**
- `P3_Torres/Figure_1.png` – Estado inicial
- `P3_Torres/Figure_2.png` – Grafo completo de estados con camino óptimo
- `P3_Torres/Figure_3.png` – Distribución de movimientos por torre
- `P3_Torres/Figure_4.png` – Curva de complejidad O(2ⁿ) para n=1..12

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
│   ├── TSP.py                     # ACO + 2-opt sobre 10 ciudades ecuatorianas
│   └── imagenes/                  # 5 PNG generadas por TSP.py
├── P2_Granjero/
│   ├── Acertijo.py                # BFS + visualizaciones
│   ├── farmer_steps.png           # Secuencia de pasos
│   ├── farmer_graph.png           # Grafo de estados
│   └── solucion_granjero.txt      # Solución impresa con estados
├── P3_Torres/
│   ├── Torres.py                  # Hanoi recursivo + animación + grafo
│   ├── Figure_1.png               # Estado inicial
│   ├── Figure_2.png               # Grafo de estados
│   ├── Figure_3.png               # Movimientos por torre
│   └── Figure_4.png               # Curva de complejidad
├── images/                        # Imágenes adicionales
├── resumen_taller1_grupo5.pdf     # Informe completo del taller
└── ensayo_chips_analogicos.pdf    # Ensayo literal C
```

## Ejecución

```bash
# Instalar dependencias
pip install numpy matplotlib networkx

# Desde la raíz del repositorio (USFQ-Wshop/)
python _Soluciones/Grupo5/P1_TSP/TSP.py
python _Soluciones/Grupo5/P2_Granjero/Acertijo.py
python _Soluciones/Grupo5/P3_Torres/Torres.py
```

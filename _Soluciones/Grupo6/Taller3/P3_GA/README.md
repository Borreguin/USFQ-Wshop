# P3 — Genetic Algorithm

String-matching Genetic Algorithm built for the USFQ AI Workshop (Taller 3).

## How to run (PyCharm)

Install dependencies first (in your conda environment):
```bash
conda install pyqt matplotlib
```

Then right-click one of these files → **Run**:

| File | Mode |
|---|---|
| `run_console.py` | Menu-driven terminal interface |
| `run_gui.py` | PyQt5 graphical interface |

---

## Architecture

```
P3_GA/
├── models/          Chromosome · Population · GAHistory
├── operators/       Fitness · Selection · Crossover · Mutation (ABCs + implementations)
├── engine/ga.py     Pure GA engine — no prints, fires callbacks
├── console/         ANSI-colored menu app
└── GUI/             PyQt5 dark-theme window (config · live output · convergence chart)
```

The engine is shared between console and GUI — same seed produces identical results in both.

---

## Demo Configurations

### Config 1 — Classic (smooth convergence, good for explaining the chart)

| Parameter | Value |
|---|---|
| Target | `GA Workshop! USFQ` |
| Population | `200` |
| Mutation rate | `0.01` |
| Iterations | `1000` |
| Seed | `42` |
| Fitness | Match Count |
| Selection | Roulette Wheel |
| Crossover | Single Point |
| Mutation | Random Gene |

---

### Config 2 — Fast (finds solution quickly, great for live demo)

| Parameter | Value |
|---|---|
| Target | `Hello USFQ` |
| Population | `300` |
| Mutation rate | `0.02` |
| Iterations | `500` |
| Seed | `42` |
| Fitness | Match Count |
| Selection | Tournament |
| Crossover | Two Point |
| Mutation | Random Gene |

---

### Config 3 — Hard (long target, many generations, best convergence chart)

| Parameter | Value |
|---|---|
| Target | `Inteligencia Artificial USFQ 2025!` |
| Population | `500` |
| Mutation rate | `0.015` |
| Iterations | `3000` |
| Seed | `123` |
| Fitness | Match Count |
| Selection | Elitist |
| Crossover | Uniform |
| Mutation | Random Gene |

---

## Operators available

| Category | Options |
|---|---|
| Fitness | Match Count · Hamming Distance |
| Selection | Roulette Wheel · Tournament · Elitist |
| Crossover | Single Point · Two Point · Uniform |
| Mutation | Random Gene · Swap Gene |

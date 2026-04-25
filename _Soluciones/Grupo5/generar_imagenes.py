"""
Genera todas las visualizaciones del Taller 1.
Cada problema guarda sus imagenes en su propia carpeta imagenes/.
Uso: python _Soluciones/Grupo5/generar_imagenes.py
"""

import sys
import os
import matplotlib
matplotlib.use("Agg")   # backend sin ventana – indispensable para modo headless

BASE = os.path.dirname(__file__)

TSP_DIR      = os.path.join(BASE, "P1_TSP",     "imagenes")
GRANJERO_DIR = os.path.join(BASE, "P2_Granjero", "imagenes")
HANOI_DIR    = os.path.join(BASE, "P3_Torres",   "imagenes")

for d in [TSP_DIR, GRANJERO_DIR, HANOI_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 60)
print("  Generador de imagenes – Taller 1")
print("=" * 60)

# ── A. TSP ───────────────────────────────────────────────────────────────────
print(f"\n[A] TSP -> {TSP_DIR}")
sys.path.insert(0, os.path.join(BASE, "P1_TSP"))
from TSP import main as tsp_main
tsp_main(save_dir=TSP_DIR)

# ── B. Granjero ──────────────────────────────────────────────────────────────
print(f"\n[B] Granjero -> {GRANJERO_DIR}")
sys.path.insert(0, os.path.join(BASE, "P2_Granjero"))
from Acertijo import main as granjero_main
granjero_main(save_dir=GRANJERO_DIR)

# ── C. Hanoi ─────────────────────────────────────────────────────────────────
print(f"\n[C] Hanoi -> {HANOI_DIR}")
sys.path.insert(0, os.path.join(BASE, "P3_Torres"))
from Torres import main as hanoi_main
hanoi_main(save_dir=HANOI_DIR, n=4)

# ── Resumen ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Imagenes generadas:")
for carpeta, label in [(TSP_DIR, "P1_TSP"), (GRANJERO_DIR, "P2_Granjero"), (HANOI_DIR, "P3_Torres")]:
    for f in sorted(os.listdir(carpeta)):
        if f.endswith(".png"):
            size = os.path.getsize(os.path.join(carpeta, f)) // 1024
            print(f"    {label}/{f:40s} {size:4d} KB")
print("=" * 60)

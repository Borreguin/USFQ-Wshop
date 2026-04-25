"""
Genera todas las visualizaciones del Taller 1 y las guarda en Taller1/images/
Uso: python Taller1/generar_imagenes.py
"""

import sys
import os
import matplotlib
matplotlib.use("Agg")   # backend sin ventana – indispensable para modo headless

# Directorio de salida relativo a este script
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")

print("=" * 60)
print("  Generador de imágenes – Taller 1")
print(f"  Salida: {IMG_DIR}")
print("=" * 60)

# ── A. TSP ───────────────────────────────────────────────────────────────────
print("\n[A] TSP – Ant Colony Optimization + 2-opt …")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "P1_TSP"))
from TSP import main as tsp_main
tsp_main(save_dir=IMG_DIR)

# ── B. Granjero ──────────────────────────────────────────────────────────────
print("\n[B] Acertijo del Granjero – BFS …")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "P2_Granjero"))
from Acertijo import main as granjero_main
granjero_main(save_dir=IMG_DIR)

# ── C. Hanoi ─────────────────────────────────────────────────────────────────
print("\n[C] Torre de Hanoi – Recursivo (4 discos) …")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "P3_Torres"))
from Torres import main as hanoi_main
hanoi_main(save_dir=IMG_DIR, n=4)

# ── Resumen ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Imágenes generadas:")
for f in sorted(os.listdir(IMG_DIR)):
    if f.endswith(".png"):
        size = os.path.getsize(os.path.join(IMG_DIR, f)) // 1024
        print(f"    {f:45s} {size:4d} KB")
print("=" * 60)

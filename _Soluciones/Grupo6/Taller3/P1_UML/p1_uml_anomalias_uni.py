"""
P1_UML — Student Productivity & Distraction Dataset
=====================================================
Pregunta C (Alternativa): Encontrar anomalías – Análisis Univariable con Z-SCORE

  1. Carga y limpieza de datos.
  2. Detección de anomalías usando el método Z-Score (Desviación Estándar).
  3. Resumen estadístico de anomalías por variable.
  4. Visualización de la distribución y los límites de anomalía (±3 sigmas).

Todos los gráficos se guardan en la subcarpeta C/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importamos las utilidades de tu archivo
from p1_uml_util_students import (
    read_csv_file, numeric_cols, lb_student_id, alias,
    lb_study_hours, lb_productivity, lb_phone_usage, lb_sleep_hours
)

# ── Carpeta de salida Pregunta C ──────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "C")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _save(filename: str):
    """Guarda el gráfico en C/ y lo muestra en pantalla."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  → Guardado: C/{filename}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. CARGA Y PREPARACIÓN
# ─────────────────────────────────────────────────────────────────────────────
def prepare_data() -> pd.DataFrame:
    data_path = os.path.join(_SCRIPT_DIR, "data")
    file_path = os.path.join(data_path,
                             "student_productivity_distraction_dataset_20000.csv")
    df = read_csv_file(file_path)
    if df.empty:
        raise FileNotFoundError(f"No se encontró el archivo en:\n  {file_path}")

    df.set_index(lb_student_id, inplace=True)

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=numeric_cols, inplace=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2 & 3. CÁLCULO DE ANOMALÍAS (MÉTODO Z-SCORE) Y RESUMEN
# ─────────────────────────────────────────────────────────────────────────────
def detect_anomalies_zscore(df: pd.DataFrame, columns: list, threshold: float = 3.0) -> dict:
    """
    Aplica el método Z-Score a cada columna para encontrar anomalías.
    Imprime un resumen tabular en consola.
    """
    print(f"\n── Resumen de Anomalías Univariables (Z-Score > {threshold}) ──")
    print(f"{'Variable':<25} | {'Anomalías':<10} | {'Porcentaje (%)':<15}")
    print("-" * 55)
    
    anomalies_summary = {}
    
    for col in columns:
        mean_val = df[col].mean()
        std_val = df[col].std()
        
        # Calcular Z-Scores
        z_scores = (df[col] - mean_val) / std_val
        
        # Límites reales en la escala original
        lower_bound = mean_val - (threshold * std_val)
        upper_bound = mean_val + (threshold * std_val)
        
        # Encontrar valores fuera del umbral (donde el valor absoluto de Z es mayor al umbral)
        outliers = df[np.abs(z_scores) > threshold]
        num_outliers = len(outliers)
        perc_outliers = (num_outliers / len(df)) * 100
        
        anomalies_summary[col] = {
            'mean': mean_val, 'std': std_val,
            'lower_bound': lower_bound, 'upper_bound': upper_bound,
            'num_outliers': num_outliers, 'perc_outliers': perc_outliers,
            'outliers_index': outliers.index.tolist()
        }
        
        print(f"{alias.get(col, col):<25} | {num_outliers:<10} | {perc_outliers:.2f}%")
        
    return anomalies_summary


# ─────────────────────────────────────────────────────────────────────────────
# 4. VISUALIZACIÓN: DISTRIBUCIÓN Y LÍMITES Z-SCORE
# ─────────────────────────────────────────────────────────────────────────────
def plot_zscore_anomalies(df: pd.DataFrame, columns_to_plot: list, summary: dict):
    """
    Genera histogramas con las líneas de la media y los límites de ±3 desviaciones estándar.
    """
    num_vars = len(columns_to_plot)
    # Crear un grid de 2x2 si son 4 variables o ajustar según el número de variables
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Detección de Anomalías — Método Z-Score (±3 Std Dev)", 
                 fontsize=15, fontweight="bold")
    
    axes = axes.flatten()

    for i, col in enumerate(columns_to_plot):
        ax = axes[i]
        data = df[col]
        bounds = summary[col]
        
        mean_v = bounds['mean']
        lower_b = bounds['lower_bound']
        upper_b = bounds['upper_bound']
        
        # Histograma base
        counts, bins, patches = ax.hist(data, bins=40, color="#4C72B0", 
                                        edgecolor="white", alpha=0.7)
        
        # Colorear anomalías de rojo
        for count, bin_edge, patch in zip(counts, bins, patches):
            if bin_edge < lower_b or bin_edge > upper_b:
                patch.set_facecolor('#E63946')
                patch.set_alpha(0.9)

        # Líneas estadísticas
        ax.axvline(mean_v, color="green", linestyle="-", linewidth=2, 
                   label=f"Media: {mean_v:.1f}")
        ax.axvline(lower_b, color="black", linestyle="--", linewidth=1.5, 
                   label=f"-3σ: {lower_b:.1f}")
        ax.axvline(upper_b, color="black", linestyle="--", linewidth=1.5, 
                   label=f"+3σ: {upper_b:.1f}")
        
        # Zonas sombreadas anómalas
        ax.axvspan(data.min(), lower_b, color='#E63946', alpha=0.1)
        ax.axvspan(upper_b, data.max(), color='#E63946', alpha=0.1)
        
        ax.set_title(alias.get(col, col), fontsize=12)
        ax.set_xlabel("Valor")
        ax.set_ylabel("Frecuencia")
        ax.legend(fontsize=9, loc="upper right")
        ax.grid(alpha=0.3)

    plt.tight_layout()
    _save("zscore_anomalies_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n[INICIO] Análisis Univariable con Z-Score. Gráficos en: {OUTPUT_DIR}\n")

    # 1. Preparar datos
    df = prepare_data()

    # 2 & 3. Calcular anomalías usando Z-Score (Umbral = 3) en todas las columnas numéricas
    anomalies_summary = detect_anomalies_zscore(df, numeric_cols, threshold=3.0)

    # 4. Visualizar las distribuciones para un subconjunto de variables clave
    vars_to_plot = [lb_study_hours, lb_phone_usage, lb_sleep_hours, lb_productivity]
    plot_zscore_anomalies(df, columns_to_plot=vars_to_plot, summary=anomalies_summary)
    
    print("\n[FIN] Análisis completado.")
"""
P1_UML — Student Productivity & Distraction Dataset
=====================================================
Pregunta E: Encontrar anomalías – Análisis Multivariable (Pares)

  1. Carga y limpieza de datos.
  2. Selección de 2 pares de variables lógicas.
  3. Detección de anomalías usando Isolation Forest (Bosque de Aislamiento).
  4. Visualización con Scatter plots resaltando las anomalías y 
     las "fronteras de decisión" del modelo.

Todos los gráficos se guardan en la subcarpeta E/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Importamos las utilidades de tu archivo
from p1_uml_util_students import (
    read_csv_file, numeric_cols, lb_student_id, alias,
    lb_study_hours, lb_productivity, lb_phone_usage, lb_sleep_hours
)

# ── Carpeta de salida Pregunta E ──────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "E")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _save(filename: str):
    """Guarda el gráfico en E/ y lo muestra en pantalla."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  → Guardado: E/{filename}")


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
# 2 & 3. DETECCIÓN BIVARIABLE Y VISUALIZACIÓN (ISOLATION FOREST)
# ─────────────────────────────────────────────────────────────────────────────
def plot_bivariate_anomalies(df: pd.DataFrame, var_x: str, var_y: str, contamination=0.05):
    """
    Aplica Isolation Forest a un par de variables, encuentra anomalías
    y grafica el resultado con la frontera de decisión.
    contamination=0.05 significa que asumimos que el 5% de los datos son anomalías.
    """
    # Extraer y escalar el par de variables
    X = df[[var_x, var_y]].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenar el modelo de Isolation Forest
    # n_estimators=100 es estándar, random_state para reproducibilidad
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(X_scaled)
    
    # Predicciones: 1 = Normal (Inlier), -1 = Anomalía (Outlier)
    predictions = model.predict(X_scaled)
    X['Anomaly'] = predictions

    # Separar normales y anomalías para contar
    normal_points = X[X['Anomaly'] == 1]
    anomalies = X[X['Anomaly'] == -1]
    
    print(f"\n── Anomalías en el Par: {alias.get(var_x)} vs {alias.get(var_y)} ──")
    print(f"  Puntos normales: {len(normal_points)}")
    print(f"  Anomalías detectadas: {len(anomalies)} (Aprox {contamination*100}%)")

    # ── CREAR LA VISUALIZACIÓN ──
    fig, ax = plt.subplots(figsize=(10, 7))

    # 1. Crear una malla (meshgrid) para dibujar las regiones de fondo
    xx, yy = np.meshgrid(np.linspace(X_scaled[:, 0].min() - 1, X_scaled[:, 0].max() + 1, 100),
                         np.linspace(X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 1, 100))
    Z = model.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Convertir la malla de vuelta a la escala original para el gráfico
    mesh_original = scaler.inverse_transform(np.c_[xx.ravel(), yy.ravel()])
    xx_orig = mesh_original[:, 0].reshape(xx.shape)
    yy_orig = mesh_original[:, 1].reshape(yy.shape)

    # Dibujar el contorno (colores de fondo). Zonas oscuras son fuertemente anómalas
    contour = ax.contourf(xx_orig, yy_orig, Z, levels=np.linspace(Z.min(), 0, 7), cmap='Reds_r', alpha=0.3)
    ax.contour(xx_orig, yy_orig, Z, levels=[0], linewidths=2, colors='red') # Línea de frontera exacta

    # 2. Graficar los puntos normales (Azul)
    ax.scatter(normal_points[var_x], normal_points[var_y], 
               c='blue', alpha=0.3, s=15, edgecolors='none', label='Datos Normales')
    
    # 3. Graficar las anomalías (Rojo)
    ax.scatter(anomalies[var_x], anomalies[var_y], 
               c='red', alpha=0.9, s=30, edgecolors='black', linewidth=0.5, label='Anomalías (Outliers)')

    ax.set_title(f"Análisis Bivariable de Anomalías\n{alias.get(var_x)} vs {alias.get(var_y)}", 
                 fontsize=14, fontweight="bold")
    ax.set_xlabel(alias.get(var_x))
    ax.set_ylabel(alias.get(var_y))
    
    # Leyenda
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    _save(f"bivariate_anomalies_{var_x}_vs_{var_y}.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n[INICIO] Detección de Anomalías Bivariables (Isolation Forest). Gráficos en: {OUTPUT_DIR}\n")

    # 1. Preparar datos
    df = prepare_data()

    # 2. Definimos que queremos encontrar aproximadamente un 3% de anomalías extremas
    porcentaje_anomalias = 0.03

    # PAR 1: Horas de Estudio vs Productividad
    plot_bivariate_anomalies(df, var_x=lb_study_hours, var_y=lb_productivity, contamination=porcentaje_anomalias)

    # PAR 2: Uso del Celular vs Horas de Sueño
    plot_bivariate_anomalies(df, var_x=lb_phone_usage, var_y=lb_sleep_hours, contamination=porcentaje_anomalias)

    print("\n[FIN] Análisis de anomalías multivariables completado.")
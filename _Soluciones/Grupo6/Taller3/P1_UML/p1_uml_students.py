"""
P1_UML — Student Productivity & Distraction Dataset
=====================================================
Pregunta A: Análisis exploratorio previo al aprendizaje no supervisado.

Todos los gráficos se guardan en la subcarpeta A/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from p1_uml_util_students import (
    read_csv_file, alias, numeric_cols,
    distraction_cols, productivity_cols,
    lb_student_id, lb_gender, lb_stress, lb_productivity,
    lb_study_hours, lb_focus, lb_final_grade, lb_phone_usage,
    lb_sleep_hours, lb_attendance
)

# ── Carpeta de salida Pregunta A ──────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "A")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _save(filename: str):
    """Guarda el gráfico en A/ y lo muestra en pantalla."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  → Guardado: A/{filename}")


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

    before = len(df)
    df.dropna(subset=numeric_cols, inplace=True)
    print(f"[prepare_data] Filas cargadas: {before} → tras limpieza: {len(df)}")
    print(df[numeric_cols].dtypes)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. ESTADÍSTICA DESCRIPTIVA — TODAS LAS VARIABLES
# ─────────────────────────────────────────────────────────────────────────────
def plot_descriptive_stats_all(df: pd.DataFrame, columns: list):
    """
    Calcula la estadística descriptiva y grafica Histogramas y Boxplots
    para TODAS las variables numéricas de la lista.
    """
    print("\n── Estadística descriptiva: Todas las Variables ──")
    print(df[columns].describe().to_string())

    num_vars = len(columns)
    # Crear una figura dinámica (1 fila por cada variable, 2 columnas)
    fig, axes = plt.subplots(nrows=num_vars, ncols=2, figsize=(14, 4 * num_vars))
    
    # Título principal adaptado para no superponerse
    fig.suptitle("Estadística Descriptiva — Todas las Variables Numéricas",
                 fontsize=16, fontweight="bold", y=1.01)

    for i, col in enumerate(columns):
        label = alias.get(col, col)
        data  = df[col].dropna()

        # 1. Histograma (Columna Izquierda)
        ax_hist = axes[i, 0]
        ax_hist.hist(data, bins=40, color="#4C72B0", edgecolor="white", alpha=0.85)
        ax_hist.set_title(f"{label} — Distribución", fontsize=12)
        ax_hist.set_ylabel("Frecuencia")
        ax_hist.axvline(data.mean(),   color="red",   linestyle="--", linewidth=1.4,
                        label=f"Media: {data.mean():.2f}")
        ax_hist.axvline(data.median(), color="green", linestyle=":",  linewidth=1.4,
                        label=f"Mediana: {data.median():.2f}")
        ax_hist.legend(fontsize=9)

        # 2. Boxplot (Columna Derecha)
        # Lo ponemos horizontal (vert=False) para que empate mejor con el histograma
        ax_box = axes[i, 1]
        ax_box.boxplot(data, vert=False, patch_artist=True,
                       boxprops=dict(facecolor="#DD8452", alpha=0.6))
        ax_box.set_title(f"{label} — Boxplot", fontsize=12)
        ax_box.set_yticks([]) # Ocultamos los ticks del eje Y porque ya sabemos qué variable es
        ax_box.set_xlabel("Valor")

    plt.tight_layout()
    _save("descriptive_stats_all.png")

# ─────────────────────────────────────────────────────────────────────────────
# 3. COORDENADAS PARALELAS
# ─────────────────────────────────────────────────────────────────────────────
def plot_parallel_coordinates(df: pd.DataFrame, n_sample: int = 600):
    df_sample = df[numeric_cols].dropna().sample(
        n=min(n_sample, len(df)), random_state=42)

    scaler = StandardScaler()
    df_norm = pd.DataFrame(
        scaler.fit_transform(df_sample),
        columns=numeric_cols, index=df_sample.index)

    prod     = df_sample[lb_productivity]
    terciles = pd.qcut(prod, q=3, labels=["Baja", "Media", "Alta"])
    color_map = {"Baja": "#E63946", "Media": "#F4A261", "Alta": "#2A9D8F"}

    cols_to_show = [lb_study_hours, lb_sleep_hours, lb_phone_usage,
                    lb_focus, lb_stress, lb_attendance,
                    lb_final_grade, lb_productivity]
    labels_show  = [alias[c] for c in cols_to_show]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle("Coordenadas Paralelas — Productividad Estudiantil",
                 fontsize=13, fontweight="bold")

    for idx in df_norm.index:
        row = df_norm.loc[idx, cols_to_show].values
        cat = terciles.loc[idx]
        ax.plot(range(len(cols_to_show)), row,
                color=color_map[cat], alpha=0.25, linewidth=0.7)

    ax.set_xticks(range(len(cols_to_show)))
    ax.set_xticklabels(labels_show, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Valor normalizado (z-score)")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.legend(handles=[
        Line2D([0], [0], color=color_map["Baja"],  lw=2, label="Productividad Baja"),
        Line2D([0], [0], color=color_map["Media"], lw=2, label="Productividad Media"),
        Line2D([0], [0], color=color_map["Alta"],  lw=2, label="Productividad Alta"),
    ], loc="upper right", fontsize=9)

    plt.tight_layout()
    _save("parallel_coordinates.png")


# ─────────────────────────────────────────────────────────────────────────────
# 4. PCA — Variables más importantes
# ─────────────────────────────────────────────────────────────────────────────
def run_pca(df: pd.DataFrame, n_components: int = 5):
    X = df[numeric_cols].dropna()
    X_scaled = StandardScaler().fit_transform(X)

    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(X_scaled)

    explained  = pca.explained_variance_ratio_ * 100
    cumulative = np.cumsum(explained)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("PCA — Análisis de Componentes Principales",
                 fontsize=13, fontweight="bold")

    # Scree plot
    ax1 = axes[0]
    bars = ax1.bar(range(1, n_components+1), explained,
                   color="#4C72B0", alpha=0.8, label="% Varianza por PC")
    ax1.plot(range(1, n_components+1), cumulative,
             color="#E63946", marker="o", linewidth=2, label="Varianza acumulada")
    ax1.axhline(80, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax1.set_xlabel("Componente Principal")
    ax1.set_ylabel("Varianza explicada (%)")
    ax1.set_title("Varianza Explicada por Componente")
    ax1.set_xticks(range(1, n_components+1))
    ax1.legend()
    for bar, val in zip(bars, explained):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    # Heatmap de loadings PC1 y PC2
    ax2 = axes[1]
    loadings = pd.DataFrame(
        pca.components_[:2].T,
        index=[alias[c] for c in numeric_cols],
        columns=["PC1", "PC2"])
    im = ax2.imshow(loadings.values, aspect="auto", cmap="coolwarm", vmin=-1, vmax=1)
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["PC1", "PC2"])
    ax2.set_yticks(range(len(numeric_cols)))
    ax2.set_yticklabels(loadings.index, fontsize=8)
    ax2.set_title("Loadings PC1 y PC2")
    plt.colorbar(im, ax=ax2, label="Loading")
    for i in range(len(numeric_cols)):
        for j in range(2):
            ax2.text(j, i, f"{loadings.values[i,j]:.2f}",
                     ha="center", va="center", fontsize=7, color="black")

    plt.tight_layout()
    _save("pca_analysis.png")

    # Top variables PC1
    pc1_loadings = pd.Series(
        np.abs(pca.components_[0]), index=numeric_cols
    ).sort_values(ascending=False)

    print("\n── Top variables por |loading| en PC1 ──")
    for col, val in pc1_loadings.items():
        print(f"  {alias[col]:<25} {val:.4f}")

    top2 = pc1_loadings.index[:2].tolist()
    print(f"\n→ Variables más importantes: {alias[top2[0]]}  &  {alias[top2[1]]}")
    return top2, pca, X_scaled, X.index


# ─────────────────────────────────────────────────────────────────────────────
# 5. SCATTER — Las 2 variables más importantes
# ─────────────────────────────────────────────────────────────────────────────
def plot_top2_scatter(df: pd.DataFrame, var1: str, var2: str):
    cols = list(dict.fromkeys([var1, var2, lb_productivity]))  # evita duplicados
    data = df[cols].dropna()
    prod = data[lb_productivity]

    norm = plt.Normalize(float(prod.min()), float(prod.max()))
    cmap = plt.colormaps["RdYlGn"]

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(data[var1], data[var2],
                    c=prod.values, cmap=cmap, norm=norm,
                    alpha=0.5, s=12, linewidths=0)
    plt.colorbar(sc, ax=ax, label=alias[lb_productivity])
    ax.set_xlabel(alias[var1], fontsize=11)
    ax.set_ylabel(alias[var2], fontsize=11)
    ax.set_title(f"Relación: {alias[var1]}  vs  {alias[var2]}\n"
                 f"(color = {alias[lb_productivity]})",
                 fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save("top2_scatter.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nGráficos guardados en: {OUTPUT_DIR}\n")

    df = prepare_data()

    # 1. Modificado: Le pasamos la lista completa de 'numeric_cols'
    plot_descriptive_stats_all(df, columns=numeric_cols)
    
    # El resto del flujo sigue igual
    plot_parallel_coordinates(df, n_sample=600)
    top2_vars, pca_model, X_scaled, idx = run_pca(df, n_components=5)
    plot_top2_scatter(df, top2_vars[0], top2_vars[1])

    print(f"\nTodos los gráficos guardados en: A/")
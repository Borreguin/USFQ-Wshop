"""
P1_UML — Student Productivity & Distraction Dataset
=====================================================
Pregunta B: Aprendizaje No Supervisado (Clustering)

  1. Carga y limpieza de datos.
  2. Escalado y reducción de dimensionalidad (PCA).
  3. Búsqueda del K óptimo (Método del Codo y Silueta).
  4. Clustering con K-Means.
  5. Visualización de los clústeres (Scatter en PC1 vs PC2).

Todos los gráficos se guardan en la subcarpeta B/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Importamos las utilidades que ya definiste
from p1_uml_util_students import (
    read_csv_file, numeric_cols, lb_student_id, alias
)

# ── Carpeta de salida Pregunta B ──────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "B")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _save(filename: str):
    """Guarda el gráfico en B/ y lo muestra en pantalla."""
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  → Guardado: B/{filename}")


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
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. PCA Y BÚSQUEDA DEL K ÓPTIMO (CODO Y SILUETA)
# ─────────────────────────────────────────────────────────────────────────────
def find_optimal_clusters(df: pd.DataFrame, max_k: int = 10):
    # Extraer y escalar datos
    X = df[numeric_cols]
    X_scaled = StandardScaler().fit_transform(X)

    # Aplicar PCA para reducir dimensionalidad y mejorar el clustering
    # Usamos 2 componentes para poder visualizar fácilmente los clústeres luego
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    var_exp = sum(pca.explained_variance_ratio_) * 100
    print(f"\n[PCA] Varianza explicada por los 2 primeros componentes: {var_exp:.2f}%")

    # Evaluar K-Means de k=2 hasta max_k
    inertias = []
    silhouette_scores = []
    k_values = range(2, max_k + 1)

    print("\nCalculando inercia y silueta para diferentes valores de K...")
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca)
        
        inertias.append(kmeans.inertia_)
        score = silhouette_score(X_pca, labels)
        silhouette_scores.append(score)
        print(f"  K={k} | Inercia: {kmeans.inertia_:.2f} | Silueta: {score:.4f}")

    # Determinar el mejor K basado en el score de silueta
    best_k = k_values[np.argmax(silhouette_scores)]
    print(f"\n→ El número óptimo de clústeres sugerido (por Silueta) es: K = {best_k}")

    # Graficar Método del Codo y Silueta
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Evaluación del Número Óptimo de Clústeres (K-Means sobre PCA)", 
                 fontsize=14, fontweight="bold")

    # Gráfico del Codo (Inercia)
    axes[0].plot(k_values, inertias, marker='o', color="#4C72B0", linewidth=2)
    axes[0].set_title("Método del Codo (Inercia)")
    axes[0].set_xlabel("Número de Clústeres (K)")
    axes[0].set_ylabel("Inercia (WCSS)")
    axes[0].set_xticks(k_values)
    axes[0].grid(alpha=0.4)

    # Gráfico de Silueta
    axes[1].plot(k_values, silhouette_scores, marker='s', color="#DD8452", linewidth=2)
    axes[1].axvline(best_k, color="red", linestyle="--", label=f"Óptimo: K={best_k}")
    axes[1].set_title("Coeficiente de Silueta")
    axes[1].set_xlabel("Número de Clústeres (K)")
    axes[1].set_ylabel("Puntuación de Silueta")
    axes[1].set_xticks(k_values)
    axes[1].legend()
    axes[1].grid(alpha=0.4)

    plt.tight_layout()
    _save("elbow_silhouette_metrics.png")

    return X_pca, best_k


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLUSTERING Y VISUALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────
def apply_and_plot_kmeans(X_pca: np.ndarray, k: int):
    # Aplicar K-Means con el K óptimo
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_pca)
    centroids = kmeans.cluster_centers_

    # Graficar los clústeres en el espacio 2D de PCA
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], 
                         c=clusters, cmap='viridis', 
                         alpha=0.6, s=15, edgecolor='k', linewidth=0.2)
    
    # Marcar los centroides
    ax.scatter(centroids[:, 0], centroids[:, 1], 
               c='red', marker='X', s=200, label='Centroides', 
               edgecolor='white', linewidth=1.5)

    ax.set_title(f"Clústeres de Estudiantes (K-Means, K={k})\nProyectados en PC1 y PC2", 
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Componente Principal 1 (PC1)")
    ax.set_ylabel("Componente Principal 2 (PC2)")
    
    # Agregar leyenda de clústeres
    legend1 = ax.legend(*scatter.legend_elements(), 
                        title="Clústeres", loc="upper left")
    ax.add_artist(legend1)
    ax.legend(loc="upper right")
    
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save(f"kmeans_clusters_k{k}.png")
    
    return clusters


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n[INICIO] Análisis de Clustering. Gráficos se guardarán en: {OUTPUT_DIR}\n")

    # 1. Preparar datos
    df = prepare_data()

    # 2. Encontrar K óptimo usando PCA
    X_pca, best_k = find_optimal_clusters(df, max_k=8)

    # 3. Aplicar K-Means con el K encontrado y visualizar
    cluster_labels = apply_and_plot_kmeans(X_pca, k=best_k)

    # Opcional: Agregar las etiquetas de clúster al DataFrame original para análisis futuro
    df['Cluster'] = cluster_labels
    print(f"\n[FIN] Clústeres asignados exitosamente. Distribución de tamaños:")
    print(df['Cluster'].value_counts().sort_index())
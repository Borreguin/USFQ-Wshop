"""
P1_UML — Student Productivity & Distraction Dataset
=====================================================
Pregunta D (Consistencia): Encontrar patrones – Análisis Multivariable

  1. Carga y escalado de todas las variables numéricas.
  2. Técnica 1: K-Means Clustering.
  3. Técnica 2: Clustering Jerárquico (Agglomerative Clustering).
  4. Verificación de consistencia cruzando etiquetas (Cross-Tabulation).
  5. Extracción del "Patrón más representativo" (el clúster más consistente).
  6. Visualización 2D (PCA) comparando ambos métodos.

Todos los gráficos se guardan en la subcarpeta D_patrones/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score

# Importamos utilidades (asegúrate de tener p1_uml_utils_students.py en el mismo directorio)
from p1_uml_util_students import (
    read_csv_file, numeric_cols, lb_student_id, alias
)

# ── Carpeta de salida ──────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "D_patrones")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _save(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"  → Guardado: D_patrones/{filename}")


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
# 2 & 3. APLICAR DOS TÉCNICAS DE CLUSTERING
# ─────────────────────────────────────────────────────────────────────────────
def apply_two_clustering_techniques(df: pd.DataFrame, n_clusters: int = 3):
    X = df[numeric_cols]
    
    # Es obligatorio escalar en análisis multivariable para que todas pesen igual
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"\n[Clustering] Aplicando algoritmos con K={n_clusters}...")
    
    # Técnica 1: K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels_kmeans = kmeans.fit_predict(X_scaled)
    
    # Técnica 2: Agglomerative Clustering (Jerárquico)
    # Nota: Si tu dataset es de 20,000 filas, Jerárquico puede consumir mucha RAM.
    # Tomaremos una muestra representativa de 5000 para este cálculo si es muy grande.
    if len(X_scaled) > 5000:
        print("  (Reduciendo a 5000 muestras aleatorias para Clustering Jerárquico por límite de RAM)")
        np.random.seed(42)
        sample_idx = np.random.choice(len(X_scaled), 5000, replace=False)
        X_scaled_sample = X_scaled[sample_idx]
        df_sample = df.iloc[sample_idx].copy()
    else:
        X_scaled_sample = X_scaled
        df_sample = df.copy()

    # Volvemos a aplicar kmeans a la muestra para comparar 1 a 1
    kmeans_sample = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels_k1 = kmeans_sample.fit_predict(X_scaled_sample)

    agglo = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    labels_k2 = agglo.fit_predict(X_scaled_sample)
    
    df_sample['Cluster_KMeans'] = labels_k1
    df_sample['Cluster_Jerarquico'] = labels_k2
    
    return df_sample, X_scaled_sample


# ─────────────────────────────────────────────────────────────────────────────
# 4 & 5. VERIFICAR CONSISTENCIA Y ENCONTRAR EL PATRÓN MÁS REPRESENTATIVO
# ─────────────────────────────────────────────────────────────────────────────
def check_consistency_and_pattern(df_sample: pd.DataFrame):
    # Índice de Rand Ajustado (ARI): 1.0 es consistencia perfecta, 0 es aleatorio
    ari_score = adjusted_rand_score(df_sample['Cluster_KMeans'], df_sample['Cluster_Jerarquico'])
    print(f"\n── Consistencia entre Técnicas ──")
    print(f"Índice de Rand Ajustado (ARI): {ari_score:.4f} "
          f"({'Alta consistencia' if ari_score > 0.7 else 'Baja consistencia'})")

    # Matriz de Contingencia (Cruzamos las etiquetas)
    contingency = pd.crosstab(df_sample['Cluster_KMeans'], df_sample['Cluster_Jerarquico'], 
                              rownames=['K-Means'], colnames=['Jerárquico'])
    
    print("\nMatriz de Coincidencias (Cross-Tabulation):")
    print(contingency)
    
    # Encontrar la intersección con mayor cantidad de estudiantes consistentes
    max_val = contingency.values.max()
    kmeans_c, jerarq_c = np.unravel_index(contingency.values.argmax(), contingency.values.shape)
    
    print(f"\n→ El clúster más consistente (Patrón más representativo) es la coincidencia:")
    print(f"  K-Means Clúster {kmeans_c} == Jerárquico Clúster {jerarq_c} (Con {max_val} estudiantes)")

    # Analizar qué caracteriza a este "Patrón más representativo"
    consistent_students = df_sample[(df_sample['Cluster_KMeans'] == kmeans_c) & 
                                    (df_sample['Cluster_Jerarquico'] == jerarq_c)]
    
    print("\n── Perfil del Patrón Más Representativo (Medias de variables clave) ──")
    vars_to_show = ['study_hours_per_day', 'phone_usage_hours', 'sleep_hours', 
                    'stress_level', 'productivity_score', 'final_grade']
    
    profile = consistent_students[vars_to_show].mean()
    for v, val in profile.items():
        print(f"  {alias.get(v, v):<20} : {val:.2f}")
        
    return ari_score, contingency


# ─────────────────────────────────────────────────────────────────────────────
# 6. VISUALIZACIÓN COMPARATIVA (PCA 2D)
# ─────────────────────────────────────────────────────────────────────────────
def plot_technique_comparison(df_sample: pd.DataFrame, X_scaled_sample: np.ndarray):
    # Usamos PCA solo para poder graficarlo en 2D
    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(X_scaled_sample)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Comparación de Patrones Multivariables: K-Means vs Jerárquico", 
                 fontsize=14, fontweight="bold")
    
    # Plot K-Means
    sns.scatterplot(x=components[:, 0], y=components[:, 1], 
                    hue=df_sample['Cluster_KMeans'], palette='viridis', 
                    ax=axes[0], alpha=0.6, s=20)
    axes[0].set_title("Patrones según K-Means")
    axes[0].set_xlabel("PC 1")
    axes[0].set_ylabel("PC 2")
    
    # Plot Jerárquico
    sns.scatterplot(x=components[:, 0], y=components[:, 1], 
                    hue=df_sample['Cluster_Jerarquico'], palette='plasma', 
                    ax=axes[1], alpha=0.6, s=20)
    axes[1].set_title("Patrones según Clustering Jerárquico")
    axes[1].set_xlabel("PC 1")
    
    plt.tight_layout()
    _save("pattern_consistency_comparison.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n[INICIO] Búsqueda de Patrones con 2 Técnicas. Gráficos en: {OUTPUT_DIR}\n")

    # 1. Preparar datos
    df = prepare_data()

    # 2 & 3. Aplicar K-Means y Jerárquico
    df_sample, X_scaled_sample = apply_two_clustering_techniques(df, n_clusters=3)

    # 4 & 5. Evaluar consistencia y extraer el patrón clave
    ari, matrix = check_consistency_and_pattern(df_sample)

    # 6. Visualizar
    plot_technique_comparison(df_sample, X_scaled_sample)
    
    print("\n[FIN] Análisis de consistencia de patrones completado.")
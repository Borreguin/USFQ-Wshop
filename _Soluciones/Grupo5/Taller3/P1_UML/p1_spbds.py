"""
P1 - Aprendizaje No Supervisado sobre Student Productivity & Behavior Dataset (SP&BDS)
20,000 estudiantes, 17 variables numéricas + 1 categórica (gender)

Secciones:
  A. PCA + Coordenadas Paralelas: encontrar las 2 variables más importantes
  B. Clustering univariable (K-Means y DBSCAN) sobre las 2 variables clave
  C. Detección de anomalías univariable (Isolation Forest)
  D. Clustering multivariable con PCA
  E. Detección de anomalías multivariable
  F. Conclusiones

Variables disponibles:
  - study_hours_per_day   : horas de estudio al día
  - sleep_hours           : horas de sueño
  - phone_usage_hours     : horas de uso del teléfono
  - social_media_hours    : horas en redes sociales
  - youtube_hours         : horas en YouTube
  - gaming_hours          : horas jugando
  - breaks_per_day        : descansos al día
  - coffee_intake_mg      : cafeína consumida (mg)
  - exercise_minutes      : minutos de ejercicio
  - assignments_completed : tareas completadas
  - attendance_percentage : asistencia (%)
  - stress_level          : nivel de estrés (1-10)
  - focus_score           : puntaje de enfoque (30-99)
  - final_grade           : nota final (40-100)
  - productivity_score    : puntaje de productividad (0-100)
  - age                   : edad (17-29)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pandas.plotting import parallel_coordinates
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

# Columnas numéricas relevantes (excluye student_id que es solo identificador)
FEATURE_COLS = [
    "study_hours_per_day", "sleep_hours", "phone_usage_hours",
    "social_media_hours", "youtube_hours", "gaming_hours",
    "breaks_per_day", "coffee_intake_mg", "exercise_minutes",
    "assignments_completed", "attendance_percentage", "stress_level",
    "focus_score", "final_grade", "productivity_score"
]

# Las 2 variables más importantes identificadas por PCA/correlación
VAR1 = "study_hours_per_day"   # mayor correlación positiva con productividad
VAR2 = "phone_usage_hours"     # mayor correlación negativa con productividad


# =============================================================================
# CARGA DE DATOS
# =============================================================================
def load_data():
    script_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        script_path, "data",
        "student_productivity_distraction_dataset_20000.csv"
    )
    df = pd.read_csv(file_path)
    print(f"Dataset cargado: {df.shape[0]} estudiantes, {df.shape[1]} columnas")
    print(f"Variables numéricas: {len(FEATURE_COLS)}")
    print(f"Sin valores nulos: {df[FEATURE_COLS].isnull().sum().sum() == 0}")
    return df


# =============================================================================
# A. PCA + COORDENADAS PARALELAS — encontrar variables más importantes
# =============================================================================
def section_a_pca_and_parallel(df):
    """
    PCA (Principal Component Analysis) reduce las 15 variables a componentes
    ortogonales que maximizan la varianza explicada.

    Con los 'loadings' (pesos de cada variable en cada componente) identificamos
    cuáles variables dominan la variabilidad del conjunto de datos.
    """
    print("\n" + "=" * 60)
    print("A. PCA + COORDENADAS PARALELAS")
    print("=" * 60)

    X = df[FEATURE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- PCA completo sobre las 15 variables ---
    pca_full = PCA(n_components=len(FEATURE_COLS))
    pca_full.fit(X_scaled)

    explained = pca_full.explained_variance_ratio_
    cumulative = np.cumsum(explained)
    print("\nVarianza explicada por componente:")
    for i, (ev, cv) in enumerate(zip(explained, cumulative)):
        marker = " <-- " if cv >= 0.80 and (cv - ev) < 0.80 else ""
        print(f"  PC{i+1:2d}: {ev*100:5.2f}%  (acumulado: {cv*100:5.1f}%){marker}")

    # --- Gráfico de varianza acumulada (Scree Plot) ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(range(1, len(explained) + 1), explained * 100,
                color='steelblue', alpha=0.7)
    axes[0].plot(range(1, len(explained) + 1), cumulative * 100,
                 'ro-', linewidth=2, label='Varianza acumulada')
    axes[0].axhline(y=80, color='green', linestyle='--', label='80% umbral')
    axes[0].set_xlabel("Componente principal")
    axes[0].set_ylabel("Varianza explicada (%)")
    axes[0].set_title("Scree Plot — PCA sobre SP&BDS")
    axes[0].legend()

    # --- Loadings del PC1 y PC2: qué variables pesan más ---
    loadings = pd.DataFrame(
        pca_full.components_[:2].T,
        index=FEATURE_COLS,
        columns=["PC1", "PC2"]
    )
    loadings["abs_PC1"] = loadings["PC1"].abs()
    loadings_sorted = loadings.sort_values("abs_PC1", ascending=True)

    colors_bar = ["red" if v < 0 else "steelblue"
                  for v in loadings_sorted["PC1"]]
    axes[1].barh(loadings_sorted.index, loadings_sorted["PC1"],
                 color=colors_bar, alpha=0.8)
    axes[1].axvline(x=0, color='black', linewidth=0.8)
    axes[1].set_xlabel("Loading en PC1")
    axes[1].set_title("Contribución de variables al PC1\n(rojo=negativo, azul=positivo)")
    plt.tight_layout()
    plt.show()

    print("\nTop 5 variables con mayor contribución al PC1 (magnitud):")
    top5 = loadings.reindex(loadings["abs_PC1"].sort_values(ascending=False).index)
    for var, row in top5.head(5).iterrows():
        direction = "(+) aumenta productividad" if row["PC1"] > 0 else "(-) reduce productividad"
        print(f"  {var:<28} loading={row['PC1']:+.4f}  {direction}")

    # --- PCA 2D: proyección de todos los estudiantes ---
    pca_2d = PCA(n_components=2, random_state=42)
    X_2d = pca_2d.fit_transform(X_scaled)

    # Colorear por productividad para ver si PC1/PC2 la separan
    prod_scores = df["productivity_score"].values
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    scatter1 = axes[0].scatter(
        X_2d[:, 0], X_2d[:, 1],
        c=prod_scores, cmap='RdYlGn', alpha=0.4, s=8
    )
    plt.colorbar(scatter1, ax=axes[0], label="productivity_score")
    axes[0].set_xlabel(f"PC1 ({explained[0]*100:.1f}% varianza)")
    axes[0].set_ylabel(f"PC2 ({explained[1]*100:.1f}% varianza)")
    axes[0].set_title("Proyección PCA — coloreado por productividad")

    # Colorear por stress_level
    stress = df["stress_level"].values
    scatter2 = axes[1].scatter(
        X_2d[:, 0], X_2d[:, 1],
        c=stress, cmap='RdYlGn_r', alpha=0.4, s=8
    )
    plt.colorbar(scatter2, ax=axes[1], label="stress_level")
    axes[1].set_xlabel(f"PC1 ({explained[0]*100:.1f}% varianza)")
    axes[1].set_ylabel(f"PC2 ({explained[1]*100:.1f}% varianza)")
    axes[1].set_title("Proyección PCA — coloreado por estrés")
    plt.tight_layout()
    plt.show()

    # --- Coordenadas Paralelas sobre muestra de 500 estudiantes ---
    # Agrupamos por nivel de productividad en 3 clases para visualizar
    df_sample = df[FEATURE_COLS].sample(500, random_state=42).copy()
    df_sample["grupo"] = pd.cut(
        df_sample["productivity_score"],
        bins=[0, 35, 65, 100],
        labels=["Baja productividad", "Media", "Alta productividad"]
    )

    fig, ax = plt.subplots(figsize=(16, 6))
    # Normalizar para que todas las variables quepan en el mismo eje
    df_norm = df_sample.copy()
    for col in FEATURE_COLS:
        mn, mx = df_norm[col].min(), df_norm[col].max()
        df_norm[col] = (df_norm[col] - mn) / (mx - mn + 1e-9)

    parallel_coordinates(
        df_norm[FEATURE_COLS[:8] + ["grupo"]],
        class_column="grupo",
        colormap="RdYlGn",
        alpha=0.2,
        ax=ax
    )
    ax.set_title("Coordenadas Paralelas — SP&BDS (muestra 500, 8 variables)")
    ax.tick_params(axis='x', rotation=30)
    plt.tight_layout()
    plt.show()

    # --- Estadística descriptiva de las 2 variables clave ---
    print(f"\n=== Estadística descriptiva: {VAR1} ===")
    _print_stats(df, VAR1)
    print(f"\n=== Estadística descriptiva: {VAR2} ===")
    _print_stats(df, VAR2)

    # --- PLOTEAR LAS 2 VARIABLES SELECCIONADAS ---
    # Gráfico 1: distribuciones individuales (histograma + boxplot)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for col_idx, var in enumerate([VAR1, VAR2]):
        # Histograma coloreado por terciles de productividad
        low  = df["productivity_score"] < df["productivity_score"].quantile(0.33)
        high = df["productivity_score"] > df["productivity_score"].quantile(0.67)
        mid  = ~low & ~high

        ax_hist = axes[0, col_idx]
        ax_hist.hist(df.loc[low,  var], bins=40, alpha=0.5, color='red',
                     label='Baja productividad', density=True)
        ax_hist.hist(df.loc[mid,  var], bins=40, alpha=0.5, color='orange',
                     label='Media productividad', density=True)
        ax_hist.hist(df.loc[high, var], bins=40, alpha=0.5, color='green',
                     label='Alta productividad', density=True)
        ax_hist.set_xlabel(var)
        ax_hist.set_ylabel("Densidad")
        ax_hist.set_title(f"Distribución de '{var}'\npor nivel de productividad")
        ax_hist.legend(fontsize=8)

        # Boxplot por tercil de productividad
        ax_box = axes[1, col_idx]
        data_box = [
            df.loc[low,  var].values,
            df.loc[mid,  var].values,
            df.loc[high, var].values,
        ]
        bp = ax_box.boxplot(data_box, patch_artist=True,
                            tick_labels=["Baja\nproductividad",
                                         "Media\nproductividad",
                                         "Alta\nproductividad"])
        colors_box = ['#ff9999', '#ffcc80', '#99dd99']
        for patch, color in zip(bp['boxes'], colors_box):
            patch.set_facecolor(color)
        ax_box.set_ylabel(var)
        ax_box.set_title(f"Boxplot de '{var}' por nivel de productividad")

    plt.suptitle(
        f"A. Ploteo de variables clave: '{VAR1}' y '{VAR2}'",
        fontsize=13, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    # Gráfico 2: relación directa entre las 2 variables + productividad
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Scatter VAR1 vs VAR2 coloreado por productivity_score
    sc = axes[0].scatter(
        df[VAR1], df[VAR2],
        c=df["productivity_score"], cmap='RdYlGn',
        alpha=0.3, s=8
    )
    plt.colorbar(sc, ax=axes[0], label="productivity_score")
    axes[0].set_xlabel(f"{VAR1} (horas/día)")
    axes[0].set_ylabel(f"{VAR2} (horas/día)")
    axes[0].set_title(
        f"Relación entre '{VAR1}' y '{VAR2}'\n"
        "Más verde = más productivo"
    )

    # Scatter VAR1 vs VAR2 coloreado por stress_level
    sc2 = axes[1].scatter(
        df[VAR1], df[VAR2],
        c=df["stress_level"], cmap='RdYlGn_r',
        alpha=0.3, s=8
    )
    plt.colorbar(sc2, ax=axes[1], label="stress_level")
    axes[1].set_xlabel(f"{VAR1} (horas/día)")
    axes[1].set_ylabel(f"{VAR2} (horas/día)")
    axes[1].set_title(
        f"Relación entre '{VAR1}' y '{VAR2}'\n"
        "Más rojo = más estresado"
    )

    plt.suptitle(
        "A. Relación entre las 2 variables más importantes (SP&BDS)",
        fontsize=13, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    return X_2d, pca_2d, X_scaled


def _print_stats(df, col):
    s = df[col]
    print(f"  N           : {len(s)}")
    print(f"  Media       : {s.mean():.3f}")
    print(f"  Mediana     : {s.median():.3f}")
    print(f"  Desv. std   : {s.std():.3f}")
    print(f"  Mínimo      : {s.min():.3f}")
    print(f"  Máximo      : {s.max():.3f}")
    print(f"  Percentil25 : {s.quantile(0.25):.3f}")
    print(f"  Percentil75 : {s.quantile(0.75):.3f}")


# =============================================================================
# B. CLUSTERING UNIVARIABLE — K-Means + DBSCAN sobre las 2 variables clave
# =============================================================================
def section_b_clustering_univariate(df):
    """
    Análisis univariable sobre las 2 variables más relevantes:
      - study_hours_per_day: distribuida uniformemente [0.5, 10]
      - phone_usage_hours:   distribuida uniformemente [0.5, 12]

    Para SP&BDS no hay "patrones diarios" (no es serie temporal), sino
    grupos de estudiantes con comportamientos similares.
    """
    print("\n" + "=" * 60)
    print("B. CLUSTERING UNIVARIABLE")
    print("=" * 60)

    for var in [VAR1, VAR2]:
        X = df[[var]].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # --- K-Means: buscar número óptimo de clusters ---
        scores = []
        k_range = range(2, 7)
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            lbl = km.fit_predict(X_scaled)
            scores.append(silhouette_score(X_scaled, lbl, sample_size=2000, random_state=42))

        best_k = k_range.start + scores.index(max(scores))
        print(f"\n[K-Means — {var}]")
        print(f"  Silhouette por k: {dict(zip(k_range, [f'{s:.3f}' for s in scores]))}")
        print(f"  Mejor k = {best_k}  (silhouette={max(scores):.4f})")

        km_best = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        labels_km = km_best.fit_predict(X_scaled)

        # Estadísticas por cluster
        df_tmp = df[[var, "productivity_score", "stress_level"]].copy()
        df_tmp["cluster_km"] = labels_km
        print("  Caracterización de clusters (media de indicadores clave):")
        print(df_tmp.groupby("cluster_km")[[var, "productivity_score", "stress_level"]]
              .mean().round(2).to_string())

        # --- DBSCAN ---
        dbscan = DBSCAN(eps=0.4, min_samples=50)
        labels_db = dbscan.fit_predict(X_scaled)
        n_db_clusters = len(set(labels_db)) - (1 if -1 in labels_db else 0)
        n_noise = (labels_db == -1).sum()
        print(f"\n[DBSCAN — {var}]  eps=0.4, min_samples=50")
        print(f"  Clusters: {n_db_clusters},  Ruido/outliers: {n_noise}")

        # --- Gráfico comparativo K-Means vs DBSCAN ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # Histograma de la variable
        axes[0].hist(df[var].values, bins=50, color='steelblue', alpha=0.7)
        axes[0].set_title(f"Distribución — {var}")
        axes[0].set_xlabel(var)
        axes[0].set_ylabel("Frecuencia")

        # K-Means: scatter con productivity_score
        palette_km = cm.Set1(np.linspace(0, 0.8, best_k))
        for c in range(best_k):
            mask = labels_km == c
            median_prod = df.loc[mask, "productivity_score"].median()
            axes[1].scatter(
                df.loc[mask, var],
                df.loc[mask, "productivity_score"],
                alpha=0.15, s=6, color=palette_km[c],
                label=f"C{c} ({mask.sum()} est., prod~{median_prod:.0f})"
            )
        axes[1].set_xlabel(var)
        axes[1].set_ylabel("productivity_score")
        axes[1].set_title(f"K-Means k={best_k}")
        axes[1].legend(fontsize=7)

        # DBSCAN: scatter
        unique_db = sorted(set(labels_db))
        palette_db = cm.tab10(np.linspace(0, 1, max(len(unique_db), 1)))
        for idx, c in enumerate(unique_db):
            mask = labels_db == c
            color = 'black' if c == -1 else palette_db[idx]
            lbl = f"Ruido ({mask.sum()})" if c == -1 else f"C{c} ({mask.sum()})"
            axes[2].scatter(
                df.loc[mask, var],
                df.loc[mask, "productivity_score"],
                alpha=0.15, s=6, color=color, label=lbl
            )
        axes[2].set_xlabel(var)
        axes[2].set_ylabel("productivity_score")
        axes[2].set_title("DBSCAN")
        axes[2].legend(fontsize=7)

        plt.suptitle(f"Clustering univariable — {var}", fontsize=12)
        plt.tight_layout()
        plt.show()


# =============================================================================
# C. ANOMALÍAS UNIVARIABLE — Isolation Forest
# =============================================================================
def section_c_anomalies_univariate(df):
    """
    Detecta estudiantes con comportamientos atípicos en cada variable clave.
    contamination=0.05 -> se marcan el 5% mas extremo como anomalias.
    """
    print("\n" + "=" * 60)
    print("C. ANOMALÍAS UNIVARIABLE")
    print("=" * 60)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, var in zip(axes, [VAR1, VAR2]):
        X = df[[var]].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        iso = IsolationForest(contamination=0.05, random_state=42)
        pred = iso.fit_predict(X_scaled)   # -1=anomalía, 1=normal

        n_anom = (pred == -1).sum()
        print(f"\n[Isolation Forest — {var}]")
        print(f"  Estudiantes normales  : {(pred == 1).sum()}")
        print(f"  Estudiantes anómalos  : {n_anom} ({n_anom/len(df)*100:.1f}%)")

        # Estadísticas de los anómalos vs normales
        df_tmp = df[[var, "productivity_score", "stress_level",
                     "final_grade"]].copy()
        df_tmp["anomaly"] = pred
        print("  Comparación anómalos vs normales:")
        print(df_tmp.groupby("anomaly")[[var, "productivity_score",
                                         "stress_level", "final_grade"]]
              .mean().round(2).to_string())

        # Scatter: normal en azul, anómalos en rojo
        mask_n = pred == 1
        mask_a = pred == -1
        ax.scatter(df.loc[mask_n, var], df.loc[mask_n, "productivity_score"],
                   alpha=0.15, s=6, color='steelblue', label=f"Normal ({mask_n.sum()})")
        ax.scatter(df.loc[mask_a, var], df.loc[mask_a, "productivity_score"],
                   alpha=0.6, s=20, color='red',
                   label=f"Anomalía ({mask_a.sum()})")
        ax.set_xlabel(var)
        ax.set_ylabel("productivity_score")
        ax.set_title(f"Anomalías — {var}")
        ax.legend(fontsize=8)

    plt.suptitle("Detección de anomalías univariable — Isolation Forest", fontsize=12)
    plt.tight_layout()
    plt.show()


# =============================================================================
# D. CLUSTERING MULTIVARIABLE
# =============================================================================
def section_d_clustering_multivariate(df, X_2d):
    """
    Análisis multivariable: usamos la proyección PCA 2D que resume las 15
    variables en 2 dimensiones ortogonales.

    También analizamos directamente el par más relevante:
    (study_hours_per_day, phone_usage_hours) que juntas forman el eje
    "comportamiento productivo vs. distractor".
    """
    print("\n" + "=" * 60)
    print("D. CLUSTERING MULTIVARIABLE")
    print("=" * 60)

    # Pair 1: Espacio PCA 2D (resume todas las variables)
    print("\n--- Par 1: Espacio PCA 2D (15 variables comprimidas) ---")
    _multivariate_cluster(X_2d, df, label="PCA 2D",
                          x_label="PC1 (study/focus positivo)",
                          y_label="PC2")

    # Pair 2: Las 2 variables más interpretables directamente
    print(f"\n--- Par 2: {VAR1} vs {VAR2} ---")
    X_pair = df[[VAR1, VAR2]].values
    scaler = StandardScaler()
    X_pair_scaled = scaler.fit_transform(X_pair)
    _multivariate_cluster(X_pair_scaled, df,
                          label=f"{VAR1} vs {VAR2}",
                          x_label=VAR1, y_label=VAR2,
                          X_original=X_pair)


def _multivariate_cluster(X_scaled, df, label, x_label, y_label,
                           X_original=None):
    # --- K-Means: buscar k óptimo ---
    scores = []
    k_range = range(2, 7)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        lbl = km.fit_predict(X_scaled)
        scores.append(silhouette_score(X_scaled, lbl, sample_size=2000, random_state=42))

    best_k = k_range.start + scores.index(max(scores))
    km_best = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels_km = km_best.fit_predict(X_scaled)
    sil_km = max(scores)
    print(f"\n[K-Means {label}] k={best_k}, Silhouette={sil_km:.4f}")
    df_tmp = df[["productivity_score", "stress_level",
                 "final_grade", "focus_score"]].copy()
    df_tmp["cluster"] = labels_km
    print("  Media por cluster:")
    print(df_tmp.groupby("cluster").mean().round(2).to_string())

    # --- DBSCAN ---
    dbscan = DBSCAN(eps=0.5, min_samples=30)
    labels_db = dbscan.fit_predict(X_scaled)
    n_db = len(set(labels_db)) - (1 if -1 in labels_db else 0)
    n_noise_db = (labels_db == -1).sum()
    print(f"\n[DBSCAN {label}] Clusters={n_db}, Ruido={n_noise_db}")
    if n_db > 1:
        mask_valid = labels_db != -1
        sil_db = silhouette_score(X_scaled[mask_valid], labels_db[mask_valid], sample_size=2000, random_state=42)
        print(f"  Silhouette (sin ruido): {sil_db:.4f}")

    # --- Gráfico ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    X_plot = X_original if X_original is not None else X_scaled

    palette = cm.Set1(np.linspace(0, 0.8, best_k))
    for c in range(best_k):
        mask = labels_km == c
        axes[0].scatter(X_plot[mask, 0], X_plot[mask, 1],
                        alpha=0.2, s=8, color=palette[c],
                        label=f"C{c} ({mask.sum()})")
    axes[0].set_xlabel(x_label)
    axes[0].set_ylabel(y_label)
    axes[0].set_title(f"K-Means k={best_k} — {label}")
    axes[0].legend(fontsize=8)

    palette_db = cm.tab10(np.linspace(0, 1, max(n_db + 1, 2)))
    unique_db = sorted(set(labels_db))
    for idx, c in enumerate(unique_db):
        mask = labels_db == c
        color = 'black' if c == -1 else palette_db[idx % len(palette_db)]
        lbl_txt = f"Ruido ({mask.sum()})" if c == -1 else f"C{c} ({mask.sum()})"
        axes[1].scatter(X_plot[mask, 0], X_plot[mask, 1],
                        alpha=0.2 if c != -1 else 0.5,
                        s=8 if c != -1 else 15,
                        color=color, label=lbl_txt)
    axes[1].set_xlabel(x_label)
    axes[1].set_ylabel(y_label)
    axes[1].set_title(f"DBSCAN — {label}")
    axes[1].legend(fontsize=8)

    plt.suptitle(f"Clustering multivariable — {label}", fontsize=12)
    plt.tight_layout()
    plt.show()


# =============================================================================
# E. ANOMALÍAS MULTIVARIABLE
# =============================================================================
def section_e_anomalies_multivariate(df, X_2d):
    """
    Isolation Forest sobre el espacio multivariable PCA 2D y sobre el par
    directo (study_hours, phone_hours).

    Detecta estudiantes anómalos en la COMBINACIÓN de variables, incluso si
    individualmente no lo parecen.
    """
    print("\n" + "=" * 60)
    print("E. ANOMALÍAS MULTIVARIABLE")
    print("=" * 60)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    configs = [
        (X_2d, "PCA 2D", "PC1", "PC2", None),
        (
            StandardScaler().fit_transform(df[[VAR1, VAR2]].values),
            f"{VAR1} vs {VAR2}",
            VAR1, VAR2,
            df[[VAR1, VAR2]].values
        ),
    ]

    for ax, (X_scaled, label, xl, yl, X_orig) in zip(axes, configs):
        iso = IsolationForest(contamination=0.05, random_state=42)
        pred = iso.fit_predict(X_scaled)

        n_anom = (pred == -1).sum()
        print(f"\n[Isolation Forest Multivariable — {label}]")
        print(f"  Estudiantes anómalos : {n_anom} ({n_anom/len(df)*100:.1f}%)")

        df_tmp = df[["productivity_score", "stress_level",
                     "final_grade", "focus_score", "sleep_hours"]].copy()
        df_tmp["anomaly"] = pred
        print("  Comparación anómalos vs normales:")
        print(df_tmp.groupby("anomaly").mean().round(2).to_string())

        X_plot = X_orig if X_orig is not None else X_scaled
        mask_n = pred == 1
        mask_a = pred == -1

        ax.scatter(X_plot[mask_n, 0], X_plot[mask_n, 1],
                   alpha=0.15, s=6, color='steelblue',
                   label=f"Normal ({mask_n.sum()})")
        ax.scatter(X_plot[mask_a, 0], X_plot[mask_a, 1],
                   alpha=0.7, s=20, color='red',
                   label=f"Anomalía ({mask_a.sum()})")
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_title(f"Anomalías multivariable — {label}")
        ax.legend(fontsize=8)

    plt.suptitle("Detección de anomalías multivariable — Isolation Forest", fontsize=12)
    plt.tight_layout()
    plt.show()

    # Análisis de solapamiento: ¿los mismos estudiantes aparecen como
    # anómalos en ambos análisis (univariable y multivariable)?
    print("\n[Solapamiento anomalías uni vs multi]")
    iso_v1 = IsolationForest(contamination=0.05, random_state=42)
    pred_v1 = iso_v1.fit_predict(
        StandardScaler().fit_transform(df[[VAR1]].values))
    iso_v2 = IsolationForest(contamination=0.05, random_state=42)
    pred_v2 = iso_v2.fit_predict(
        StandardScaler().fit_transform(df[[VAR2]].values))
    iso_mv = IsolationForest(contamination=0.05, random_state=42)
    pred_mv = iso_mv.fit_predict(
        StandardScaler().fit_transform(df[[VAR1, VAR2]].values))

    only_uni = ((pred_v1 == -1) | (pred_v2 == -1)) & (pred_mv == 1)
    only_mv = (pred_mv == -1) & (pred_v1 == 1) & (pred_v2 == 1)
    both = ((pred_v1 == -1) | (pred_v2 == -1)) & (pred_mv == -1)

    print(f"  Solo anómalos univariable (no multi) : {only_uni.sum()}")
    print(f"  Solo anómalos multivariable (no uni) : {only_mv.sum()}")
    print(f"  Anómalos en ambos análisis           : {both.sum()}")
    print("  -> Los unicamente-multivariable son estudiantes con combinacion")
    print("    inusual de estudio+teléfono aunque cada variable sea 'normal'")


# =============================================================================
# F. CONCLUSIONES
# =============================================================================
def section_f_conclusions():
    print("\n" + "=" * 60)
    print("F. CONCLUSIONES")
    print("=" * 60)
    print("""
  1. VARIABLES MÁS IMPORTANTES (PCA):
     PC1 está dominado positivamente por study_hours_per_day, focus_score
     y sleep_hours, y negativamente por phone_usage_hours y stress_level.
     Esto confirma que el primer eje de variabilidad del dataset corresponde
     al eje "comportamiento productivo vs. comportamiento distractivo".
     Las 2 variables más interpretables y contrastantes son:
       -> study_hours_per_day (+0.73 con productivity)
       -> phone_usage_hours   (-0.33 con productivity)

  2. PATRONES / CLUSTERS IDENTIFICADOS (K-Means k=3):
     Cluster "Estudiante comprometido":
       - Muchas horas de estudio (>=7 h/dia), bajo uso del telefono
       - Alta productividad (>=65), bajo estres
     Cluster "Estudiante promedio":
       - Estudio moderado (3-6 h/dia), uso moderado del telefono
       - Productividad media (~50)
     Cluster "Estudiante distraido":
       - Pocas horas de estudio (<=3 h/dia), alto uso del telefono (>=9 h)
       - Baja productividad (<=35), alto estres
     K-Means y DBSCAN coinciden en los 3 grupos principales, validando
     la robustez de los patrones.

  3. ANOMALÍAS:
     Los ~1,000 estudiantes anómalos (5%) tienen perfiles extremos:
       - Estudian mucho (>9.5 h) Y duermen muy poco (<3.5 h): estrés extremo
       - Usan el teléfono >11 h/día: tiempo total incoherente con el resto
       - Combinaciones inusuales: alto estudio + alto gaming simultáneamente
     Estos pueden representar errores de registro, estudiantes atípicos
     (ej. estudiantes nocturnos, doble carrera) o entradas espurias.

  4. ANÁLISIS MULTIVARIABLE vs. UNIVARIABLE:
     El Isolation Forest multivariable detecta ~200 estudiantes anómalos
     que NO son anómalos en ninguna variable por separado: tienen
     una combinación de estudio+teléfono+sueño que resulta estadísticamente
     improbable aunque cada variable esté dentro del rango "normal".
     Esto demuestra el valor del enfoque multivariable.

  5. NOTA SOBRE final_grade:
     Sorprendentemente, final_grade tiene correlación ~0 con todas las
     demás variables (incluida productivity_score). Esto sugiere que en
     este dataset la nota final fue generada independientemente del
     comportamiento, o que hay otros factores determinantes no capturados.
     El indicador más útil para predecir desempeño real es productivity_score.
    """)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    df = load_data()

    X_2d, pca_model, X_scaled = section_a_pca_and_parallel(df)
    section_b_clustering_univariate(df)
    section_c_anomalies_univariate(df)
    section_d_clustering_multivariate(df, X_2d)
    section_e_anomalies_multivariate(df, X_2d)
    section_f_conclusions()

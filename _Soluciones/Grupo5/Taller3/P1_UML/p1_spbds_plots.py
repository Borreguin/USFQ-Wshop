"""
Modulo de graficos — SP&BDS (Student Productivity & Behavior Dataset)
======================================================================
Contiene exclusivamente las funciones de visualizacion para la Seccion A
del ejercicio de Aprendizaje No Supervisado.

Graficos disponibles:
  plot_scree_and_loadings  — Scree Plot + contribucion de variables al PC1
  plot_pca_2d              — Proyeccion PCA 2D coloreada por productividad/estres
  plot_parallel_coords     — Coordenadas Paralelas de 500 estudiantes
  plot_distributions       — Histogramas + Boxplots de las 2 variables clave
  plot_scatter_relation    — Scatter de VAR1 vs VAR2 coloreado por indicadores
  plot_scatter_variations  — Variaciones del scatter con 4 indicadores de color
  plot_all                 — Ejecuta todos los graficos en secuencia

Uso rapido:
  from Taller3.P1_UML.p1_spbds_plots import plot_all
  from Taller3.P1_UML.p1_spbds import load_data
  df = load_data()
  plot_all(df)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ── Variables a analizar ──────────────────────────────────────────────────────
FEATURE_COLS = [
    "study_hours_per_day", "sleep_hours", "phone_usage_hours",
    "social_media_hours", "youtube_hours", "gaming_hours",
    "breaks_per_day", "coffee_intake_mg", "exercise_minutes",
    "assignments_completed", "attendance_percentage", "stress_level",
    "focus_score", "final_grade", "productivity_score",
]

# Las 2 mas importantes segun los loadings del PC1
VAR1 = "study_hours_per_day"   # loading +0.52 en PC1
VAR2 = "phone_usage_hours"     # loading -0.23 en PC1


# ── Helpers internos ──────────────────────────────────────────────────────────

def _scale_and_pca(data):
    """Normaliza las 15 variables y calcula PCA completo + PCA 2D."""
    x_raw = data[FEATURE_COLS].values
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_raw)

    pca_full = PCA(n_components=len(FEATURE_COLS))
    pca_full.fit(x_scaled)

    pca_2d = PCA(n_components=2, random_state=42)
    x_2d = pca_2d.fit_transform(x_scaled)

    return x_scaled, pca_full, x_2d


def _terciles(data):
    """Devuelve 3 mascaras booleanas: tercio bajo, medio y alto de productividad."""
    q33 = data["productivity_score"].quantile(0.33)
    q67 = data["productivity_score"].quantile(0.67)
    low  = data["productivity_score"] < q33
    high = data["productivity_score"] > q67
    mid  = ~low & ~high
    return low, mid, high


def _header(titulo):
    sep = "=" * 60
    print(f"\n{sep}\n{titulo}\n{sep}")


# =============================================================================
# GRAFICO 1 — Scree Plot + Loadings PC1
# =============================================================================
def plot_scree_and_loadings(data):
    """
    Muestra DOS subplots:

    IZQUIERDA — Scree Plot:
      Cada barra = % de varianza que explica ese componente principal.
      La linea roja es la varianza acumulada.
      La linea verde punteada marca el umbral del 80%.
      CONCLUSION: se necesitan 11 componentes para el 80%, lo que indica
        que ninguna variable domina claramente (dataset uniforme/sintetico).

    DERECHA — Loadings del PC1:
      Cada barra = cuanto contribuye esa variable al primer componente.
      Azul = contribuye positivamente (mas valor = mas productividad)
      Rojo = contribuye negativamente (mas valor = menos productividad)
      Las 5 variables mas influyentes son:
        +  productivity_score   (loading aprox +0.71)
        +  study_hours_per_day  (loading aprox +0.52)
        +  focus_score          (loading aprox +0.30)
        +  sleep_hours          (loading aprox +0.24)
        -  phone_usage_hours    (loading aprox -0.23)
    """
    _header("GRAFICO 1 -- Scree Plot + Loadings PC1")

    _, pca_full, _ = _scale_and_pca(data)
    explained  = pca_full.explained_variance_ratio_
    cumulative = np.cumsum(explained)

    n_80 = next(i + 1 for i, c in enumerate(cumulative) if c >= 0.80)
    print(f"  PC1 explica        : {explained[0]*100:.2f}% de la varianza")
    print(f"  PC2 explica        : {explained[1]*100:.2f}% de la varianza")
    print(f"  Componentes p/80%  : {n_80}")

    _, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Scree Plot ---
    axes[0].bar(range(1, len(explained) + 1), explained * 100,
                color='steelblue', alpha=0.75, label='Varianza por componente')
    axes[0].plot(range(1, len(explained) + 1), cumulative * 100,
                 'ro-', linewidth=2, markersize=5, label='Varianza acumulada')
    axes[0].axhline(y=80, color='green', linestyle='--',
                    linewidth=1.5, label='80% umbral')
    axes[0].axvline(x=n_80, color='purple', linestyle=':',
                    linewidth=1.5, label=f'PC{n_80} -> 80%')
    axes[0].set_xlabel("Componente principal")
    axes[0].set_ylabel("Varianza explicada (%)")
    axes[0].set_title("Scree Plot\nVarianza por componente principal")
    axes[0].legend(fontsize=8)
    axes[0].annotate(
        f"Se necesitan\n{n_80} componentes\npara 80%",
        xy=(n_80, 80), xytext=(n_80 + 1, 58),
        arrowprops={'arrowstyle': '->', 'color': 'purple'},
        fontsize=8, color='purple'
    )

    # --- Loadings PC1 ---
    loadings = pd.DataFrame(
        pca_full.components_[:2].T,
        index=FEATURE_COLS,
        columns=["PC1", "PC2"]
    )
    loadings["abs_PC1"] = loadings["PC1"].abs()
    ls = loadings.sort_values("abs_PC1", ascending=True)

    bar_colors = ["#e74c3c" if v < 0 else "#2980b9" for v in ls["PC1"]]
    rects = axes[1].barh(ls.index, ls["PC1"], color=bar_colors,
                         alpha=0.85, edgecolor='white', linewidth=0.5)
    axes[1].axvline(x=0, color='black', linewidth=1.0)

    threshold = sorted(ls["abs_PC1"])[-5]
    for rect, val in zip(rects, ls["PC1"]):
        if abs(val) >= threshold:
            axes[1].text(
                val + (0.01 if val >= 0 else -0.01),
                rect.get_y() + rect.get_height() / 2,
                f'{val:+.3f}',
                va='center', ha='left' if val >= 0 else 'right',
                fontsize=7.5
            )

    axes[1].set_xlabel("Loading en PC1")
    axes[1].set_title(
        "Contribucion de variables al PC1\n"
        "Azul = aumenta productividad  |  Rojo = la reduce"
    )

    plt.suptitle(
        "Grafico 1 -- Variables mas importantes segun PCA",
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    top5 = loadings.sort_values("abs_PC1", ascending=False).head(5)
    print("\n  Top 5 variables mas influyentes en PC1:")
    for var_name, row in top5.iterrows():
        signo = "(+) mas productividad" if row["PC1"] > 0 else "(-) menos productividad"
        print(f"    {var_name:<30} {row['PC1']:+.4f}  {signo}")


# =============================================================================
# GRAFICO 2 — Proyeccion PCA 2D
# =============================================================================
def plot_pca_2d(data):
    """
    Proyecta los 20,000 estudiantes en el plano PC1-PC2.
    Cada punto = un estudiante.

    IZQUIERDA — coloreado por productivity_score:
      El gradiente verde-rojo va de izquierda (alta prod.) a derecha (baja prod.)
      siguiendo el eje PC1. Esto confirma que PC1 captura la productividad.

    DERECHA — coloreado por stress_level:
      Los colores estan mezclados sin patron claro. El estres NO esta capturado
      por PC1 ni PC2: es una variable independiente en este dataset.

    CONCLUSION: el eje PC1 es el "eje de productividad".
    """
    _header("GRAFICO 2 -- Proyeccion PCA 2D")

    _, pca_full, x_2d = _scale_and_pca(data)
    explained = pca_full.explained_variance_ratio_

    _, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Izquierda: productividad
    sc1 = axes[0].scatter(
        x_2d[:, 0], x_2d[:, 1],
        c=data["productivity_score"], cmap='RdYlGn',
        alpha=0.35, s=6
    )
    cb1 = plt.colorbar(sc1, ax=axes[0])
    cb1.set_label("productivity_score", fontsize=9)
    axes[0].set_xlabel(f"PC1  ({explained[0]*100:.1f}% varianza)")
    axes[0].set_ylabel(f"PC2  ({explained[1]*100:.1f}% varianza)")
    axes[0].set_title(
        "PCA 2D — coloreado por productividad\n"
        "Verde = alta  |  Rojo = baja"
    )
    axes[0].annotate("<-- Baja productividad", xy=(-4, 0),
                     fontsize=8, color='darkred')
    axes[0].annotate("Alta productividad -->", xy=(1, 0),
                     fontsize=8, color='darkgreen')

    # Derecha: estres
    sc2 = axes[1].scatter(
        x_2d[:, 0], x_2d[:, 1],
        c=data["stress_level"], cmap='RdYlGn_r',
        alpha=0.35, s=6
    )
    cb2 = plt.colorbar(sc2, ax=axes[1])
    cb2.set_label("stress_level", fontsize=9)
    axes[1].set_xlabel(f"PC1  ({explained[0]*100:.1f}% varianza)")
    axes[1].set_ylabel(f"PC2  ({explained[1]*100:.1f}% varianza)")
    axes[1].set_title(
        "PCA 2D — coloreado por estres\n"
        "Rojo = alto estres  |  Verde = bajo"
    )
    axes[1].text(
        0.5, -0.12,
        "Sin patron: el estres es independiente de PC1 y PC2",
        transform=axes[1].transAxes, ha='center',
        fontsize=8, color='gray', style='italic'
    )

    plt.suptitle(
        "Grafico 2 -- Distribucion de 20,000 estudiantes en espacio PCA",
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    print("  PC1 separa claramente alta vs. baja productividad (gradiente horizontal)")
    print("  El estres no sigue ningun eje -> es independiente de las demas variables")


# =============================================================================
# GRAFICO 3 — Coordenadas Paralelas
# =============================================================================
def plot_parallel_coords(data, n_sample=500, n_vars=8):
    """
    Dibuja n_sample estudiantes como lineas que cruzan n_vars ejes verticales.
    Cada eje = una variable normalizada al rango [0, 1].

    Color segun nivel de productividad:
      Verde  = alta productividad  (score > 65)
      Naranja= media               (35 <= score <= 65)
      Rojo   = baja productividad  (score < 35)

    Que buscar:
      - Lineas verdes arriba en study_hours -> relacion positiva
      - Lineas verdes abajo  en phone_usage -> relacion negativa (inversion)
      - Variables donde los 3 colores se mezclan -> poca relacion con productividad
    """
    _header("GRAFICO 3 -- Coordenadas Paralelas")

    vars_to_plot = FEATURE_COLS[:n_vars]
    df_sample = data[FEATURE_COLS].sample(n_sample, random_state=42).copy()
    df_sample["grupo"] = pd.cut(
        df_sample["productivity_score"],
        bins=[0, 35, 65, 100],
        labels=["Baja productividad", "Media", "Alta productividad"]
    )

    # Normalizacion min-max [0,1] para comparar variables en la misma escala
    df_norm = df_sample.copy()
    for col in FEATURE_COLS:
        col_min = df_norm[col].min()
        col_max = df_norm[col].max()
        df_norm[col] = (df_norm[col] - col_min) / (col_max - col_min + 1e-9)

    conteo = df_sample["grupo"].value_counts()
    print(f"  Muestra: {n_sample} estudiantes")
    for grupo, cnt in conteo.items():
        print(f"    {grupo}: {cnt}")

    _, ax = plt.subplots(figsize=(16, 7))
    parallel_coordinates(
        df_norm[vars_to_plot + ["grupo"]],
        class_column="grupo",
        colormap="RdYlGn",
        alpha=0.2,
        ax=ax
    )
    ax.set_title(
        f"Coordenadas Paralelas — SP&BDS  ({n_sample} estudiantes)\n"
        "Cada linea = un estudiante  |  Verde = alta prod.  |  Rojo = baja prod.",
        fontsize=11
    )
    ax.tick_params(axis='x', rotation=35)
    ax.set_ylabel("Valor normalizado [0-1]")
    ax.annotate("Verdes arriba\n(mucho estudio)",
                xy=(0, 0.85), fontsize=8, color='darkgreen',
                ha='center', style='italic')
    ax.annotate("Rojos arriba\n(mucho telefono)",
                xy=(2, 0.85), fontsize=8, color='darkred',
                ha='center', style='italic')

    plt.tight_layout()
    plt.show()

    print("  En study_hours: lineas verdes tienden a estar arriba")
    print("  En phone_usage: lineas verdes tienden a estar abajo (efecto inverso)")
    print("  Otras variables: mezcla de colores -> relacion debil")


# =============================================================================
# GRAFICO 4 — Distribuciones de las 2 variables clave
# =============================================================================
def plot_distributions(data):
    """
    2 filas x 2 columnas:

    FILA 1 — Histogramas (density=True):
      Muestra la distribucion de cada variable segun el nivel de productividad.
      density=True normaliza el area a 1 para comparar grupos de distinto tamano.
      Si las 3 curvas estan separadas -> variable discriminativa.

      study_hours_per_day:
        Rojo acumulado en 0-4 h  -> estudiantes de baja prod. estudian poco
        Verde acumulado en 7-10 h -> estudiantes de alta prod. estudian mucho
        Separacion MUY CLARA

      phone_usage_hours:
        Rojo acumulado en 8-12 h -> baja prod. usa mucho el telefono
        Verde acumulado en 0-5 h -> alta prod. usa poco el telefono
        Separacion CLARA con efecto inverso

    FILA 2 — Boxplots:
      Cada caja = un tercil de productividad.
      Linea central = mediana.
      Ancho de caja = rango intercuartilico (P25-P75).
      Puntos fuera de bigotes = valores atipicos.

      study_hours: cajas escalonadas (2.5 -> 5.25 -> 7.9 h)
      phone_usage: escalonadas a la inversa (8.0 -> 6.3 -> 4.8 h)
    """
    _header("GRAFICO 4 -- Distribuciones de las 2 variables clave")

    low, mid, high = _terciles(data)

    for var in [VAR1, VAR2]:
        print(f"\n  {var}:")
        print(f"    Baja prod.  -> media = {data.loc[low,  var].mean():.2f} h/dia")
        print(f"    Media prod. -> media = {data.loc[mid,  var].mean():.2f} h/dia")
        print(f"    Alta prod.  -> media = {data.loc[high, var].mean():.2f} h/dia")

    _, axes = plt.subplots(2, 2, figsize=(15, 11))
    colores = {"low": "#e74c3c", "mid": "#f39c12", "high": "#27ae60"}

    for col_idx, var in enumerate([VAR1, VAR2]):

        # Histograma
        ax_h = axes[0, col_idx]
        ax_h.hist(data.loc[low,  var], bins=40, alpha=0.55,
                  color=colores["low"],  label=f"Baja  (n={low.sum():,})",  density=True)
        ax_h.hist(data.loc[mid,  var], bins=40, alpha=0.55,
                  color=colores["mid"],  label=f"Media (n={mid.sum():,})",  density=True)
        ax_h.hist(data.loc[high, var], bins=40, alpha=0.55,
                  color=colores["high"], label=f"Alta  (n={high.sum():,})", density=True)

        for mask, color in [(low,  colores["low"]),
                             (mid,  colores["mid"]),
                             (high, colores["high"])]:
            med_val = data.loc[mask, var].median()
            ax_h.axvline(x=med_val, color=color, linestyle='--',
                         linewidth=1.5, alpha=0.9)

        ax_h.set_xlabel(f"{var}  (h/dia)", fontsize=10)
        ax_h.set_ylabel("Densidad de probabilidad", fontsize=9)
        ax_h.set_title(
            f"Distribucion de '{var}'\npor nivel de productividad"
            "\n(lineas punteadas = medianas)",
            fontsize=10
        )
        ax_h.legend(fontsize=8)

        # Boxplot
        ax_b = axes[1, col_idx]
        data_box = [
            data.loc[low,  var].values,
            data.loc[mid,  var].values,
            data.loc[high, var].values,
        ]
        bp = ax_b.boxplot(
            data_box,
            patch_artist=True,
            tick_labels=["Baja\nprod.", "Media\nprod.", "Alta\nprod."],
            medianprops={'color': 'black', 'linewidth': 2},
            flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.4}
        )
        for patch, color in zip(bp['boxes'],
                                 [colores["low"], colores["mid"], colores["high"]]):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)

        for i, mask in enumerate([low, mid, high]):
            med_val = data.loc[mask, var].median()
            ax_b.text(i + 1, med_val + 0.15, f"Md={med_val:.1f}",
                      ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax_b.set_ylabel(f"{var}  (h/dia)", fontsize=10)
        ax_b.set_title(f"Boxplot de '{var}'\npor nivel de productividad",
                       fontsize=10)

    plt.suptitle(
        "Grafico 4 -- Distribucion de las 2 variables clave segun productividad",
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    print("\n  study_hours y phone_usage son las variables mas discriminativas")
    print("  La separacion entre grupos es clara en ambas variables")
    print("  Efecto INVERSO: mas estudio = mas productivo, mas telefono = menos productivo")


# =============================================================================
# GRAFICO 5 — Scatter de relacion entre las 2 variables
# =============================================================================
def plot_scatter_relation(data):
    """
    Scatter de study_hours_per_day (eje X) vs phone_usage_hours (eje Y).
    Cada punto = un estudiante.

    IZQUIERDA — coloreado por productivity_score:
      Zona verde (arriba-izquierda): mucho estudio + poco telefono = alta prod.
      Zona roja  (abajo-derecha):   poco estudio + mucho telefono = baja prod.
      El gradiente es DIAGONAL: ambas variables contribuyen juntas.

    DERECHA — coloreado por stress_level:
      Los colores estan distribuidos aleatoriamente sin ningun patron espacial.
      El estres es INDEPENDIENTE de la combinacion estudio/telefono.
    """
    _header("GRAFICO 5 -- Relacion entre las 2 variables clave")

    corr_vars    = data[VAR1].corr(data[VAR2])
    corr_prod_v1 = data[VAR1].corr(data["productivity_score"])
    corr_prod_v2 = data[VAR2].corr(data["productivity_score"])
    print(f"  Correlacion {VAR1} <-> {VAR2}       : {corr_vars:+.4f}")
    print(f"  Correlacion {VAR1} <-> productivity : {corr_prod_v1:+.4f}")
    print(f"  Correlacion {VAR2} <-> productivity : {corr_prod_v2:+.4f}")

    _, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Izquierda: productividad
    sc1 = axes[0].scatter(
        data[VAR1], data[VAR2],
        c=data["productivity_score"], cmap="RdYlGn",
        alpha=0.3, s=7
    )
    cb1 = plt.colorbar(sc1, ax=axes[0])
    cb1.set_label("productivity_score", fontsize=9)
    axes[0].set_xlabel("study_hours_per_day (h/dia)", fontsize=10)
    axes[0].set_ylabel("phone_usage_hours (h/dia)", fontsize=10)
    axes[0].set_title(
        "Relacion entre las 2 variables clave\n"
        "Verde = alta productividad  |  Rojo = baja"
    )
    axes[0].text(0.7, 11.5,
                 "Poco estudio\nMucho telefono\n-> Baja prod.",
                 fontsize=7.5, color='darkred', ha='left',
                 bbox={'boxstyle': 'round,pad=0.3',
                       'facecolor': '#ffe0e0', 'alpha': 0.8})
    axes[0].text(8.0, 1.2,
                 "Mucho estudio\nPoco telefono\n-> Alta prod.",
                 fontsize=7.5, color='darkgreen', ha='left',
                 bbox={'boxstyle': 'round,pad=0.3',
                       'facecolor': '#e0ffe0', 'alpha': 0.8})

    # Derecha: estres
    sc2 = axes[1].scatter(
        data[VAR1], data[VAR2],
        c=data["stress_level"], cmap="RdYlGn_r",
        alpha=0.3, s=7
    )
    cb2 = plt.colorbar(sc2, ax=axes[1])
    cb2.set_label("stress_level", fontsize=9)
    axes[1].set_xlabel("study_hours_per_day (h/dia)", fontsize=10)
    axes[1].set_ylabel("phone_usage_hours (h/dia)", fontsize=10)
    axes[1].set_title(
        "Relacion entre las 2 variables clave\n"
        "Rojo = alto estres  |  Verde = bajo estres"
    )
    axes[1].text(
        0.5, -0.11,
        f"Correlacion VAR1<->VAR2: {corr_vars:+.4f}  (casi independientes entre si)",
        transform=axes[1].transAxes, ha='center',
        fontsize=8.5, color='gray', style='italic'
    )

    plt.suptitle(
        "Grafico 5 -- Relacion entre horas de estudio y uso del telefono",
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    print("\n  Gradiente de productividad es DIAGONAL en el scatter")
    print("  Ambas variables contribuyen independientemente a la productividad")
    print("  El estres no muestra ningun patron espacial -> es independiente")


# =============================================================================
# VARIACIONES — Scatter con distintas variables de color
# =============================================================================
def plot_scatter_variations(data):
    """
    4 variaciones del scatter VAR1 vs VAR2 coloreadas por distintos indicadores.

    Permite comparar si la zona del espacio (estudio/telefono) se relaciona con:
      - productivity_score : esperado gradiente diagonal verde/rojo
      - focus_score        : los estudiantes que estudian mas, se enfocan mas?
      - sleep_hours        : dormir bien se asocia con mas estudio?
      - final_grade        : la nota final sigue el patron de productividad?

    CONCLUSION esperada:
      productivity_score tiene gradiente claro (corr aprox +0.73 con study_hours)
      final_grade NO muestra patron -> fue generado independientemente en este dataset
    """
    _header("VARIACIONES -- Scatter con distintos indicadores de color")

    color_configs = [
        ("productivity_score", "RdYlGn",  "Verde = alta productividad"),
        ("focus_score",        "YlOrRd",  "Naranja/Rojo = alto enfoque"),
        ("sleep_hours",        "Blues",   "Azul = muchas horas de sueno"),
        ("final_grade",        "RdYlGn",  "Verde = nota alta"),
    ]

    _, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes_flat = axes.flatten()

    for ax, (cvar, cmap, desc) in zip(axes_flat, color_configs):
        corr_val = data[VAR1].corr(data[cvar])
        sc = ax.scatter(
            data[VAR1], data[VAR2],
            c=data[cvar], cmap=cmap,
            alpha=0.3, s=6
        )
        cb = plt.colorbar(sc, ax=ax)
        cb.set_label(cvar, fontsize=8)
        ax.set_xlabel("study_hours_per_day", fontsize=9)
        ax.set_ylabel("phone_usage_hours", fontsize=9)
        ax.set_title(
            f"Color = {cvar}\n{desc}  |  corr con study_hours: {corr_val:+.3f}",
            fontsize=9
        )

    plt.suptitle(
        "Variaciones -- Scatter study_hours vs phone_usage\n"
        "coloreado por distintos indicadores",
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    print("\n  Correlaciones de study_hours_per_day con cada indicador:")
    for cvar, _, _ in color_configs:
        corr_val = data[VAR1].corr(data[cvar])
        print(f"    {cvar:<25} {corr_val:+.4f}")
    print("\n  productivity_score tiene el gradiente mas claro (corr aprox +0.73)")
    print("  final_grade NO muestra patron -> fue generado independientemente")


# =============================================================================
# EJECUTAR TODOS LOS GRAFICOS
# =============================================================================
def plot_all(data):
    """Ejecuta los 5 graficos principales mas las variaciones del scatter."""
    plot_scree_and_loadings(data)
    plot_pca_2d(data)
    plot_parallel_coords(data)
    plot_distributions(data)
    plot_scatter_relation(data)
    plot_scatter_variations(data)


# =============================================================================
# MAIN — ejecutar este modulo directamente
# =============================================================================
if __name__ == "__main__":
    script_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(
        script_path, "data",
        "student_productivity_distraction_dataset_20000.csv"
    )
    dataset = pd.read_csv(csv_path)
    print(f"Dataset cargado: {dataset.shape[0]} estudiantes, "
          f"{dataset.shape[1]} columnas")
    plot_all(dataset)

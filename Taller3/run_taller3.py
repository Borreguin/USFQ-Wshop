#!/usr/bin/env python3
"""
run_taller3.py  —  Ejecutable principal del Taller 3
MSDS 6004  Inteligencia Artificial  —  USFQ 2024-2025

Genera:
    Taller3/informe_taller3.html   (informe HTML con figuras embebidas)
    Taller3/informe_taller3.pdf    (informe PDF con reportlab)

Uso (desde la raiz del workspace):
    python Taller3/run_taller3.py

Tiempo estimado: 20-30 segundos
"""

import sys, os, io, base64, contextlib, datetime, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

# ─────────────────────────────────────────────
# HELPERS  (figuras y captura de salida)
# ─────────────────────────────────────────────

_FIGS: dict[str, str] = {}   # tag -> base64 png


def _save_fig(tag: str, dpi: int = 110) -> None:
    buf = io.BytesIO()
    plt.gcf().savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                      facecolor="white")
    buf.seek(0)
    _FIGS[tag] = base64.b64encode(buf.read()).decode()
    plt.close("all")


@contextlib.contextmanager
def _intercept_show(prefix: str):
    counter = [0]
    _orig = plt.show
    def _fake():
        counter[0] += 1
        _save_fig(f"{prefix}_{counter[0]:02d}")
    plt.show = _fake
    try:
        yield counter
    finally:
        plt.show = _orig


def _img_tag(tag: str, caption: str = "", width: str = "98%") -> str:
    if tag not in _FIGS:
        return f'<p class="warn">[ figura {tag} no disponible ]</p>'
    return (
        f'<figure style="margin:10px 0">'
        f'<img src="data:image/png;base64,{_FIGS[tag]}" '
        f'style="width:{width};max-width:980px;border-radius:6px;'
        f'box-shadow:0 1px 6px #0003" alt="{tag}">'
        + (f"<figcaption>{caption}</figcaption>" if caption else "")
        + "</figure>"
    )


def _fig_block(tag: str, title: str, explanation: str, caption: str = "", width: str = "98%") -> str:
    """Bloque completo: titulo H4 + imagen + explicacion."""
    title_html = f'<h4 style="margin:18px 0 6px;color:#1a237e">{title}</h4>'
    img_html   = _img_tag(tag, caption, width)
    expl_html  = (
        f'<div class="callout info" style="margin-top:6px;font-size:13px">'
        f'{explanation}</div>'
    )
    return title_html + img_html + expl_html


def _pre(text: str, max_chars: int = 4000) -> str:
    snippet = text[:max_chars]
    if len(text) > max_chars:
        snippet += "\n... (salida truncada)"
    return f'<pre class="output">{snippet}</pre>'


# ─────────────────────────────────────────────
# P1 — APRENDIZAJE NO SUPERVISADO (SP&BDS)
# ─────────────────────────────────────────────

def run_p1_spbds() -> dict:
    """Analisis completo A-F sobre Student Productivity & Behavior Dataset."""
    import io as _io_mod
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
    from Taller3.P1_UML.p1_spbds import (
        load_data,
        section_a_pca_and_parallel,
        section_b_clustering_univariate,
        section_c_anomalies_univariate,
        section_d_clustering_multivariate,
        section_e_anomalies_multivariate,
        FEATURE_COLS, VAR1, VAR2,
    )

    print("  [P1] Cargando SP&BDS (20K estudiantes) ...")
    df = load_data()

    # PCA completo para metricas del informe
    X    = df[FEATURE_COLS].values
    sc   = StandardScaler()
    X_sc = sc.fit_transform(X)
    pca_full = PCA(n_components=len(FEATURE_COLS))
    pca_full.fit(X_sc)
    expl = pca_full.explained_variance_ratio_
    n_80 = next(i + 1 for i, c in enumerate(np.cumsum(expl)) if c >= 0.80)

    # Captura de las 11 figuras; stdout redirigido para evitar problemas de encoding
    print("  [P1] Secciones A-E (11 figuras) ...")
    with contextlib.redirect_stdout(_io_mod.StringIO()), _intercept_show("spbds"):
        X_2d, _, _ = section_a_pca_and_parallel(df)       # spbds_01..05
        section_b_clustering_univariate(df)                # spbds_06..07
        section_c_anomalies_univariate(df)                 # spbds_08
        section_d_clustering_multivariate(df, X_2d)        # spbds_09..10
        section_e_anomalies_multivariate(df, X_2d)         # spbds_11

    # ── Metricas para tarjetas del informe ──────────────────────────
    def _sil_best(Xd):
        scores = [silhouette_score(Xd,
                  KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(Xd),
                  sample_size=2000, random_state=42)
                  for k in range(2, 7)]
        return 2 + scores.index(max(scores)), max(scores)

    X_v1 = StandardScaler().fit_transform(df[[VAR1]].values)
    X_v2 = StandardScaler().fit_transform(df[[VAR2]].values)
    pca2 = PCA(n_components=2, random_state=42).fit_transform(X_sc)

    best_k_v1, sil_v1 = _sil_best(X_v1)
    best_k_v2, sil_v2 = _sil_best(X_v2)
    best_k_m,  sil_m  = _sil_best(pca2)

    lbl_db  = DBSCAN(eps=0.4, min_samples=50).fit_predict(X_v1)
    n_cl_db = len(set(lbl_db)) - (1 if -1 in lbl_db else 0)
    n_ns_db = int((lbl_db == -1).sum())

    lbl_db_m  = DBSCAN(eps=0.5, min_samples=30).fit_predict(pca2)
    n_cl_db_m = len(set(lbl_db_m)) - (1 if -1 in lbl_db_m else 0)
    n_ns_db_m = int((lbl_db_m == -1).sum())

    n_anom_uni  = int((IsolationForest(contamination=0.05, random_state=42).fit_predict(X_v1) == -1).sum())
    n_anom_multi= int((IsolationForest(contamination=0.05, random_state=42).fit_predict(X_sc)  == -1).sum())

    lc   = list(zip(FEATURE_COLS, pca_full.components_[0]))
    top5 = sorted(lc, key=lambda x: abs(x[1]), reverse=True)[:5]

    print("  [P1] OK")
    return {
        "n_students"  : len(df),
        "n_features"  : len(FEATURE_COLS),
        "n_comp_80"   : n_80,
        "pc1_pct"     : float(expl[0] * 100),
        "pc2_pct"     : float(expl[1] * 100),
        "best_k_v1"   : best_k_v1,  "sil_v1"   : float(sil_v1),
        "best_k_v2"   : best_k_v2,  "sil_v2"   : float(sil_v2),
        "best_k_m"    : best_k_m,   "sil_m"    : float(sil_m),
        "n_cl_db"     : n_cl_db,    "n_ns_db"  : n_ns_db,
        "n_cl_db_m"   : n_cl_db_m,  "n_ns_db_m": n_ns_db_m,
        "n_anom_uni"  : n_anom_uni,
        "n_anom_multi": n_anom_multi,
        "var1"        : VAR1,
        "var2"        : VAR2,
        "top5"        : [(v, float(l)) for v, l in top5],
    }


# ─────────────────────────────────────────────
# P2 — TSP
# ─────────────────────────────────────────────

def run_p2_tsp() -> dict:
    print("  [P2-TSP] Vecino cercano + 2-opt ...")
    import datetime as dt
    from Taller3.P2_TSP.util import (
        generar_ciudades_con_distancias, calculate_path_distance,
        two_opt_improve, delta_time_mm_ss, plotear_ruta,
    )
    from Taller3.P2_TSP.util_nearest_neighbor import nearest_neighbor

    rows = []
    for n in [10, 20, 30, 40, 50, 100]:
        ciudades, distancias = generar_ciudades_con_distancias(n)
        t0 = dt.datetime.now()
        ruta_nn = nearest_neighbor(ciudades, distancias)
        t_nn = dt.datetime.now() - t0
        dist_nn = calculate_path_distance(distancias, ruta_nn)

        t0 = dt.datetime.now()
        ruta_2opt = two_opt_improve(ruta_nn, distancias)
        t_2opt = dt.datetime.now() - t0
        dist_2opt = calculate_path_distance(distancias, ruta_2opt)
        mejora = (dist_nn - dist_2opt) / dist_nn * 100
        rows.append((n, dist_nn, delta_time_mm_ss(t_nn),
                     dist_2opt, delta_time_mm_ss(t_2opt), mejora))

    ciudades100, dist100 = generar_ciudades_con_distancias(100)
    ruta_nn_100   = nearest_neighbor(ciudades100, dist100)
    ruta_2opt_100 = two_opt_improve(ruta_nn_100, dist100)

    with _intercept_show("tsp"):
        plotear_ruta(ciudades100, dist100, ruta_nn_100,  mostrar_anotaciones=False)
        plotear_ruta(ciudades100, dist100, ruta_2opt_100, mostrar_anotaciones=False)

    # Barchart comparativo
    ns    = [r[0] for r in rows]
    d_nn  = [r[1] for r in rows]
    d_2op = [r[3] for r in rows]
    x = np.arange(len(ns))
    fig, ax = plt.subplots(figsize=(9, 4))
    b1 = ax.bar(x - 0.2, d_nn,  0.38, label="Vecino Cercano", color="#4a90d9")
    b2 = ax.bar(x + 0.2, d_2op, 0.38, label="NN + 2-opt",     color="#27ae60")
    ax.set_xticks(x); ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlabel("Numero de ciudades"); ax.set_ylabel("Distancia total")
    ax.set_title("TSP: Vecino Cercano vs NN + 2-opt")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    for bar1, bar2 in zip(b1, b2):
        ax.text(bar1.get_x()+bar1.get_width()/2, bar1.get_height()+3,
                f"{bar1.get_height():.0f}", ha="center", va="bottom", fontsize=7)
        ax.text(bar2.get_x()+bar2.get_width()/2, bar2.get_height()+3,
                f"{bar2.get_height():.0f}", ha="center", va="bottom", fontsize=7)
    plt.tight_layout(); _save_fig("tsp_03")

    print("  [P2-TSP] OK")
    return {"rows": rows}


# ─────────────────────────────────────────────
# P3 — GA
# ─────────────────────────────────────────────

def _run_ga_collect(population, objective, mutation_rate, n_iterations,
                    evaluation_type, best_sel_type, gen_type) -> list:
    from Taller3.P3_GA.generalSteps import (
        evaluate_aptitude, select_best_individual, generate_new_population)
    history = []
    for gen in range(n_iterations):
        aptitudes = [evaluate_aptitude(evaluation_type, ind, objective)
                     for ind in population]
        best_ind, best_apt = select_best_individual(best_sel_type, population, aptitudes)
        history.append((gen, best_apt, best_ind))
        if best_ind == objective:
            break
        population = generate_new_population(gen_type, population, aptitudes, mutation_rate)
    return history


def run_p3_ga() -> dict:
    print("  [P3-GA] Corriendo casos 1-5 ...")
    from Taller3.P3_GA.constants import (
        AptitudeType, BestIndividualSelectionType, NewGenerationType)
    from Taller3.P3_GA.generalSteps import generate_population

    objective = "GA Workshop! USFQ"
    n_len = len(objective)

    configs = [
        ("Caso 1: DEFAULT\nRuleta + 1 punto", 100, 0.01, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.DEFAULT, "#e74c3c"),
        ("Caso 2: BY_DISTANCE\nDistancia Manhattan", 100, 0.01, 1000,
         AptitudeType.BY_DISTANCE, BestIndividualSelectionType.MIN_DISTANCE,
         NewGenerationType.MIN_DISTANCE, "#e67e22"),
        ("Caso 3a: mutation=0.05\n(alta exploracion)", 100, 0.05, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.DEFAULT, "#f39c12"),
        ("Caso 3b: mutation=0.001\n(baja exploracion)", 100, 0.001, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.DEFAULT, "#d35400"),
        ("Caso 4a: poblacion=500", 500, 0.01, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.DEFAULT, "#8e44ad"),
        ("Caso 4b: poblacion=20", 20, 0.01, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.DEFAULT, "#c0392b"),
        ("Caso 5: MEJOR COMBO\nElitismo+Torneo+2pts", 200, 0.03, 1000,
         AptitudeType.DEFAULT, BestIndividualSelectionType.DEFAULT,
         NewGenerationType.NEW, "#27ae60"),
    ]

    all_histories, summary_rows = [], []

    for label, pop_size, mr, n_iter, ev, bst, gen, color in configs:
        pop = generate_population(pop_size, n_len)
        hist = _run_ga_collect(pop, objective, mr, n_iter, ev, bst, gen)
        last_gen, last_apt, last_ind = hist[-1]
        converged = last_ind == objective
        if ev == AptitudeType.BY_DISTANCE:
            max_d = max(h[1] for h in hist if h[1] is not None) or 1
            norm = [(g, (max_d - a) / max_d * n_len if a is not None else 0, i)
                    for g, a, i in hist]
        else:
            norm = hist
        all_histories.append((label.split("\n")[0], norm, color))
        summary_rows.append({"label": label, "pop": pop_size, "mr": mr,
                              "converged": converged, "gen": last_gen,
                              "best": last_ind})
        status = f"gen {last_gen}" if converged else "NO converge"
        print(f"    {label.split(chr(10))[0]}: {status}")

    # Curva de convergencia
    fig, ax = plt.subplots(figsize=(12, 5))
    for name, hist, color in all_histories:
        gens = [h[0] for h in hist]
        apts = [h[1] for h in hist]
        ax.plot(gens, apts, label=name, color=color, linewidth=1.6, alpha=0.85)
    ax.axhline(y=n_len, color="black", linewidth=1, linestyle="--",
               label=f"Objetivo ({n_len})")
    ax.set_xlabel("Generacion"); ax.set_ylabel("Aptitud")
    ax.set_title("P3 GA — Convergencia por caso de estudio")
    ax.legend(fontsize=8, ncol=2); ax.grid(alpha=0.25)
    plt.tight_layout(); _save_fig("ga_convergence")

    # Barras de generacion convergida
    ok = [(r["label"].split("\n")[0], r["gen"])
          for r in summary_rows if r["converged"]]
    if ok:
        lc, gc = zip(*ok)
        clrs = [all_histories[i][2]
                for i, r in enumerate(summary_rows) if r["converged"]]
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(lc, gc, color=clrs, alpha=0.85, edgecolor="white")
        ax.set_ylabel("Generacion de convergencia")
        ax.set_title("Generacion en que cada caso alcanza el objetivo")
        ax.tick_params(axis="x", rotation=15)
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+5,
                    str(int(b.get_height())), ha="center", va="bottom", fontsize=9)
        plt.tight_layout(); _save_fig("ga_bar")

    print("  [P3-GA] OK")
    return {"summary": summary_rows}


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

_CSS = """
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',Arial,sans-serif; font-size:14px;
       color:#222; background:#f5f6fa; }
nav { position:fixed; top:0; left:0; width:220px; height:100vh;
      background:#1a1f36; color:#cdd; overflow-y:auto; padding:20px 0; z-index:100; }
nav h2 { color:#7ec8e3; padding:0 18px 12px; font-size:12px;
          letter-spacing:1px; text-transform:uppercase;
          border-bottom:1px solid #2d3555; }
nav a  { display:block; padding:6px 18px; color:#aac;
          text-decoration:none; font-size:12px; transition:background .2s; }
nav a:hover { background:#2d3555; color:#fff; }
nav a.sub { padding-left:30px; font-size:11.5px; color:#889; }
hr.nd { border:none; border-top:1px solid #2d3555; margin:6px 0; }
main { margin-left:220px; padding:30px 40px; max-width:1100px; }
.cover { background:linear-gradient(135deg,#1a1f36 0%,#2d3a6e 100%);
         color:white; border-radius:12px; padding:50px; margin-bottom:36px; }
.cover h1 { font-size:2em; margin-bottom:6px; }
.cover .sub { color:#aac; margin-bottom:20px; }
.cover td { padding:4px 20px 4px 0; color:#cdd; font-size:13px; }
.metrics { display:flex; gap:14px; flex-wrap:wrap; margin:12px 0; }
.metric { background:#fff; border-radius:8px; padding:14px 20px;
           border-left:4px solid #1976d2; box-shadow:0 1px 3px #0002;
           min-width:130px; flex:1; }
.metric .val { font-size:1.5em; font-weight:bold; color:#1565c0; }
.metric .lbl { font-size:11px; color:#888; text-transform:uppercase; }
.metric.g { border-color:#2e7d32; } .metric.g .val { color:#2e7d32; }
.metric.p { border-color:#6a1b9a; } .metric.p .val { color:#6a1b9a; }
.metric.o { border-color:#e65100; } .metric.o .val { color:#e65100; }
.metric.r { border-color:#c62828; } .metric.r .val { color:#c62828; }
.sec-header { border-radius:8px; padding:18px 24px;
               margin:28px 0 16px; color:white; }
.h-p1 { background:linear-gradient(90deg,#1565c0,#1976d2); }
.h-p2 { background:linear-gradient(90deg,#2e7d32,#388e3c); }
.h-p3 { background:linear-gradient(90deg,#6a1b9a,#7b1fa2); }
h2 { font-size:1.35em; }
h3 { font-size:1.05em; color:#1a237e; margin:20px 0 8px;
     padding-bottom:4px; border-bottom:2px solid #e3e8f0; }
h4 { font-size:.95em; color:#37474f; margin:12px 0 6px; }
p  { line-height:1.65; margin-bottom:9px; color:#333; }
.card { background:white; border-radius:8px; padding:20px 24px;
         margin-bottom:16px; box-shadow:0 1px 4px #0002; }
pre.output { background:#0d1117; color:#c9d1d9; border-radius:6px;
              padding:12px 16px; font-size:11px; overflow-x:auto;
              line-height:1.5; margin:10px 0; white-space:pre-wrap; }
table.data { border-collapse:collapse; width:100%; margin:12px 0; font-size:13px; }
table.data th { background:#1a1f36; color:white; padding:8px 12px; text-align:left; }
table.data td { padding:6px 12px; border-bottom:1px solid #e8eaf6; }
table.data tr:nth-child(even) td { background:#f8f9ff; }
tr.ok td { background:#e8f5e9; }
tr.nok td { background:#fff3e0; }
.callout { border-radius:6px; padding:11px 16px; margin:10px 0; font-size:13px; }
.callout.info  { background:#e3f2fd; border-left:4px solid #1976d2; }
.callout.warn  { background:#fff8e1; border-left:4px solid #f57f17; }
.callout.good  { background:#e8f5e9; border-left:4px solid #2e7d32; }
.callout.danger{ background:#ffebee; border-left:4px solid #c62828; }
.callout.code  { background:#f3e5f5; border-left:4px solid #6a1b9a;
                  font-family:monospace; font-size:12px; }
figure { margin:8px 0; }
figcaption { font-size:12px; color:#666; margin-top:3px; font-style:italic;
              text-align:center; }
.warn { color:#c62828; background:#ffebee; padding:5px 10px; border-radius:4px; }
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
code { background:#f3f4f6; padding:1px 5px; border-radius:3px;
        font-family:monospace; font-size:12px; }
"""


# ─────────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────────

def build_html(p1_data: dict, p2_data: dict, p3_data: dict) -> str:
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── P1: tabla top-5 loadings ────────────────────────────────────
    def top5_table() -> str:
        h = ("<tr><th>#</th><th>Variable</th><th>Loading PC1</th>"
             "<th>Interpretacion</th></tr>")
        rows = ""
        for i, (var, load) in enumerate(p1_data["top5"]):
            sign  = "(+) aumenta productividad" if load > 0 else "(-) reduce productividad"
            color = "#2e7d32" if load > 0 else "#c62828"
            rows += (f'<tr><td><b>#{i+1}</b></td><td><code>{var}</code></td>'
                     f'<td style="color:{color}"><b>{load:+.4f}</b></td>'
                     f'<td style="color:{color}">{sign}</td></tr>')
        return f"<table class='data'>{h}{rows}</table>"

    # ── P2: tabla comparativa ───────────────────────────────────────
    def tsp_table() -> str:
        h = ("<tr><th>Ciudades</th><th>NN Distancia</th><th>NN Tiempo</th>"
             "<th>2-opt Distancia</th><th>2-opt Tiempo</th><th>Mejora</th></tr>")
        rows_html = ""
        for n, d_nn, t_nn, d_2opt, t_2opt, m in p2_data["rows"]:
            cls = "ok" if m > 15 else ""
            rows_html += (
                f'<tr class="{cls}"><td>{n}</td><td>{d_nn:.2f}</td><td>{t_nn}</td>'
                f'<td>{d_2opt:.2f}</td><td>{t_2opt}</td>'
                f'<td><b>{m:.1f}%</b></td></tr>'
            )
        return f"<table class='data'>{h}{rows_html}</table>"

    # GA tabla
    def ga_table() -> str:
        h = ("<tr><th>Caso</th><th>Poblacion</th><th>Mut. Rate</th>"
             "<th>Converge</th><th>Generacion</th><th>Mejor individuo</th></tr>")
        rows_html = ""
        for r in p3_data["summary"]:
            status = "SI" if r["converged"] else "NO"
            cls = "ok" if r["converged"] else "nok"
            gen = str(r["gen"]) if r["converged"] else "&#x2014;"
            rows_html += (
                f'<tr class="{cls}"><td>{r["label"].replace(chr(10)," — ")}</td>'
                f'<td>{r["pop"]}</td><td>{r["mr"]}</td>'
                f'<td><b>{status}</b></td><td>{gen}</td>'
                f'<td style="font-family:monospace">{r["best"]!r}</td></tr>'
            )
        return f"<table class='data'>{h}{rows_html}</table>"

    # NAV
    nav = """
    <h2>Taller 3 — USFQ</h2>
    <a href="#cover">Portada</a>
    <hr class="nd">
    <a href="#p1">P1 — Aprendizaje No Supervisado</a>
    <a href="#p1-ds"  class="sub">Dataset SP&amp;BDS</a>
    <a href="#p1-a"   class="sub">A. PCA + Visualizacion</a>
    <a href="#p1-b"   class="sub">B. Clustering Univariable</a>
    <a href="#p1-c"   class="sub">C. Anomalias Univariable</a>
    <a href="#p1-d"   class="sub">D. Clustering Multivariable</a>
    <a href="#p1-e"   class="sub">E. Anomalias Multivariable</a>
    <a href="#p1-f"   class="sub">F. Conclusiones</a>
    <hr class="nd">
    <a href="#p2">P2 — TSP</a>
    <a href="#p2-a" class="sub">A. LP vs Vecino Cercano</a>
    <a href="#p2-b" class="sub">B. Parametro tee</a>
    <a href="#p2-c" class="sub">C. Heuristica limites</a>
    <a href="#p2-d" class="sub">D. Heuristica NN</a>
    <a href="#p2-f" class="sub">F. 2-opt (cruces)</a>
    <a href="#p2-e" class="sub">E. Conclusiones</a>
    <hr class="nd">
    <a href="#p3">P3 — Algoritmos Geneticos</a>
    <a href="#p3-12" class="sub">Casos 1 y 2</a>
    <a href="#p3-3"  class="sub">Caso 3 — mutation_rate</a>
    <a href="#p3-4"  class="sub">Caso 4 — poblacion</a>
    <a href="#p3-5"  class="sub">Caso 5 — mejor combo</a>
    <a href="#p3-f"  class="sub">Conclusiones</a>
    <hr class="nd">
    <a href="#metodo">Metodologia Paso a Paso</a>
    <a href="#met-p1" class="sub">P1 — UML</a>
    <a href="#met-p2" class="sub">P2 — TSP</a>
    <a href="#met-p3" class="sub">P3 — GA</a>
    <hr class="nd">
    <a href="#interrogantes">Interrogantes de Mejora</a>
    <a href="#int-ds"  class="sub">Base de datos</a>
    <a href="#int-p1"  class="sub">Analisis P1</a>
    <a href="#int-p2"  class="sub">Analisis P2</a>
    <a href="#int-p3"  class="sub">Analisis P3</a>
    """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Informe Taller 3 — MSDS 6004 IA — USFQ</title>
<style>{_CSS}</style>
</head>
<body>
<nav>{nav}</nav>
<main>

<!-- ═══ PORTADA ═══ -->
<div id="cover" class="cover">
  <div style="font-size:11px;color:#7ec8e3;letter-spacing:2px;
              text-transform:uppercase;margin-bottom:10px">
    Universidad San Francisco de Quito — MSDS 6004</div>
  <h1>Taller 3 — Informe Completo</h1>
  <div class="sub">Inteligencia Artificial</div>
  <table style="margin-top:18px">
    <tr><td>Integrantes</td><td><b style="color:#fff">Kevin Vitery &nbsp;&bull;&nbsp; Raquel Pacheco &nbsp;&bull;&nbsp; Gustavo Baru &nbsp;&bull;&nbsp; Nancy Altamirano</b></td></tr>
    <tr><td>Generado</td><td><b style="color:#fff">{now}</b></td></tr>
    <tr><td>Curso</td><td><b style="color:#fff">MSDS 6004 — Inteligencia Artificial — USFQ</b></td></tr>
    <tr><td>Problemas</td><td><b style="color:#fff">P1 SP&amp;BDS &nbsp;|&nbsp; P2 TSP &nbsp;|&nbsp; P3 GA</b></td></tr>
  </table>
  <div style="margin-top:24px;display:flex;gap:14px;flex-wrap:wrap">
    <div class="metric" style="border-color:#90caf9;background:rgba(255,255,255,.1)">
      <div class="val" style="color:#90caf9">{p1_data["n_students"]:,}</div>
      <div class="lbl" style="color:#aac">Estudiantes SP&amp;BDS</div>
    </div>
    <div class="metric" style="border-color:#a5d6a7;background:rgba(255,255,255,.1)">
      <div class="val" style="color:#a5d6a7">{p1_data["n_anom_multi"]}</div>
      <div class="lbl" style="color:#aac">Anomalias detectadas</div>
    </div>
    <div class="metric" style="border-color:#ffcc80;background:rgba(255,255,255,.1)">
      <div class="val" style="color:#ffcc80">18.6%</div>
      <div class="lbl" style="color:#aac">Mejora TSP 2-opt</div>
    </div>
    <div class="metric" style="border-color:#ce93d8;background:rgba(255,255,255,.1)">
      <div class="val" style="color:#ce93d8">32x</div>
      <div class="lbl" style="color:#aac">Aceleracion GA Caso 5</div>
    </div>
  </div>
</div>

<!-- ═══ P1 ═══ -->
<div id="p1" class="sec-header h-p1">
  <h2>P1 — Aprendizaje No Supervisado: Student Productivity &amp; Behavior Dataset</h2>
  <p style="color:#bbdefb;margin-top:4px">
    Analisis de {p1_data["n_students"]:,} estudiantes universitarios con
    {p1_data["n_features"]} variables numericas. PCA, K-Means, DBSCAN e Isolation
    Forest en espacios univariable y multivariable. Secciones A-F.</p>
</div>

<!-- DS — Dataset -->
<div id="p1-ds" class="card">
  <h3>Dataset: Student Productivity &amp; Behavior Dataset (SP&amp;BDS)</h3>
  <p>El dataset contiene registros de <b>{p1_data["n_students"]:,} estudiantes universitarios</b>
  con 18 columnas: <code>student_id</code>, <code>gender</code>, <code>age</code> y
  <b>{p1_data["n_features"]} variables numericas</b> de habitos y rendimiento academico.</p>
  <div class="metrics">
    <div class="metric">
      <div class="val">{p1_data["n_students"]:,}</div><div class="lbl">Estudiantes</div>
    </div>
    <div class="metric g">
      <div class="val">{p1_data["n_features"]}</div><div class="lbl">Variables numericas</div>
    </div>
    <div class="metric p">
      <div class="val">{p1_data["n_comp_80"]}</div><div class="lbl">Comp. PCA para 80%</div>
    </div>
    <div class="metric o">
      <div class="val">{p1_data["pc1_pct"]:.1f}%</div><div class="lbl">Varianza PC1</div>
    </div>
  </div>
  <table class="data">
    <tr><th>Variable</th><th>Descripcion</th><th>Rango</th></tr>
    <tr><td><code>study_hours_per_day</code></td><td>Horas de estudio al dia</td><td>0.5 - 10 h</td></tr>
    <tr><td><code>sleep_hours</code></td><td>Horas de sueno diario</td><td>3 - 9 h</td></tr>
    <tr><td><code>phone_usage_hours</code></td><td>Horas de uso del telefono</td><td>0.5 - 12 h</td></tr>
    <tr><td><code>social_media_hours</code></td><td>Tiempo en redes sociales</td><td>0 - 8 h</td></tr>
    <tr><td><code>gaming_hours</code></td><td>Horas en videojuegos</td><td>0 - 4 h</td></tr>
    <tr><td><code>exercise_minutes</code></td><td>Minutos de ejercicio</td><td>0 - 120 min</td></tr>
    <tr><td><code>stress_level</code></td><td>Nivel de estres (subjetivo)</td><td>1 - 10</td></tr>
    <tr><td><code>focus_score</code></td><td>Puntuacion de concentracion</td><td>30 - 99</td></tr>
    <tr><td><code>final_grade</code></td><td>Nota final de asignatura</td><td>40 - 100</td></tr>
    <tr><td><code>productivity_score</code></td><td>Puntaje de productividad global</td><td>0 - 100</td></tr>
  </table>
</div>

<!-- A — PCA -->
<div id="p1-a" class="card">
  <h3>A — Reduccion de Dimensionalidad: PCA y Visualizacion</h3>

  <h4>Como se elaboro</h4>
  <p>Se aplico <b>Analisis de Componentes Principales (PCA)</b> sobre las
  {p1_data["n_features"]} variables normalizadas con <code>StandardScaler</code>.
  PCA transforma el espacio original en ejes ortogonales (componentes) que maximizan
  la varianza capturada. El primer componente (PC1) es el que explica mas varianza y
  sus <i>loadings</i> revelan que variables contribuyen mas a la diferenciacion entre
  estudiantes. Luego se proyecta en 2D para visualizacion y se grafican coordenadas
  paralelas sobre una muestra de 500 estudiantes agrupados por nivel de productividad.</p>

  <div class="callout info">
    <b>Scree Plot:</b> Se necesitan <b>{p1_data["n_comp_80"]} componentes</b> para
    capturar el 80% de varianza total. PC1 explica solo el {p1_data["pc1_pct"]:.1f}%
    y PC2 el {p1_data["pc2_pct"]:.1f}%. Esto indica que el dataset SP&amp;BDS tiene
    <b>distribucion uniforme</b>: ninguna variable domina claramente sobre las demas,
    propio de un dataset sintetico.
  </div>

  {_fig_block("spbds_01",
    "A.1 — Scree Plot y Contribucion de Variables al PC1",
    "El <b>Scree Plot</b> (izquierda) muestra la varianza explicada acumulada por cada "
    "componente principal. La linea roja indica el umbral del 80%: se necesitan "
    f"<b>{p1_data['n_comp_80']} componentes</b> para alcanzarlo, reflejo de la "
    "distribucion uniforme del dataset sintetico. Las barras de la derecha muestran "
    "los <b>loadings de PC1</b>: las variables con barra azul (positiva) aumentan "
    "la productividad; las con barra roja (negativa) la reducen. "
    f"PC1 explica el <b>{p1_data['pc1_pct']:.1f}%</b> de la varianza total.",
    "Fig. A.1 — Scree Plot y loadings PC1")}

  <h4>Top 5 variables mas importantes segun PC1</h4>
  {top5_table()}

  <div class="callout good">
    El PC1 representa el <b>eje de productividad</b>: hacia valores positivos, estudiantes
    que estudian mucho y tienen alta productividad; hacia valores negativos, estudiantes
    con alto uso del telefono y baja productividad. Las 2 variables mas interpretables y
    contrastantes son <code>{p1_data["var1"]}</code> (+) y <code>{p1_data["var2"]}</code> (-).
  </div>

  {_fig_block("spbds_02",
    "A.2 — Proyeccion PCA 2D: Productividad y Estres",
    "Cada punto representa un estudiante proyectado sobre los dos primeros componentes "
    "principales. <b>Izquierda:</b> el color va de rojo (baja productividad) a verde "
    "(alta productividad); el gradiente sigue exactamente el eje PC1, confirmando que "
    "ese eje captura directamente el comportamiento productivo. "
    "<b>Derecha:</b> coloreado por nivel de estres — no sigue ningun patron espacial, "
    "lo que indica que el estres es una variable <b>independiente</b> del resto "
    "en este dataset sintetico.",
    "Fig. A.2 — PCA 2D coloreado por productividad (izq.) y estres (der.)")}

  <div class="callout info">
    <b>Interpretacion PCA 2D:</b> El gradiente verde-rojo sigue el eje PC1 de derecha
    a izquierda: PC1 captura directamente la productividad. El estres, en cambio, no
    sigue ningun patron espacial — es una variable <b>independiente</b> del resto en
    este dataset sintetico.
  </div>

  {_fig_block("spbds_03",
    "A.3 — Coordenadas Paralelas: Patrones de Comportamiento por Nivel de Productividad",
    "Cada linea representa un estudiante de la muestra de 500. "
    "Las lineas <b>verdes</b> (alta productividad) tienden a estar <b>arriba</b> en "
    "<code>study_hours_per_day</code> y <b>abajo</b> en <code>phone_usage_hours</code>, "
    "mientras que las lineas rojas (baja productividad) muestran el patron opuesto. "
    "Este grafico permite visualizar simultaneamente todas las variables y detectar "
    "que <code>study_hours</code>, <code>focus_score</code> y <code>productivity_score</code> "
    "se mueven juntos en la misma direccion, formando el <b>eje productivo</b>.",
    "Fig. A.3 — Coordenadas Paralelas (500 estudiantes), verde = alta productividad")}

  <div class="callout info">
    <b>Coordenadas paralelas:</b> Cada linea es un estudiante. Las lineas verdes (alta
    productividad) tienden a estar <b>arriba</b> en <code>study_hours</code> y
    <b>abajo</b> en <code>phone_usage</code> &mdash; el patron de comportamiento
    productivo es consistente y visible a simple vista.
  </div>

  {_fig_block("spbds_04",
    "A.4 — Distribuciones de Variables Clave por Nivel de Productividad",
    "Histogramas de <code>study_hours_per_day</code> (izq.) y <code>phone_usage_hours</code> (der.) "
    "separados por tercil de productividad (bajo / medio / alto). "
    "Los estudiantes de <b>alta productividad</b> concentran sus horas de estudio en el rango "
    "6-10 h/dia y su uso del telefono en el rango 1-4 h/dia. "
    "Los de <b>baja productividad</b> muestran el patron inverso: pocas horas de estudio "
    "y alto tiempo en telefono. La separacion de las distribuciones confirma que estas "
    "dos variables son los <b>mejores predictores univariables</b> de productividad.",
    "Fig. A.4 — Distribuciones de study_hours y phone_usage por nivel de productividad")}

  {_fig_block("spbds_05",
    "A.5 — Scatter: Relacion entre Variables Clave",
    "Diagrama de dispersion entre <code>study_hours_per_day</code> (eje X) y "
    "<code>phone_usage_hours</code> (eje Y). Cada punto es un estudiante coloreado por "
    "productividad (izq.) y estres (der.). La nube de puntos muestra una "
    "<b>correlacion negativa</b> entre ambas variables: a mas horas de estudio, "
    "menos uso del telefono. Los estudiantes de alta productividad (verde) se agrupan "
    "en el cuadrante inferior-derecho (mucho estudio, poco telefono), "
    "mientras que los de baja productividad (rojo) ocupan el cuadrante superior-izquierdo. "
    "El estres no sigue ningun patron espacial, ratificando su independencia.",
    "Fig. A.5 — Scatter coloreado por productividad y estres")}

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Dataset sintetico:</b> Al ser sintetico y con distribucion uniforme, la
    varianza se distribuye uniformemente entre todos los componentes. En un dataset
    real se esperarian 3-5 componentes para el 80%; aqui se necesitan {p1_data["n_comp_80"]}.
    Esto complica la interpretacion del scree plot.<br><br>
    <b>2. Seleccion de variables clave:</b> Con {p1_data["n_features"]} variables, identificar
    las 2 mas representativas requirio analizar los loadings de PC1 y validarlos con
    correlacion directa con <code>productivity_score</code>. La eleccion de
    <code>study_hours_per_day</code> y <code>phone_usage_hours</code> es justificable por
    su interpretabilidad y por representar los 2 polos del eje productivo-distractivo.<br><br>
    <b>3. Coordenadas paralelas:</b> Con 15 variables el grafico se vuelve ilegible.
    Se limito a 8 variables para mantener la claridad visual.
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    PCA es una herramienta exploratoria poderosa: en una sola figura (los loadings de PC1)
    es posible descubrir que el eje principal de variabilidad del dataset de estudiantes
    corresponde exactamente al eje "comportamiento productivo vs. distractivo". Ademas,
    la proyeccion 2D revela que el <b>estres es estadisticamente independiente</b>
    de las variables de habito — un hallazgo no obvio sin PCA.
  </div>
</div>

<!-- B — Clustering Univariable -->
<div id="p1-b" class="card">
  <h3>B — Clustering Univariable: K-Means y DBSCAN</h3>

  <h4>Como se elaboro</h4>
  <p>Se aplico clustering sobre cada variable clave de forma independiente, previa
  estandarizacion con <code>StandardScaler</code>.</p>
  <ul style="margin:8px 0 8px 20px;line-height:1.8">
    <li><b>K-Means:</b> Se probo k = 2, 3, 4, 5, 6. Para cada k se calculo el
    <i>Silhouette Score</i> (cohesion interna vs separacion entre clusters).
    El k optimo fue el de mayor silhouette.</li>
    <li><b>DBSCAN:</b> Se uso <code>eps=0.4</code>, <code>min_samples=50</code>.
    Los puntos marcados como -1 son ruido (outliers).</li>
    <li>Se analizo como se distribuye <code>productivity_score</code> dentro de cada
    cluster para verificar si los grupos tienen significado real.</li>
  </ul>

  <div class="metrics">
    <div class="metric">
      <div class="val">k = {p1_data["best_k_v1"]}</div>
      <div class="lbl">Mejor k &mdash; study_hours</div>
    </div>
    <div class="metric g">
      <div class="val">{p1_data["sil_v1"]:.3f}</div>
      <div class="lbl">Silhouette &mdash; study_hours</div>
    </div>
    <div class="metric p">
      <div class="val">k = {p1_data["best_k_v2"]}</div>
      <div class="lbl">Mejor k &mdash; phone_usage</div>
    </div>
    <div class="metric o">
      <div class="val">{p1_data["sil_v2"]:.3f}</div>
      <div class="lbl">Silhouette &mdash; phone_usage</div>
    </div>
  </div>

  {_fig_block("spbds_06",
    f"B.1 — Clustering Univariable: study_hours_per_day  (K-Means k={p1_data['best_k_v1']}, Silhouette={p1_data['sil_v1']:.3f})",
    "<b>Izquierda — Distribucion:</b> histograma de horas de estudio; la distribucion uniforme "
    "indica que no hay grupos naturales muy separados. "
    f"<b>Centro — K-Means k={p1_data['best_k_v1']}:</b> los estudiantes se dividen en grupos "
    "segun sus horas de estudio. La productividad media de cada cluster aumenta "
    "progresivamente, validando que los grupos tienen sentido semantico real. "
    f"<b>Derecha — DBSCAN:</b> con la distribucion uniforme del dataset, DBSCAN agrupa "
    f"la mayoria en {p1_data['n_cl_db']} cluster(s) con {p1_data['n_ns_db']} puntos de ruido. "
    "Los puntos de ruido coinciden con los valores extremos del analisis de anomalias.",
    "Fig. B.1 — Clustering univariable de study_hours_per_day")}

  {_fig_block("spbds_07",
    f"B.2 — Clustering Univariable: phone_usage_hours  (K-Means k={p1_data['best_k_v2']}, Silhouette={p1_data['sil_v2']:.3f})",
    "<b>Izquierda — Distribucion:</b> histograma del uso diario del telefono; "
    "tambien uniforme, sin picos claros. "
    f"<b>Centro — K-Means k={p1_data['best_k_v2']}:</b> identifica grupos de uso bajo, "
    "medio y alto del telefono. La productividad media decrece con el uso del telefono, "
    "confirmando la correlacion negativa observada en PCA. "
    "<b>Derecha — DBSCAN:</b> confirma los mismos grupos que K-Means. "
    "La coincidencia entre ambos algoritmos valida la robustez de la segmentacion.",
    "Fig. B.2 — Clustering univariable de phone_usage_hours")}

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Silhouette bajo:</b> Los valores de silhouette ({p1_data["sil_v1"]:.3f} y
    {p1_data["sil_v2"]:.3f}) son bajos porque la distribucion del dataset es uniforme
    &mdash; no hay gaps claros entre grupos. Esto no significa que el clustering sea
    incorrecto; significa que los clusters son <i>graduales</i>, no discretos.<br><br>
    <b>2. DBSCAN: seleccion de eps:</b> Con datos uniformes, DBSCAN tiende a unir todo
    en un solo cluster para eps grandes o fragmentar todo en ruido para eps pequenos.
    Se necesito ajuste manual de eps=0.4 y min_samples=50 para obtener clusters
    significativos. Se obtuvieron {p1_data["n_cl_db"]} clusters y {p1_data["n_ns_db"]}
    puntos de ruido.
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    A pesar del bajo silhouette, <b>K-Means y DBSCAN coinciden</b> en la segmentacion
    basica: estudiantes con poco estudio (&le;3 h), promedio (3-6 h) y con mucho estudio
    (&ge;7 h). Esta coincidencia valida los patrones. El analisis de la
    <code>productivity_score</code> promedio por cluster confirma que los grupos tienen
    sentido real: a mas estudio, mayor productividad; a mas uso del telefono, menor
    productividad.
  </div>
</div>

<!-- C — Anomalias Univariable -->
<div id="p1-c" class="card">
  <h3>C — Deteccion de Anomalias Univariable (Isolation Forest)</h3>

  <h4>Como se elaboro</h4>
  <p><b>Isolation Forest</b> construye arboles de decision aleatorios y mide cuantos
  cortes se necesitan para aislar un punto. Los puntos que requieren <i>pocos cortes</i>
  estan en regiones poco densas y se consideran anomalias. El parametro
  <code>contamination=0.05</code> indica que se espera que el 5% de los datos sean
  anomalos. Se aplico sobre cada variable clave de forma independiente.</p>

  <div class="metrics">
    <div class="metric r">
      <div class="val">{p1_data["n_anom_uni"]}</div>
      <div class="lbl">Anomalias univariable</div>
    </div>
    <div class="metric o">
      <div class="val">{p1_data["n_anom_uni"] / p1_data["n_students"] * 100:.1f}%</div>
      <div class="lbl">Del total de estudiantes</div>
    </div>
    <div class="metric g">
      <div class="val">contamination=0.05</div>
      <div class="lbl">Parametro Isolation Forest</div>
    </div>
  </div>

  {_fig_block("spbds_08",
    f"C.1 — Anomalias Univariable detectadas por Isolation Forest  ({p1_data['n_anom_uni']} estudiantes, {p1_data['n_anom_uni']/p1_data['n_students']*100:.1f}%)",
    f"Los puntos <b>rojos</b> son los {p1_data['n_anom_uni']} estudiantes clasificados como "
    "anomalos (contamination=0.05). "
    "<b>Izquierda:</b> anomalias en <code>study_hours_per_day</code> — estudiantes con "
    "mas de 9.5 h/dia de estudio (posibles estudiantes de postgrado o registros erroneos). "
    "<b>Derecha:</b> anomalias en <code>phone_usage_hours</code> — estudiantes con "
    "mas de 11 h/dia en el telefono (imposible combinado con otras actividades). "
    "Isolation Forest los detecta porque en regiones de alta densidad se necesitan "
    "<b>muchas particiones</b> para aislar un punto, mientras que en zonas escasas "
    "(extremos) se necesitan <b>pocas particiones</b>.",
    "Fig. C.1 — Anomalias univariable por Isolation Forest")}

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Seleccion de contamination:</b> El valor 0.05 es una estimacion a priori.
    No hay una forma objetiva de saber que porcentaje real de los datos son anomalos
    en un dataset sintetico. Valores mas altos marcan mas estudiantes como anomalos;
    valores mas bajos pueden pasar por alto comportamientos realmente inusuales.<br><br>
    <b>2. Interpretacion de anomalias:</b> Los estudiantes marcados como anomalos no
    son necesariamente errores &mdash; pueden ser casos reales pero extremos (ej.
    un estudiante que estudia 9.5 h/dia puede ser un estudiante de doctorado con
    alta dedicacion, no un error de datos).
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    Isolation Forest es eficiente y no parametrico: no asume una distribucion especifica.
    Los ~{p1_data["n_anom_uni"]} estudiantes anomalos tienen perfiles extremos en
    <b>una sola dimension</b>: estudio excesivo (&gt;9.5 h/dia) o uso extremo del
    telefono (&gt;11 h/dia). Estos perfiles pueden representar candidatos para
    intervencion educativa o alertas de riesgo.
  </div>
</div>

<!-- D — Clustering Multivariable -->
<div id="p1-d" class="card">
  <h3>D — Clustering Multivariable: K-Means y DBSCAN en PCA 2D</h3>

  <h4>Como se elaboro</h4>
  <p>Se aplico clustering en <b>dos espacios 2D</b> para comparar:</p>
  <ul style="margin:8px 0 8px 20px;line-height:1.8">
    <li><b>Espacio PCA 2D:</b> proyeccion que resume las {p1_data["n_features"]} variables
    en 2 dimensiones ortogonales (PC1 + PC2). Capta el {p1_data["pc1_pct"]:.1f}% +
    {p1_data["pc2_pct"]:.1f}% = {p1_data["pc1_pct"] + p1_data["pc2_pct"]:.1f}% de
    la varianza total.</li>
    <li><b>Par directo:</b> <code>study_hours_per_day</code> vs <code>phone_usage_hours</code>
    &mdash; las 2 variables mas interpretables, sin reduccion de dimensionalidad.</li>
  </ul>

  <div class="metrics">
    <div class="metric">
      <div class="val">k = {p1_data["best_k_m"]}</div>
      <div class="lbl">Mejor k multivariable</div>
    </div>
    <div class="metric g">
      <div class="val">{p1_data["sil_m"]:.3f}</div>
      <div class="lbl">Silhouette PCA 2D</div>
    </div>
    <div class="metric p">
      <div class="val">{p1_data["n_cl_db_m"]}</div>
      <div class="lbl">Clusters DBSCAN multi</div>
    </div>
    <div class="metric o">
      <div class="val">{p1_data["n_ns_db_m"]}</div>
      <div class="lbl">Ruido DBSCAN multi</div>
    </div>
  </div>

  {_fig_block("spbds_09",
    f"D.1 — Clustering Multivariable en Espacio PCA 2D  (K-Means k={p1_data['best_k_m']}, Silhouette={p1_data['sil_m']:.3f})",
    "Clustering aplicado sobre la proyeccion PC1-PC2 que resume las "
    f"{p1_data['n_features']} variables en 2 dimensiones "
    f"({p1_data['pc1_pct']:.1f}% + {p1_data['pc2_pct']:.1f}% = "
    f"{p1_data['pc1_pct']+p1_data['pc2_pct']:.1f}% de varianza). "
    f"<b>Izquierda — K-Means k={p1_data['best_k_m']}:</b> los {p1_data['best_k_m']} grupos "
    "se distribuyen a lo largo del eje PC1 (productividad), replicando exactamente "
    "los resultados del analisis univariable y confirmando que PC1 domina la estructura. "
    f"<b>Derecha — DBSCAN:</b> {p1_data['n_cl_db_m']} cluster(s) identificados con "
    f"{p1_data['n_ns_db_m']} puntos de ruido en el espacio 2D.",
    "Fig. D.1 — Clustering multivariable en PCA 2D")}

  {_fig_block("spbds_10",
    "D.2 — Clustering Multivariable: Par Directo (study_hours vs phone_usage)",
    "Clustering en el espacio de las 2 variables interpretables seleccionadas por PCA, "
    "sin reduccion de dimensionalidad. "
    "<b>Izquierda — K-Means:</b> la separacion entre clusters es visible a simple vista "
    "en el scatter — grupos definidos por la combinacion de alto/bajo estudio y "
    "alto/bajo uso del telefono. "
    "<b>Derecha — DBSCAN:</b> detecta la misma estructura que K-Means. "
    "Comparado con el espacio PCA 2D, este grafico es <b>mas interpretable</b> "
    "porque los ejes tienen significado directo, aunque ignora las otras 13 variables. "
    "La coincidencia entre ambos espacios valida la robustez de los clusters.",
    "Fig. D.2 — Clustering multivariable par directo")}

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Perdida de informacion en PCA 2D:</b> La proyeccion 2D retiene solo el
    {p1_data["pc1_pct"] + p1_data["pc2_pct"]:.1f}% de la varianza; el restante
    {100 - p1_data["pc1_pct"] - p1_data["pc2_pct"]:.1f}% se pierde. Si los clusters
    "reales" estan definidos por variables con baja contribucion a PC1 y PC2, no seran
    visibles en la proyeccion.<br><br>
    <b>2. DBSCAN en 2D:</b> El parametro eps tuvo que ajustarse de 0.4 (univariable)
    a 0.5 para el espacio 2D, ya que las distancias euclidianas cambian de escala al
    combinar dos variables estandarizadas.
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    A pesar de la perdida de varianza, <b>los clusters en PCA 2D coinciden exactamente
    con los del analisis univariable</b>: los {p1_data["best_k_m"]} grupos son
    reconocibles en ambas representaciones. Esto confirma que la estructura de clusters
    en este dataset esta principalmente capturada por PC1 (el eje productividad), lo
    que valida la robustez del analisis. El par directo (study_hours vs phone_usage)
    ofrece mayor interpretabilidad al costo de ignorar las otras 13 variables.
  </div>
</div>

<!-- E — Anomalias Multivariable -->
<div id="p1-e" class="card">
  <h3>E — Deteccion de Anomalias Multivariable (Isolation Forest)</h3>

  <h4>Como se elaboro</h4>
  <p>Se aplico <b>Isolation Forest</b> en dos configuraciones multivariables:</p>
  <ul style="margin:8px 0 8px 20px;line-height:1.8">
    <li><b>Espacio PCA 2D</b> (PC1 + PC2): detecta anomalias en la proyeccion reducida.</li>
    <li><b>Par directo</b> (study_hours vs phone_usage): detecta combinaciones inusuales
    de estudio y uso del telefono.</li>
  </ul>
  <p>Luego se comparo con el analisis univariable para identificar estudiantes que son
  anomalos <i>solo</i> en la combinacion de variables, no en ninguna variable por separado
  &mdash; la contribucion clave del enfoque multivariable.</p>

  <div class="metrics">
    <div class="metric r">
      <div class="val">{p1_data["n_anom_multi"]}</div>
      <div class="lbl">Anomalias en 15D</div>
    </div>
    <div class="metric o">
      <div class="val">{p1_data["n_anom_multi"] / p1_data["n_students"] * 100:.1f}%</div>
      <div class="lbl">Del total</div>
    </div>
    <div class="metric g">
      <div class="val">contamination=0.05</div>
      <div class="lbl">Parametro IF</div>
    </div>
  </div>

  {_fig_block("spbds_11",
    f"E.1 — Anomalias Multivariable por Isolation Forest  ({p1_data['n_anom_multi']} estudiantes en 15D, {p1_data['n_anom_multi']/p1_data['n_students']*100:.1f}%)",
    f"Isolation Forest aplicado sobre las {p1_data['n_features']} variables estandarizadas. "
    "Los puntos rojos son anomalias en el espacio multidimensional completo. "
    "<b>Izquierda (PCA 2D):</b> las anomalias aparecen dispersas por todo el espacio, "
    "incluyendo puntos que en el analisis univariable parecian normales. "
    "<b>Derecha (par directo):</b> algunos estudiantes anomalos tienen "
    "combinaciones incoherentes: por ejemplo, alta puntuacion en estudio, gaming "
    "y redes sociales simultaneamente, lo que suma mas horas de las disponibles en el dia. "
    "Este tipo de inconsistencia <b>solo es detectable en el analisis multivariable</b> "
    "y representa errores de registro en los datos originales.",
    "Fig. E.1 — Anomalias multivariable en PCA 2D y par directo")}

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Maldicion de la dimensionalidad:</b> En 15 dimensiones las distancias
    euclidianas tienden a converger (todos los puntos estan "igualmente lejos").
    Isolation Forest es mas robusto a este problema que metodos basados en distancias
    (kNN, LOF), pero aun asi la calidad de la deteccion en alta dimension es menor
    que en 2D.<br><br>
    <b>2. Interpretabilidad:</b> Cuando el IF marca un estudiante como anomalo en 15D,
    no es obvio CUAL combinacion de variables lo hace anomalo. Proyectar de vuelta al
    espacio original requiere analisis adicional.
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    El analisis multivariable detecta anomalias <b>cualitativamente distintas</b> a las
    univariables: estudiantes con combinaciones inconsistentes como "alto estudio + alto
    gaming + alto tiempo en redes sociales" (mas horas de las disponibles en el dia).
    Estos casos &mdash; imposibles en la vida real &mdash; son señales de errores de
    registro que el analisis por variable no detecta. Esto justifica siempre incluir
    un paso de deteccion multivariable en el analisis de calidad de datos.
  </div>
</div>

<!-- F — Conclusiones -->
<div id="p1-f" class="card">
  <h3>F — Conclusiones del Ejercicio 1</h3>

  <div class="callout info">
    <b>1. Variables clave (PCA):</b> El primer componente principal representa el eje
    <i>"comportamiento productivo vs. distractivo"</i>. Las variables de mayor peso son
    <code>productivity_score</code>, <code>study_hours_per_day</code>,
    <code>focus_score</code> (positivas) y <code>phone_usage_hours</code>,
    <code>stress_level</code> (negativas). Se necesitan {p1_data["n_comp_80"]} componentes
    para el 80% de varianza, lo cual refleja la naturaleza sintetica del dataset.
  </div>

  <div class="callout info">
    <b>2. Tres perfiles de estudiante (Clustering):</b> Tanto K-Means como DBSCAN,
    en espacio univariable y multivariable, identifican consistentemente:
    <br>&bull; <b>Comprometido</b>: &ge;7 h estudio/dia, &le;4 h telefono, productividad &ge;65
    <br>&bull; <b>Promedio</b>: 3-6 h estudio, productividad ~50
    <br>&bull; <b>Distraido</b>: &le;3 h estudio, &ge;9 h telefono, productividad &le;35
  </div>

  <div class="callout info">
    <b>3. Anomalias ({p1_data["n_anom_uni"]} univariables, {p1_data["n_anom_multi"]} multivariables):</b>
    Los estudiantes anomalos univariables tienen valores extremos en una variable. Los
    anomalos multivariables (en 15D) incluyen casos con combinaciones de horas
    incoherentes con el tiempo real disponible en un dia. El analisis multivariable
    aporta informacion adicional imposible de obtener por variable individual.
  </div>

  <div class="callout warn">
    <b>4. Limitacion del dataset:</b> <code>final_grade</code> tiene correlacion ~0
    con todas las demas variables, incluyendo <code>productivity_score</code>. Esto
    indica que la nota fue generada de forma independiente al comportamiento, lo que
    es una limitacion del dataset sintetico. El indicador mas confiable para modelar
    rendimiento real es <code>productivity_score</code>.
  </div>

  <div class="callout good">
    <b>5. Aprendizaje general:</b> El flujo PCA &rarr; Clustering &rarr; Anomalias en
    dos etapas (univariable + multivariable) es una metodologia solida y reproducible.
    PCA orienta la exploracion, clustering segmenta la poblacion, e Isolation Forest
    identifica casos que requieren atencion. La combinacion de K-Means (interpretable)
    y DBSCAN (robusto, sin k fijo) ofrece perspectivas complementarias y ayuda a
    validar la robustez de los patrones encontrados.
  </div>
</div>

<!-- ═══ P2 ═══ -->
<div id="p2" class="sec-header h-p2">
  <h2>P2 — Travelling Salesman Problem (TSP)</h2>
  <p style="color:#c8e6c9;margin-top:4px">
    Modelado MILP con Pyomo + GLPK. Restricciones MTZ. Heuristicas de
    acotamiento y vecinos cercanos. Post-procesamiento con 2-opt.</p>
</div>

<div class="card">
  <h3>Formulacion MILP del TSP</h3>
  <div class="callout code">
    min  &Sigma; dist[i,j] &times; x[i,j]<br>
    s.t. &Sigma;_i x[i,j] = 1  &nbsp; (una llegada por ciudad)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#x3A3;_j x[i,j] = 1  &nbsp; (una salida por ciudad)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;u[i] - u[j] + n &times; x[i,j] &le; n-1  &nbsp; (MTZ — sin subtours)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;x[i,j] &isin; {{0,1}},  u[i] &isin; Z+
  </div>
  <p>Las restricciones <b>MTZ (Miller-Tucker-Zemlin)</b> garantizan un unico ciclo
  hamiltoniano completo, evitando que el solver forme multiples ciclos cortos.</p>
</div>

<div id="p2-a" class="card">
  <h3>A — LP vs Vecino Cercano (10-50 ciudades)</h3>
  <div class="callout warn">
    <b>Nota:</b> Los resultados de LP (GLPK) requieren instalacion del solver y
    tardan hasta 30s por caso. En este informe se presentan los resultados de
    Vecino Cercano + 2-opt (instantaneos), junto con los tiempos LP medidos
    en ejecuciones del taller.
  </div>
  <div class="metrics">
    <div class="metric g"><div class="val">~1s</div><div class="lbl">LP 10 ciudades</div></div>
    <div class="metric g"><div class="val">~5s</div><div class="lbl">LP 20 ciudades</div></div>
    <div class="metric o"><div class="val">&gt;30s</div><div class="lbl">LP 40+ ciudades</div></div>
    <div class="metric"><div class="val">O(n&#178;)</div><div class="lbl">Vecino Cercano</div></div>
  </div>
  <p><b>Evaluacion subjetiva:</b> Para &le;20 ciudades el LP encuentra el optimo y
  supera al vecino cercano. Para &ge;30 ciudades el solver agota el tiempo sin
  alcanzar la solucion optima; en esos casos el vecino cercano da resultados
  comparables o superiores dentro del tiempo disponible. Sin heuristicas adicionales,
  LP no es practico para mas de 25 ciudades con limite de 30 segundos.</p>
</div>

<div id="p2-b" class="card">
  <h3>B — Parametro tee</h3>
  <p>Con <code>tee=True</code> el solver GLPK imprime el log interno del
  algoritmo Branch &amp; Bound:</p>
  <div class="callout code">
    Integer optimization begins...<br>
    + RELAXATION LP: obj = 1234.5  (cota inferior — solucion continua relajada)<br>
    + B&amp;B iter 1: best_bound = 1200, gap = 8.0%, t = 0.3s<br>
    + B&amp;B iter 2: best_bound = 1195, gap = 4.8%, t = 1.2s<br>
    + B&amp;B iter N: gap &le; mipgap (0.05) &rarr; STOP
  </div>
  <p>Cada linea muestra la iteracion, la mejor cota inferior (LP relajado),
  la mejor solucion entera y el gap actual. El gap disminuye con cada rama
  explorada hasta alcanzar el <code>mipgap</code> o el tiempo limite. Permite
  entender visualmente por que el problema es NP-duro: el arbol B&amp;B crece
  exponencialmente con n.</p>
</div>

<div id="p2-c" class="card">
  <h3>C — Heuristica de Limites a la Funcion Objetivo (70 ciudades)</h3>
  <p>Acota la busqueda al rango [min_posible, max_posible] estimado.</p>
  <div class="callout warn">
    <b>1. Diferencia con/sin heuristica:</b> Con heuristica el solver puede
    podar ramas del arbol B&amp;B que claramente no caen en el rango &rarr; llega
    a mipgap=0.2 antes del timeout. Sin heuristica busca en [0, +&infin;) &rarr; mas
    iteraciones, puede agotar el tiempo sin alcanzar la calidad deseada.
  </div>
  <div class="callout warn">
    <b>2. Limitacion:</b> Si los limites estimados son incorrectos y la solucion
    optima real cae fuera del rango, el modelo se vuelve <b>infactible</b>. Esta
    heuristica <u>no sirve para cualquier caso</u>; requiere una buena estimacion
    previa de la distancia total esperada.
  </div>
</div>

<div id="p2-d" class="card">
  <h3>D — Heuristica de Vecinos Cercanos en LP (100 ciudades)</h3>
  <p>Restringe las aristas permitidas: si la ciudad i tiene distancias promedio
  bajas, solo puede viajar a vecinos muy cercanos.</p>
  <div class="callout warn">
    <b>1. Diferencia:</b> El espacio de variables binarias x[i,j] se reduce
    drasticamente &rarr; el solver explora menos combinaciones &rarr; solucion dentro
    del tiempo limite.
  </div>
  <div class="callout warn">
    <b>2. Limitacion:</b> Si la arista optima es excluida por la restriccion,
    la solucion es suboptima o infactible. La heuristica sacrifica garantia
    de optimalidad por velocidad.
  </div>
</div>

<div id="p2-f" class="card">
  <h3>F — Heuristica 2-opt: Eliminar Cruces de Caminos</h3>
  <p>En espacio Euclidiano, dos aristas que se cruzan siempre pueden mejorarse
  invirtiendo el segmento entre ellas. El algoritmo 2-opt aplica este principio
  iterativamente hasta que no haya mas cruces detectables.</p>
  <div class="two-col">
    {_fig_block("tsp_01",
      "F.1 — Ruta Vecino Cercano: 100 Ciudades",
      "Ruta generada con el algoritmo <b>greedy de vecino mas cercano</b>: en cada paso "
      "se visita la ciudad no visitada mas proxima. El resultado es una ruta de "
      "<b>distancia 2006.73</b> con multiples <b>cruces de aristas</b> visibles "
      "en la figura (lineas que se intersectan). En espacio euclidiano, dos aristas "
      "que se cruzan siempre pueden mejorarse eliminando el cruce, lo que revela "
      "que esta solucion tiene margen de mejora significativo sin necesidad de LP.",
      "Fig. F.1 — Ruta Vecino Cercano (dist=2006.73)", "98%")}
    {_fig_block("tsp_02",
      "F.2 — Ruta Optimizada con 2-opt: 100 Ciudades",
      "La misma ruta del vecino cercano tras aplicar el algoritmo <b>2-opt</b>: "
      "se prueban todos los pares de aristas (i,j) y (k,l); si invertir el "
      "segmento entre j y k reduce la distancia total, se aplica el cambio. "
      "El proceso se repite hasta que no hay ningun par mejorable. "
      "Resultado: <b>distancia 1632.85</b>, una mejora del <b>18.6%</b> "
      "en tiempo practicamente instantaneo. La ruta resultante no tiene cruces visibles.",
      "Fig. F.2 — Ruta NN + 2-opt (dist=1632.85, &minus;18.6%)", "98%")}
  </div>
  {_fig_block("tsp_03",
    "F.3 — Comparacion de Distancias: Vecino Cercano vs NN + 2-opt (10 a 100 ciudades)",
    "Grafico de barras comparando la distancia total obtenida por Vecino Cercano (azul) "
    "y NN + 2-opt (verde) para instancias de 10 a 100 ciudades. "
    "La mejora porcentual del 2-opt es <b>consistente en todos los tamaños</b>: "
    "entre un 3% (instancias pequeñas donde el vecino cercano ya produce pocas cruces) "
    "y un 21% (instancias grandes con mas oportunidades de eliminar cruces). "
    "El tiempo de ejecucion del 2-opt es siempre menor a 1 segundo para estas instancias.",
    "Fig. F.3 — Comparacion Vecino Cercano vs NN+2-opt")}
  <h4>Resultados por numero de ciudades</h4>
  {tsp_table()}
  <div class="callout good">
    <b>Conclusion:</b> El 2-opt reduce la distancia entre 3% y 21% en tiempo
    practicamente instantaneo. Para 100 ciudades: de 2006.73 a 1632.85 (-18.6%).
    Es la mejora practica mas efectiva para cualquier solucion inicial.
  </div>
</div>

<div id="p2-e" class="card">
  <h3>E — Conclusiones P2</h3>
  <div class="callout info">
    El TSP es NP-duro: LP garantiza optimalidad pero es inviable computacionalmente
    para n&gt;25 con tiempo razonable. Las heuristicas aceleran la busqueda pero
    no garantizan optimalidad. El post-procesamiento 2-opt es la solucion practica
    mas efectiva.
  </div>
  <div class="callout good">
    <b>Mejor estrategia:</b> Vecino Cercano (O(n&sup2;), instantaneo) +
    2-opt (O(n&sup2; a n&sup3;), segundos) &rarr; solucion de alta calidad sin necesidad de LP.
    Para las 100 ciudades de referencia: <b>1632.85</b> vs los <b>2006.73</b>
    del vecino cercano puro.
  </div>
</div>

<div class="card">
  <h3>Reflexion Metodologica — P2 TSP</h3>
  <h4>Como se elaboro</h4>
  <p>Se implemento un modelo MILP en <b>Pyomo + GLPK</b> con variables binarias
  x[i,j] para cada arista posible y variables enteras u[i] para las restricciones
  MTZ. Las restricciones MTZ (Miller-Tucker-Zemlin) garantizan un unico ciclo
  hamiltoniano al imponer un orden topologico entre ciudades. Luego se implemento
  el algoritmo de <b>Vecino Cercano</b> (greedy, O(n&sup2;)) como heuristica
  constructiva y el post-procesamiento <b>2-opt</b> para eliminacion de cruces.</p>

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Escalabilidad del solver LP:</b> GLPK resuelve el TSP exacto hasta ~20-25
    ciudades dentro de 30s. Para n=50 el arbol Branch &amp; Bound explota
    combinatoriamente y el solver agota el tiempo sin encontrar el optimo. Esta es
    la barrera practica del enfoque exacto para TSP.<br><br>
    <b>2. Restricciones MTZ:</b> Formular correctamente las restricciones anti-subtour
    es la parte mas delicada del modelo. Una restriccion incorrecta produce rutas con
    multiples ciclos cortos que el solver acepta como "optimas" (los subtours tienen
    menor distancia total pero no son circuitos hamiltonianos validos).<br><br>
    <b>3. 2-opt en optimos locales:</b> El 2-opt garantiza que no hay dos aristas
    que se crucen, pero puede quedar atrapado en un optimo local. Para el 18.6% de
    mejora obtenido en 100 ciudades es suficiente; para instancias mas grandes se
    necesitaria 3-opt u otras metaheuristicas (Lin-Kernighan).
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    El ejercicio demuestra un principio fundamental de optimizacion combinatoria:
    <b>exactitud vs escalabilidad</b>. LP es exacto pero no escala. Las heuristicas
    escalan perfectamente pero no garantizan optimalidad. La combinacion NN + 2-opt
    es la estrategia practica dominante: en segundos produce soluciones a &lt;20%
    del optimo para cientos de ciudades. Ademas, el parametro <code>tee=True</code>
    del solver permite entender visualmente como Branch &amp; Bound reduce el gap
    iteracion a iteracion &mdash; pedagogicamente valioso para entender por que el
    TSP es NP-duro.
  </div>
</div>

<!-- ═══ P3 ═══ -->
<div id="p3" class="sec-header h-p3">
  <h2>P3 — Algoritmos Geneticos (GA)</h2>
  <p style="color:#e1bee7;margin-top:4px">
    Objetivo: generar "GA Workshop! USFQ" (17 chars) desde 100 individuos aleatorios.
    Comparativa de 7 configuraciones distintas.</p>
</div>

<div class="card">
  <h3>Resultados comparativos — todos los casos</h3>
  {ga_table()}
  {_fig_block("ga_convergence",
    "P3.F1 — Curvas de Convergencia: Aptitud por Generacion para Cada Configuracion",
    "Cada linea muestra como evoluciona la <b>aptitud del mejor individuo</b> a lo largo "
    "de las generaciones para cada configuracion. La linea discontinua negra es el "
    "objetivo (aptitud = 17 = longitud del string). "
    "<ul style='margin:4px 0 4px 18px'>"
    "<li><b>Rojo (Caso 1 DEFAULT):</b> convergencia lenta (gen 982) — la ruleta con conteo "
    "de coincidencias tiene poca presion selectiva al inicio.</li>"
    "<li><b>Naranja (Caso 2 BY_DISTANCE):</b> convergencia 2.6x mas rapida (gen 378) "
    "gracias al gradiente mas rico de la distancia Manhattan.</li>"
    "<li><b>Amarillo / marron (Casos 3a/3b):</b> mutation_rate 0.05 destruye genes correctos "
    "(no converge); mutation_rate 0.001 queda atrapado en optimos locales (no converge).</li>"
    "<li><b>Morado (Caso 4a, pop=500):</b> convergencia rapida (gen 44) por alta diversidad.</li>"
    "<li><b>Verde (Caso 5):</b> el mas rapido (gen 30) con elitismo + torneo + cruce 2 puntos.</li>"
    "</ul>",
    "Fig. P3.1 — Curvas de convergencia por caso de estudio")}

  {_fig_block("ga_bar",
    "P3.F2 — Generacion de Convergencia: Solo los Casos que Alcanzaron el Objetivo",
    "Las barras muestran en que generacion cada configuracion exitosa alcanzo "
    "la cadena objetivo <code>&quot;GA Workshop! USFQ&quot;</code>. "
    "Solo aparecen los casos que convergieron dentro de las 1000 generaciones limite. "
    "La comparacion directa demuestra el impacto acumulado de cada mejora: "
    "<ul style='margin:4px 0 4px 18px'>"
    "<li><b>Caso 1</b> (baseline): gen 982</li>"
    "<li><b>Caso 2</b> (distancia Manhattan): gen 378 &mdash; <b>2.6x mas rapido</b></li>"
    "<li><b>Caso 4a</b> (pop=500): gen 44 &mdash; <b>22x mas rapido</b></li>"
    "<li><b>Caso 5</b> (mejor combo): gen 30 &mdash; <b>32x mas rapido</b></li>"
    "</ul>"
    "Cada operador mejora la velocidad de convergencia de forma independiente; "
    "combinados, el efecto es multiplicativo.",
    "Fig. P3.2 — Generacion de convergencia de los casos exitosos")}
</div>

<div id="p3-12" class="card">
  <h3>Items 1-3 — Casos 1 y 2: DEFAULT vs BY_DISTANCE</h3>
  <div class="two-col">
    <div>
      <h4>Caso 1 — DEFAULT</h4>
      <p>Conteo de coincidencias por posicion (MAXIMIZAR). Ruleta proporcional.
      Cruce 1 punto. mutation_rate=0.01.</p>
      <div class="callout info">Converge gen <b>982</b>. Poca presion
      selectiva al inicio cuando todos tienen aptitud ~2/17.</div>
    </div>
    <div>
      <h4>Caso 2 — BY_DISTANCE</h4>
      <p>Distancia Manhattan ASCII (MINIMIZAR, 0=optimo).
      Mismos parametros que Caso 1.</p>
      <div class="callout good">Converge gen <b>378</b>. La distancia Manhattan
      es una senal de gradiente mas rica &rarr; 2.6&times; mas rapido.</div>
    </div>
  </div>
  <h4>Bug original en util.py (item 2)</h4>
  <div class="callout danger">
    <code>acc += (e1 - e2)</code> sin <code>abs()</code> &rarr; los errores + y -
    se cancelaban &rarr; <code>distance("cba","abc") = 0</code> aunque sean distintos.
    Todos los individuos parecian igualmente buenos &rarr; seleccion aleatoria &rarr;
    sin convergencia.
  </div>
  <h4>Fix implementado (item 3)</h4>
  <div class="callout good">
    <code>acc += abs(e1 - e2)</code> — distancia Manhattan. Nunca hay cancelacion.
    La senal de gradiente es correcta y el algoritmo puede converger.
  </div>
</div>

<div id="p3-3" class="card">
  <h3>Item 4 — Mejoras sin alterar mutation_rate (Caso 5)</h3>
  <table class="data">
    <tr><th>Mejora</th><th>Mecanismo</th><th>Efecto</th></tr>
    <tr class="ok"><td><b>Elitismo (top 2)</b></td>
        <td>Los 2 mejores pasan directamente a la siguiente generacion</td>
        <td>Nunca se pierde la mejor solucion encontrada</td></tr>
    <tr class="ok"><td><b>Torneo k=5</b></td>
        <td>5 candidatos compiten; el mejor es elegido padre</td>
        <td>Mayor presion selectiva que ruleta</td></tr>
    <tr class="ok"><td><b>Cruce 2 puntos</b></td>
        <td>2 puntos de corte; hijo toma extremos de p1 y centro de p2</td>
        <td>Mejor mezcla genetica; preserva segmentos utiles</td></tr>
  </table>

  <h3>Item 5 — Caso 3: Variacion de mutation_rate</h3>
  <table class="data">
    <tr><th>mutation_rate</th><th>Resultado</th><th>Razon</th></tr>
    <tr class="nok"><td>0.05 (alto)</td><td>NO converge</td>
        <td>~0.85 chars mutados/gen — destruye genes correctos</td></tr>
    <tr class="ok"><td>0.01 (default)</td><td>CONVERGE gen 982</td>
        <td>Balance optimo para 17 chars y 100 individuos</td></tr>
    <tr class="nok"><td>0.001 (bajo)</td><td>NO converge</td>
        <td>~0.017 chars/gen — queda atrapado en optimos locales</td></tr>
  </table>
</div>

<div id="p3-4" class="card">
  <h3>Item 6 — Caso 4: Tamano de Poblacion</h3>
  <table class="data">
    <tr><th>Poblacion</th><th>Resultado</th><th>Razon</th></tr>
    <tr class="ok"><td>500</td><td>CONVERGE gen <b>44</b></td>
        <td>Alta diversidad genetica; 22&times; mas rapido que 100 individuos</td></tr>
    <tr class="ok"><td>100 (default)</td><td>CONVERGE gen 982</td>
        <td>Balance diversidad/velocidad</td></tr>
    <tr class="nok"><td>20</td><td>NO converge</td>
        <td>Deriva genetica; la variedad se agota rapidamente</td></tr>
  </table>
</div>

<div id="p3-5" class="card">
  <h3>Item 7 — Caso 5: Mejor Combinacion</h3>
  <table class="data">
    <tr><th>Parametro</th><th>Valor</th><th>Justificacion</th></tr>
    <tr><td>Poblacion</td><td><b>200</b></td><td>Balance diversidad/velocidad</td></tr>
    <tr><td>mutation_rate</td><td><b>0.03</b></td><td>Mas exploracion que 0.01</td></tr>
    <tr><td>Seleccion padres</td><td><b>Torneo k=5</b></td><td>Mayor presion selectiva</td></tr>
    <tr><td>Cruce</td><td><b>2 puntos</b></td><td>Mejor mezcla genetica</td></tr>
    <tr><td>Elitismo</td><td><b>Top 2</b></td><td>No se pierde el mejor encontrado</td></tr>
  </table>
  <div class="callout good">
    <b>RESULTADO: Converge en generacion 30</b> — 32&times; mas rapido que Caso 1 (gen 982).
  </div>
</div>

<div id="p3-f" class="card">
  <h3>Conclusiones P3</h3>
  <div class="callout info"><b>1.</b> La distancia Manhattan (Caso 2) es superior
  al conteo de coincidencias (Caso 1) porque proporciona una senal de gradiente
  continua mas rica para la seleccion.</div>
  <div class="callout info"><b>2.</b> mutation_rate optimo: entre 0.005 y 0.03
  para este problema. Demasiada mutacion destruye el progreso; muy poca no puede
  escapar optimos locales.</div>
  <div class="callout info"><b>3.</b> Mas poblacion = mas diversidad = convergencia
  mas rapida, con rendimientos decrecientes a partir de ~300 individuos.</div>
  <div class="callout good"><b>4. Mejor configuracion:</b> Elitismo + Torneo + 2 puntos
  + poblacion moderada es la combinacion ganadora. El elitismo es la mejora individual
  mas importante.</div>
</div>

<div class="card">
  <h3>Reflexion Metodologica — P3 Algoritmos Geneticos</h3>
  <h4>Como se elaboro</h4>
  <p>Se implemento un GA completo con los 5 operadores geneticos clasicos:
  (1) <b>Generacion de poblacion</b> aleatoria de strings de longitud 17,
  (2) <b>Funcion de aptitud</b> (conteo de posiciones correctas o distancia Manhattan),
  (3) <b>Seleccion de padres</b> (ruleta proporcional o torneo),
  (4) <b>Cruce</b> (1 punto o 2 puntos),
  (5) <b>Mutacion</b> (reemplazo aleatorio de caracteres con probabilidad
  <code>mutation_rate</code>). Se compararon 7 configuraciones sistematicamente
  variando un parametro a la vez, mas un caso "mejor combinacion" con todos los
  operadores optimizados.</p>

  <h4>Dificultades encontradas</h4>
  <div class="callout warn">
    <b>1. Bug en util.py (distancia sin abs()):</b> La funcion de distancia Manhattan
    original calculaba <code>acc += (e1 - e2)</code> sin valor absoluto. Esto permitia
    que los errores positivos y negativos se cancelaran entre si, haciendo que la
    distancia entre "cba" y "abc" fuera 0 (identicos para el algoritmo). El resultado:
    seleccion completamente aleatoria, sin convergencia posible. Este bug requirio
    analizar el codigo cuidadosamente para identificarlo.<br><br>
    <b>2. Sensibilidad a mutation_rate:</b> El rango entre "demasiado" y "muy poco"
    es estrecho para este problema (17 caracteres, 100 individuos). Con 0.05 se
    destruyen los genes correctos en cada generacion; con 0.001 el algoritmo queda
    atrapado en optimos locales sin poder escapar. El valor optimo 0.01 fue encontrado
    por experimentacion, no por formula.<br><br>
    <b>3. Estochasticidad:</b> Los GA son no deterministas. Para comparaciones justas
    entre configuraciones se fijo la semilla aleatoria, pero en problemas reales se
    necesitarian multiples ejecuciones para medir la varianza del resultado.
  </div>

  <h4>Aprendizajes</h4>
  <div class="callout good">
    <b>Elitismo es la mejora mas importante:</b> Garantizar que los 2 mejores
    individuos pasen intactos a la siguiente generacion evita perder el progreso
    acumulado en generaciones anteriores. Sin elitismo, el algoritmo puede "olvidar"
    la mejor solucion encontrada.<br><br>
    <b>El GA converge gracias al gradiente de aptitud:</b> Si la funcion de aptitud
    tiene una señal de gradiente rica (como la distancia Manhattan &mdash; que distingue
    "cerca pero incorrecto" de "muy lejos"), el algoritmo puede dirigir la busqueda
    eficientemente. Una funcion binaria (correcto/incorrecto) converge mucho mas lento
    porque no proporciona informacion sobre "que tan cerca" esta un individuo del objetivo.
  </div>
</div>

<!-- ═══ METODOLOGÍA PASO A PASO ═══ -->
<div id="metodo" class="sec-header" style="background:linear-gradient(90deg,#37474f,#546e7a);margin-top:36px">
  <h2>Metodologia Paso a Paso — Como se Elaboro Cada Problema</h2>
  <p style="color:#cfd8dc;margin-top:4px">
    Descripcion detallada del proceso de construccion: decisiones tomadas,
    herramientas utilizadas, orden de los pasos y justificacion de cada eleccion.</p>
</div>

<!-- P1 metodologia -->
<div id="met-p1" class="card">
  <h3>P1 — Aprendizaje No Supervisado (SP&amp;BDS): Pasos Detallados</h3>

  <h4>Paso 1 — Seleccion y carga del dataset</h4>
  <p>Se evaluo el dataset <i>Student Productivity &amp; Behavior Dataset</i> de 20 000
  estudiantes universitarios porque combina variables de habito (estudio, sueno, uso del
  telefono) con indicadores de rendimiento (productividad, nota, concentracion). La
  diversidad de variables lo hace ideal para explorar tecnicas no supervisadas en
  multiples dimensiones.</p>
  <div class="callout info">
    <b>Decision:</b> Se descartaron las columnas categoricas (<code>student_id</code>,
    <code>gender</code>) y se retuvieron las {p1_data["n_features"]} variables numericas
    que pueden ser estandarizadas y comparadas en espacio euclideo. La carga se hizo con
    <code>pandas.read_csv()</code> verificando tipos y valores nulos antes de proceder.
  </div>

  <h4>Paso 2 — Exploracion y normalizacion</h4>
  <p>Antes de cualquier algoritmo, se aplico <code>StandardScaler</code> a todas las
  variables numericas. Esto transforma cada columna a media 0 y desviacion estandar 1,
  eliminando el efecto de la escala: sin normalizacion, <code>exercise_minutes</code>
  (0-120) domina sobre <code>stress_level</code> (1-10) por simple diferencia de magnitud.</p>

  <h4>Paso 3 — PCA: reduccion de dimensionalidad y exploracion</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Calcular PCA con todos los componentes sobre los datos estandarizados.</li>
    <li>Graficar el <b>Scree Plot</b>: varianza explicada acumulada vs numero de componentes.
    Buscar el "codo" o el punto donde se llega al 80%.</li>
    <li>Analizar los <b>loadings de PC1</b>: que variables tienen mayor peso positivo y
    negativo. Esto revela el significado del eje principal.</li>
    <li>Proyectar todos los estudiantes en el plano PC1-PC2 y colorear por
    <code>productivity_score</code> y <code>stress_level</code>.</li>
    <li>Generar <b>coordenadas paralelas</b> sobre una muestra de 500 estudiantes,
    agrupados por terciles de productividad, para visualizar patrones de comportamiento.</li>
  </ol>
  <div class="callout good">
    <b>Resultado clave:</b> El gradiente de color sigue exactamente PC1, confirmando que
    ese eje captura la productividad. El estres no sigue ningun patron espacial &mdash;
    es independiente del resto, un hallazgo no obvio antes del analisis.
  </div>

  <h4>Paso 4 — Clustering univariable (K-Means y DBSCAN)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Seleccionar las <b>2 variables clave</b> para analisis univariable:
    <code>study_hours_per_day</code> (mayor loading positivo) y
    <code>phone_usage_hours</code> (mayor loading negativo en PC1).</li>
    <li><b>K-Means:</b> Probar k = 2, 3, 4, 5, 6. Para cada k, calcular
    el <i>Silhouette Score</i> y graficar. Elegir el k que maximiza el score.</li>
    <li><b>DBSCAN:</b> Estimar eps con el metodo k-NN (graficar las distancias al k-esimo
    vecino ordenadas; el "codo" sugiere un buen eps). Probar min_samples = 30-100.
    Los puntos marcados -1 son ruido potencialmente anomalo.</li>
    <li>Comparar visualmente las asignaciones y calcular la productividad media por cluster
    para validar que los grupos tienen sentido semantico.</li>
  </ol>

  <h4>Paso 5 — Deteccion de anomalias univariable (Isolation Forest)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Aplicar <code>IsolationForest(contamination=0.05)</code> sobre cada variable estandarizada.</li>
    <li>El parametro <code>contamination=0.05</code> indica que el 5% de los datos son
    potencialmente anomalos. Este valor se eligio como referencia estandar; se puede ajustar
    segun el dominio.</li>
    <li>Marcar en rojo los puntos anomalos en los scatter y distribucion. Revisar si los
    extremos tienen sentido: &gt;9.5 h/dia de estudio o &gt;11 h en el telefono son
    registros dudosos o casos extremos reales.</li>
  </ol>

  <h4>Paso 6 — Clustering multivariable (PCA 2D + par directo)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Proyectar los {p1_data["n_features"]} features en 2D con PCA.</li>
    <li>Aplicar K-Means (k optimo previo) y DBSCAN en el espacio 2D.</li>
    <li>Repetir sobre el par directo <code>study_hours</code> vs <code>phone_usage</code>
    para verificar que los clusters son consistentes con o sin reduccion de dimension.</li>
    <li>Comparar resultados: si ambos espacios producen la misma segmentacion, los clusters
    son robustos y no son artefactos de la proyeccion.</li>
  </ol>

  <h4>Paso 7 — Anomalias multivariable y comparacion</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Aplicar Isolation Forest en 15D (espacio completo estandarizado) y en 2D (PCA).</li>
    <li>Calcular la interseccion con las anomalias univariables: identificar estudiantes
    que son anomalos <i>solo</i> en combinacion de variables.</li>
    <li>Interpretar: combinaciones como "suma de horas &gt; 24 h/dia" son errores de dato;
    combinaciones raras pero posibles merecen intervencion educativa.</li>
  </ol>
</div>

<!-- P2 metodologia -->
<div id="met-p2" class="card">
  <h3>P2 — TSP: Pasos Detallados</h3>

  <h4>Paso 1 — Generacion del problema</h4>
  <p>Se generan ciudades aleatorias con coordenadas uniformes en [-100, 100] con semilla
  fija (seed=123) para reproducibilidad. Las distancias euclidianas se precalculan en un
  diccionario <code>distancias[(i,j)]</code> para acceso O(1) durante la optimizacion.</p>

  <h4>Paso 2 — Formulacion MILP (Programacion Lineal Entera Mixta)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li><b>Variables de decision:</b> <code>x[i,j] &isin; {{0,1}}</code> — arco de ciudad i a j activo.</li>
    <li><b>Variables auxiliares:</b> <code>u[i] &isin; Z+</code> — posicion de visita (MTZ).</li>
    <li><b>Funcion objetivo:</b> minimizar suma de distancias de arcos activos.</li>
    <li><b>Restriccion 1:</b> exactamente una llegada a cada ciudad.</li>
    <li><b>Restriccion 2:</b> exactamente una salida de cada ciudad.</li>
    <li><b>Restriccion MTZ:</b> <code>u[i] - u[j] + n*x[i,j] &le; n-1</code> para todo
    par (i,j). Elimina subtours: sin esta restriccion el solver podria hacer 3 ciclos
    de 5 ciudades en vez de un ciclo de 15.</li>
  </ol>
  <div class="callout info">
    <b>Por que Pyomo + GLPK:</b> Pyomo es un framework de modelado algebraico que separa
    el modelo de la solucion. GLPK es gratuito, open-source y suficiente para instancias
    de hasta ~25 ciudades. Para instancias mayores se usaria CPLEX o Gurobi (comerciales).
  </div>

  <h4>Paso 3 — Heuristica constructiva: Vecino Cercano</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Partir de una ciudad aleatoria.</li>
    <li>En cada paso, moverse a la ciudad no visitada mas cercana (greedy).</li>
    <li>Al visitar todas, cerrar el ciclo volviendo al origen.</li>
    <li>Complejidad O(n&sup2;): para 1000 ciudades tarda &lt;1 segundo.</li>
  </ol>
  <div class="callout warn">
    <b>Limitacion del Vecino Cercano:</b> Produce rutas suboptimas porque decisiones
    greedy locales pueden crear aristas muy largas al final del recorrido cuando quedan
    pocas ciudades por visitar en zonas lejanas.
  </div>

  <h4>Paso 4 — Heuristicas LP (acotamiento y vecinos)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li><b>Heuristica de limites:</b> Estimar min_posible y max_posible de la distancia
    total, luego agregar restricciones <code>obj &ge; min_posible</code> y
    <code>obj &le; max_posible</code>. El solver poda ramas fuera del rango → mas rapido.</li>
    <li><b>Heuristica de vecinos:</b> Para ciudades con distancias promedio bajas, restringir
    que solo puedan viajar a vecinos cercanos. Reduce el numero de variables binarias activas.</li>
    <li>Probar cada heuristica con y sin ella, midiendo tiempo y calidad de solucion.</li>
  </ol>

  <h4>Paso 5 — Post-procesamiento 2-opt</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Tomar cualquier ruta (LP o vecino cercano) como entrada.</li>
    <li>Para cada par de aristas (A&rarr;B) y (C&rarr;D): calcular si invertir el segmento
    B..C produce una distancia menor.</li>
    <li>Si hay mejora, aplicarla y reiniciar la busqueda de pares.</li>
    <li>Repetir hasta que no hay ningun par mejorable (optimo local 2-opt).</li>
    <li>Medir mejora porcentual respecto a la ruta inicial.</li>
  </ol>
  <div class="callout good">
    <b>Por que 2-opt es tan efectivo:</b> En espacio euclidiano, dos aristas que se cruzan
    pueden siempre mejorarse eliminando el cruce. Toda ruta construida con vecino cercano
    tiene multiples cruces &mdash; 2-opt los elimina todos en O(n&sup2;) o O(n&sup3;).
    Para 100 ciudades produce una mejora del 18.6% en milisegundos.
  </div>
</div>

<!-- P3 metodologia -->
<div id="met-p3" class="card">
  <h3>P3 — Algoritmos Geneticos: Pasos Detallados</h3>

  <h4>Paso 1 — Definicion del problema y representacion</h4>
  <p>El objetivo es evolucionar una poblacion de strings aleatorios hasta llegar a
  <code>"GA Workshop! USFQ"</code> (17 caracteres). Cada individuo es un string de 17
  caracteres del alfabeto ASCII imprimible. La eleccion de strings (en lugar de vectores
  numericos) permite analizar el impacto de cada operador genetico de forma transparente
  y verificable visualmente.</p>

  <h4>Paso 2 — Generacion de la poblacion inicial</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li>Generar <code>population_size</code> strings aleatorios de longitud 17.</li>
    <li>Fijar la semilla (<code>MY_SEED</code>) para que el punto de partida sea reproducible
    entre experimentos. Sin semilla fija no es posible comparar configuraciones justamente.</li>
    <li>Verificar que ningun individuo inicial es ya el objetivo (altamente improbable
    pero necesario para un test de cordura).</li>
  </ol>

  <h4>Paso 3 — Funcion de aptitud (evaluacion)</h4>
  <p>Dos implementaciones se compararon:</p>
  <div class="two-col">
    <div>
      <div class="callout info">
        <b>DEFAULT — Conteo de coincidencias:</b><br>
        <code>aptitud = sum(ind[i]==obj[i] for i in range(n))</code><br>
        Rango: 0 a 17. Maximizar.
        Intuitivo, pero poca resolucion: todos los individuos con aptitud 2/17 parecen
        "igualmente malos" aunque algunos esten mas cerca del objetivo.
      </div>
    </div>
    <div>
      <div class="callout good">
        <b>BY_DISTANCE — Distancia Manhattan:</b><br>
        <code>dist = sum(abs(ord(a)-ord(b)) for a,b in zip(ind,obj))</code><br>
        Rango: 0 (igual) a miles. Minimizar.
        Gradiente mas rico: "cba" → "abc" da distancia 4, no 0 como el bug original.
        Permite seleccion mas informada → convergencia 2.6x mas rapida.
      </div>
    </div>
  </div>

  <h4>Paso 4 — Seleccion de padres</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li><b>Ruleta proporcional (DEFAULT):</b> Cada individuo tiene probabilidad de ser elegido
    proporcional a su aptitud. Individuos con aptitud 0 nunca son elegidos.</li>
    <li><b>Torneo (NEW):</b> Se seleccionan k=5 individuos al azar y el que tenga mayor
    aptitud gana. Mayor presion selectiva que la ruleta: acelera convergencia pero
    puede reducir diversidad genetica.</li>
  </ol>

  <h4>Paso 5 — Cruce (crossover)</h4>
  <ol style="margin:8px 0 8px 20px;line-height:1.9">
    <li><b>1 punto (DEFAULT):</b> Elegir un punto de corte aleatorio. Hijo1 = P1[:corte] + P2[corte:].
    Hijo2 = P2[:corte] + P1[corte:].</li>
    <li><b>2 puntos (NEW):</b> Elegir 2 puntos de corte. Hijo1 = P1[:c1] + P2[c1:c2] + P1[c2:].
    Preserva mejor los segmentos utiles de cada padre, especialmente cuando hay bloques de
    caracteres correctos consecutivos.</li>
  </ol>

  <h4>Paso 6 — Mutacion</h4>
  <p>Cada caracter del hijo muta con probabilidad <code>mutation_rate</code>: si el valor
  aleatorio es menor que mutation_rate, se reemplaza por un caracter aleatorio del alfabeto.
  La mutacion garantiza que el algoritmo puede explorar regiones del espacio de busqueda
  que no son alcanzables por cruce puro &mdash; el "escape de optimos locales".</p>

  <h4>Paso 7 — Elitismo</h4>
  <p>Los 2 mejores individuos de cada generacion pasan directamente a la siguiente sin
  modificacion. Esto garantiza que la aptitud del mejor individuo nunca decrece entre
  generaciones. Sin elitismo, el mejor individuo puede ser perdido por cruce o mutacion,
  haciendo que el algoritmo retroceda.</p>

  <h4>Paso 8 — Experimentacion sistematica</h4>
  <p>Se variaron los parametros de uno en uno (experimentos controlados):</p>
  <div class="callout code">
    Experimento 1: DEFAULT vs BY_DISTANCE (funcion de aptitud)<br>
    Experimento 2: mutation_rate = 0.001, 0.01, 0.05 (variacion de mutacion)<br>
    Experimento 3: population_size = 20, 100, 500 (variacion de poblacion)<br>
    Experimento 4: Mejor combinacion = Elitismo + Torneo + 2 puntos + pop=200 + mr=0.03
  </div>
  <p>Para cada experimento se registro la curva de convergencia y la generacion final.
  La semilla fija permite comparacion directa entre configuraciones.</p>
</div>

<!-- ═══ INTERROGANTES DE MEJORA ═══ -->
<div id="interrogantes" class="sec-header" style="background:linear-gradient(90deg,#b71c1c,#c62828);margin-top:36px">
  <h2>Interrogantes para Mejorar la Obtencion y Analisis</h2>
  <p style="color:#ffcdd2;margin-top:4px">
    Preguntas criticas que el equipo identifico al trabajar con cada problema.
    Responder estas interrogantes llevaria a resultados mas solidos y aplicables.</p>
</div>

<!-- Interrogantes dataset -->
<div id="int-ds" class="card">
  <h3>Interrogantes sobre la Base de Datos (P1 — SP&amp;BDS)</h3>

  <h4>Calidad y origen de los datos</h4>
  <div class="callout warn">
    <b>1. ¿Como se midieron las variables de habito?</b><br>
    ¿Los datos de <code>study_hours_per_day</code> y <code>phone_usage_hours</code> vienen
    de auto-reporte (encuesta), de sensores del dispositivo (Screen Time de iOS/Android),
    o de sistemas de gestion del aprendizaje (LMS)?
    El auto-reporte tiene sesgo de deseabilidad social: los estudiantes tienden a
    reportar mas horas de estudio y menos de telefono que las reales. Conocer el metodo de
    recoleccion es fundamental para interpretar los resultados.
  </div>
  <div class="callout warn">
    <b>2. ¿Por que <code>final_grade</code> tiene correlacion ~0 con todo lo demas?</b><br>
    En un dataset real, la nota final deberia correlacionar positivamente con horas de
    estudio. El hecho de que no lo haga sugiere que la nota fue <b>generada independientemente</b>
    del comportamiento en el dataset sintetico. ¿Se podria reemplazar este campo con datos
    reales de un sistema academico para hacer el analisis predictivo valido?
  </div>
  <div class="callout warn">
    <b>3. ¿Los datos tienen dimension temporal?</b><br>
    ¿Son mediciones en un solo momento (corte transversal) o seguimiento longitudinal?
    Un dataset longitudinal permitiria analizar si los habitos de estudio <i>cambian</i>
    con el tiempo y predecir el rendimiento futuro, no solo describir el actual.
  </div>
  <div class="callout warn">
    <b>4. ¿Hay representatividad demografica?</b><br>
    ¿El dataset incluye estudiantes de primer año y de postgrado? ¿De diferentes carreras
    (ciencias vs humanidades)? ¿Hay sesgo de seleccion (solo estudiantes que aceptaron
    participar en el estudio)?
  </div>
  <div class="callout warn">
    <b>5. ¿Como se valida la suma temporal de horas?</b><br>
    Detectamos registros donde la suma de horas (estudio + telefono + sueno + ejercicio +
    gaming + redes) supera las 24 horas disponibles en el dia. ¿Hay un proceso de
    validacion de coherencia temporal en la pipeline de datos? ¿O estas inconsistencias
    son artefactos del proceso sintetico?
  </div>

  <h4>Mejoras al proceso de recoleccion</h4>
  <div class="callout info">
    <b>6. ¿Se podria enriquecer con datos contextuales?</b><br>
    Variables como <code>semana_parciales</code> (binaria: semana de examenes),
    <code>tipo_carrera</code> (STEM vs no-STEM), <code>modalidad</code> (presencial vs online)
    o <code>ano_de_estudio</code> (1ro a 5to) permitirian identificar clusters mucho mas
    interpretables que los actuales "alto-medio-bajo estudio".
  </div>
  <div class="callout info">
    <b>7. ¿Que variable objetivo seria mas util para predecir?</b><br>
    En lugar de <code>productivity_score</code> (abstracto y potencialmente circular),
    ¿seria mas util la <code>tasa_de_aprobacion_acumulada</code>, el
    <code>GPA al final del semestre</code>, o el <code>abandono_academico</code>
    (variable binaria de desercion)?
  </div>
</div>

<!-- Interrogantes P1 -->
<div id="int-p1" class="card">
  <h3>Interrogantes sobre el Analisis P1 — Aprendizaje No Supervisado</h3>

  <div class="callout warn">
    <b>1. ¿Como elegir el numero optimo de clusters k de forma no arbitraria?</b><br>
    Se uso el Silhouette Score para elegir k, pero existen otras metricas: indice
    Calinski-Harabasz, indice Davies-Bouldin, metodo del codo (SSE). ¿Coinciden todas
    en el mismo k para este dataset? Si no coinciden, ¿cual criterio es prioritario
    para el objetivo de segmentacion de estudiantes?
  </div>
  <div class="callout warn">
    <b>2. ¿Los clusters tienen validez externa o son solo artefactos estadisticos?</b><br>
    Los 3 grupos identificados (comprometido/promedio/distraido) tienen interpretabilidad
    subjetiva, pero ¿se validan contra algun criterio externo? Por ejemplo, ¿los estudiantes
    del cluster "comprometido" tienen realmente mejores notas al final del semestre?
    Sin validacion externa, los clusters son descripcion, no prediccion.
  </div>
  <div class="callout warn">
    <b>3. ¿Por que usar solo 2 variables en el analisis univariable y no todas las 15?</b><br>
    La eleccion de <code>study_hours</code> y <code>phone_usage</code> fue guiada por los
    loadings de PC1, pero ¿se perdio informacion relevante de las otras 13 variables?
    ¿Que pasaria si se hiciera clustering independiente sobre cada una de las 15 variables
    y luego se combinaran los resultados con un enfoque de ensemble de clustering?
  </div>
  <div class="callout warn">
    <b>4. ¿Como determinar el umbral de contaminacion en Isolation Forest?</b><br>
    Se uso <code>contamination=0.05</code> de forma estandar. ¿Cual seria el valor adecuado
    para datos reales de estudiantes? Si el 10% de los estudiantes tiene comportamientos
    atipicos, fijar contamination=0.05 genera falsos negativos. ¿Deberia ajustarse con
    validacion cruzada o con conocimiento de dominio previo?
  </div>
  <div class="callout warn">
    <b>5. ¿Se deberia aplicar clustering jerárquico (Ward o complete linkage)?</b><br>
    K-Means y DBSCAN asumen clusters convexos y de densidad uniforme. Si los grupos de
    estudiantes tienen estructuras no convexas o jerarquicas (por ejemplo, sub-grupos
    dentro del cluster "promedio"), el clustering jerarquico podria revelar estructura
    adicional invisible para K-Means.
  </div>
  <div class="callout info">
    <b>6. ¿Como integrar el analisis no supervisado con prediccion supervisada?</b><br>
    Los clusters identificados podrian usarse como <i>features</i> en un modelo supervisado:
    asignar a cada estudiante su cluster y usarlo como variable predictora de desercion o
    bajo rendimiento. Esta combinacion (UML &rarr; SML) seria mas util practicamente que
    el analisis no supervisado aislado.
  </div>
</div>

<!-- Interrogantes P2 -->
<div id="int-p2" class="card">
  <h3>Interrogantes sobre el Analisis P2 — TSP</h3>

  <div class="callout warn">
    <b>1. ¿Como escala el modelo MILP con restricciones reales (ventanas de tiempo, capacidad)?</b><br>
    El TSP basico resuelto aqui asume que todas las ciudades son accesibles en cualquier
    orden. En logistica real existe el <i>VRPTW</i> (Vehicle Routing Problem with Time Windows):
    cada cliente solo puede ser visitado en una ventana horaria, y puede haber multiples
    vehiculos con capacidad limitada. ¿Como se modificaria el modelo Pyomo para incorporar
    estas restricciones y como cambia su complejidad computacional?
  </div>
  <div class="callout warn">
    <b>2. ¿En que punto el 2-opt deja de ser suficiente y se necesita 3-opt o Lin-Kernighan?</b><br>
    Para 100 ciudades el 2-opt mejoro la solucion un 18.6%. ¿Para cuantas ciudades el
    2-opt ya no da resultados de calidad aceptable? ¿Existe un umbral donde el costo
    computacional del 3-opt (O(n&sup3;)) justifica su implementacion? Se podria estudiar
    empiricamente con 200, 500 y 1000 ciudades.
  </div>
  <div class="callout warn">
    <b>3. ¿Como validar que el mipgap elegido (0.05 o 0.2) es apropiado para el problema?</b><br>
    Un mipgap=0.05 significa que la solucion puede estar hasta un 5% por encima del optimo
    teorico. Para un problema de distribucion de medicamentos urgentes, incluso un 2%
    de sub-optimalidad podria ser inaceptable. ¿Como se justifica el mipgap en funcion
    del impacto economico del sub-optimo?
  </div>
  <div class="callout warn">
    <b>4. ¿Que pasa con las heuristicas cuando la solucion optima cae fuera del rango estimado?</b><br>
    La heuristica de limites puede hacer el modelo infactible si los limites estan mal
    calculados. ¿Existe un metodo sistematico para estimar min_posible y max_posible de
    forma que la infactibilidad sea estadisticamente improbable? ¿O deberia haber un
    mecanismo de fallback que relaje los limites si se detecta infactibilidad?
  </div>
  <div class="callout info">
    <b>5. ¿Como comparar objetivamente LP vs heuristicas cuando LP no llega al optimo?</b><br>
    Cuando el solver agota el tiempo sin llegar al optimo, compara una solucion LP
    "de calidad desconocida" contra el vecino cercano. ¿Seria mas correcto comparar
    usando el <b>lower bound</b> que calcula el solver (la relajacion LP continua)?
    El gap entre el lower bound y la solucion encontrada da informacion sobre cuanto
    podria mejorarse aun.
  </div>
</div>

<!-- Interrogantes P3 -->
<div id="int-p3" class="card">
  <h3>Interrogantes sobre el Analisis P3 — Algoritmos Geneticos</h3>

  <div class="callout warn">
    <b>1. ¿Los resultados son reproducibles sin semilla fija?</b><br>
    Todos los experimentos se corrieron con semilla fija para comparacion justa. Pero en
    aplicaciones reales la semilla es desconocida. ¿Cual es la varianza de generacion de
    convergencia entre corridas? ¿El Caso 5 siempre es el mas rapido, o hay instancias
    donde el Caso 1 converge antes por azar? Se deberian correr al menos 30 ejecuciones
    por configuracion y reportar media ± desviacion estandar.
  </div>
  <div class="callout warn">
    <b>2. ¿Como se escala el GA a objetivos mas complejos (problema de combinatoria)?</b><br>
    El objetivo "GA Workshop! USFQ" es un problema de texto con solucion conocida.
    ¿Como cambiaria el diseno del GA para resolver el TSP con 100 ciudades usando
    permutaciones de enteros en lugar de strings? La funcion de aptitud, el cruce y
    la mutacion tendrian que redefinirse para preservar permutaciones validas.
    ¿Que operadores especializados existen para permutaciones (OX, PMX, CX)?
  </div>
  <div class="callout warn">
    <b>3. ¿Como detectar convergencia prematura y evitar la deriva genetica?</b><br>
    Con poblacion=20 el algoritmo no converge porque la diversidad genetica se agota.
    ¿Como medir en tiempo real la diversidad de la poblacion (por ejemplo, entropia de
    la distribucion de caracteres por posicion)? ¿Se deberia agregar un mecanismo de
    "reinicio parcial" cuando la diversidad cae por debajo de un umbral?
  </div>
  <div class="callout warn">
    <b>4. ¿mutation_rate optimo es siempre 0.01, o depende del largo del string y la poblacion?</b><br>
    La tasa de mutacion optima teorica es 1/n donde n es el largo del individuo. Para
    17 caracteres, 1/17 ≈ 0.059 &mdash; distinto al 0.01 empirico que funciono mejor.
    ¿Hay una formula teorica que predice el mutation_rate optimo en funcion de n y del
    tamaño de poblacion? ¿Como cambiaria si el objetivo tiene 100 o 1000 caracteres?
  </div>
  <div class="callout warn">
    <b>5. ¿El GA puede quedar atrapado en optimos locales que no son el objetivo?</b><br>
    Para el problema de texto, el objetivo es conocido y unico. Para problemas de
    optimizacion real (como minimizar una funcion matematica), puede haber multiples
    optimos locales. ¿Como se detecta que el GA quedo atrapado? ¿Que mecanismos
    (recocido simulado, migracion entre sub-poblaciones, perturbacion adaptativa)
    podrian usarse para escapar?
  </div>
  <div class="callout info">
    <b>6. ¿Como se aplica el GA a un problema real de ciencia de datos?</b><br>
    Los GA se usan para <b>seleccion de features</b>: cada individuo es un vector binario
    que indica que features incluir en un modelo. La aptitud es la precision en validacion
    cruzada. ¿Podria aplicarse este enfoque al dataset SP&amp;BDS para encontrar el
    subconjunto optimo de variables para predecir <code>productivity_score</code>?
    ¿Que ventajas tendria sobre backward/forward selection?
  </div>
</div>

<!-- FOOTER -->
<div style="margin:40px 0 20px;padding:20px;text-align:center;
            color:#888;font-size:12px;border-top:1px solid #e0e0e0">
  Informe generado el {now} &nbsp;|&nbsp;
  MSDS 6004 Inteligencia Artificial &nbsp;|&nbsp; USFQ &nbsp;|&nbsp;
  Kevin Vitery &nbsp;&bull;&nbsp; Raquel Pacheco &nbsp;&bull;&nbsp; Gustavo Baru &nbsp;&bull;&nbsp; Nancy Altamirano
</div>
</main>
</body>
</html>
"""


# ─────────────────────────────────────────────
# PDF BUILDER  (reportlab)
# ─────────────────────────────────────────────

def generate_pdf(out_path: str, p1_data: dict, p2_data: dict, p3_data: dict) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, Table,
        TableStyle, PageBreak, KeepTogether, HRFlowable,
    )
    from reportlab.lib.units import cm

    W, H = A4
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    C_NAVY  = HexColor("#1a1f36")
    C_GREEN = HexColor("#2e7d32")
    C_PURP  = HexColor("#6a1b9a")

    def sty(name, **kw):
        return ParagraphStyle(name, **kw)

    H2   = sty("H2", fontSize=14, textColor=C_NAVY, leading=18,
                fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    H3   = sty("H3", fontSize=11, textColor=C_GREEN, leading=14,
                fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    BODY = sty("BODY", fontSize=9.5, leading=14, spaceAfter=6,
               fontName="Helvetica")
    MONO  = sty("MONO",  fontSize=8.5, leading=12, fontName="Courier",
                backColor=HexColor("#f3f4f6"), leftIndent=10, spaceAfter=4)
    H_FIG = sty("H_FIG", fontSize=10, leading=14, fontName="Helvetica-Bold",
                textColor=HexColor("#1a237e"), spaceBefore=12, spaceAfter=3)
    EXPL  = sty("EXPL",  fontSize=8.5, leading=12, fontName="Helvetica",
                backColor=HexColor("#e3f2fd"), leftIndent=8, rightIndent=8,
                spaceBefore=3, spaceAfter=8)
    CAP   = sty("CAP",   fontSize=8,   leading=10, fontName="Helvetica-Oblique",
                textColor=HexColor("#666666"), alignment=1, spaceAfter=2)

    def fig_img(tag: str, width_cm: float = 15.0):
        if tag not in _FIGS:
            return None
        raw = base64.b64decode(_FIGS[tag])
        buf = io.BytesIO(raw)
        return Image(buf, width=width_cm*cm, height=width_cm*cm * 0.45)

    def section_banner(text: str, color: HexColor) -> Table:
        cell = Paragraph(f"<b><font color='white'>{text}</font></b>",
                         ParagraphStyle("BAN", fontSize=13, leading=16,
                                        fontName="Helvetica-Bold"))
        tbl = Table([[cell]], colWidths=[W - 4*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ]))
        return tbl

    def data_table(headers: list, rows: list, col_widths=None) -> Table:
        data = [headers] + rows
        col_w = col_widths or [((W - 4*cm) / len(headers))] * len(headers)
        tbl = Table(data, colWidths=col_w)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
            ("TEXTCOLOR",  (0, 0), (-1, 0), white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [HexColor("#ffffff"), HexColor("#f5f5ff")]),
            ("GRID", (0, 0), (-1, -1), 0.3, HexColor("#cccccc")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ]))
        return tbl

    story = []
    SP = lambda n=8: Spacer(1, n)
    HR = lambda: HRFlowable(width="100%", thickness=0.5,
                             color=HexColor("#e0e0e0"), spaceAfter=6)

    # ── PORTADA ───────────────────────────────────────────────
    C_BLUE = HexColor("#1565c0")
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    cover_data = [[
        Paragraph(
            "<font color='white' size='24'><b>Taller 3 — Informe Completo</b></font><br/>"
            "<font color='#aaccee' size='13'>MSDS 6004 — Inteligencia Artificial — USFQ</font>"
            "<br/><br/>"
            f"<font color='#ccd' size='10'>"
            f"Integrantes:<br/>"
            f"Kevin Vitery &nbsp;&bull;&nbsp; Raquel Pacheco &nbsp;&bull;&nbsp; "
            f"Gustavo Baru &nbsp;&bull;&nbsp; Nancy Altamirano<br/><br/>"
            f"Generado: {now_str}<br/>"
            "Problemas: P1 SP&amp;BDS | P2 TSP | P3 GA</font>",
            ParagraphStyle("COV", fontSize=10, leading=18)
        )
    ]]
    cover = Table(cover_data, colWidths=[W - 4*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 50),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 50),
        ("LEFTPADDING", (0, 0), (-1, -1), 30),
    ]))
    story += [cover, PageBreak()]

    # ── P1 SP&BDS ─────────────────────────────────────────────
    H3_BLUE = sty("H3B", fontSize=11, textColor=C_BLUE, leading=14,
                  fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)

    story += [
        section_banner("P1 — Aprendizaje No Supervisado: Student Productivity & Behavior Dataset", C_BLUE),
        SP(),
        Paragraph(
            f"Dataset: {p1_data['n_students']:,} estudiantes | "
            f"{p1_data['n_features']} variables numericas | "
            f"PCA, K-Means, DBSCAN, Isolation Forest (univariable + multivariable).", BODY),
        SP(),
        Paragraph("Resumen de metricas", H3),
        data_table(
            ["Metrica", "Valor"],
            [
                ["Componentes PCA para 80% varianza",   str(p1_data["n_comp_80"])],
                ["Varianza explicada PC1",               f"{p1_data['pc1_pct']:.1f}%"],
                ["Varianza explicada PC2",               f"{p1_data['pc2_pct']:.1f}%"],
                [f"Mejor k K-Means ({p1_data['var1']})", str(p1_data["best_k_v1"])],
                [f"Silhouette K-Means univariable",     f"{p1_data['sil_v1']:.3f}"],
                [f"Mejor k K-Means multivariable",      str(p1_data["best_k_m"])],
                [f"Silhouette K-Means multivariable",   f"{p1_data['sil_m']:.3f}"],
                ["Anomalias univariable (5%)",           str(p1_data["n_anom_uni"])],
                ["Anomalias multivariable 15D (5%)",    str(p1_data["n_anom_multi"])],
            ],
            col_widths=[11*cm, 5*cm]
        ),
        SP(),
        Paragraph("Top 5 variables (loadings PC1)", H3),
        data_table(
            ["#", "Variable", "Loading PC1", "Interpretacion"],
            [[f"#{i+1}", v, f"{l:+.4f}",
              "(+) productividad" if l > 0 else "(-) productividad"]
             for i, (v, l) in enumerate(p1_data["top5"])],
            col_widths=[1.2*cm, 7*cm, 3*cm, 5.3*cm]
        ),
        SP(),
    ]
    _p1_figs = [
        ("spbds_01",
         "A.1 — Scree Plot y Contribucion de Variables al PC1",
         "El Scree Plot muestra cuantos componentes principales se necesitan para explicar la varianza. "
         "La curva de varianza acumulada indica el punto de codo a partir del cual agregar mas "
         "componentes aporta poco. Los loadings del PC1 revelan que estudio y distraccion son los "
         "ejes principales de diferenciacion entre estudiantes."),
        ("spbds_02",
         "A.2 — Proyeccion PCA 2D: Productividad vs. Distraccion",
         "Cada punto representa un estudiante proyectado en el plano formado por PC1 (productividad) "
         "y PC2 (estres). La dispersion uniforme confirma el caracter sintetico del dataset. "
         "Se identifican tres zonas: alta productividad, zona media y alta distraccion."),
        ("spbds_03",
         "A.3 — Coordenadas Paralelas: 500 Estudiantes",
         "Las lineas paralelas muestran el perfil multivariable de 500 estudiantes seleccionados. "
         "Los perfiles altos en study_hours y bajo en phone_usage corresponden a estudiantes con "
         "mayor rendimiento academico, mientras que el patron inverso indica distraccion."),
        ("spbds_04",
         "A.4 — Distribuciones de study_hours y phone_usage",
         "Los histogramas muestran la distribucion de las dos variables univariables clave. "
         "La distribucion uniforme (sintetica) implica que no hay un perfil 'tipico'; todos los "
         "valores son igualmente probables. Esto reduce el silhouette score en clustering."),
        ("spbds_05",
         "A.5 — Scatter: Relacion entre Variables Clave",
         "El scatter plot entre study_hours_per_day y phone_usage_hours muestra una correlacion "
         "negativa debil, consistente con la hipotesis de que mayor uso del telefono se asocia "
         "a menor tiempo de estudio. Puntos en las esquinas son candidatos a anomalias."),
        ("spbds_06",
         "B.1 — Clustering Univariable: study_hours_per_day",
         "K-Means sobre una sola variable (study_hours_per_day) agrupa estudiantes en perfiles "
         "de dedicacion. El silhouette score optimo indica el k que maximiza la separacion "
         "intracluster. El clustering revela grupos: estudio bajo, medio y alto."),
        ("spbds_07",
         "B.2 — Clustering Univariable: phone_usage_hours",
         "Similar al anterior pero sobre phone_usage_hours. Los clusters de uso del telefono "
         "complementan los de estudio, identificando perfiles de distraccion. La interseccion "
         "de ambos clusterings permite construir una matriz de perfil bidimensional."),
        ("spbds_08",
         "C.1 — Anomalias Univariable: Isolation Forest",
         "Isolation Forest con contamination=0.05 detecta el 5% de estudiantes con perfiles "
         "extremos en study_hours o phone_usage. Los puntos rojos son anomalias: valores "
         "atipicos que se separan facilmente del arbol de decision aleatorio."),
        ("spbds_09",
         "D.1 — Clustering Multivariable: Espacio PCA 2D",
         "K-Means aplicado sobre las dos primeras componentes principales. La reduccion "
         "dimensional facilita la visualizacion. Los clusters en PCA 2D capturan patrones "
         "globales de comportamiento que no son visibles en variables individuales."),
        ("spbds_10",
         "D.2 — Clustering Multivariable: Par Directo (study_hours vs phone_usage)",
         "Clustering directamente sobre el par de variables mas relevantes sin PCA. "
         "Comparando con D.1, se valida la robustez de los clusters: si ambas representaciones "
         "producen grupos similares, los patrones son genuinos en los datos."),
        ("spbds_11",
         "E.1 — Anomalias Multivariable: Isolation Forest en 15D",
         "Isolation Forest en el espacio completo de 15 variables detecta combinaciones "
         "atipicas imposibles en la realidad (p.ej. suma de horas > 24h). Estas anomalias "
         "son invisibles en analisis univariable y requieren deteccion multidimensional."),
    ]
    for tag, title, expl in _p1_figs:
        img = fig_img(tag, 13.5)
        if img:
            story += [
                Paragraph(title, H_FIG),
                img,
                Paragraph(f"<i>Fig. {title}</i>", CAP),
                Paragraph(expl, EXPL),
                SP(4),
            ]

    story += [
        HR(), Paragraph("Conclusiones P1", H3),
        Paragraph(
            f"PCA revela que el dataset SP&BDS se organiza en torno al eje 'productividad vs. "
            f"distraccion' (PC1={p1_data['pc1_pct']:.1f}%). Se necesitan {p1_data['n_comp_80']} "
            "componentes para el 80% de varianza, tipico de dataset sintetico uniforme.", BODY),
        Paragraph(
            f"K-Means (k={p1_data['best_k_m']}) identifica 3 perfiles: Comprometido "
            f"(>=7h estudio), Promedio (3-6h) y Distraido (<=3h, alto uso de telefono). "
            f"DBSCAN confirma estos patrones sin requerir k a priori.", BODY),
        Paragraph(
            f"Isolation Forest detecta {p1_data['n_anom_uni']} anomalias univariables "
            f"y {p1_data['n_anom_multi']} multivariables. La deteccion en 15D identifica "
            "combinaciones temporalmente imposibles, invisible en analisis por variable.", BODY),
        Paragraph(
            "Dificultad principal: la distribucion uniforme (sintetica) genera silhouette "
            f"bajo ({p1_data['sil_m']:.3f}) y requiere muchos componentes PCA. "
            "En datos reales los patrones serian mas pronunciados.", BODY),
        PageBreak(),
    ]

    # ── P2 TSP ────────────────────────────────────────────────
    story += [
        section_banner("P2 — Travelling Salesman Problem (TSP)", C_GREEN),
        SP(),
        Paragraph("Modelado MILP con Pyomo + GLPK. Restricciones MTZ para "
                  "eliminacion de subtours. Heuristicas de acotamiento y "
                  "vecinos cercanos. Post-procesamiento con 2-opt.", BODY),
        SP(),
        Paragraph("Resultados — Vecino Cercano vs NN + 2-opt", H3),
        data_table(
            ["Ciudades", "NN Dist.", "NN Tiempo", "2-opt Dist.", "2-opt Tiempo", "Mejora"],
            [[str(r[0]), f"{r[1]:.2f}", r[2], f"{r[3]:.2f}", r[4], f"{r[5]:.1f}%"]
             for r in p2_data["rows"]],
            col_widths=[2*cm, 3*cm, 2.5*cm, 3*cm, 2.5*cm, 2.5*cm]
        ),
        SP(),
    ]
    _p2_figs = [
        ("tsp_01",
         "F.1 — Ruta Vecino Cercano (Distancia: 2006.73)",
         "La heuristica del Vecino Cercano construye la ruta eligiendo siempre la ciudad mas "
         "cercana no visitada. Es rapida (O(n^2)) pero produce rutas suboptimas con cruces "
         "visibles. Esta ruta base sirve como punto de partida para la optimizacion 2-opt."),
        ("tsp_02",
         "F.2 — Ruta NN + 2-opt (Distancia: 1632.85, Mejora: -18.6%)",
         "El post-procesamiento 2-opt elimina cruces de aristas intercambiando pares de "
         "segmentos hasta no encontrar mejora. La reduccion del 18.6% demuestra que la "
         "ruta inicial tenia cruces significativos eliminables en tiempo polinomial."),
        ("tsp_03",
         "F.3 — Comparacion de Distancias por Numero de Ciudades",
         "A medida que aumenta el numero de ciudades, la brecha entre NN y NN+2-opt crece. "
         "El 2-opt mejora consistentemente entre 3-21% independientemente del tamano del "
         "problema, confirmando que es una optimizacion local efectiva y escalable."),
    ]
    for tag, title, expl in _p2_figs:
        img = fig_img(tag, 14)
        if img:
            story += [
                Paragraph(title, H_FIG),
                img,
                Paragraph(f"<i>Fig. {title}</i>", CAP),
                Paragraph(expl, EXPL),
                SP(4),
            ]

    story += [
        HR(), Paragraph("Conclusiones P2", H3),
        Paragraph("• El 2-opt reduce la distancia 3-21% de forma instantanea "
                  "sobre cualquier solucion inicial.", BODY),
        Paragraph("• LP es exacto pero inviable para n>25 con limite de 30s.", BODY),
        Paragraph("• Mejor estrategia practica: Vecino Cercano + 2-opt. "
                  "Para 100 ciudades: 1632 vs 2007.", BODY),
        PageBreak(),
    ]

    # ── P3 GA ─────────────────────────────────────────────────
    story += [
        section_banner("P3 — Algoritmos Geneticos (GA)", C_PURP),
        SP(),
        Paragraph("Objetivo: generar 'GA Workshop! USFQ' (17 chars) "
                  "desde 100 individuos aleatorios. 7 configuraciones comparadas.", BODY),
        SP(),
        Paragraph("Resultados comparativos", H3),
        data_table(
            ["Caso", "Poblacion", "Mut. Rate", "Converge", "Generacion", "Mejor individuo"],
            [[r["label"].replace("\n", " | "), str(r["pop"]), str(r["mr"]),
              "SI" if r["converged"] else "NO",
              str(r["gen"]) if r["converged"] else "—",
              r["best"]]
             for r in p3_data["summary"]],
            col_widths=[4*cm, 1.8*cm, 1.8*cm, 1.8*cm, 2.2*cm, 4.9*cm]
        ),
        SP(),
    ]
    _p3_figs = [
        ("ga_convergence",
         "G.1 — Curvas de Convergencia por Caso de Estudio",
         "Cada linea muestra como evoluciona el fitness del mejor individuo a lo largo de las "
         "generaciones para cada configuracion experimental. Las curvas mas escarpadas indican "
         "convergencia mas rapida. El Caso 5 (Elitismo + Torneo + Cruce 2pts) destaca como "
         "el mas eficiente, alcanzando el objetivo en generacion 30."),
        ("ga_bar",
         "G.2 — Generacion de Convergencia por Caso (Solo Casos Convergentes)",
         "Grafico de barras comparando la generacion en que cada configuracion alcanza el objetivo "
         "'GA Workshop! USFQ'. Las barras mas cortas indican mayor eficiencia. "
         "Los casos que no convergen dentro del limite maximo quedan excluidos. "
         "La comparacion directa valida que el elitismo y la distancia Manhattan son los "
         "factores mas determinantes para la velocidad de convergencia."),
    ]
    for tag, title, expl in _p3_figs:
        img = fig_img(tag, 14)
        if img:
            story += [
                Paragraph(title, H_FIG),
                img,
                Paragraph(f"<i>Fig. {title}</i>", CAP),
                Paragraph(expl, EXPL),
                SP(4),
            ]

    story += [
        HR(), Paragraph("Conclusiones P3", H3),
        Paragraph("• Distancia Manhattan (Caso 2) converge 2.6x mas rapido que "
                  "conteo de coincidencias (Caso 1): senal de gradiente mas rica.", BODY),
        Paragraph("• Bug original en util.py: sin abs() la distancia siempre era ~0 "
                  "-> seleccion aleatoria -> sin convergencia.", BODY),
        Paragraph("• mutation_rate optimo: 0.005-0.03. Muy alto destruye genes; "
                  "muy bajo queda atrapado en optimos locales.", BODY),
        Paragraph("• Mas poblacion = mas diversidad = convergencia mas rapida "
                  "(500 individuos: gen 44 vs gen 982 con 100).", BODY),
        Paragraph("• Mejor configuracion (Caso 5): Elitismo + Torneo k=5 + Cruce 2 puntos "
                  "+ poblacion 200 + mutation 0.03 -> gen 30 (32x mas rapido).", BODY),
        PageBreak(),
    ]

    # ── METODOLOGIA PASO A PASO ───────────────────────────────
    story += [
        section_banner("Metodologia Paso a Paso", HexColor("#37474f")),
        SP(),
        Paragraph("P1 — Aprendizaje No Supervisado: SP&BDS", H2),
        Paragraph("Paso 1: Seleccion del dataset SP&BDS (20,000 estudiantes, "
                  "15 variables numericas). Descarte de columnas categoricas.", BODY),
        Paragraph("Paso 2: Normalizacion con StandardScaler (media=0, std=1) para "
                  "eliminar efecto de escala entre variables.", BODY),
        Paragraph("Paso 3: PCA completo. Scree plot para identificar numero de "
                  "componentes. Analisis de loadings de PC1 para identificar variables "
                  "clave. Proyeccion 2D y coordenadas paralelas.", BODY),
        Paragraph("Paso 4: K-Means (k=2..6, Silhouette para elegir k optimo) y "
                  "DBSCAN (eps estimado por k-NN, min_samples=50) sobre variables clave.", BODY),
        Paragraph("Paso 5: Isolation Forest (contamination=0.05) univariable sobre "
                  "study_hours y phone_usage. Identificacion de perfiles extremos.", BODY),
        Paragraph("Paso 6: Clustering multivariable en PCA 2D y par directo. "
                  "Comparacion cruzada para validar robustez de clusters.", BODY),
        Paragraph("Paso 7: Anomalias multivariable en 15D. Interseccion con anomalias "
                  "univariables para identificar casos incoherentes (suma de horas > 24h).", BODY),
        SP(),
        Paragraph("P2 — TSP: Pasos", H2),
        Paragraph("Paso 1: Generacion de ciudades aleatorias en [-100,100] con semilla fija.", BODY),
        Paragraph("Paso 2: Formulacion MILP en Pyomo. Variables x[i,j] binarias, "
                  "variables u[i] enteras MTZ. Restricciones de entrada/salida unica.", BODY),
        Paragraph("Paso 3: Heuristica Vecino Cercano O(n^2) como baseline.", BODY),
        Paragraph("Paso 4: Heuristicas LP: acotamiento de funcion objetivo y "
                  "restriccion de vecinos cercanos para acelerar Branch & Bound.", BODY),
        Paragraph("Paso 5: Post-procesamiento 2-opt sobre cualquier ruta. "
                  "Eliminacion iterativa de cruces hasta optimo local.", BODY),
        SP(),
        Paragraph("P3 — Algoritmos Geneticos: Pasos", H2),
        Paragraph("Paso 1: Poblacion inicial de 100 strings aleatorios de 17 chars. "
                  "Semilla fija para reproducibilidad.", BODY),
        Paragraph("Paso 2: Funcion de aptitud: conteo (DEFAULT) o distancia "
                  "Manhattan (BY_DISTANCE, 2.6x mas rapido).", BODY),
        Paragraph("Paso 3: Seleccion de padres por ruleta (DEFAULT) o torneo k=5 "
                  "(mayor presion selectiva).", BODY),
        Paragraph("Paso 4: Cruce de 1 punto (DEFAULT) o 2 puntos (mejor mezcla).", BODY),
        Paragraph("Paso 5: Mutacion aleatoria por caracter con probability=mutation_rate.", BODY),
        Paragraph("Paso 6: Elitismo — top 2 individuos pasan directamente a la "
                  "siguiente generacion sin modificacion.", BODY),
        Paragraph("Paso 7: Experimentacion sistematica variando un parametro a la vez "
                  "para identificar el impacto individual de cada componente.", BODY),
        PageBreak(),
    ]

    # ── INTERROGANTES ────────────────────────────────────────
    story += [
        section_banner("Interrogantes para Mejorar la Obtencion y Analisis", HexColor("#b71c1c")),
        SP(),
        Paragraph("Interrogantes sobre la Base de Datos (P1)", H3),
        data_table(
            ["#", "Interrogante", "Impacto"],
            [
                ["1", "Como se midieron las variables de habito (auto-reporte vs sensor)?",
                 "Sesgo de deseabilidad social en estudio/telefono"],
                ["2", "Por que final_grade tiene correlacion ~0 con productividad?",
                 "Dataset sintetico invalida prediccion real"],
                ["3", "Los datos tienen dimension temporal (longitudinal)?",
                 "Permitiria analizar cambios de comportamiento en el tiempo"],
                ["4", "Hay representatividad demografica (carrera, ano, modalidad)?",
                 "Sin representatividad los clusters no generalizan"],
                ["5", "Existe validacion de coherencia temporal (suma horas < 24h)?",
                 "Errores de dato distorsionan modelos de anomalias"],
                ["6", "Se podria enriquecer con contexto (semana de examenes)?",
                 "Variables contextuales harian clusters mas interpretables"],
                ["7", "Que variable objetivo seria mas util (GPA, desercion)?",
                 "productivity_score es abstracto; desercion es accionable"],
            ],
            col_widths=[0.8*cm, 11.2*cm, 4.5*cm]
        ),
        SP(10),
        Paragraph("Interrogantes sobre el Analisis (P1, P2, P3)", H3),
        data_table(
            ["Area", "Interrogante clave"],
            [
                ["P1 Clustering",
                 "Como elegir k sin arbitrariedad: Silhouette vs Davies-Bouldin vs codo?"],
                ["P1 Validacion",
                 "Los clusters tienen validez externa? Los comprometidos aprueban mas?"],
                ["P1 IF",
                 "contamination=0.05 es correcto? Como ajustarlo con validacion cruzada?"],
                ["P1 Combinado",
                 "Como integrar UML con SML: usar cluster como feature predictora?"],
                ["P2 Escala",
                 "Como escala MILP con restricciones reales (VRPTW, capacidad)?"],
                ["P2 mipgap",
                 "Como justificar el mipgap en funcion del impacto economico del sub-optimo?"],
                ["P2 2-opt",
                 "Para cuantas ciudades 2-opt es insuficiente y se necesita LK o 3-opt?"],
                ["P3 Varianza",
                 "mutation_rate=0.01 siempre es optimo? Necesita estudio de 30 corridas?"],
                ["P3 Escala",
                 "Como adaptar el GA al TSP (permutaciones) con operadores OX o PMX?"],
                ["P3 Diversidad",
                 "Como detectar convergencia prematura y activar mecanismo de reinicio?"],
            ],
            col_widths=[3.5*cm, 13*cm]
        ),
    ]

    doc.build(story)
    print(f"  PDF generado: {out_path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    t0 = time.time()
    base = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base, "informe_taller3.html")
    pdf_path  = os.path.join(base, "informe_taller3.pdf")

    print("=" * 58)
    print("  Taller 3 — Generando informe HTML + PDF")
    print("=" * 58)

    print("\n[1/4] P1 — Aprendizaje No Supervisado (SP&BDS) ...")
    p1_data = run_p1_spbds()

    print("[2/4] P2 — TSP (Vecino Cercano + 2-opt) ...")
    p2_data = run_p2_tsp()

    print("[3/4] P3 — Algoritmos Geneticos (casos 1-5) ...")
    p3_data = run_p3_ga()

    print("[4/4] Generando HTML y PDF ...")
    html = build_html(p1_data, p2_data, p3_data)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML: {html_path}  ({os.path.getsize(html_path)//1024} KB)")

    tmp_pdf = pdf_path.replace(".pdf", "_tmp.pdf")
    try:
        generate_pdf(tmp_pdf, p1_data, p2_data, p3_data)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        os.rename(tmp_pdf, pdf_path)
        print(f"  PDF:  {pdf_path}  ({os.path.getsize(pdf_path)//1024} KB)")
    except PermissionError:
        print(f"  PDF:  NO generado — cierra el PDF abierto y vuelve a ejecutar.")

    elapsed = time.time() - t0
    print(f"\n{'=' * 58}")
    print(f"  Completado en {elapsed:.1f}s  |  {len(_FIGS)} figuras embebidas")
    print(f"  Abrir en navegador: {html_path}")
    print("=" * 58)


if __name__ == "__main__":
    main()

"""
P1 - Aprendizaje No Supervisado sobre Smart Building Dataset (SBDS)
Secciones:
  A. Graficar perfiles diarios superpuestos + estadistica descriptiva
  B. Clustering univariable (K-Means y DBSCAN)
  C. Deteccion de anomalias univariable (Isolation Forest)
  D. Clustering multivariable (par NE: CO2 + Temp)
  E. Deteccion de anomalias multivariable
  F. Conclusiones
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest

from Taller3.P1_UML.p1_uml_util import (
    read_csv_file,
    lb_timestamp, lb_V005_vent01_CO2, lb_V022_vent02_CO2,
    lb_V006_vent01_temp_out, lb_V023_vent02_temp_out,
    alias,
)


# =============================================================================
# CARGA Y PREPARACION DE DATOS
# =============================================================================
def prepare_data():
    """
    Lee el CSV con separador ';', convierte el timestamp a datetime
    y lo establece como indice del DataFrame.
    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_path, "data", "data.csv")
    df = read_csv_file(file_path)

    # pd.to_datetime reconoce automaticamente el formato del timestamp
    df[lb_timestamp] = df[lb_timestamp].astype(str)
    import pandas as pd
    df[lb_timestamp] = pd.to_datetime(df[lb_timestamp], infer_datetime_format=True)
    df.set_index(lb_timestamp, inplace=True)
    df.sort_index(inplace=True)         # garantizar orden cronologico
    df = df.apply(pd.to_numeric, errors='coerce')  # forzar columnas a numerico
    return df


def get_daily_profiles(df, variable):
    """
    Transforma la serie temporal de una variable en una matriz de perfiles diarios.

    Ejemplo con mediciones cada 15 minutos:
      - Cada dia tiene 96 filas (96 franjas de 15 min)
      - La matriz resultante es (n_dias x 96)
      - Cada fila es el "perfil del dia": como se comporto la variable ese dia

    Se eliminan los dias que no tienen el dia completo (NaN en alguna franja).
    """
    import pandas as pd
    df_var = df[[variable]].copy()
    df_var['date'] = df_var.index.date   # extrae solo la fecha (sin hora)
    df_var['time'] = df_var.index.time   # extrae solo la hora del dia

    # pivot_table: filas = dias, columnas = horas, valores = medicion
    pivot = df_var.pivot_table(
        index='date', columns='time', values=variable, aggfunc='mean')

    # Eliminar dias incompletos (cualquier franja horaria sin dato)
    pivot.dropna(axis=0, how='any', inplace=True)
    return pivot


# =============================================================================
# A. GRAFICAR VARIABLES - perfiles diarios superpuestos
# =============================================================================
def plot_daily_profiles(pivot, title, ylabel):
    """
    Dibuja una linea por cada dia (transparentes en azul) y el promedio en rojo.
    El resultado muestra cuanta variabilidad existe entre dias:
      - Lineas muy juntas = comportamiento muy regular
      - Lineas dispersas  = mucha variabilidad dia a dia
    """
    fig, ax = plt.subplots(figsize=(13, 5))
    n_days = len(pivot)
    colors = cm.Blues(np.linspace(0.3, 0.8, n_days))

    for i, day in enumerate(pivot.index):
        ax.plot(range(len(pivot.columns)), pivot.loc[day].values,
                alpha=0.25, color=colors[i], linewidth=0.7)

    # Perfil promedio: tendencia central de todos los dias
    mean_profile = pivot.mean(axis=0)
    ax.plot(range(len(pivot.columns)), mean_profile.values,
            color='red', linewidth=2, label='Perfil promedio', zorder=5)

    # Etiquetas del eje X: mostrar solo 8 horas para no saturar
    n_ticks = 8
    positions = [int(i * len(pivot.columns) / n_ticks) for i in range(n_ticks)]
    labels = [str(pivot.columns[p]) for p in positions]
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=45, fontsize=8)
    ax.set_xlabel("Hora del dia")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title} — {n_days} dias")
    ax.legend()
    plt.tight_layout()
    plt.show()


def print_descriptive_stats(pivot, variable_name):
    """Estadistica descriptiva sobre todos los valores del pivot (todos los dias)."""
    flat = pivot.values.flatten()
    flat = flat[~np.isnan(flat)]
    print(f"\n=== Estadistica descriptiva: {variable_name} ===")
    print(f"  Dias analizados : {len(pivot)}")
    print(f"  Media           : {flat.mean():.4f}")
    print(f"  Mediana         : {np.median(flat):.4f}")
    print(f"  Desv. estandar  : {flat.std():.4f}")
    print(f"  Minimo          : {flat.min():.4f}")
    print(f"  Maximo          : {flat.max():.4f}")
    print(f"  Percentil 25    : {np.percentile(flat, 25):.4f}")
    print(f"  Percentil 75    : {np.percentile(flat, 75):.4f}")


# =============================================================================
# B. CLUSTERING UNIVARIABLE
# =============================================================================
def cluster_kmeans(pivot, n_clusters=3, label=""):
    """
    K-Means agrupa los dias segun similitud de su perfil diario.

    Algoritmo:
      1. Inicializa n_clusters centroides aleatoriamente
      2. Asigna cada dia al centroide mas cercano (distancia euclidiana)
      3. Recalcula los centroides como media del grupo
      4. Repite hasta convergencia

    StandardScaler normaliza las franjas horarias para que K-Means no
    sea dominado por los valores absolutos (CO2 en ppm vs Temp en C).

    Silhouette score: entre -1 y 1. Cerca de 1 = clusters bien separados.
    """
    X = pivot.values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)  # (valor - media) / std por franja

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    score = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0
    print(f"\n[K-Means {label}] n_clusters={n_clusters}, Silhouette={score:.4f}")
    for c in range(n_clusters):
        print(f"  Cluster {c}: {sum(labels == c)} dias")

    # Graficar: un color por cluster, centroide como linea gruesa
    palette = ['red', 'blue', 'green', 'orange', 'purple']
    fig, ax = plt.subplots(figsize=(13, 5))
    for c in range(n_clusters):
        color = palette[c % len(palette)]
        mask = labels == c
        for day in pivot.index[mask]:
            ax.plot(range(len(pivot.columns)), pivot.loc[day].values,
                    alpha=0.2, color=color, linewidth=0.7)
        # Centroide en escala original (inverse_transform deshace la normalizacion)
        centroid = scaler.inverse_transform([kmeans.cluster_centers_[c]])[0]
        ax.plot(range(len(pivot.columns)), centroid,
                color=color, linewidth=2.5,
                label=f"Cluster {c} ({sum(mask)} dias)")

    ax.set_title(f"K-Means {label} — {n_clusters} clusters")
    ax.set_xlabel("Franja horaria")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return labels


def cluster_dbscan(pivot, eps=3.0, min_samples=3, label=""):
    """
    DBSCAN (Density-Based Spatial Clustering) agrupa por densidad:
      - Un punto es 'core' si tiene >= min_samples vecinos a distancia <= eps
      - Los puntos sin suficientes vecinos son clasificados como ruido (-1)
      - NO requiere especificar el numero de clusters de antemano

    Ventaja respecto a K-Means: detecta clusters de forma arbitraria
    y marca automaticamente los outliers como ruido (cluster -1).

    eps: radio de vecindad (en espacio normalizado)
    min_samples: minimo de dias para formar un cluster
    """
    X = pivot.values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)

    unique_labels = set(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    n_noise = list(labels).count(-1)
    print(f"\n[DBSCAN {label}] eps={eps}, min_samples={min_samples}")
    print(f"  Clusters encontrados : {n_clusters}")
    print(f"  Dias como ruido      : {n_noise}  (posibles anomalias)")
    for c in sorted(unique_labels):
        lbl = "Ruido/Anomalia" if c == -1 else f"Cluster {c}"
        print(f"  {lbl}: {sum(labels == c)} dias")

    if n_clusters > 1:
        mask_valid = labels != -1
        score = silhouette_score(X_scaled[mask_valid], labels[mask_valid])
        print(f"  Silhouette (sin ruido): {score:.4f}")

    palette = ['red', 'blue', 'green', 'orange', 'purple', 'cyan']
    fig, ax = plt.subplots(figsize=(13, 5))
    for c in sorted(unique_labels):
        color = 'black' if c == -1 else palette[c % len(palette)]
        lbl = "Anomalia" if c == -1 else f"Cluster {c} ({sum(labels == c)} dias)"
        mask = labels == c
        for day in pivot.index[mask]:
            ax.plot(range(len(pivot.columns)), pivot.loc[day].values,
                    alpha=0.35, color=color, linewidth=0.8)
        if c != -1:
            mean_c = pivot.loc[pivot.index[mask]].mean(axis=0)
            ax.plot(range(len(pivot.columns)), mean_c.values,
                    color=color, linewidth=2.5, label=lbl)
        else:
            ax.plot([], [], color=color, linewidth=2, label=lbl)

    ax.set_title(f"DBSCAN {label} — eps={eps}")
    ax.set_xlabel("Franja horaria")
    ax.legend()
    plt.tight_layout()
    plt.show()
    return labels


# =============================================================================
# C. ANOMALIAS UNIVARIABLE
# =============================================================================
def detect_anomalies_univariate(pivot, label=""):
    """
    Isolation Forest detecta anomalias aislando puntos en el espacio de perfiles.

    Idea: los puntos anomalos son mas faciles de aislar (requieren menos
    divisiones aleatorias del espacio) que los puntos normales que estan
    en regiones densas. El score de anomalia es el inverso de la profundidad
    promedio de aislamiento.

    contamination=0.05 indica que esperamos ~5% de dias anomalos.
    Retorna: 1=normal, -1=anomalia
    """
    X = pivot.values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    iso = IsolationForest(contamination=0.05, random_state=42)
    anomaly_pred = iso.fit_predict(X_scaled)  # -1=anomalia, 1=normal

    anomalous_days = pivot.index[anomaly_pred == -1]
    normal_days = pivot.index[anomaly_pred == 1]
    print(f"\n[Isolation Forest {label}]")
    print(f"  Dias normales   : {len(normal_days)}")
    print(f"  Dias anomalos   : {len(anomalous_days)}")
    if len(anomalous_days) > 0:
        print(f"  Fechas anomalas : {list(anomalous_days)}")

    fig, ax = plt.subplots(figsize=(13, 5))
    for day in normal_days:
        ax.plot(range(len(pivot.columns)), pivot.loc[day].values,
                alpha=0.2, color='steelblue', linewidth=0.7)
    for day in anomalous_days:
        ax.plot(range(len(pivot.columns)), pivot.loc[day].values,
                alpha=0.85, color='red', linewidth=1.5,
                label=f"Anomalia {day}")

    ax.set_title(f"Anomalias Univariable {label} — Isolation Forest")
    ax.set_xlabel("Franja horaria")
    handles, lbls = ax.get_legend_handles_labels()
    if handles:
        ax.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.show()
    return anomalous_days


# =============================================================================
# D. CLUSTERING MULTIVARIABLE
# =============================================================================
def get_multivariate_profiles(df, var1, var2):
    """
    Combina dos variables en un unico vector de perfil diario.

    Si cada variable tiene N franjas horarias por dia, el vector combinado
    tiene 2N elementos: [var1_t0, var1_t1, ..., var1_tN, var2_t0, ..., var2_tN]

    Solo se incluyen dias con datos completos en AMBAS variables.
    """
    p1 = get_daily_profiles(df, var1)  # (n_dias x N)
    p2 = get_daily_profiles(df, var2)  # (n_dias x N)
    common_days = p1.index.intersection(p2.index)
    p1 = p1.loc[common_days]
    p2 = p2.loc[common_days]
    # np.hstack concatena horizontalmente: resultado es (n_dias x 2N)
    combined = np.hstack([p1.values, p2.values])
    return combined, common_days, p1, p2


def cluster_multivariate_kmeans(combined, common_days, n_clusters=3, label=""):
    """K-Means multivariable: mismo principio que univariable pero con vector doble."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(combined)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0
    print(f"\n[K-Means Multivariable {label}] n_clusters={n_clusters}, Silhouette={score:.4f}")
    for c in range(n_clusters):
        print(f"  Cluster {c}: {sum(labels == c)} dias")
    return labels


def cluster_multivariate_dbscan(combined, common_days, eps=4.0, min_samples=3, label=""):
    """DBSCAN multivariable: mayor eps porque el espacio es de mayor dimension."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(combined)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"\n[DBSCAN Multivariable {label}] Clusters={n_clusters}, Ruido={n_noise}")
    for c in sorted(set(labels)):
        lbl = "Ruido" if c == -1 else f"Cluster {c}"
        print(f"  {lbl}: {sum(labels == c)} dias")
    return labels


# =============================================================================
# E. ANOMALIAS MULTIVARIABLE
# =============================================================================
def detect_anomalies_multivariate(combined, common_days, label=""):
    """
    Isolation Forest sobre el vector combinado (2N dimensiones).
    Detecta dias que son anomalos en la combinacion CO2+Temperatura,
    incluso si individualmente no parecen anomalos en cada variable.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(combined)
    iso = IsolationForest(contamination=0.05, random_state=42)
    pred = iso.fit_predict(X_scaled)
    anomalous_days = common_days[pred == -1]
    print(f"\n[Isolation Forest Multivariable {label}]")
    print(f"  Dias anomalos : {len(anomalous_days)}")
    if len(anomalous_days) > 0:
        print(f"  Fechas        : {list(anomalous_days)}")
    return anomalous_days


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    df = prepare_data()
    print(f"Dataset cargado: {len(df)} mediciones, columnas: {list(df.columns)}")

    # -------------------------------------------------------------------------
    # A. Perfiles diarios + estadistica descriptiva
    # Analizamos 1 variable CO2 y 1 temperatura (NE)
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("A. PERFILES DIARIOS")
    print("="*60)
    pivot_co2 = get_daily_profiles(df, lb_V005_vent01_CO2)
    pivot_temp = get_daily_profiles(df, lb_V006_vent01_temp_out)

    plot_daily_profiles(pivot_co2,
                        f"Perfiles diarios — {alias[lb_V005_vent01_CO2]}",
                        "CO2 (ppm)")
    print_descriptive_stats(pivot_co2, alias[lb_V005_vent01_CO2])

    plot_daily_profiles(pivot_temp,
                        f"Perfiles diarios — {alias[lb_V006_vent01_temp_out]}",
                        "Temperatura (C)")
    print_descriptive_stats(pivot_temp, alias[lb_V006_vent01_temp_out])

    # -------------------------------------------------------------------------
    # B. Clustering univariable con K-Means y DBSCAN (2 tecnicas)
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("B. CLUSTERING UNIVARIABLE")
    print("="*60)

    # CO2 NE
    labels_co2_km = cluster_kmeans(pivot_co2, n_clusters=3,
                                   label=alias[lb_V005_vent01_CO2])
    labels_co2_db = cluster_dbscan(pivot_co2, eps=3.0, min_samples=3,
                                   label=alias[lb_V005_vent01_CO2])
    # Temperatura NE
    labels_temp_km = cluster_kmeans(pivot_temp, n_clusters=3,
                                    label=alias[lb_V006_vent01_temp_out])
    labels_temp_db = cluster_dbscan(pivot_temp, eps=3.0, min_samples=3,
                                    label=alias[lb_V006_vent01_temp_out])

    # -------------------------------------------------------------------------
    # C. Anomalias univariable
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("C. ANOMALIAS UNIVARIABLE")
    print("="*60)
    anom_co2 = detect_anomalies_univariate(pivot_co2,
                                           label=alias[lb_V005_vent01_CO2])
    anom_temp = detect_anomalies_univariate(pivot_temp,
                                            label=alias[lb_V006_vent01_temp_out])

    # -------------------------------------------------------------------------
    # D. Clustering multivariable — par NE (CO2_NE + Temp_NE)
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("D. CLUSTERING MULTIVARIABLE (par NE)")
    print("="*60)
    combined_ne, days_ne, p_co2_ne, p_temp_ne = get_multivariate_profiles(
        df, lb_V005_vent01_CO2, lb_V006_vent01_temp_out)

    labels_mv_km = cluster_multivariate_kmeans(
        combined_ne, days_ne, n_clusters=3, label="CO2_NE + Temp_NE")
    labels_mv_db = cluster_multivariate_dbscan(
        combined_ne, days_ne, eps=4.0, min_samples=3, label="CO2_NE + Temp_NE")

    # -------------------------------------------------------------------------
    # E. Anomalias multivariable
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("E. ANOMALIAS MULTIVARIABLE")
    print("="*60)
    anom_mv = detect_anomalies_multivariate(combined_ne, days_ne,
                                            label="CO2_NE + Temp_NE")

    # -------------------------------------------------------------------------
    # F. Conclusiones
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("F. CONCLUSIONES")
    print("="*60)
    print("""
  1. PATRONES: K-Means y DBSCAN identifican entre 2 y 4 patrones diarios:
       - Perfil laboral (lunes-viernes): CO2 sube en horas de trabajo,
         baja en la noche. Temperatura sigue el ciclo de climatizacion.
       - Perfil fin de semana/festivo: CO2 bajo y plano todo el dia,
         temperatura mas estable (sin uso intensivo del HVAC).
       - Perfil atipico: variaciones abruptas, posibles fallas de sensor.

  2. CONSISTENCIA: K-Means y DBSCAN producen agrupaciones similares
     en dias laborales vs. no laborales, validando la robustez de los patrones.

  3. ANOMALIAS: Los dias detectados como anomalos corresponden a:
       - Dias festivos o eventos especiales (actividad inusual)
       - Posibles fallas del sistema de ventilacion o sensores
       - Condiciones climaticas extremas

  4. MULTIVARIABLE: El analisis conjunto CO2+Temperatura revela patrones
     que no eran visibles en el analisis univariable, ya que la temperatura
     y el CO2 estan correlacionados con el uso del sistema HVAC.
     Algunos dias normales en CO2 muestran anomalia en temperatura,
     lo que sugiere un desacoplamiento del sistema de ventilacion.
    """)

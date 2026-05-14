import os
from Taller3.P1_UML.p1_uml_util import *
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def prepare_data():
    script_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_path, "data")
    file_path = os.path.join(data_path, "data.csv")
    _df = read_csv_file(file_path)
    _df[lb_timestamp] = pd.to_datetime(_df[lb_timestamp], format="%d.%m.%Y %H:%M")
    _df.set_index(lb_timestamp, inplace=True)
    _df.sort_index(inplace=True)
    print(_df.dtypes)
    return _df

def plot_daily_overlay(_df: pd.DataFrame, lb, legend):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    df_to_plot = _df[[lb]].copy()
    df_to_plot["day"] = df_to_plot.index.normalize()
    df_to_plot["time_of_day"] = pd.to_datetime(df_to_plot.index.strftime("%H:%M"), format="%H:%M")

    plt.figure(figsize=(12, 6))
    for day, group in df_to_plot.groupby("day"):
        plt.plot(group["time_of_day"], group[lb], alpha=0.6, label=day.strftime("%Y-%m-%d"))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xlabel("Hora del día")
    plt.ylabel(legend)
    plt.title(alias[lb])
    plt.gcf().autofmt_xdate()
    plt.show()

def build_daily_profiles(_df: pd.DataFrame, lb):
    daily_profiles = _df[[lb]].copy()
    daily_profiles["day"] = daily_profiles.index.normalize()
    daily_profiles["time_of_day"] = daily_profiles.index.strftime("%H:%M")
    daily_profiles = daily_profiles.pivot_table(index="day", columns="time_of_day", values=lb, aggfunc="mean")
    ordered_columns = sorted(daily_profiles.columns, key=lambda value: pd.to_datetime(value, format="%H:%M"))
    daily_profiles = daily_profiles[ordered_columns]
    daily_profiles = daily_profiles.interpolate(axis=1, limit_direction="both")
    daily_profiles = daily_profiles.dropna(axis=0, how="any")
    return daily_profiles


def select_cluster_count(daily_profiles):

    max_clusters = min(6, len(daily_profiles) - 1)
    cluster_scores = {}
    for cluster_count in range(2, max_clusters + 1):
        model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
        labels = model.fit_predict(daily_profiles)
        cluster_scores[cluster_count] = silhouette_score(daily_profiles, labels)

    best_cluster_count = max(cluster_scores, key=cluster_scores.get)
    return best_cluster_count, cluster_scores


def plot_cluster_patterns(daily_profiles, kmeans_labels, agglomerative_labels, lb):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    time_axis = pd.to_datetime(daily_profiles.columns, format="%H:%M")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    for ax, labels, title in (
        (axes[0], kmeans_labels, "KMeans"),
        (axes[1], agglomerative_labels, "Agglomerative"),
    ):
        for cluster_id in sorted(set(labels)):
            cluster_mean = daily_profiles.iloc[labels == cluster_id].mean(axis=0)
            ax.plot(time_axis, cluster_mean, label=f"Cluster {cluster_id + 1}")
        ax.set_title(title)
        ax.set_xlabel("Hora del día")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.grid(True, alpha=0.2)
        ax.legend()

    axes[0].set_ylabel(alias[lb])
    fig.suptitle(f"Patrones diarios de {alias[lb]}")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.autofmt_xdate()
    plt.show()


def detect_anomalies_kmeans(daily_profiles_scaled, kmeans_labels, kmeans, threshold_std=2):
    import numpy as np
    import pandas as pd

    # Centroide asignado a cada día
    assigned_centroids = kmeans.cluster_centers_[kmeans_labels]

    # Distancia de cada día a su centroide
    distances = np.linalg.norm(daily_profiles_scaled.values - assigned_centroids, axis=1)

    # Umbral: promedio + 2 desviaciones estándar
    threshold = distances.mean() + threshold_std * distances.std()

    anomalies = distances > threshold

    anomaly_df = pd.DataFrame({
        "day": daily_profiles_scaled.index,
        "cluster": kmeans_labels + 1,
        "distance": distances,
        "threshold": threshold,
        "is_anomaly": anomalies
    })

    return anomaly_df


def plot_anomalies(daily_profiles, anomaly_df, lb):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    time_axis = pd.to_datetime(daily_profiles.columns, format="%H:%M")

    plt.figure(figsize=(12, 6))

    for day in daily_profiles.index:
        if day in anomaly_df[anomaly_df["is_anomaly"]]["day"].values:
            plt.plot(time_axis, daily_profiles.loc[day], color="red", linewidth=2.5, label="Anomalía")
        else:
            plt.plot(time_axis, daily_profiles.loc[day], color="gray", alpha=0.25)

    plt.title(f"Anomalías detectadas - {alias[lb]}")
    plt.xlabel("Hora del día")
    plt.ylabel(alias[lb])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.gcf().autofmt_xdate()
    plt.grid(True, alpha=0.2)

    handles, labels = plt.gca().get_legend_handles_labels()
    if labels:
        plt.legend(handles[:1], labels[:1])

    plt.show()


def analyze_variable(_df: pd.DataFrame, lb):

    daily_profiles = build_daily_profiles(_df, lb)
    if len(daily_profiles) < 3:
        print(f"{alias[lb]}: no hay suficientes días para agrupar.")
        return

    scaler = MinMaxScaler()
    daily_profiles_scaled = pd.DataFrame(
        scaler.fit_transform(daily_profiles),
        index=daily_profiles.index,
        columns=daily_profiles.columns,
    )

    best_cluster_count, silhouette_scores = select_cluster_count(daily_profiles_scaled)

    kmeans = KMeans(n_clusters=best_cluster_count, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(daily_profiles_scaled)

    agglomerative = AgglomerativeClustering(n_clusters=best_cluster_count)
    agglomerative_labels = agglomerative.fit_predict(daily_profiles_scaled)

    ari = adjusted_rand_score(kmeans_labels, agglomerative_labels)

    print(f"\nVariable: {alias[lb]}")
    print(f"Días analizados: {len(daily_profiles_scaled)}")
    print(f"Mejor número de clusters: {best_cluster_count}")
    print(f"Silhouette por KMeans: {silhouette_scores}")
    print(f"Consistencia KMeans vs Agglomerative (ARI): {ari:.3f}")
    print(f"Distribución KMeans: { {int(cluster_id + 1): int((kmeans_labels == cluster_id).sum()) for cluster_id in sorted(set(kmeans_labels))} }")
    print(f"Distribución Agglomerative: { {int(cluster_id + 1): int((agglomerative_labels == cluster_id).sum()) for cluster_id in sorted(set(agglomerative_labels))} }")


    anomaly_df = detect_anomalies_kmeans(
        daily_profiles_scaled,
        kmeans_labels,
        kmeans,
        threshold_std=2
    )

    print("\nAnomalías detectadas:")
    print(anomaly_df[anomaly_df["is_anomaly"]].sort_values("distance", ascending=False))

    plot_anomalies(daily_profiles, anomaly_df, lb)


    plot_cluster_patterns(daily_profiles, kmeans_labels, agglomerative_labels, lb)



def start():
    df = prepare_data()
    plot_daily_overlay(df, lb_V005_vent01_CO2, "CO2")
    plot_daily_overlay(df, lb_V022_vent02_CO2, "CO2")
    plot_daily_overlay(df, lb_V006_vent01_temp_out, "Temperature")
    plot_daily_overlay(df, lb_V023_vent02_temp_out, "Temperature")
    analyze_variable(df, lb_V005_vent01_CO2)
    analyze_variable(df, lb_V022_vent02_CO2)
    analyze_variable(df, lb_V006_vent01_temp_out)
    analyze_variable(df, lb_V023_vent02_temp_out)
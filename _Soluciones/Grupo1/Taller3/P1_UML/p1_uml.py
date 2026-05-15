import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from Taller3.P1_UML.p1_uml_util import *
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Literal A

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
    save_plot(f"overlay_{lb}")
    plt.show()

# Literal B

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
    save_plot(f"clusters_{lb}")
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

    save_plot(f"anomalies_{lb}")
    plt.show()

def save_plot(fig_name):
    import os
    import matplotlib.pyplot as plt

    script_path = os.path.dirname(os.path.abspath(__file__))

    images_path = os.path.join(script_path, "images_P1")

    os.makedirs(images_path, exist_ok=True)

    save_path = os.path.join(images_path, f"{fig_name}.png")

    plt.savefig(save_path, dpi=300, bbox_inches='tight')

    print(f"Imagen guardada en: {save_path}")


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


# Literal D

def build_multivariable_daily_profiles(_df: pd.DataFrame, variables):

    daily_profiles = []

    for variable in variables:
        variable_profile = _df[[variable]].copy()
        variable_profile["day"] = variable_profile.index.normalize()
        variable_profile["time_of_day"] = variable_profile.index.strftime("%H:%M")

        variable_profile = variable_profile.pivot_table(
            index="day",
            columns="time_of_day",
            values=variable,
            aggfunc="mean"
        )

        ordered_columns = sorted(
            variable_profile.columns,
            key=lambda value: pd.to_datetime(value, format="%H:%M")
        )

        variable_profile = variable_profile[ordered_columns]

        variable_profile = variable_profile.interpolate(
            axis=1,
            limit_direction="both"
        )

        variable_profile.columns = [
            f"{variable}_{column}" for column in variable_profile.columns
        ]

        daily_profiles.append(variable_profile)

    combined_profiles = pd.concat(daily_profiles, axis=1)

    combined_profiles = combined_profiles.dropna(axis=0, how="any")

    return combined_profiles


def plot_multivariable_patterns(
        original_profiles,
        labels,
        variables,
        title
):

    fig, axes = plt.subplots(
        len(variables),
        1,
        figsize=(14, 8),
        sharex=True
    )

    if len(variables) == 1:
        axes = [axes]

    for variable_index, variable in enumerate(variables):

        ax = axes[variable_index]

        variable_columns = [
            column for column in original_profiles.columns
            if column.startswith(variable)
        ]

        time_labels = [
            column.replace(f"{variable}_", "")
            for column in variable_columns
        ]

        time_axis = pd.to_datetime(time_labels, format="%H:%M")

        for cluster_id in sorted(set(labels)):

            cluster_mean = original_profiles.iloc[
                labels == cluster_id
            ][variable_columns].mean(axis=0)

            ax.plot(
                time_axis,
                cluster_mean.values,
                label=f"Cluster {cluster_id + 1}"
            )

        ax.set_title(alias[variable])
        ax.set_ylabel("Valor")
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M")
        )

    axes[-1].set_xlabel("Hora del día")

    fig.suptitle(title)

    fig.tight_layout(rect=[0, 0, 1, 0.96])

    fig_name = title.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
    save_plot(fig_name)

    plt.show()


def analyze_multivariable_patterns(
        _df: pd.DataFrame,
        variables,
        zone_name
):

    daily_profiles = build_multivariable_daily_profiles(
        _df,
        variables
    )

    if len(daily_profiles) < 3:
        print(f"{zone_name}: no hay suficientes días.")
        return

    scaler = MinMaxScaler()

    scaled_profiles = pd.DataFrame(
        scaler.fit_transform(daily_profiles),
        index=daily_profiles.index,
        columns=daily_profiles.columns
    )

    best_cluster_count, silhouette_scores = select_cluster_count(
        scaled_profiles
    )

    kmeans = KMeans(
        n_clusters=best_cluster_count,
        random_state=42,
        n_init=10
    )

    kmeans_labels = kmeans.fit_predict(scaled_profiles)

    agglomerative = AgglomerativeClustering(
        n_clusters=best_cluster_count
    )

    agglomerative_labels = agglomerative.fit_predict(
        scaled_profiles
    )

    ari = adjusted_rand_score(
        kmeans_labels,
        agglomerative_labels
    )

    print(f"\n===== {zone_name} =====")
    print(f"Días analizados: {len(daily_profiles)}")
    print(f"Mejor número de clusters: {best_cluster_count}")
    print(f"Silhouette scores: {silhouette_scores}")
    print(f"Consistencia entre métodos (ARI): {ari:.3f}")

    print(
        f"Distribución KMeans: "
        f"{ {int(cluster_id + 1): int((kmeans_labels == cluster_id).sum()) for cluster_id in sorted(set(kmeans_labels))} }"
    )

    print(
        f"Distribución Agglomerative: "
        f"{ {int(cluster_id + 1): int((agglomerative_labels == cluster_id).sum()) for cluster_id in sorted(set(agglomerative_labels))} }"
    )

    plot_multivariable_patterns(
        daily_profiles,
        kmeans_labels,
        variables,
        f"Multivariable Clusters - {zone_name} (KMeans)"
    )

    plot_multivariable_patterns(
        daily_profiles,
        agglomerative_labels,
        variables,
        f"Multivariable Clusters - {zone_name} (Agglomerative)"
    )

def start():
    df = prepare_data()
    start_a(df)
    start_b_y_c(df)
    start_d_y_e(df)

def start_a(df = None):
    if df is None:
        df = prepare_data()
    plot_daily_overlay(df, lb_V005_vent01_CO2, "CO2")
    plot_daily_overlay(df, lb_V022_vent02_CO2, "CO2")
    plot_daily_overlay(df, lb_V006_vent01_temp_out, "Temperature")
    plot_daily_overlay(df, lb_V023_vent02_temp_out, "Temperature")

def start_b_y_c(df = None):
    if df is None:
        df = prepare_data()
    analyze_variable(df, lb_V005_vent01_CO2)
    analyze_variable(df, lb_V022_vent02_CO2)
    analyze_variable(df, lb_V006_vent01_temp_out)
    analyze_variable(df, lb_V023_vent02_temp_out)

def start_d_y_e(df = None):
    if df is None:
        df = prepare_data()
    analyze_multivariable_patterns(
        df,
        [lb_V005_vent01_CO2, lb_V006_vent01_temp_out],
        "Zona Norte Este"
    )
    analyze_multivariable_patterns(
        df,
        [lb_V022_vent02_CO2, lb_V023_vent02_temp_out],
        "Zona Sur Oeste"
    )

<<<<<<< Updated upstream
def start_e(df = None):
    if df is None:
        df = prepare_data()
    pass
=======

if __name__ == "__main__":
    start()
>>>>>>> Stashed changes

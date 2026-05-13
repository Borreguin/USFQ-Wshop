import numpy as np
import pandas as pd


def load_cities(csv_path: str) -> pd.DataFrame:
    """Load city coordinates from CSV (columns: city, x, y)."""
    return pd.read_csv(csv_path)


def compute_distance_matrix(cities: pd.DataFrame) -> np.ndarray:
    """Vectorized Euclidean distance matrix for all city pairs."""
    coords = cities[["x", "y"]].values.astype(float)
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))


def tour_distance(tour: list, dist_matrix: np.ndarray) -> float:
    """Total distance of a closed tour (last city back to first)."""
    n = len(tour)
    return sum(dist_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n))

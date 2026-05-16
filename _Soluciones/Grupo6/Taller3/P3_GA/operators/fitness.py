from .base import FitnessEvaluator


class MatchCount(FitnessEvaluator):
    """Counts characters matching at same position (maximize)."""

    @property
    def maximize(self) -> bool:
        return True

    @property
    def label(self) -> str:
        return "Match Count"

    def evaluate(self, individual: str, objective: str) -> float:
        return sum(1 for a, b in zip(individual, objective) if a == b)


class HammingDistance(FitnessEvaluator):
    """Sum of absolute ASCII differences between characters (minimize)."""

    @property
    def maximize(self) -> bool:
        return False

    @property
    def label(self) -> str:
        return "Hamming Distance"

    def evaluate(self, individual: str, objective: str) -> float:
        return sum(abs(ord(a) - ord(b)) for a, b in zip(individual, objective))

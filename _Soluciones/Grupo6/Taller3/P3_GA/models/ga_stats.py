from dataclasses import dataclass, field
from typing import List


@dataclass
class GenerationStats:
    generation: int
    best_fitness: float
    mean_fitness: float
    worst_fitness: float
    diversity: float
    best_individual: str
    objective: str

    @property
    def match_count(self) -> int:
        return sum(a == b for a, b in zip(self.best_individual, self.objective))

    @property
    def match_ratio(self) -> float:
        if not self.objective:
            return 0.0
        return self.match_count / len(self.objective)

    def diff_str(self) -> str:
        """Returns a visual diff: matched chars shown, mismatches shown as '_'."""
        result = ""
        for a, b in zip(self.best_individual, self.objective):
            result += a if a == b else "_"
        return result


@dataclass
class GAHistory:
    generations: List[GenerationStats] = field(default_factory=list)
    success: bool = False
    total_generations: int = 0

    def add(self, stats: GenerationStats):
        self.generations.append(stats)

    @property
    def best_fitness_history(self) -> List[float]:
        return [g.best_fitness for g in self.generations]

    @property
    def mean_fitness_history(self) -> List[float]:
        return [g.mean_fitness for g in self.generations]

    @property
    def diversity_history(self) -> List[float]:
        return [g.diversity for g in self.generations]

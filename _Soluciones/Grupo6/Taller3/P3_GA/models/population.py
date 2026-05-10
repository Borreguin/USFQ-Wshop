import random
from typing import List, Optional

from .chromosome import Chromosome


class Population:
    def __init__(self, chromosomes: List[Chromosome]):
        self.chromosomes = chromosomes

    @classmethod
    def random(cls, size: int, length: int, gene_set: str, seed: Optional[int] = None) -> "Population":
        if seed is not None:
            random.seed(seed)
        chromosomes = [
            Chromosome(genes="".join(random.choice(gene_set) for _ in range(length)))
            for _ in range(size)
        ]
        return cls(chromosomes)

    def __len__(self):
        return len(self.chromosomes)

    def __iter__(self):
        return iter(self.chromosomes)

    @property
    def fitness_list(self) -> List[float]:
        return [c.fitness for c in self.chromosomes]

    def diversity(self) -> float:
        """Ratio of unique individuals to population size."""
        if not self.chromosomes:
            return 0.0
        return len(set(c.genes for c in self.chromosomes)) / len(self.chromosomes)

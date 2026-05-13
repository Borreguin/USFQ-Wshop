from dataclasses import dataclass, field


@dataclass
class Chromosome:
    genes: str
    fitness: float = 0.0
    generation: int = 0

    def __eq__(self, other):
        if isinstance(other, Chromosome):
            return self.genes == other.genes
        return self.genes == other

    def __hash__(self):
        return hash(self.genes)

    def __len__(self):
        return len(self.genes)

    def __repr__(self):
        return f"Chromosome(genes={self.genes!r}, fitness={self.fitness:.2f})"

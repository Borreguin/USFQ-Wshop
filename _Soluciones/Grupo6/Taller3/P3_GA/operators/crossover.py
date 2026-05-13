import random
from typing import Tuple

from .base import CrossoverOperator
from ..models.chromosome import Chromosome


class SinglePoint(CrossoverOperator):
    """Splits both parents at one random point and swaps tails."""

    @property
    def label(self) -> str:
        return "Single Point"

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        point = random.randint(1, len(parent1) - 1)
        c1 = Chromosome(genes=parent1.genes[:point] + parent2.genes[point:])
        c2 = Chromosome(genes=parent2.genes[:point] + parent1.genes[point:])
        return c1, c2


class TwoPoint(CrossoverOperator):
    """Splits at two random points and swaps the middle segment."""

    @property
    def label(self) -> str:
        return "Two Point"

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        n = len(parent1)
        p1, p2 = sorted(random.sample(range(1, n), 2))
        g1 = parent1.genes[:p1] + parent2.genes[p1:p2] + parent1.genes[p2:]
        g2 = parent2.genes[:p1] + parent1.genes[p1:p2] + parent2.genes[p2:]
        return Chromosome(genes=g1), Chromosome(genes=g2)


class Uniform(CrossoverOperator):
    """Each gene is independently taken from either parent with 50% probability."""

    @property
    def label(self) -> str:
        return "Uniform"

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        g1, g2 = [], []
        for a, b in zip(parent1.genes, parent2.genes):
            if random.random() < 0.5:
                g1.append(a); g2.append(b)
            else:
                g1.append(b); g2.append(a)
        return Chromosome(genes="".join(g1)), Chromosome(genes="".join(g2))

import random
from typing import Tuple

from .base import SelectionOperator
from ..models.chromosome import Chromosome
from ..models.population import Population


class RouletteWheel(SelectionOperator):
    """Fitness-proportionate selection (roulette wheel)."""

    @property
    def label(self) -> str:
        return "Roulette Wheel"

    def select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        fitnesses = population.fitness_list
        total = sum(fitnesses)
        if total == 0:
            return tuple(random.choices(population.chromosomes, k=2))
        weights = [f / total for f in fitnesses]
        return tuple(random.choices(population.chromosomes, weights=weights, k=2))


class Tournament(SelectionOperator):
    """Selects the best individual from a random subset of size k."""

    def __init__(self, k: int = 3):
        self.k = k

    @property
    def label(self) -> str:
        return f"Tournament (k={self.k})"

    def select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        def pick():
            sample = random.sample(population.chromosomes, min(self.k, len(population)))
            return max(sample, key=lambda c: c.fitness)
        return pick(), pick()


class Elitist(SelectionOperator):
    """Selects parents exclusively from the top fraction of the population."""

    def __init__(self, top_fraction: float = 0.3):
        self.top_fraction = top_fraction

    @property
    def label(self) -> str:
        return f"Elitist (top {self.top_fraction:.0%})"

    def select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]:
        sorted_pop = sorted(population.chromosomes, key=lambda c: c.fitness, reverse=True)
        elite_size = max(2, int(len(sorted_pop) * self.top_fraction))
        elite = sorted_pop[:elite_size]
        return random.choice(elite), random.choice(elite)

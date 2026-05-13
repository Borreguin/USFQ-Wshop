import random
from dataclasses import dataclass
from typing import Callable, List, Optional

from ..constants import all_possible_gens
from ..models.chromosome import Chromosome
from ..models.ga_stats import GAHistory, GenerationStats
from ..models.population import Population
from ..operators.base import (
    CrossoverOperator,
    FitnessEvaluator,
    MutationOperator,
    SelectionOperator,
)
from ..operators.crossover import SinglePoint
from ..operators.fitness import MatchCount
from ..operators.mutation import RandomGene
from ..operators.selection import RouletteWheel


@dataclass
class GAConfig:
    population_size: int = 100
    mutation_rate: float = 0.01
    n_iterations: int = 1000
    seed: Optional[int] = None


class GeneticAlgorithm:
    """
    Pure computation engine. No I/O — consumers register callbacks.
    Both console and GUI subscribe to the same events, so results are identical.
    """

    def __init__(
        self,
        objective: str,
        config: GAConfig = None,
        fitness: FitnessEvaluator = None,
        selection: SelectionOperator = None,
        crossover: CrossoverOperator = None,
        mutation: MutationOperator = None,
    ):
        self.objective = objective
        self.config = config or GAConfig()
        self.fitness_evaluator = fitness or MatchCount()
        self.selection_op = selection or RouletteWheel()
        self.crossover_op = crossover or SinglePoint()
        self.mutation_op = mutation or RandomGene()

        self._generation_callbacks: List[Callable[[GenerationStats], None]] = []
        self._complete_callbacks: List[Callable[[GAHistory], None]] = []
        self._stop_requested = False

    def on_generation(self, callback: Callable[[GenerationStats], None]):
        self._generation_callbacks.append(callback)

    def on_complete(self, callback: Callable[[GAHistory], None]):
        self._complete_callbacks.append(callback)

    def stop(self):
        self._stop_requested = True

    def run(self) -> GAHistory:
        if self.config.seed is not None:
            random.seed(self.config.seed)

        self._stop_requested = False
        history = GAHistory()
        maximize = self.fitness_evaluator.maximize

        population = Population.random(
            size=self.config.population_size,
            length=len(self.objective),
            gene_set=all_possible_gens,
        )

        for gen in range(self.config.n_iterations):
            if self._stop_requested:
                break

            for chrom in population:
                chrom.fitness = self.fitness_evaluator.evaluate(chrom.genes, self.objective)
                chrom.generation = gen

            fitnesses = population.fitness_list
            if maximize:
                best = max(population.chromosomes, key=lambda c: c.fitness)
                worst_fitness = min(fitnesses)
            else:
                best = min(population.chromosomes, key=lambda c: c.fitness)
                worst_fitness = max(fitnesses)

            stats = GenerationStats(
                generation=gen,
                best_fitness=best.fitness,
                mean_fitness=sum(fitnesses) / len(fitnesses),
                worst_fitness=worst_fitness,
                diversity=population.diversity(),
                best_individual=best.genes,
                objective=self.objective,
            )
            history.add(stats)

            for cb in self._generation_callbacks:
                cb(stats)

            if best.genes == self.objective:
                history.success = True
                history.total_generations = gen
                break

            new_chromosomes = []
            for _ in range(len(population) // 2):
                p1, p2 = self.selection_op.select_parents(population)
                c1, c2 = self.crossover_op.crossover(p1, p2)
                c1 = self.mutation_op.mutate(c1, self.config.mutation_rate)
                c2 = self.mutation_op.mutate(c2, self.config.mutation_rate)
                new_chromosomes.extend([c1, c2])

            population = Population(new_chromosomes)

        if not history.success:
            history.total_generations = self.config.n_iterations

        for cb in self._complete_callbacks:
            cb(history)

        return history

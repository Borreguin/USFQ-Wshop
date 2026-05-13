import random

from .base import MutationOperator
from ..models.chromosome import Chromosome
from ..constants import all_possible_gens


class RandomGene(MutationOperator):
    """Replaces each gene with a random one from the alphabet at mutation_rate probability."""

    @property
    def label(self) -> str:
        return "Random Gene"

    def mutate(self, chromosome: Chromosome, mutation_rate: float) -> Chromosome:
        genes = list(chromosome.genes)
        for i in range(len(genes)):
            if random.random() < mutation_rate:
                genes[i] = random.choice(all_possible_gens)
        return Chromosome(genes="".join(genes))


class SwapGene(MutationOperator):
    """Swaps a gene with another random position at mutation_rate probability."""

    @property
    def label(self) -> str:
        return "Swap Gene"

    def mutate(self, chromosome: Chromosome, mutation_rate: float) -> Chromosome:
        genes = list(chromosome.genes)
        for i in range(len(genes)):
            if random.random() < mutation_rate:
                j = random.randint(0, len(genes) - 1)
                genes[i], genes[j] = genes[j], genes[i]
        return Chromosome(genes="".join(genes))

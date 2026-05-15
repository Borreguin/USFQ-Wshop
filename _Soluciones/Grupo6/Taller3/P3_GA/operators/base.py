from abc import ABC, abstractmethod
from typing import Tuple

from ..models.chromosome import Chromosome
from ..models.population import Population


class FitnessEvaluator(ABC):
    @abstractmethod
    def evaluate(self, individual: str, objective: str) -> float: ...

    @property
    @abstractmethod
    def maximize(self) -> bool:
        """True if higher fitness is better, False if lower is better."""
        ...

    @property
    @abstractmethod
    def label(self) -> str: ...


class SelectionOperator(ABC):
    @abstractmethod
    def select_parents(self, population: Population) -> Tuple[Chromosome, Chromosome]: ...

    @property
    @abstractmethod
    def label(self) -> str: ...


class CrossoverOperator(ABC):
    @abstractmethod
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]: ...

    @property
    @abstractmethod
    def label(self) -> str: ...


class MutationOperator(ABC):
    @abstractmethod
    def mutate(self, chromosome: Chromosome, mutation_rate: float) -> Chromosome: ...

    @property
    @abstractmethod
    def label(self) -> str: ...

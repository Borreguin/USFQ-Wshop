import random
from Taller3.P3_GA.constants import *
from Taller3.P3_GA.util import *


def parent_selection(_type: ParentSelectionType, population, aptitudes):
    if _type == ParentSelectionType.DEFAULT:
        total = sum(aptitudes)
        if total == 0:
            return random.choices(population, k=2)
        weights = [a / total for a in aptitudes]
        return random.choices(population, weights=weights, k=2)

    if _type == ParentSelectionType.MIN_DISTANCE:
        cut = random.randint(1, len(population) - 1)
        parent1 = choose_best_individual_by_distance(population[:cut], aptitudes[:cut])
        parent2 = choose_best_individual_by_distance(population[cut:], aptitudes[cut:])
        return parent1, parent2

    if _type == ParentSelectionType.TOURNAMENT:
        k = 3

        def _pick():
            indices = random.sample(range(len(population)), min(k, len(population)))
            best = max(indices, key=lambda i: aptitudes[i])
            return population[best]

        return _pick(), _pick()

    if _type == ParentSelectionType.ELITISM:
        n_elite = max(2, int(len(population) * 0.3))
        ranked = sorted(range(len(population)), key=lambda i: aptitudes[i], reverse=True)
        elite_pool = [population[i] for i in ranked[:n_elite]]
        return random.choice(elite_pool), random.choice(elite_pool)

    raise ValueError(f"ParentSelectionType desconocido: {_type}")


def crossover(_type: CrossoverType, parent1, parent2):
    n = len(parent1)

    if _type == CrossoverType.DEFAULT:
        point = random.randint(1, n - 1)
        return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]

    if _type == CrossoverType.TWO_POINT:
        if n < 3:
            return crossover(CrossoverType.DEFAULT, parent1, parent2)
        p1, p2 = sorted(random.sample(range(1, n), 2))
        child1 = parent1[:p1] + parent2[p1:p2] + parent1[p2:]
        child2 = parent2[:p1] + parent1[p1:p2] + parent2[p2:]
        return child1, child2

    if _type == CrossoverType.UNIFORM:
        g1, g2 = [], []
        for a, b in zip(parent1, parent2):
            if random.random() < 0.5:
                g1.append(a); g2.append(b)
            else:
                g1.append(b); g2.append(a)
        return ''.join(g1), ''.join(g2)

    raise ValueError(f"CrossoverType desconocido: {_type}")


def mutate(_type: MutationType, individual, mutation_rate):
    if _type == MutationType.DEFAULT:
        genes = list(individual)
        for i in range(len(genes)):
            if random.random() < mutation_rate:
                genes[i] = random.choice(all_possible_gens)
        return ''.join(genes)

    if _type == MutationType.SWAP:
        genes = list(individual)
        for i in range(len(genes)):
            if random.random() < mutation_rate:
                j = random.randint(0, len(genes) - 1)
                genes[i], genes[j] = genes[j], genes[i]
        return ''.join(genes)

    raise ValueError(f"MutationType desconocido: {_type}")

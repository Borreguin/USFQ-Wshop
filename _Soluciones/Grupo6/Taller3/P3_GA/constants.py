from enum import Enum

MY_SEED = 123

all_possible_gens = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !"


class AptitudeType(str, Enum):
    DEFAULT    = 'default'      # Conteo de coincidencias exactas (maximizar)
    BY_DISTANCE = 'by_distance' # Distancia de Hamming ASCII (minimizar)


class ParentSelectionType(str, Enum):
    DEFAULT      = 'default'       # Ruleta proporcional al fitness
    MIN_DISTANCE = 'min_distance'  # Partición aleatoria, mejor de cada mitad (caso 2)
    TOURNAMENT   = 'tournament'    # Torneo: mejor de k=3 individuos aleatorios
    ELITISM      = 'elitism'       # Solo del top 30% de la población


class MutationType(str, Enum):
    DEFAULT = 'default'  # Reemplazar gen por uno aleatorio del alfabeto
    SWAP    = 'swap'     # Intercambiar posición de dos genes


class CrossoverType(str, Enum):
    DEFAULT   = 'default'    # Cruce de un punto
    TWO_POINT = 'two_point'  # Cruce de dos puntos
    UNIFORM   = 'uniform'    # Cruce uniforme (gen a gen, 50/50)


class BestIndividualSelectionType(str, Enum):
    DEFAULT      = 'default'      # Mayor aptitud (maximizar)
    MIN_DISTANCE = 'min_distance' # Menor distancia (minimizar)


class NewGenerationType(str, Enum):
    DEFAULT      = 'default'      # Ruleta + cruce un punto (caso 1/3/4)
    MIN_DISTANCE = 'min_distance' # Partición aleatoria + cruce un punto (caso 2)
    IMPROVED     = 'improved'     # Elitismo + torneo + cruce dos puntos (caso 5)

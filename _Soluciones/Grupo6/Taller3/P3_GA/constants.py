from enum import Enum

MY_SEED = 123

all_possible_gens = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !"


class AptitudeType(str, Enum):
    DEFAULT     = 'default'
    BY_DISTANCE = 'by_distance'


class ParentSelectionType(str, Enum):
    DEFAULT      = 'default'
    MIN_DISTANCE = 'min_distance'
    TOURNAMENT   = 'tournament'
    ELITISM      = 'elitism'


class MutationType(str, Enum):
    DEFAULT = 'default'
    SWAP    = 'swap'


class CrossoverType(str, Enum):
    DEFAULT   = 'default'
    TWO_POINT = 'two_point'
    UNIFORM   = 'uniform'


class BestIndividualSelectionType(str, Enum):
    DEFAULT      = 'default'
    MIN_DISTANCE = 'min_distance'


class NewGenerationType(str, Enum):
    DEFAULT      = 'default'
    MIN_DISTANCE = 'min_distance'
    IMPROVED     = 'improved'

from enum import Enum
MY_SEED = 123

all_possible_gens = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ !"

class AptitudeType(str, Enum):
    DEFAULT = 'default'
    BY_DISTANCE = 'by_distance'
    NEW = 'new'


class ParentSelectionType(str, Enum):
    DEFAULT = 'default'
    MIN_DISTANCE = 'min_distance'
    NEW = 'new'

class MutationType(str, Enum):
    DEFAULT = 'default'
    NEW = 'new'

class CrossoverType(str, Enum):
    DEFAULT = 'default'
    NEW = 'new'

class SelectionType(str, Enum):
    DEFAULT = 'default'
    NEW = 'new'

class BestIndividualSelectionType(str, Enum):
    DEFAULT = 'default'
    MIN_DISTANCE = 'min_distance'
    NEW = 'new'

class NewGenerationType(str, Enum):
    DEFAULT = 'default'
    MIN_DISTANCE = 'min_distance'
    NEW = 'new'
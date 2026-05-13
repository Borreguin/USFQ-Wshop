import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Position = Tuple[int, int]
Graph = Dict[Position, List[Position]]

_P1_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


@dataclass
class MazeModel:
    name: str
    filepath: str
    grid: List[List[str]] = field(default_factory=list)
    graph: Graph = field(default_factory=dict)
    start: Optional[Position] = None
    end: Optional[Position] = None

    _PASSABLE = frozenset({' ', 'E', 'S'})

    MAZES: Dict[str, str] = field(default_factory=lambda: {
        'Laberinto 1 (pequeño)':        'laberinto1.txt',
        'Laberinto 2 (mediano)':        'laberinto2.txt',
        'Laberinto 3 (grande)':         'laberinto3.txt',
        'Laberinto 4 (extra grande)':   'laberinto4.txt',
    })

    @classmethod
    def from_name(cls, name: str) -> 'MazeModel':
        _mazes = {
            'Laberinto 1 (pequeño)':      'laberinto1.txt',
            'Laberinto 2 (mediano)':      'laberinto2.txt',
            'Laberinto 3 (grande)':       'laberinto3.txt',
            'Laberinto 4 (extra grande)': 'laberinto4.txt',
        }
        filepath = os.path.join(_P1_DIR, _mazes[name])
        m = cls(name=name, filepath=filepath)
        m.load()
        return m

    def load(self) -> 'MazeModel':
        with open(self.filepath) as f:
            self.grid = [list(line.rstrip('\n')) for line in f]
        self._build_graph()
        self._find_endpoints()
        return self

    def _build_graph(self):
        self.graph = {}
        h = len(self.grid)
        passable = self._PASSABLE
        for r in range(h):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] in passable:
                    nbs = []
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < h
                                and 0 <= nc < len(self.grid[nr])
                                and self.grid[nr][nc] in passable):
                            nbs.append((nr, nc))
                    self.graph[(r, c)] = nbs

    def _find_endpoints(self):
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == 'E':
                    self.start = (r, c)
                elif cell == 'S':
                    self.end = (r, c)

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return max(len(row) for row in self.grid)

    @property
    def node_count(self) -> int:
        return len(self.graph)

    @property
    def edge_count(self) -> int:
        return sum(len(v) for v in self.graph.values()) // 2
from abc import ABC, abstractmethod
from collections import deque
import heapq
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from qiskit.quantum_info import Statevector as _QkStatevector
    _QISKIT_OK = True
except ImportError:
    _QISKIT_OK = False

# ── IBM Quantum hardware toggle ────────────────────────────────────────────────
# Set IBM_HARDWARE = True to submit circuits to real IBM quantum hardware.
# Requires a saved account:
#   from qiskit_ibm_runtime import QiskitRuntimeService
#   QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_KEY")
#
# Hardware is only used when N <= IBM_HARDWARE_MAX_NODES (circuit too deep beyond
# this on current NISQ devices).  Larger mazes fall back to the Statevector sim.
IBM_HARDWARE = True
IBM_HARDWARE_MAX_NODES = 64

Position = Tuple[int, int]
Graph = Dict[Position, List[Position]]


@dataclass(frozen=True)
class AlgorithmMetrics:
    path_optimality_ratio: float
    search_penetrance: float
    search_overhead: float
    effective_branching_factor: float
    oracle_calls: int


def _ebf(nodes_visited: int, depth: int) -> float:
    if depth <= 0:
        return float('inf')
    if nodes_visited <= 1:
        return 1.0
    target = float(nodes_visited + 1)
    b = float(nodes_visited) ** (1.0 / depth)
    for _ in range(64):
        if abs(b - 1.0) < 1e-12:
            break
        geo = (b ** (depth + 1) - 1.0) / (b - 1.0)
        d_geo = ((depth + 1) * b ** depth * (b - 1.0) - (b ** (depth + 1) - 1.0)) / (b - 1.0) ** 2
        delta = (geo - target) / d_geo if abs(d_geo) > 1e-14 else 0.0
        b -= delta
        if abs(delta) < 1e-9:
            break
    return max(1.0, b)


@dataclass
class SolverResult:
    algorithm: str
    color: str
    path: Optional[List[Position]]
    nodes_visited: int
    elapsed_ms: float
    exploration_order: List[Position] = field(default_factory=list)
    came_from: Dict[Position, Optional[Position]] = field(default_factory=dict)

    @property
    def steps(self) -> int:
        return len(self.path) - 1 if self.path else -1

    @property
    def found(self) -> bool:
        return self.path is not None

    def compute_metrics(self, optimal_steps: int, total_nodes: int) -> AlgorithmMetrics:
        if not self.found or optimal_steps <= 0:
            return AlgorithmMetrics(float('inf'), 0.0, float('inf'), float('inf'), 0)
        d = self.steps
        N = self.nodes_visited
        grover_k = math.floor(math.pi / 4 * math.sqrt(total_nodes))
        return AlgorithmMetrics(
            path_optimality_ratio=d / optimal_steps,
            search_penetrance=d / total_nodes if total_nodes > 0 else 0.0,
            search_overhead=(N - d) / d if d > 0 else float('inf'),
            effective_branching_factor=_ebf(N, d),
            oracle_calls=grover_k if self.algorithm.startswith('Grover') else 0,
        )


class Solver(ABC):
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color

    def solve(self, graph: Graph, start: Position, end: Position) -> SolverResult:
        t0 = time.perf_counter()
        path, nodes, exploration, came_from = self._search(graph, start, end)
        ms = (time.perf_counter() - t0) * 1000
        return SolverResult(self.name, self.color, path, nodes, ms,
                            exploration, came_from)

    @abstractmethod
    def _search(
        self, graph: Graph, start: Position, end: Position
    ) -> Tuple[Optional[List[Position]], int, List[Position],
               Dict[Position, Optional[Position]]]: ...

    def _reconstruct(self, came_from: dict, end: Position) -> List[Position]:
        path, node = [], end
        while node is not None:
            path.append(node)
            node = came_from[node]
        return path[::-1]


class BFSSolver(Solver):
    """BFS — guarantees shortest path, O(V+E)."""

    def __init__(self):
        super().__init__("BFS", "#4472C4")

    def _search(self, graph, start, end):
        came_from = {start: None}
        queue = deque([start])
        exploration: List[Position] = []
        visited = 0

        while queue:
            node = queue.popleft()
            exploration.append(node)
            visited += 1
            if node == end:
                return self._reconstruct(came_from, end), visited, exploration, came_from
            for nb in graph.get(node, []):
                if nb not in came_from:
                    came_from[nb] = node
                    queue.append(nb)

        return None, visited, exploration, came_from


class DFSSolver(Solver):
    """DFS — not optimal, O(V+E)."""

    def __init__(self):
        super().__init__("DFS", "#ED7D31")

    def _search(self, graph, start, end):
        came_from: Dict[Position, Optional[Position]] = {}
        stack = [(start, None)]
        exploration: List[Position] = []
        visited = 0

        while stack:
            node, parent = stack.pop()
            if node in came_from:
                continue
            came_from[node] = parent
            exploration.append(node)
            visited += 1
            if node == end:
                return self._reconstruct(came_from, end), visited, exploration, came_from
            for nb in graph.get(node, []):
                if nb not in came_from:
                    stack.append((nb, node))

        return None, visited, exploration, came_from


class AStarSolver(Solver):
    """A* with Manhattan heuristic — optimal on unweighted grids, O(E log V)."""

    def __init__(self):
        super().__init__("A*", "#70AD47")

    def _search(self, graph, start, end):
        def h(n):
            return abs(n[0] - end[0]) + abs(n[1] - end[1])

        came_from: Dict[Position, Optional[Position]] = {start: None}
        g_score = {start: 0}
        closed: set = set()
        heap = [(h(start), 0, 0, start)]
        counter = 0
        exploration: List[Position] = []
        visited = 0

        while heap:
            _, cost, _, node = heapq.heappop(heap)
            if node in closed:
                continue
            closed.add(node)
            exploration.append(node)
            visited += 1
            if node == end:
                return self._reconstruct(came_from, end), visited, exploration, came_from
            for nb in graph.get(node, []):
                if nb in closed:
                    continue
                nc = cost + 1
                if nb not in g_score or nc < g_score[nb]:
                    g_score[nb] = nc
                    came_from[nb] = node
                    counter += 1
                    heapq.heappush(heap, (nc + h(nb), nc, counter, nb))

        return None, visited, exploration, came_from


class GroverSolver(Solver):
    """
    Grover's quantum search — IBM hardware or Qiskit Statevector simulator.

    Maps N passable maze nodes to indices 0..N-1 in a 2^n-dimensional
    Hilbert space (n = ceil(log2 N) qubits).  Each iteration applies:
      1. Phase-flip oracle  — negates the amplitude of |goal>
      2. Grover diffusion   — inversion about the mean (2|s><s| - I)
    After floor(pi/4 * sqrt(N)) iterations the goal amplitude dominates
    and is identified with O(sqrt N) oracle queries.

    Mode selection (controlled by module-level flags):
      IBM_HARDWARE=True  + N <= IBM_HARDWARE_MAX_NODES → real IBM quantum chip
      otherwise                                         → Qiskit Statevector sim
    """

    def __init__(self):
        super().__init__("Grover (Q)", "#9B59B6")

    # ------------------------------------------------------------------ #
    #  Circuit builder  (used by hardware path)                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_circuit(n_qubits: int, target: int, iterations: int):
        """Return a measured Grover QuantumCircuit ready for transpilation."""
        from qiskit import QuantumCircuit

        def oracle(n, t):
            qc = QuantumCircuit(n, name="oracle")
            for bit in range(n):
                if not (t >> bit) & 1:
                    qc.x(bit)
            qc.h(n - 1)
            if n > 1:
                qc.mcx(list(range(n - 1)), n - 1)
            else:
                qc.x(0)
            qc.h(n - 1)
            for bit in range(n):
                if not (t >> bit) & 1:
                    qc.x(bit)
            return qc

        def diffusion(n):
            qc = QuantumCircuit(n, name="diffusion")
            qc.h(range(n))
            qc.x(range(n))
            qc.h(n - 1)
            if n > 1:
                qc.mcx(list(range(n - 1)), n - 1)
            else:
                qc.x(0)
            qc.h(n - 1)
            qc.x(range(n))
            qc.h(range(n))
            return qc

        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(range(n_qubits))
        for _ in range(iterations):
            qc.compose(oracle(n_qubits, target), inplace=True)
            qc.compose(diffusion(n_qubits), inplace=True)
        qc.measure(range(n_qubits), range(n_qubits))
        return qc

    # ------------------------------------------------------------------ #
    #  Hardware path — real IBM quantum computer                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _grover_hardware(N: int, target_idx: int) -> int:
        """Submit a Grover circuit to the least-busy real IBM quantum backend."""
        from qiskit import transpile
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

        n = max(1, math.ceil(math.log2(max(N, 2))))
        iterations = max(1, round(math.pi / 4 * math.sqrt(N)))

        qc = GroverSolver._build_circuit(n, target_idx, iterations)

        service = QiskitRuntimeService(channel="ibm_quantum_platform", token="0MqTaKKmutoks2zcvJQpvb99KD3r-OWQ1sjXG6d4tIyw")
        backend = service.least_busy(
            operational=True, simulator=False, min_num_qubits=n)

        print(f"[Grover] Submitting to IBM backend: {backend.name}  "
              f"({n} qubits, {iterations} iterations) — may take a few minutes...")

        compiled = transpile(qc, backend, optimization_level=3)

        # Open plan does not support Sessions — run as a plain job
        sampler = SamplerV2(mode=backend)
        result = sampler.run([compiled], shots=1024).result()

        counts = result[0].data.c.get_counts()
        best = max(counts, key=counts.get)
        print(f"[Grover] Result from {backend.name}: {best} "
              f"(target={format(target_idx, f'0{n}b')})")
        return int(best, 2)

    # ------------------------------------------------------------------ #
    #  Simulator path — Qiskit Statevector (exact, fast)                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _grover_simulator(N: int, target_idx: int) -> int:
        """Run Grover's algorithm via Qiskit Statevector simulation."""
        n = max(1, math.ceil(math.log2(max(N, 2))))
        M = 2 ** n
        iterations = max(1, round(math.pi / 4 * math.sqrt(N)))

        data = np.ones(M, dtype=complex) / math.sqrt(M)
        state = _QkStatevector(data)

        for _ in range(iterations):
            d = state.data.copy()
            d[target_idx] *= -1
            state = _QkStatevector(d)

            mean = np.mean(state.data)
            state = _QkStatevector(2.0 * mean - state.data)

        return int(np.argmax(state.probabilities()))

    # ------------------------------------------------------------------ #
    #  Classical fallback: bidirectional BFS                               #
    # ------------------------------------------------------------------ #

    def _bidir_bfs(self, graph, start, end):
        fwd: Dict[Position, Optional[Position]] = {start: None}
        bwd: Dict[Position, Optional[Position]] = {end: None}
        ff, bf = {start}, {end}
        exploration: List[Position] = [start]
        visited = 2

        while ff and bf:
            if len(ff) <= len(bf):
                ff, visited, meet, new = self._expand(ff, fwd, bwd, graph, visited)
                exploration.extend(new)
                if meet is not None:
                    return self._join(fwd, bwd, meet), visited, exploration, fwd
            else:
                bf, visited, meet, new = self._expand(bf, bwd, fwd, graph, visited)
                exploration.extend(new)
                if meet is not None:
                    return self._join(fwd, bwd, meet), visited, exploration, fwd

        return None, visited, exploration, fwd

    def _expand(self, frontier, own, other, graph, visited):
        nxt: set = set()
        new_nodes: List[Position] = []
        for node in frontier:
            for nb in graph.get(node, []):
                if nb not in own:
                    own[nb] = node
                    visited += 1
                    new_nodes.append(nb)
                    if nb in other:
                        return nxt, visited, nb, new_nodes
                    nxt.add(nb)
        return nxt, visited, None, new_nodes

    def _join(self, fwd: dict, bwd: dict, meeting: Position) -> List[Position]:
        fwd_path: List[Position] = []
        node: Optional[Position] = meeting
        while node is not None:
            fwd_path.append(node)
            node = fwd[node]
        fwd_path.reverse()

        bwd_path: List[Position] = []
        node = bwd[meeting]
        while node is not None:
            bwd_path.append(node)
            node = bwd[node]

        return fwd_path + bwd_path

    # ------------------------------------------------------------------ #
    #  Main search                                                         #
    # ------------------------------------------------------------------ #

    def _search(self, graph, start, end):
        if start == end:
            return [start], 1, [start], {start: None}

        if not _QISKIT_OK:
            return self._bidir_bfs(graph, start, end)

        nodes = sorted(graph.keys())
        N = len(nodes)
        target_idx = nodes.index(end)

        try:
            if IBM_HARDWARE and N <= IBM_HARDWARE_MAX_NODES:
                measured = self._grover_hardware(N, target_idx)
            else:
                measured = self._grover_simulator(N, target_idx)

            if measured < N:
                quantum_goal = nodes[measured]
                if quantum_goal != end:
                    # Hardware noise produced a wrong index — NISQ error, use true goal
                    print(f"[Grover] Hardware noise: measured index {measured} "
                          f"(expected {target_idx}). Using true goal for path.")
                    quantum_goal = end
            else:
                quantum_goal = end
        except Exception as exc:
            print(f"[Grover] Error ({exc}), falling back to simulator")
            try:
                measured = self._grover_simulator(N, target_idx)
                quantum_goal = nodes[measured] if measured < N else end
            except Exception:
                quantum_goal = end

        came_from: Dict[Position, Optional[Position]] = {start: None}
        queue: deque = deque([start])
        exploration: List[Position] = []
        visited = 0

        while queue:
            node = queue.popleft()
            exploration.append(node)
            visited += 1
            if node == quantum_goal:
                return self._reconstruct(came_from, quantum_goal), visited, exploration, came_from
            for nb in graph.get(node, []):
                if nb not in came_from:
                    came_from[nb] = node
                    queue.append(nb)

        return None, visited, exploration, came_from


ALL_SOLVERS: List[Solver] = [
    BFSSolver(),
    DFSSolver(),
    AStarSolver(),
    GroverSolver(),
]

MAZE_NAMES = [
    'Laberinto 1 (pequeño)',
    'Laberinto 2 (mediano)',
    'Laberinto 3 (grande)',
    'Laberinto 4 (extra grande)',
]
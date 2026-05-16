import random
from typing import List

from ..constants import all_possible_gens
from ..models.ga_stats import GAHistory, GenerationStats

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def _colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def print_header():
    print()
    print(_colored("=" * 62, CYAN))
    print(_colored("   GENETIC ALGORITHM  —  Workshop USFQ  —  Console", BOLD + CYAN))
    print(_colored("=" * 62, CYAN))
    print()


def print_separator(char: str = "-", width: int = 62):
    print(_colored(char * width, DIM))


def print_generation(stats: GenerationStats, verbose: bool = True):
    if not verbose:
        if stats.generation % 50 == 0:
            pct = stats.match_ratio * 100
            bar_len = 30
            filled = int(bar_len * stats.match_ratio)
            bar = "#" * filled + "-" * (bar_len - filled)
            print(f"  Gen {stats.generation:5d} [{bar}] {pct:5.1f}%  best: {stats.best_individual!r}")
        return

    # Colored diff: green for match, red for mismatch
    diff_colored = ""
    for a, b in zip(stats.best_individual, stats.objective):
        if a == b:
            diff_colored += _colored(a, GREEN)
        else:
            diff_colored += _colored(a, RED)

    match_str = f"{stats.match_count}/{len(stats.objective)}"
    print(
        f"  Gen {stats.generation:5d} | "
        f"Best {_colored(f'{stats.best_fitness:6.1f}', YELLOW)} | "
        f"Mean {stats.mean_fitness:6.1f} | "
        f"Div {stats.diversity:.2f} | "
        f"Match {_colored(match_str, GREEN)}"
    )
    print(f"           -> {diff_colored}")


def print_ascii_chart(history: GAHistory, width: int = 58, height: int = 12):
    """Renders a simple ASCII convergence chart for best fitness."""
    data = history.best_fitness_history
    if not data:
        return

    max_val = max(data) or 1
    min_val = min(data)
    span = max_val - min_val or 1

    print()
    print(_colored("  Fitness Convergence", BOLD))
    print(_colored(f"  {'─' * width}", DIM))

    rows = []
    for row in range(height, 0, -1):
        threshold = min_val + span * (row / height)
        line = ""
        step = max(1, len(data) // width)
        for i in range(0, len(data), step):
            line += "*" if data[i] >= threshold else " "
        label = f"{threshold:6.1f} |"
        rows.append(f"  {label}{line}")

    print("\n".join(rows))
    x_axis = "  " + " " * 8 + "0" + " " * (width // 2 - 3) + f"gen {len(data)}"
    print(_colored(f"  {'─' * (width + 8)}", DIM))
    print(_colored(x_axis, DIM))
    print()


def print_stats_summary(history: GAHistory):
    """Prints a final statistics table after a run."""
    print()
    print(_colored("  ── Final Statistics ──────────────────────────────", BOLD))
    status = _colored("SUCCESS", GREEN) if history.success else _colored("NOT FOUND", RED)
    print(f"  Status          : {status}")
    print(f"  Generations     : {history.total_generations}")

    if history.generations:
        last = history.generations[-1]
        first = history.generations[0]
        print(f"  Initial best    : {first.best_fitness:.1f}  ({first.best_individual!r})")
        print(f"  Final best      : {last.best_fitness:.1f}  ({last.best_individual!r})")
        print(f"  Objective       : {last.objective!r}")
        print(f"  Match           : {last.match_count}/{len(last.objective)} chars")

        fitnesses = history.best_fitness_history
        print(f"  Peak fitness    : {max(fitnesses):.1f}")
        print(f"  Avg fitness     : {sum(fitnesses)/len(fitnesses):.2f}")
        divs = history.diversity_history
        print(f"  Avg diversity   : {sum(divs)/len(divs):.2%}")
    print()


def print_chromosome_demo(target_len: int = 20, n: int = 8):
    """Displays randomly generated chromosomes to illustrate the search space."""
    print()
    print(_colored("  ── Random Chromosome Demo ──────────────────────────", BOLD))
    print(f"  Alphabet size: {len(all_possible_gens)} chars  |  Chromosome length: {target_len}")
    print_separator()
    for i in range(n):
        chrom = "".join(random.choice(all_possible_gens) for _ in range(target_len))
        print(f"  [{i+1}] {chrom}")
    print_separator()
    total = len(all_possible_gens) ** target_len
    print(f"  Search space: {len(all_possible_gens)}^{target_len} = {total:.2e} combinations")
    print()

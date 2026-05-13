from ..engine.ga import GAConfig, GeneticAlgorithm
from ..operators.crossover import SinglePoint, TwoPoint, Uniform
from ..operators.fitness import HammingDistance, MatchCount
from ..operators.mutation import RandomGene, SwapGene
from ..operators.selection import Elitist, RouletteWheel, Tournament
from .display import (
    GREEN, RED, YELLOW, CYAN, BOLD, RESET,
    print_ascii_chart,
    print_chromosome_demo,
    print_generation,
    print_header,
    print_separator,
    print_stats_summary,
)


class ConsoleApp:
    def __init__(self):
        self.objective = "GA Workshop! USFQ"
        self.config = GAConfig(population_size=100, mutation_rate=0.01, n_iterations=1000, seed=42)
        self.fitness_op = MatchCount()
        self.selection_op = RouletteWheel()
        self.crossover_op = SinglePoint()
        self.mutation_op = RandomGene()
        self.history = None
        self.verbose = True

    # ── menu helpers ────────────────────────────────────────────────────────

    def _banner(self, title: str):
        print()
        print(f"{CYAN}{BOLD}  ── {title} {'─' * (50 - len(title))}{RESET}")

    def _prompt(self, msg: str, default: str = "") -> str:
        hint = f" [{default}]" if default else ""
        val = input(f"  {msg}{hint}: ").strip()
        return val if val else default

    def _current_config(self):
        print()
        print(f"  Target       : {YELLOW}{self.objective!r}{RESET}")
        print(f"  Population   : {self.config.population_size}")
        print(f"  Mutation rate: {self.config.mutation_rate}")
        print(f"  Iterations   : {self.config.n_iterations}")
        print(f"  Seed         : {self.config.seed}")
        print(f"  Fitness      : {self.fitness_op.label}")
        print(f"  Selection    : {self.selection_op.label}")
        print(f"  Crossover    : {self.crossover_op.label}")
        print(f"  Mutation     : {self.mutation_op.label}")
        print(f"  Verbose      : {self.verbose}")

    # ── sub-menus ───────────────────────────────────────────────────────────

    def _set_objective(self):
        self._banner("Set Target Expression")
        val = self._prompt("Enter target string", self.objective)
        if val:
            self.objective = val
        print(f"  Target set to: {YELLOW}{self.objective!r}{RESET}")

    def _set_parameters(self):
        self._banner("Set GA Parameters")
        try:
            val = self._prompt("Population size", str(self.config.population_size))
            self.config.population_size = int(val)
            val = self._prompt("Mutation rate (0-1)", str(self.config.mutation_rate))
            self.config.mutation_rate = float(val)
            val = self._prompt("Max iterations", str(self.config.n_iterations))
            self.config.n_iterations = int(val)
            val = self._prompt("Random seed (blank=none)", str(self.config.seed) if self.config.seed else "")
            self.config.seed = int(val) if val else None
        except ValueError:
            print(f"  {RED}Invalid input — keeping previous values.{RESET}")

    def _select_operators(self):
        self._banner("Select Operators")

        fitness_opts = [MatchCount(), HammingDistance()]
        print("  Fitness evaluator:")
        for i, op in enumerate(fitness_opts, 1):
            print(f"    {i}. {op.label}")
        try:
            idx = int(self._prompt("Choice", "1")) - 1
            self.fitness_op = fitness_opts[idx]
        except (ValueError, IndexError):
            pass

        selection_opts = [RouletteWheel(), Tournament(k=3), Elitist(top_fraction=0.3)]
        print("  Selection operator:")
        for i, op in enumerate(selection_opts, 1):
            print(f"    {i}. {op.label}")
        try:
            idx = int(self._prompt("Choice", "1")) - 1
            self.selection_op = selection_opts[idx]
        except (ValueError, IndexError):
            pass

        crossover_opts = [SinglePoint(), TwoPoint(), Uniform()]
        print("  Crossover operator:")
        for i, op in enumerate(crossover_opts, 1):
            print(f"    {i}. {op.label}")
        try:
            idx = int(self._prompt("Choice", "1")) - 1
            self.crossover_op = crossover_opts[idx]
        except (ValueError, IndexError):
            pass

        mutation_opts = [RandomGene(), SwapGene()]
        print("  Mutation operator:")
        for i, op in enumerate(mutation_opts, 1):
            print(f"    {i}. {op.label}")
        try:
            idx = int(self._prompt("Choice", "1")) - 1
            self.mutation_op = mutation_opts[idx]
        except (ValueError, IndexError):
            pass

        verbose_val = self._prompt("Verbose output? (y/n)", "y" if self.verbose else "n")
        self.verbose = verbose_val.lower() != "n"

    def _run_ga(self):
        self._banner("Running Genetic Algorithm")
        self._current_config()
        print_separator()

        ga = GeneticAlgorithm(
            objective=self.objective,
            config=self.config,
            fitness=self.fitness_op,
            selection=self.selection_op,
            crossover=self.crossover_op,
            mutation=self.mutation_op,
        )

        def on_gen(stats):
            print_generation(stats, verbose=self.verbose)

        ga.on_generation(on_gen)
        self.history = ga.run()

        print_separator()
        status = f"{GREEN}SUCCESS{RESET}" if self.history.success else f"{RED}NOT FOUND{RESET}"
        print(f"\n  Result: {status} in {self.history.total_generations} generations")

    def _show_stats(self):
        if self.history is None:
            print(f"\n  {RED}No run data yet — run the GA first (option 4).{RESET}")
            return
        self._banner("Statistics")
        print_stats_summary(self.history)
        print_ascii_chart(self.history)

    def _random_demo(self):
        self._banner("Random Chromosome Demo")
        try:
            n = int(self._prompt("How many chromosomes to show", "8"))
            length = int(self._prompt("Chromosome length", str(len(self.objective))))
        except ValueError:
            n, length = 8, len(self.objective)
        print_chromosome_demo(target_len=length, n=n)

    # ── main loop ───────────────────────────────────────────────────────────

    def _show_menu(self):
        print()
        print(f"{BOLD}  Main Menu{RESET}")
        print_separator()
        print("  1. Set target expression")
        print("  2. Set GA parameters")
        print("  3. Select operators")
        print("  4. Run GA")
        print("  5. View statistics & chart")
        print("  6. Random chromosome demo")
        print("  0. Exit")
        print_separator()

    def run(self):
        print_header()
        while True:
            self._show_menu()
            choice = input("  Option: ").strip()
            if choice == "0":
                print(f"\n  {CYAN}Bye!{RESET}\n")
                break
            elif choice == "1":
                self._set_objective()
            elif choice == "2":
                self._set_parameters()
            elif choice == "3":
                self._select_operators()
            elif choice == "4":
                self._run_ga()
            elif choice == "5":
                self._show_stats()
            elif choice == "6":
                self._random_demo()
            else:
                print(f"  {RED}Unknown option.{RESET}")


def main():
    ConsoleApp().run()


if __name__ == "__main__":
    main()

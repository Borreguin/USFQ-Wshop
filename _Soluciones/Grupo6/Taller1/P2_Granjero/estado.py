from dataclasses import dataclass

@dataclass(frozen=True)
class Estado:
    granjero: int
    lobo:     int
    cabra:    int
    col:      int

    def es_valido(self) -> bool:
        if self.lobo == self.cabra and self.granjero != self.lobo:
            return False
        if self.cabra == self.col and self.granjero != self.cabra:
            return False
        return True

    def es_objetivo(self) -> bool:
        return self.granjero == self.lobo == self.cabra == self.col == 1

    def __str__(self):
        lado = lambda x: "der" if x else "izq"
        return (f"G:{lado(self.granjero)} "
                f"L:{lado(self.lobo)} "
                f"C:{lado(self.cabra)} "
                f"Col:{lado(self.col)}")
import tkinter as tk
from tkinter import ttk

W, H          = 900, 560
BASE_Y        = 460
POLE_W        = 14
POLE_H        = 300
DISK_H        = 32
DISK_MAX_W    = 200
DISK_MIN_W    = 50
PEG_XS        = [150, 450, 750]
BASE_H        = 18
COLORS        = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c", "#3498db", "#9b59b6"]
BG            = "#1e1e2e"
POLE_COLOR    = "#a0856c"
BASE_COLOR    = "#7d5a45"
TEXT_COLOR    = "#cdd6f4"
HIGHLIGHT     = "#ffd700"
DEFAULT_DELAY = 700


def disk_width(disk: int, n: int) -> float:
    return DISK_MIN_W + (disk - 1) * (DISK_MAX_W - DISK_MIN_W) / max(n - 1, 1)


class HanoiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Torres de Hanoi – Simulación")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._running = False
        self._build_ui()
        self.reset()

    def _build_ui(self):
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=20, pady=8)

        tk.Label(ctrl, text="Discos:", bg=BG, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.disk_var = tk.IntVar(value=3)
        self.disk_var.trace_add("write", lambda *_: self.root.after(50, self._safe_reset))
        self.disk_spin = ttk.Spinbox(ctrl, from_=1, to=7, textvariable=self.disk_var,
                                     width=4, font=("Segoe UI", 11))
        self.disk_spin.pack(side=tk.LEFT, padx=(4, 20))

        tk.Label(ctrl, text="Velocidad:", bg=BG, fg=TEXT_COLOR, font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=DEFAULT_DELAY)
        for label, val in [("Lento", 1200), ("Normal", 700), ("Rápido", 300), ("Turbo", 80)]:
            tk.Radiobutton(ctrl, text=label, variable=self.speed_var, value=val,
                           bg=BG, fg=TEXT_COLOR, selectcolor="#313244",
                           activebackground=BG, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=4)

        self.start_btn = tk.Button(ctrl, text="▶  Iniciar", command=self.start,
                                   bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                                   relief=tk.FLAT, padx=12, pady=4, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=(20, 6))

        tk.Button(ctrl, text="↺  Reiniciar", command=self.reset,
                  bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=4)

        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 4))

        status_bar = tk.Frame(self.root, bg="#313244")
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.status_var = tk.StringVar(value="Configura los discos y pulsa Iniciar.")
        tk.Label(status_bar, textvariable=self.status_var, bg="#313244", fg=TEXT_COLOR,
                 font=("Segoe UI", 10), anchor=tk.W, padx=8, pady=4).pack(fill=tk.X)

    def _safe_reset(self):
        if not self._running:
            self.reset()

    def reset(self):
        self._running = False
        self.start_btn.config(state=tk.NORMAL)
        self.disk_spin.config(state=tk.NORMAL)
        n = self.disk_var.get()
        self.towers = {0: list(range(n, 0, -1)), 1: [], 2: []}
        self.moves: list[tuple[int, int]] = []
        self._solve(n, 0, 2, 1)
        self.step = 0
        self.status_var.set(
            f"Discos: {n}  |  Movimientos necesarios: {len(self.moves)}  (2ⁿ−1 = {2**n - 1})"
        )
        self._draw()

    def _solve(self, n: int, src: int, dst: int, aux: int):
        if n == 0:
            return
        self._solve(n - 1, src, aux, dst)
        self.moves.append((src, dst))
        self._solve(n - 1, aux, dst, src)

    def start(self):
        if self._running:
            return
        self.reset()
        self._running = True
        self.start_btn.config(state=tk.DISABLED)
        self.disk_spin.config(state=tk.DISABLED)
        self._animate()

    def _animate(self):
        if not self._running or self.step >= len(self.moves):
            self._running = False
            n = self.disk_var.get()
            self.status_var.set(
                f"¡Completado! {len(self.moves)} movimientos para {n} disco{'s' if n > 1 else ''}."
            )
            self.start_btn.config(state=tk.NORMAL)
            return

        src, dst = self.moves[self.step]
        disk = self.towers[src].pop()
        self.towers[dst].append(disk)
        self.step += 1

        self.status_var.set(
            f"Movimiento {self.step}/{len(self.moves)}  |  Torre {src + 1} → Torre {dst + 1}  |  Disco {disk}"
        )
        self._draw(last_peg=dst, last_disk=disk)
        self.root.after(self.speed_var.get(), self._animate)

    def _draw(self, last_peg: int | None = None, last_disk: int | None = None):
        self.canvas.delete("all")
        n = self.disk_var.get()

        self.canvas.create_rectangle(20, BASE_Y, W - 20, BASE_Y + BASE_H, fill=BASE_COLOR, outline="")

        peg_labels = ["Torre 1\n(Origen)", "Torre 2\n(Auxiliar)", "Torre 3\n(Destino)"]
        for idx, px in enumerate(PEG_XS):
            self.canvas.create_rectangle(
                px - POLE_W // 2, BASE_Y - POLE_H,
                px + POLE_W // 2, BASE_Y,
                fill=POLE_COLOR, outline="")
            self.canvas.create_text(px, BASE_Y + BASE_H + 22, text=peg_labels[idx],
                                    fill=TEXT_COLOR, font=("Segoe UI", 9), justify=tk.CENTER)

            for pos, disk in enumerate(self.towers[idx]):
                w  = disk_width(disk, n)
                y  = BASE_Y - BASE_H - pos * DISK_H
                x0, x1 = px - w / 2, px + w / 2
                y0, y1 = y - DISK_H + 4, y - 2

                is_highlight = (idx == last_peg and disk == last_disk)
                self.canvas.create_rectangle(x0 + 3, y0 + 3, x1 + 3, y1 + 3, fill="#111111", outline="")
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=COLORS[(disk - 1) % len(COLORS)],
                                             outline=HIGHLIGHT if is_highlight else "#000000",
                                             width=3 if is_highlight else 1)
                self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                        text=str(disk), fill="white", font=("Segoe UI", 10, "bold"))

        self.canvas.create_text(W - 20, 20, text=f"Paso {self.step} / {len(self.moves)}",
                                anchor=tk.NE, fill=TEXT_COLOR, font=("Segoe UI", 13, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    HanoiApp(root)
    root.mainloop()

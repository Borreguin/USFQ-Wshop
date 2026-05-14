import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

from util import generar_ciudades_con_distancias, calculate_path_distance, plotear_ruta
from util_nearest_neighbor import nearest_neighbor
from TSP import TSP
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime as dt

# ── colores ANSI ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

def clr(): os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    print(f"{CYAN}{BOLD}")
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        TRAVELLING SALESMAN PROBLEM — TSP            ║")
    print("  ║        MSDS 6004 Inteligencia Artificial            ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print(f"{RESET}")

def separador():
    print(f"{GRAY}  {'─'*54}{RESET}")

def menu_principal():
    clr()
    banner()
    print(f"  {BOLD}Selecciona un caso de estudio:{RESET}\n")
    print(f"  {CYAN}[0]{RESET}  Referencia — Vecino Cercano (100 ciudades)")
    print(f"  {CYAN}[1]{RESET}  Caso 1     — LP sin heurísticas (10–50 ciudades)")
    print(f"  {CYAN}[2]{RESET}  Caso 2     — Heurística de límites (70 ciudades)")
    print(f"  {CYAN}[3]{RESET}  Caso 3     — Heurística vecinos cercanos (100 ciudades)")
    print(f"  {CYAN}[4]{RESET}  Comparación — Todos los casos")
    separador()
    print(f"  {RED}[q]{RESET}  Salir\n")
    return input(f"  {BOLD}Opción: {RESET}").strip().lower()

def pedir_parametros_caso1():
    print(f"\n  {YELLOW}Parámetros del Caso 1:{RESET}")
    print(f"  {GRAY}(Enter para usar valor por defecto){RESET}\n")
    try:
        n_list_str = input(f"  Ciudades a probar {GRAY}[10,20,30,40,50]{RESET}: ").strip()
        n_list = [int(x) for x in n_list_str.split(",")] if n_list_str else [10, 20, 30, 40, 50]
        mipgap = float(input(f"  mipgap {GRAY}[0.05]{RESET}: ") or "0.05")
        time_limit = int(input(f"  Tiempo límite en segundos {GRAY}[30]{RESET}: ") or "30")
        tee_str = input(f"  Mostrar salida del solver (tee) {GRAY}[n]{RESET}: ").strip().lower()
        tee = tee_str in ("s", "si", "y", "yes")
        return n_list, mipgap, time_limit, tee
    except ValueError:
        print(f"\n  {RED}Parámetro inválido, usando valores por defecto.{RESET}")
        return [10, 20, 30, 40, 50], 0.05, 30, False

def pedir_parametros_caso2():
    print(f"\n  {YELLOW}Parámetros del Caso 2:{RESET}")
    print(f"  {GRAY}(Enter para usar valor por defecto){RESET}\n")
    try:
        n = int(input(f"  Número de ciudades {GRAY}[70]{RESET}: ") or "70")
        mipgap = float(input(f"  mipgap {GRAY}[0.2]{RESET}: ") or "0.2")
        time_limit = int(input(f"  Tiempo límite en segundos {GRAY}[40]{RESET}: ") or "40")
        tee_str = input(f"  Mostrar salida del solver (tee) {GRAY}[s]{RESET}: ").strip().lower()
        tee = tee_str not in ("n", "no")
        return n, mipgap, time_limit, tee
    except ValueError:
        print(f"\n  {RED}Parámetro inválido, usando valores por defecto.{RESET}")
        return 70, 0.2, 40, True

def pedir_parametros_caso3():
    print(f"\n  {YELLOW}Parámetros del Caso 3:{RESET}")
    print(f"  {GRAY}(Enter para usar valor por defecto){RESET}\n")
    try:
        n = int(input(f"  Número de ciudades {GRAY}[100]{RESET}: ") or "100")
        mipgap = float(input(f"  mipgap {GRAY}[0.05]{RESET}: ") or "0.05")
        time_limit = int(input(f"  Tiempo límite en segundos {GRAY}[60]{RESET}: ") or "60")
        tee_str = input(f"  Mostrar salida del solver (tee) {GRAY}[s]{RESET}: ").strip().lower()
        tee = tee_str not in ("n", "no")
        return n, mipgap, time_limit, tee
    except ValueError:
        print(f"\n  {RED}Parámetro inválido, usando valores por defecto.{RESET}")
        return 100, 0.05, 60, True

# ── RESULTADOS almacenados para comparación ───────────────────────────────────
resultados = []  # lista de dicts con info de cada corrida

def guardar_resultado(label, n, distancia, tiempo_seg, heuristica):
    resultados.append({
        "label": label,
        "n": n,
        "distancia": distancia,
        "tiempo": tiempo_seg,
        "heuristica": heuristica,
    })

def imprimir_tabla_resultados():
    if not resultados:
        print(f"\n  {YELLOW}Aún no hay resultados. Corre al menos un caso primero.{RESET}\n")
        return
    separador()
    print(f"\n  {BOLD}{'Caso':<35} {'N':>5} {'Distancia':>12} {'Tiempo':>10} {'Heurística'}{RESET}")
    separador()
    best_dist = min(r["distancia"] for r in resultados)
    for r in resultados:
        dist_str = f"{r['distancia']:.2f}"
        color = GREEN if r["distancia"] == best_dist else WHITE
        print(f"  {CYAN}{r['label']:<35}{RESET} {r['n']:>5} {color}{dist_str:>12}{RESET} {r['tiempo']:>9.1f}s  {GRAY}{r['heuristica']}{RESET}")
    separador()

def grafica_comparacion():
    if not resultados:
        print(f"\n  {YELLOW}No hay resultados para comparar.{RESET}\n")
        return
    labels = [r["label"] for r in resultados]
    distancias = [r["distancia"] for r in resultados]
    colores = ["#2ecc71" if d == min(distancias) else "#3498db" for d in distancias]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels, distancias, color=colores, edgecolor="white", height=0.5)
    ax.set_xlabel("Distancia total recorrida", fontsize=11)
    ax.set_title("Comparación de casos TSP", fontsize=13, fontweight="bold")
    ax.bar_label(bars, fmt="%.1f", padding=5, fontsize=9)
    ax.set_xlim(0, max(distancias) * 1.15)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

# ── CASO 0: referencia ────────────────────────────────────────────────────────
def run_referencia():
    clr(); banner()
    print(f"  {BOLD}REFERENCIA — Vecino Cercano (100 ciudades){RESET}\n")
    t0 = dt.datetime.now()
    ciudades, distancias = generar_ciudades_con_distancias(100)
    ruta = nearest_neighbor(ciudades, distancias)
    dist = calculate_path_distance(distancias, ruta)
    elapsed = (dt.datetime.now() - t0).total_seconds()
    print(f"  {GREEN}Distancia: {dist:.2f}{RESET}  ({elapsed:.2f}s)")
    guardar_resultado("Referencia — Vecino Cercano (100c)", 100, dist, elapsed, "greedy")
    plotear_ruta(ciudades, distancias, ruta, True)
    imprimir_tabla_resultados()
    input(f"\n  {GRAY}Enter para volver al menú...{RESET}")

# ── CASO 1 ────────────────────────────────────────────────────────────────────
def run_caso1():
    clr(); banner()
    print(f"  {BOLD}CASO 1 — LP sin heurísticas{RESET}\n")
    n_list, mipgap, time_limit, tee = pedir_parametros_caso1()

    rutas_lp = []
    rutas_nn = []
    labels_plot = []

    for n in n_list:
        separador()
        print(f"\n  {CYAN}▶ {n} ciudades...{RESET}")
        ciudades, distancias = generar_ciudades_con_distancias(n)

        t0 = dt.datetime.now()
        tsp = TSP(ciudades, distancias, heuristics=[])
        ruta_lp = tsp.encontrar_la_ruta_mas_corta(mipgap=mipgap, time_limit=time_limit, tee=tee)
        elapsed = (dt.datetime.now() - t0).total_seconds()

        ruta_nn = nearest_neighbor(ciudades, distancias)
        dist_nn = calculate_path_distance(distancias, ruta_nn)
        dist_lp = calculate_path_distance(distancias, ruta_lp)
        mejora = (dist_nn - dist_lp) / dist_nn * 100

        color = GREEN if mejora > 0 else RED
        print(f"  LP: {color}{dist_lp:.2f}{RESET}  |  NN: {dist_nn:.2f}  |  Mejora: {color}{mejora:+.1f}%{RESET}  ({elapsed:.1f}s)")

        guardar_resultado(f"Caso 1 — LP sin heurística ({n}c)", n, dist_lp, elapsed, "ninguna")
        rutas_lp.append((ciudades, distancias, ruta_lp, dist_lp))
        rutas_nn.append((ciudades, distancias, ruta_nn, dist_nn))
        labels_plot.append(n)

    # Gráfica comparativa LP vs NN por n
    fig, axes = plt.subplots(2, len(n_list), figsize=(4 * len(n_list), 8))
    if len(n_list) == 1:
        axes = [[axes[0]], [axes[1]]]
    for idx, n in enumerate(n_list):
        ciudades, distancias, ruta_lp, dist_lp = rutas_lp[idx]
        _, _, ruta_nn, dist_nn = rutas_nn[idx]
        for ax, ruta, dist, titulo in [
            (axes[0][idx], ruta_lp, dist_lp, f"LP ({n}c)\n{dist_lp:.1f}"),
            (axes[1][idx], ruta_nn, dist_nn, f"NN ({n}c)\n{dist_nn:.1f}"),
        ]:
            xs = [ciudades[c][0] for c in ruta]
            ys = [ciudades[c][1] for c in ruta]
            ax.plot(xs, ys, 'r-o', markersize=3, linewidth=0.8)
            ax.set_title(titulo, fontsize=9)
            ax.axis("off")
    axes[0][0].set_ylabel("LP", fontsize=10, fontweight="bold")
    axes[1][0].set_ylabel("Vecino Cercano", fontsize=10, fontweight="bold")
    plt.suptitle("Caso 1 — LP vs Vecino Cercano", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.show()

    imprimir_tabla_resultados()
    input(f"\n  {GRAY}Enter para volver al menú...{RESET}")

# ── CASO 2 ────────────────────────────────────────────────────────────────────
def run_caso2():
    clr(); banner()
    print(f"  {BOLD}CASO 2 — Heurística de límites{RESET}\n")
    n, mipgap, time_limit, tee = pedir_parametros_caso2()

    ciudades, distancias = generar_ciudades_con_distancias(n)

    print(f"\n  {CYAN}▶ CON heurística: limitar_funcion_objetivo...{RESET}")
    t0 = dt.datetime.now()
    tsp_con = TSP(ciudades, distancias, heuristics=["limitar_funcion_objetivo"])
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap=mipgap, time_limit=time_limit, tee=tee)
    t_con = (dt.datetime.now() - t0).total_seconds()
    dist_con = calculate_path_distance(distancias, ruta_con)
    print(f"  {GREEN}CON heurística: {dist_con:.2f}{RESET}  ({t_con:.1f}s)")
    guardar_resultado(f"Caso 2 — CON límites ({n}c)", n, dist_con, t_con, "limitar_funcion_objetivo")

    print(f"\n  {CYAN}▶ SIN heurística...{RESET}")
    t0 = dt.datetime.now()
    tsp_sin = TSP(ciudades, distancias, heuristics=[])
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap=mipgap, time_limit=time_limit, tee=tee)
    t_sin = (dt.datetime.now() - t0).total_seconds()
    dist_sin = calculate_path_distance(distancias, ruta_sin)
    print(f"  {YELLOW}SIN heurística: {dist_sin:.2f}{RESET}  ({t_sin:.1f}s)")
    guardar_resultado(f"Caso 2 — SIN heurística ({n}c)", n, dist_sin, t_sin, "ninguna")

    diferencia = (dist_sin - dist_con) / dist_sin * 100
    color = GREEN if diferencia > 0 else RED
    print(f"\n  Diferencia: {color}{diferencia:+.1f}% {'(con heurística es mejor)' if diferencia > 0 else '(sin heurística es mejor)'}{RESET}")

    # Gráfica lado a lado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for ax, ruta, dist, titulo, color_line in [
        (ax1, ruta_con, dist_con, f"CON heurística de límites\nDistancia: {dist_con:.2f}", "red"),
        (ax2, ruta_sin, dist_sin, f"SIN heurística\nDistancia: {dist_sin:.2f}", "red"),
    ]:
        xs = [ciudades[c][0] for c in ruta]
        ys = [ciudades[c][1] for c in ruta]
        ax.plot(xs, ys, f'{color_line}-o', markersize=4, linewidth=1)
        ax.set_title(titulo, fontsize=10, fontweight="bold")
        ax.set_xlabel("Coordenada X"); ax.set_ylabel("Coordenada Y")
        ax.grid(True, alpha=0.3)
    plt.suptitle(f"Caso 2 — {n} ciudades | mipgap={mipgap} | límite={time_limit}s", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.show()

    imprimir_tabla_resultados()
    input(f"\n  {GRAY}Enter para volver al menú...{RESET}")

# ── CASO 3 ────────────────────────────────────────────────────────────────────
def run_caso3():
    clr(); banner()
    print(f"  {BOLD}CASO 3 — Heurística de vecinos cercanos{RESET}\n")
    n, mipgap, time_limit, tee = pedir_parametros_caso3()

    ciudades, distancias = generar_ciudades_con_distancias(n)

    print(f"\n  {CYAN}▶ CON heurística: vecino_cercano...{RESET}")
    t0 = dt.datetime.now()
    tsp_con = TSP(ciudades, distancias, heuristics=["vecino_cercano"])
    ruta_con = tsp_con.encontrar_la_ruta_mas_corta(mipgap=mipgap, time_limit=time_limit, tee=tee)
    t_con = (dt.datetime.now() - t0).total_seconds()
    dist_con = calculate_path_distance(distancias, ruta_con)
    print(f"  {GREEN}CON heurística: {dist_con:.2f}{RESET}  ({t_con:.1f}s)")
    guardar_resultado(f"Caso 3 — CON vecinos ({n}c)", n, dist_con, t_con, "vecino_cercano")

    print(f"\n  {CYAN}▶ SIN heurística...{RESET}")
    t0 = dt.datetime.now()
    tsp_sin = TSP(ciudades, distancias, heuristics=[])
    ruta_sin = tsp_sin.encontrar_la_ruta_mas_corta(mipgap=mipgap, time_limit=time_limit, tee=tee)
    t_sin = (dt.datetime.now() - t0).total_seconds()
    dist_sin = calculate_path_distance(distancias, ruta_sin)
    print(f"  {YELLOW}SIN heurística: {dist_sin:.2f}{RESET}  ({t_sin:.1f}s)")
    guardar_resultado(f"Caso 3 — SIN heurística ({n}c)", n, dist_sin, t_sin, "ninguna")

    # Vecino cercano como referencia adicional
    ruta_nn = nearest_neighbor(ciudades, distancias)
    dist_nn = calculate_path_distance(distancias, ruta_nn)
    print(f"  {GRAY}Referencia vecino cercano: {dist_nn:.2f}{RESET}")
    guardar_resultado(f"Caso 3 — Vecino Cercano ({n}c)", n, dist_nn, 0, "greedy")

    diferencia = (dist_sin - dist_con) / dist_sin * 100
    color = GREEN if diferencia > 0 else RED
    print(f"\n  Diferencia LP: {color}{diferencia:+.1f}% {'(con heurística es mejor)' if diferencia > 0 else '(sin heurística es mejor)'}{RESET}")

    # Gráfica tres rutas
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    for ax, ruta, dist, titulo in [
        (ax1, ruta_con, dist_con, f"CON heurística vecinos\n{dist_con:.2f}"),
        (ax2, ruta_sin, dist_sin, f"SIN heurística\n{dist_sin:.2f}"),
        (ax3, ruta_nn,  dist_nn,  f"Vecino Cercano (ref.)\n{dist_nn:.2f}"),
    ]:
        xs = [ciudades[c][0] for c in ruta]
        ys = [ciudades[c][1] for c in ruta]
        ax.plot(xs, ys, 'r-o', markersize=3, linewidth=0.8)
        ax.set_title(titulo, fontsize=10, fontweight="bold")
        ax.set_xlabel("X"); ax.set_ylabel("Y")
        ax.grid(True, alpha=0.3)
    plt.suptitle(f"Caso 3 — {n} ciudades | mipgap={mipgap} | límite={time_limit}s", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.show()

    imprimir_tabla_resultados()
    input(f"\n  {GRAY}Enter para volver al menú...{RESET}")

# ── COMPARACIÓN TOTAL ─────────────────────────────────────────────────────────
def run_comparacion():
    clr(); banner()
    print(f"  {BOLD}COMPARACIÓN — Todos los casos corridos hasta ahora{RESET}\n")
    imprimir_tabla_resultados()
    if resultados:
        ver = input(f"\n  {CYAN}Ver gráfica de barras comparativa? [s/n]{RESET}: ").strip().lower()
        if ver in ("s", "si", "y", "yes", ""):
            grafica_comparacion()
    input(f"\n  {GRAY}Enter para volver al menú...{RESET}")

# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
def main():
    while True:
        opcion = menu_principal()
        if opcion == "0":
            run_referencia()
        elif opcion == "1":
            run_caso1()
        elif opcion == "2":
            run_caso2()
        elif opcion == "3":
            run_caso3()
        elif opcion == "4":
            run_comparacion()
        elif opcion in ("q", "quit", "exit"):
            clr()
            print(f"\n  {CYAN}Hasta luego.{RESET}\n")
            break
        else:
            print(f"\n  {RED}Opción no válida. Intenta de nuevo.{RESET}")
            import time; time.sleep(1)

if __name__ == "__main__":
    main()

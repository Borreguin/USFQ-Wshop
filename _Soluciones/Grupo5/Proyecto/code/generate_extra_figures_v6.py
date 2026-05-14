from pathlib import Path
import math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
FIGURES = ROOT / 'figures'
FIGURES.mkdir(exist_ok=True)

summary = pd.read_csv(RESULTS / 'summary_all_datasets.csv')
histories = {}
for path in sorted(RESULTS.glob('*_history.csv')):
    name = path.name.replace('_history.csv', '')
    histories[name] = pd.read_csv(path)

def panel_from_histories(histories, metric_cols, labels, ylabel, title, path):
    datasets = list(histories.keys())
    n = len(datasets)
    cols = 2
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(13, rows * 3.1))
    axes = np.array(axes).reshape(-1)
    for ax, ds in zip(axes, datasets):
        hist = histories[ds]
        for col, label in zip(metric_cols, labels):
            ax.plot(hist['generation'], hist[col], label=label, linewidth=1.15)
        ax.set_title(ds, fontsize=9)
        ax.grid(True, alpha=0.25)
        ax.set_xlabel('Generación')
        ax.set_ylabel(ylabel)
    for ax in axes[n:]:
        ax.axis('off')
    handles, leg_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, leg_labels, loc='upper center', ncol=len(labels), bbox_to_anchor=(0.5, 1.00))
    fig.suptitle(title, y=1.025, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(path, dpi=180, bbox_inches='tight')
    plt.close(fig)

panel_from_histories(histories,
                     ['best_fitness','avg_fitness','worst_fitness'],
                     ['Mejor fitness','Fitness promedio','Peor fitness'],
                     'Fitness = 1 / distancia',
                     'Evolución del fitness por generación y por dataset',
                     FIGURES / 'panel_fitness_all_datasets_v5.png')

panel_from_histories(histories,
                     ['best_distance_so_far','avg_distance','worst_distance'],
                     ['Mejor distancia acumulada','Distancia promedio','Peor distancia'],
                     'Distancia total',
                     'Convergencia por distancia por generación y por dataset',
                     FIGURES / 'panel_convergencia_distancia_all_datasets_v5.png')

panel_from_histories(histories,
                     ['unique_pct','hamming_pct'],
                     ['Individuos únicos (%)','Hamming promedio (%)'],
                     'Diversidad poblacional (%)',
                     'Evolución de la diversidad poblacional por dataset',
                     FIGURES / 'panel_diversidad_all_datasets_v5.png')

# Dispersión diversidad-calidad: gap negativo indica mejora vs NN.
plt.figure(figsize=(8.6,5.2))
plt.scatter(summary['unique_pct_final'], summary['gap_vs_nn_pct'])
for _, r in summary.iterrows():
    plt.annotate(r['dataset'].replace('cities_100_', ''), (r['unique_pct_final'], r['gap_vs_nn_pct']), fontsize=8, xytext=(3,3), textcoords='offset points')
plt.axhline(0, linewidth=1)
plt.xlabel('Diversidad final: individuos únicos (%)')
plt.ylabel('Gap relativo vs Nearest Neighbor (%)')
plt.title('Relación entre diversidad final y calidad de solución')
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIGURES / 'diversidad_vs_calidad_solucion.png', dpi=180)
plt.close()

# Dispersión diversidad-convergencia: más no-improve final suele indicar estancamiento.
plt.figure(figsize=(8.6,5.2))
plt.scatter(summary['hamming_pct_final'], summary['final_no_improve'])
for _, r in summary.iterrows():
    plt.annotate(r['dataset'].replace('cities_100_', ''), (r['hamming_pct_final'], r['final_no_improve']), fontsize=8, xytext=(3,3), textcoords='offset points')
plt.xlabel('Diversidad final: Hamming promedio (%)')
plt.ylabel('Generaciones finales sin mejora')
plt.title('Relación entre diversidad final y convergencia/estancamiento')
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIGURES / 'diversidad_vs_convergencia.png', dpi=180)
plt.close()

# Regenerar algunas figuras agregadas con títulos/acentos correctos.
x = np.arange(len(summary))
labels = summary['dataset'].tolist()
plt.figure(figsize=(12,5.8))
width=0.36
plt.bar(x-width/2, summary['nn_distance'], width, label='Nearest Neighbor')
plt.bar(x+width/2, summary['ga_2opt_distance'], width, label='AG elitista + 2-opt')
plt.xticks(x, labels, rotation=50, ha='right')
plt.ylabel('Distancia total')
plt.title('Comparación de calidad: heurística NN vs AG elitista + 2-opt')
plt.grid(axis='y', alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIGURES / 'comparacion_nn_vs_ag2opt_v5.png', dpi=180)
plt.close()

plt.figure(figsize=(11,5.5))
plt.bar(summary['dataset'], summary['gap_vs_nn_pct'])
plt.axhline(0, linewidth=1)
plt.xticks(rotation=50, ha='right')
plt.ylabel('Gap relativo vs NN (%)')
plt.title('Error relativo respecto a la heurística NN (negativo = mejora)')
plt.grid(axis='y', alpha=0.25)
plt.tight_layout()
plt.savefig(FIGURES / 'gap_relativo_vs_nn_v5.png', dpi=180)
plt.close()

plt.figure(figsize=(11,5.5))
plt.bar(summary['dataset'], summary['unique_pct_final'], label='Individuos únicos finales (%)')
plt.xticks(rotation=50, ha='right')
plt.ylabel('Diversidad final (%)')
plt.title('Diversidad final por dataset')
plt.grid(axis='y', alpha=0.25)
plt.tight_layout()
plt.savefig(FIGURES / 'diversidad_final_por_dataset_v5.png', dpi=180)
plt.close()

print('Figuras adicionales v5 generadas en', FIGURES)

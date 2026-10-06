"""Exportación de figuras con ejes, leyendas y resolución consistente."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .25,
                     'lines.linewidth': 1.6, 'figure.figsize': (7.2, 4.0)})


def guardar(fig, carpeta, nombre):
    for ax in fig.axes:
        ax.set_xlabel('t (unidades de tiempo)')
        ax.legend(loc='best', fontsize=8, framealpha=.85)
    fig.tight_layout()
    fig.savefig(carpeta / (nombre + '.png'), dpi=240, bbox_inches='tight')
    fig.savefig(carpeta / (nombre + '.pdf'), bbox_inches='tight')
    plt.close(fig)

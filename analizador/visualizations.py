"""Gráficos estadísticos reutilizables con Matplotlib."""

from __future__ import annotations

import inspect
from matplotlib.figure import Figure
import numpy as np

from .statistics_engine import AnalysisResult


COLORS = {
    "navy": "#DCE4EE",     # Títulos y textos principales
    "blue": "#3B82F6",     # Azul vibrante para histogramas
    "cyan": "#06B6D4",     # Cyan para barras
    "violet": "#8B5CF6",   # Violeta para polígonos
    "amber": "#F59E0B",    # Ambar para resaltados/curva
    "slate": "#94A3B8",    # Textos secundarios (ticks)
    "grid": "#475569",     # Grilla oscura
    "ink": "#F8FAFC",      # Texto claro
}

BG_COLOR = "#2B2B2B"       # Fondo que hace match con CustomTkinter Dark Mode


def create_analysis_figure(result: AnalysisResult) -> Figure:
    """Crea histograma, barras, polígono y curva acumulada."""
    figure = Figure(
        # Tamaño contenido para que el lienzo no fuerce la ventana fuera del
        # área visible cuando Windows usa escalado DPI (125 % o superior).
        figsize=(7.6, 4.2),
        dpi=100,
        facecolor=BG_COLOR,
    )
    axes = figure.subplots(2, 2)
    series = result.series
    table = result.frequency_table
    count = len(table)

    # Histograma
    axes[0, 0].hist(
        series,
        bins=count if result.grouped else min(15, max(3, int(series.nunique()))),
        color=COLORS["blue"],
        edgecolor=BG_COLOR,
        linewidth=0.8,
        alpha=0.9,
    )
    axes[0, 0].axvline(
        float(result.metrics["Media"]),
        color=COLORS["amber"],
        linestyle="--",
        linewidth=2,
        label="Media",
    )
    axes[0, 0].set_title("Histograma", loc="left", fontweight="bold", color=COLORS["navy"])
    axes[0, 0].set_xlabel(result.variable, color=COLORS["slate"])
    axes[0, 0].set_ylabel("Frecuencia", color=COLORS["slate"])
    
    # Arreglar la leyenda para modo oscuro
    legend = axes[0, 0].legend(frameon=False)
    for text in legend.get_texts():
        text.set_color(COLORS["slate"])

    # Barras de la distribución de frecuencias
    positions = np.arange(count)
    frequencies = table["Frecuencia absoluta"].to_numpy()
    axes[0, 1].bar(positions, frequencies, color=COLORS["cyan"], width=0.78)
    axes[0, 1].set_title("Gráfico de barras", loc="left", fontweight="bold", color=COLORS["navy"])
    axes[0, 1].set_xlabel("Clases", color=COLORS["slate"])
    axes[0, 1].set_ylabel("Frecuencia absoluta", color=COLORS["slate"])

    # Polígono
    marks = table["Marca de clase"].to_numpy(dtype=float)
    axes[1, 0].plot(
        marks,
        frequencies,
        color=COLORS["violet"],
        marker="o",
        markersize=5,
        linewidth=2.2,
    )
    axes[1, 0].fill_between(
        marks, frequencies, color=COLORS["violet"], alpha=0.15
    )
    axes[1, 0].set_title("Polígono de frecuencias", loc="left", fontweight="bold", color=COLORS["navy"])
    axes[1, 0].set_xlabel(result.variable, color=COLORS["slate"])
    axes[1, 0].set_ylabel("Frecuencia absoluta", color=COLORS["slate"])

    # Curva acumulada (ojiva)
    x_curve = table["Límite superior"].to_numpy(dtype=float)
    y_curve = table["Porcentaje acumulado"].to_numpy(dtype=float)
    axes[1, 1].plot(
        x_curve,
        y_curve,
        color=COLORS["amber"],
        marker="o",
        markersize=5,
        linewidth=2.4,
    )
    axes[1, 1].fill_between(x_curve, y_curve, color=COLORS["amber"], alpha=0.15)
    axes[1, 1].set_ylim(0, 105)
    axes[1, 1].set_title(
        "Curva de frecuencia acumulada", loc="left", fontweight="bold", color=COLORS["navy"]
    )
    axes[1, 1].set_xlabel(result.variable, color=COLORS["slate"])
    axes[1, 1].set_ylabel("Porcentaje acumulado", color=COLORS["slate"])

    if count > 8:
        tick_step = max(1, int(np.ceil(count / 8)))
        selected = positions[::tick_step]
    else:
        selected = positions
    labels = table["Clase"].astype(str).tolist()
    if result.grouped:
        display_labels = [f"C{index + 1}" for index in range(count)]
        axes[0, 1].set_xlabel("Clases (límites en tabla)", color=COLORS["slate"])
    else:
        display_labels = labels
    axes[0, 1].set_xticks(selected)
    axes[0, 1].set_xticklabels(
        [display_labels[index] for index in selected],
        rotation=0 if result.grouped else 35,
        ha="center" if result.grouped else "right",
        fontsize=8,
    )

    for axis in axes.flat:
        axis.set_facecolor(BG_COLOR)
        axis.grid(axis="y", color=COLORS["grid"], linewidth=0.8)
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines["bottom"].set_color(COLORS["grid"])
        axis.spines["left"].set_color(COLORS["grid"])
        axis.tick_params(colors=COLORS["slate"], labelsize=8)
        axis.title.set_color(COLORS["navy"])

    figure.suptitle(
        f"Distribución de {result.variable}",
        x=0.04,
        y=0.975,
        ha="left",
        fontsize=13,
        fontweight="bold",
        color=COLORS["ink"],
    )
    figure.subplots_adjust(
        left=0.075,
        right=0.985,
        bottom=0.11,
        top=0.86,
        wspace=0.26,
        hspace=0.70,
    )
    return figure


def create_boxplot_figure(result: AnalysisResult) -> Figure:
    """Crea un boxplot horizontal con límites del criterio RIC."""
    figure = Figure(
        figsize=(7.6, 3.6),
        dpi=100,
        facecolor=BG_COLOR,
    )
    axis = figure.subplots()
    axis.set_facecolor(BG_COLOR)
    orientation_argument = (
        {"orientation": "horizontal"}
        if "orientation" in inspect.signature(axis.boxplot).parameters
        else {"vert": False}
    )
    axis.boxplot(
        result.series,
        patch_artist=True,
        boxprops={"facecolor": COLORS["cyan"], "alpha": 0.65, "color": BG_COLOR},
        medianprops={"color": COLORS["ink"], "linewidth": 2},
        flierprops={
            "marker": "o",
            "markerfacecolor": COLORS["amber"],
            "markeredgecolor": BG_COLOR,
            "markersize": 5,
        },
        **orientation_argument,
    )
    axis.set_title(
        f"Diagrama de cajas: {result.variable}",
        loc="left",
        fontsize=13,
        fontweight="bold",
        color=COLORS["navy"],
    )
    axis.set_xlabel(result.variable, color=COLORS["slate"])
    axis.set_yticks([])
    axis.grid(axis="x", color=COLORS["grid"])
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color(COLORS["grid"])
    axis.tick_params(colors=COLORS["slate"])

    figure.subplots_adjust(left=0.06, right=0.985, bottom=0.18, top=0.84)
    return figure

"""Exportación del análisis de una variable a PDF."""

from __future__ import annotations

from pathlib import Path
import tempfile

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .interpretation import generate_interpretation
from .statistics_engine import AnalysisResult
from .visualizations import create_analysis_figure, create_boxplot_figure


NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
CYAN = colors.HexColor("#06B6D4")
SLATE = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F1F5F9")


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:,.4f}"
    return str(value)


def _save_figure_for_pdf(figure, path: Path) -> None:
    """Guarda una figura respetando el tema con el que fue creada."""
    figure.savefig(
        path,
        dpi=150,
        bbox_inches="tight",
        facecolor=figure.get_facecolor(),
    )


def _page(canvas, document) -> None:
    canvas.saveState()
    width, height = landscape(A4)
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 1.25 * cm, width, 1.25 * cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.4 * cm, height - 0.8 * cm, "STATLAB · REPORTE DE ANÁLISIS")
    canvas.setFillColor(SLATE)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        width - 1.4 * cm, 0.65 * cm, f"Página {document.page}"
    )
    canvas.restoreState()


def export_variable_report(
    path: str | Path,
    dataset_name: str,
    data: pd.DataFrame,
    result: AnalysisResult,
) -> Path:
    """Genera un PDF autocontenido con resultados, gráficos e interpretación."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodySmall",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            textColor=SLATE,
        )
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=landscape(A4),
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.2 * cm,
        title=f"Análisis estadístico de {result.variable}",
        author="StatLab",
    )
    story: list[object] = [
        Spacer(1, 0.25 * cm),
        Paragraph("Reporte de análisis estadístico", styles["ReportTitle"]),
        Paragraph(
            f"<b>Dataset:</b> {dataset_name} &nbsp;&nbsp; "
            f"<b>Variable:</b> {result.variable} &nbsp;&nbsp; "
            f"<b>Dimensiones:</b> {data.shape[0]:,} × {data.shape[1]}",
            styles["BodySmall"],
        ),
        Spacer(1, 0.35 * cm),
        Paragraph("Indicadores principales", styles["Section"]),
    ]

    selected_metrics = [
        "Datos válidos",
        "Media",
        "Mediana",
        "Moda",
        "Rango",
        "Desviación media",
        "Varianza poblacional",
        "Desviación estándar",
        "Coeficiente de variación",
        "Valores atípicos",
    ]
    metric_rows = [["Indicador", "Resultado"]]
    metric_rows.extend(
        [[key, _fmt(result.metrics[key])] for key in selected_metrics]
    )
    metrics_table = Table(metric_rows, colWidths=[7.5 * cm, 5.5 * cm], repeatRows=1)
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(metrics_table)

    with tempfile.TemporaryDirectory(prefix="statlab_") as temp:
        charts_path = Path(temp) / "charts.png"
        boxplot_path = Path(temp) / "boxplot.png"
        _save_figure_for_pdf(create_analysis_figure(result), charts_path)
        _save_figure_for_pdf(create_boxplot_figure(result), boxplot_path)
        story.extend(
            [
                PageBreak(),
                Paragraph("Representaciones gráficas", styles["Section"]),
                Image(str(charts_path), width=24.3 * cm, height=14.2 * cm),
                PageBreak(),
                Paragraph("Diagrama de cajas y valores atípicos", styles["Section"]),
                Image(str(boxplot_path), width=23.0 * cm, height=10.9 * cm),
                PageBreak(),
                Paragraph("Tabla de distribución de frecuencias", styles["Section"]),
            ]
        )

        columns = [
            "Clase",
            "Frecuencia absoluta",
            "Frecuencia relativa",
            "Frecuencia porcentual",
            "Frecuencia acumulada",
        ]
        frequency_rows = [
            [
                "Clase",
                "f",
                "fr",
                "%",
                "F acum.",
            ]
        ]
        for _, row in result.frequency_table[columns].iterrows():
            frequency_rows.append(
                [
                    str(row["Clase"]),
                    f"{int(row['Frecuencia absoluta'])}",
                    f"{row['Frecuencia relativa']:.4f}",
                    f"{row['Frecuencia porcentual']:.2f}",
                    f"{int(row['Frecuencia acumulada'])}",
                ]
            )
        frequency_table = Table(
            frequency_rows,
            colWidths=[9.5 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm],
            repeatRows=1,
        )
        frequency_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(frequency_table)
        story.extend(
            [
                PageBreak(),
                Paragraph("Análisis e interpretación", styles["Section"]),
            ]
        )
        for heading, body in generate_interpretation(result, data):
            story.append(
                Paragraph(
                    f"<font color='#2563EB'><b>{heading}</b></font>", styles["BodySmall"]
                )
            )
            story.append(Paragraph(body, styles["BodySmall"]))
            story.append(Spacer(1, 0.20 * cm))

        doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return output

"""Genera el informe técnico final a partir del dataset, capturas y configuración."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from PIL import Image as PILImage
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from analizador.statistics_engine import analyze_variable, variability_ranking


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config_informe.json"
DATA_PATH = ROOT / "data" / "SeoulBikeData.csv"
CAPTURE_DIR = ROOT / "docs" / "capturas"
OUTPUT_PATH = ROOT / "docs" / "Informe_Tecnico_StatLab.pdf"

NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
CYAN = colors.HexColor("#06B6D4")
VIOLET = colors.HexColor("#7C3AED")
AMBER = colors.HexColor("#D97706")
INK = colors.HexColor("#0F172A")
SLATE = colors.HexColor("#475569")
MUTED = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white


def load_report_config() -> dict:
    """Carga la portada y evita generar un informe con marcadores pendientes."""
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    required_text = (
        "institucion",
        "carrera",
        "asignatura",
        "titulo",
        "nombre_aplicacion",
        "docente",
        "ciudad",
        "fecha",
    )
    missing = [key for key in required_text if not str(config.get(key, "")).strip()]
    integrantes = [
        str(name).strip() for name in config.get("integrantes", []) if str(name).strip()
    ]
    if not integrantes:
        missing.append("integrantes")

    values = [str(config.get(key, "")) for key in required_text] + integrantes
    placeholders = [
        value
        for value in values
        if value.strip().upper().startswith(("NOMBRE ", "PENDIENTE", "COMPLETAR "))
    ]
    if missing or placeholders:
        details: list[str] = []
        if missing:
            details.append("campos vacíos: " + ", ".join(sorted(set(missing))))
        if placeholders:
            details.append("marcadores sin reemplazar: " + ", ".join(placeholders))
        raise ValueError(
            "Complete config_informe.json antes de generar el informe ("
            + "; ".join(details)
            + ")."
        )

    config["integrantes"] = integrantes
    return config


def validate_capture_files() -> None:
    """Comprueba que las cuatro capturas finales estén disponibles."""
    expected = (
        "01_resumen.png",
        "02_frecuencias.png",
        "03_graficos.png",
        "04_interpretacion.png",
    )
    missing = [name for name in expected if not (CAPTURE_DIR / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "Faltan capturas requeridas en docs/capturas: " + ", ".join(missing)
        )


def register_fonts() -> None:
    regular = Path(r"C:\Windows\Fonts\calibri.ttf")
    bold = Path(r"C:\Windows\Fonts\calibrib.ttf")
    italic = Path(r"C:\Windows\Fonts\calibrii.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Body", str(regular)))
        pdfmetrics.registerFont(TTFont("Body-Bold", str(bold)))
        pdfmetrics.registerFont(
            TTFont("Body-Italic", str(italic if italic.exists() else regular))
        )
    else:
        pdfmetrics.registerFontFamily(
            "Body",
            normal="Helvetica",
            bold="Helvetica-Bold",
            italic="Helvetica-Oblique",
        )


register_fonts()


class TechnicalReport(BaseDocTemplate):
    """Plantilla con tabla de contenido, encabezado y numeración."""

    def __init__(self, filename: str, title: str) -> None:
        super().__init__(
            filename,
            pagesize=A4,
            rightMargin=1.7 * cm,
            leftMargin=1.7 * cm,
            topMargin=1.8 * cm,
            bottomMargin=1.55 * cm,
            title=title,
            author="Equipo de proyecto - StatLab",
        )
        page_width, page_height = A4
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            page_width - self.leftMargin - self.rightMargin,
            page_height - self.topMargin - self.bottomMargin,
            id="content",
        )
        self.addPageTemplates(
            PageTemplate(id="report", frames=[frame], onPage=self._draw_page)
        )

    def _draw_page(self, canvas, _doc) -> None:
        page_width, page_height = A4
        page = canvas.getPageNumber()
        canvas.saveState()
        if page == 1:
            canvas.setFillColor(NAVY)
            canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)
            canvas.setFillColor(BLUE)
            canvas.rect(0, 0, 0.55 * cm, page_height, stroke=0, fill=1)
            canvas.setFillColor(CYAN)
            canvas.circle(page_width - 1.9 * cm, page_height - 1.8 * cm, 0.45 * cm, 0, 1)
        else:
            canvas.setStrokeColor(BORDER)
            canvas.line(
                self.leftMargin,
                page_height - 1.08 * cm,
                page_width - self.rightMargin,
                page_height - 1.08 * cm,
            )
            canvas.setFont("Body-Bold", 8)
            canvas.setFillColor(NAVY)
            canvas.drawString(
                self.leftMargin, page_height - 0.78 * cm, "STATLAB"
            )
            canvas.setFont("Body", 8)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(
                page_width - self.rightMargin,
                page_height - 0.78 * cm,
                "Informe técnico",
            )
            canvas.line(
                self.leftMargin,
                1.05 * cm,
                page_width - self.rightMargin,
                1.05 * cm,
            )
            canvas.drawString(self.leftMargin, 0.68 * cm, "Probabilidad y Procesos Estocásticos")
            canvas.drawRightString(
                page_width - self.rightMargin, 0.68 * cm, f"Página {page}"
            )
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name in {"H1", "H2"}:
                level = 0 if style_name == "H1" else 1
                text = flowable.getPlainText()
                key = f"heading-{level}-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "CoverKicker",
            fontName="Body-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#BAE6FD"),
            spaceAfter=12,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            fontName="Body-Bold",
            fontSize=27,
            leading=31,
            textColor=WHITE,
            spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            fontName="Body",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#DBEAFE"),
            spaceAfter=20,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            fontName="Body",
            fontSize=10,
            leading=14,
            textColor=WHITE,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Body-Bold",
            fontSize=19,
            leading=23,
            textColor=NAVY,
            spaceBefore=4,
            spaceAfter=12,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Body-Bold",
            fontSize=13,
            leading=16,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Body",
            fontSize=9.5,
            leading=13.6,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "body_small": ParagraphStyle(
            "BodySmall",
            parent=base["BodyText"],
            fontName="Body",
            fontSize=8.4,
            leading=11.4,
            textColor=SLATE,
            alignment=TA_LEFT,
        ),
        "caption": ParagraphStyle(
            "Caption",
            fontName="Body-Italic",
            fontSize=8,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "callout": ParagraphStyle(
            "Callout",
            fontName="Body",
            fontSize=9,
            leading=13,
            textColor=NAVY,
            leftIndent=4,
            rightIndent=4,
        ),
        "toc_title": ParagraphStyle(
            "TocTitle",
            fontName="Body-Bold",
            fontSize=20,
            leading=24,
            textColor=NAVY,
            spaceAfter=18,
        ),
        "bibliography": ParagraphStyle(
            "Bibliography",
            fontName="Body",
            fontSize=8.7,
            leading=12.2,
            textColor=INK,
            leftIndent=0.65 * cm,
            firstLineIndent=-0.65 * cm,
            spaceAfter=8,
        ),
    }


STYLES = make_styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def callout(title: str, text: str, color=BLUE) -> Table:
    content = Paragraph(
        f"<font color='{color.hexval()}'><b>{title}</b></font><br/>{text}",
        STYLES["callout"],
    )
    table = Table([[content]], colWidths=[16.6 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.8, color),
                ("LINEBEFORE", (0, 0), (0, -1), 4, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def styled_table(
    rows: list[list[object]],
    widths: list[float],
    alignments: list[str] | None = None,
    font_size: float = 8.3,
) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Body-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Body"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2.8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if alignments:
        for column, alignment in enumerate(alignments):
            commands.append(("ALIGN", (column, 1), (column, -1), alignment))
    table.setStyle(TableStyle(commands))
    return table


def architecture_diagram() -> Drawing:
    drawing = Drawing(475, 285)
    drawing.add(
        String(
            10,
            270,
            "Flujo modular de StatLab",
            fontName="Body-Bold",
            fontSize=13,
            fillColor=NAVY,
        )
    )
    boxes = [
        (135, 215, 205, 38, NAVY, "Interfaz gráfica - ui.py"),
        (15, 140, 135, 44, BLUE, "Carga y perfilado\ndata_loader.py"),
        (170, 140, 135, 44, VIOLET, "Cálculos estadísticos\nstatistics_engine.py"),
        (325, 140, 135, 44, CYAN, "Gráficos\nvisualizations.py"),
        (80, 58, 145, 44, AMBER, "Interpretación automática\ninterpretation.py"),
        (255, 58, 145, 44, colors.HexColor("#16A34A"), "Exportación PDF\nreporting.py"),
    ]
    for x, y, width, height, color, label in boxes:
        drawing.add(Rect(x, y, width, height, rx=7, ry=7, fillColor=color, strokeColor=color))
        lines = label.split("\n")
        for index, line in enumerate(lines):
            drawing.add(
                String(
                    x + width / 2,
                    y + height / 2 + 6 - index * 13,
                    line,
                    textAnchor="middle",
                    fontName="Body-Bold" if index == 0 else "Body",
                    fontSize=8.5,
                    fillColor=WHITE,
                )
            )
    for start, end in [
        ((237, 215), (82, 184)),
        ((237, 215), (237, 184)),
        ((237, 215), (392, 184)),
        ((237, 140), (152, 102)),
        ((237, 140), (327, 102)),
        ((82, 140), (152, 102)),
        ((392, 140), (327, 102)),
    ]:
        drawing.add(
            Line(start[0], start[1], end[0], end[1], strokeColor=BORDER, strokeWidth=1.4)
        )
    drawing.add(
        String(
            237,
            25,
            "Entrada: CSV/XLSX   |   Salida: métricas, tablas, gráficos, interpretación y PDF",
            textAnchor="middle",
            fontName="Body",
            fontSize=8.5,
            fillColor=MUTED,
        )
    )
    return drawing


def capture(path: Path, caption: str) -> KeepTogether:
    max_width = 16.9 * cm
    max_height = 10.7 * cm
    with PILImage.open(path) as source:
        width_px, height_px = source.size
    scale = min(max_width / width_px, max_height / height_px)
    screenshot = Image(
        str(path),
        width=width_px * scale,
        height=height_px * scale,
    )
    screenshot.hAlign = "CENTER"
    return KeepTogether(
        [
            screenshot,
            p(caption, "caption"),
        ]
    )


def build_report() -> Path:
    config = load_report_config()
    validate_capture_files()
    data = pd.read_csv(DATA_PATH)
    result = analyze_variable(data, "Rented Bike Count")
    ranking = variability_ranking(data)
    seasonal = (
        data.groupby("Seasons")["Rented Bike Count"]
        .agg(["count", "mean", "median", "std"])
        .round(2)
    )
    correlations = (
        data.select_dtypes(include="number")
        .corr()["Rented Bike Count"]
        .drop("Rented Bike Count")
        .sort_values(ascending=False)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = TechnicalReport(str(OUTPUT_PATH), config["titulo"])
    story: list[object] = []

    # Portada
    story.extend(
        [
            Spacer(1, 3.7 * cm),
            p(config["institucion"].upper(), "cover_kicker"),
            p(config["titulo"], "cover_title"),
            p(
                f"{config['nombre_aplicacion']} - Aplicación de escritorio reutilizable",
                "cover_subtitle",
            ),
            Table(
                [
                    [
                        p("<b>Asignatura</b><br/>" + config["asignatura"], "cover_meta"),
                        p("<b>Carrera</b><br/>" + config["carrera"], "cover_meta"),
                    ],
                    [
                        p(
                            "<b>Integrantes</b><br/>"
                            + "<br/>".join(config["integrantes"]),
                            "cover_meta",
                        ),
                        p("<b>Docente</b><br/>" + config["docente"], "cover_meta"),
                    ],
                ],
                colWidths=[8.1 * cm, 8.1 * cm],
                rowHeights=[1.7 * cm, 2.3 * cm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E3A8A")),
                        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#60A5FA")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#3B82F6")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ]
                ),
            ),
            Spacer(1, 2.2 * cm),
            p(f"{config['ciudad']} - {config['fecha']}", "cover_meta"),
            PageBreak(),
        ]
    )

    # Índice
    story.append(Paragraph("Índice general", STYLES["toc_title"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            name="TOC1",
            fontName="Body-Bold",
            fontSize=10,
            leading=16,
            leftIndent=0,
            firstLineIndent=0,
            textColor=NAVY,
        ),
        ParagraphStyle(
            name="TOC2",
            fontName="Body",
            fontSize=9,
            leading=14,
            leftIndent=14,
            firstLineIndent=0,
            textColor=SLATE,
        ),
    ]
    story.extend([toc, PageBreak()])

    story.extend(
        [
            p("1. Introducción", "h1"),
            p(
                "El análisis estadístico descriptivo transforma registros tabulares en "
                "información comprensible mediante medidas, distribuciones y gráficos. "
                "En proyectos de software, automatizar este proceso reduce cálculos "
                "repetitivos, mejora la trazabilidad y permite aplicar el mismo procedimiento "
                "a distintos conjuntos de datos.",
            ),
            p(
                "Como respuesta al proyecto integrador de Probabilidad y Procesos "
                "Estocásticos, se desarrolló <b>StatLab</b>, una aplicación de escritorio "
                "en Python capaz de importar archivos CSV o Excel, identificar sus variables "
                "numéricas y generar un análisis descriptivo completo sin modificar el código "
                "fuente. El sistema separa la carga, los cálculos, los gráficos, la "
                "interpretación y la exportación en módulos independientes.",
            ),
            p("1.1 Problema abordado", "h2"),
            p(
                "Calcular manualmente tablas de frecuencia y medidas para cada variable "
                "consume tiempo y aumenta el riesgo de errores de transcripción. Además, "
                "los resultados numéricos aislados no siempre explican la forma, dispersión "
                "o presencia de valores atípicos. StatLab integra cálculo, visualización e "
                "interpretación en un flujo único y verificable.",
            ),
            callout(
                "Alcance",
                "La aplicación realiza análisis descriptivo. No pretende demostrar causalidad "
                "ni sustituir el criterio del analista sobre la calidad y procedencia de los datos.",
            ),
            Spacer(1, 0.3 * cm),
            p("2. Objetivos", "h1"),
            p("2.1 Objetivo general", "h2"),
            p(
                "Diseñar e implementar una aplicación de escritorio reutilizable en Python "
                "que automatice el análisis estadístico descriptivo de conjuntos de datos "
                "tabulares y comunique los resultados mediante tablas, gráficos e "
                "interpretaciones contextualizadas.",
            ),
            p("2.2 Objetivos específicos", "h2"),
        ]
    )
    objectives = [
        "Importar y validar archivos CSV y Excel (.xlsx).",
        "Detectar automáticamente las variables numéricas disponibles.",
        "Calcular distribuciones de frecuencia y medidas de tendencia central y dispersión.",
        "Generar representaciones gráficas con títulos, ejes y escalas legibles.",
        "Detectar atípicos e interpretar el comportamiento de la variable seleccionada.",
        "Organizar el código en módulos reutilizables, documentados y probados.",
        "Permitir la exportación de resultados a CSV y PDF.",
    ]
    story.extend([p("• " + objective) for objective in objectives])
    story.append(PageBreak())

    story.extend(
        [
            p("3. Dataset utilizado", "h1"),
            p(
                "Para demostrar el sistema se utilizó <b>Seoul Bike Sharing Demand</b>, "
                "publicado por UCI Machine Learning Repository. El archivo contiene el "
                "número de bicicletas alquiladas por hora en el sistema público de Seúl y "
                "variables meteorológicas relacionadas. UCI informa 8.760 instancias, "
                "variables enteras y reales, y ausencia de valores faltantes. El recurso "
                "se distribuye con licencia CC BY 4.0 y DOI 10.24432/C5F62R.",
            ),
            styled_table(
                [
                    ["Propiedad", "Valor"],
                    ["Registros", "8.760"],
                    ["Columnas del archivo", "14"],
                    ["Variables numéricas", "10"],
                    ["Variables no numéricas", "4"],
                    ["Periodo", "Diciembre de 2017 a noviembre de 2018"],
                    ["Valores faltantes", "0"],
                    ["Fuente", "UCI Machine Learning Repository"],
                    ["Licencia", "Creative Commons Attribution 4.0"],
                ],
                [5.2 * cm, 11.2 * cm],
            ),
            p("3.1 Variables principales", "h2"),
            styled_table(
                [
                    ["Variable", "Tipo", "Descripción"],
                    ["Rented Bike Count", "Entera", "Bicicletas alquiladas por hora."],
                    ["Hour", "Entera", "Hora del día, de 0 a 23."],
                    ["Temperature_C", "Continua", "Temperatura del aire en grados Celsius."],
                    ["Humidity_pct", "Entera", "Humedad relativa en porcentaje."],
                    ["Wind speed_m_s", "Continua", "Velocidad del viento en m/s."],
                    ["Visibility_10m", "Entera", "Visibilidad medida en unidades de 10 m."],
                    ["Solar Radiation_MJ_m2", "Continua", "Radiación solar en MJ/m2."],
                    ["Rainfall_mm / Snowfall_cm", "Continua", "Precipitación de lluvia y nieve."],
                    ["Seasons / Holiday", "Categórica", "Estación y condición de feriado."],
                    ["Functioning Day", "Categórica", "Indica si el sistema operó."],
                ],
                [4.4 * cm, 2.2 * cm, 9.8 * cm],
                font_size=7.9,
            ),
            callout(
                "Consideración de entrega",
                "El dataset debe ser aprobado por el docente para confirmar que no haya sido "
                "registrado por otro grupo. Si se cambia, StatLab lo analizará sin cambios de código.",
                color=AMBER,
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("4. Arquitectura de la aplicación", "h1"),
            p(
                "La solución sigue una arquitectura modular. La interfaz coordina las "
                "acciones del usuario, mientras que cada responsabilidad estadística permanece "
                "en un archivo independiente. Esta separación facilita pruebas, mantenimiento "
                "y reutilización.",
            ),
            architecture_diagram(),
            p("4.1 Responsabilidades de los módulos", "h2"),
            styled_table(
                [
                    ["Módulo", "Responsabilidad"],
                    ["data_loader.py", "Carga CSV/XLSX, codificaciones, validación y perfil general."],
                    ["statistics_engine.py", "Frecuencias, medidas, cuartiles, atípicos y ranking de CV."],
                    ["visualizations.py", "Histograma, barras, polígono, curva acumulada y boxplot."],
                    ["interpretation.py", "Explicaciones automáticas prudentes y comparación de variables."],
                    ["reporting.py", "Exportación del análisis seleccionado a PDF."],
                    ["ui.py", "Interfaz, navegación, selección de variable y coordinación del flujo."],
                ],
                [4.2 * cm, 12.2 * cm],
                font_size=8,
            ),
            p("4.2 Flujo de procesamiento", "h2"),
            p(
                "El usuario selecciona un archivo; el cargador valida formato y contenido; "
                "la interfaz obtiene el perfil y lista las columnas numéricas; el motor limpia "
                "temporalmente nulos o infinitos de la variable seleccionada; luego calcula "
                "métricas y frecuencias. Finalmente se actualizan tablas, gráficos, texto "
                "interpretativo y opciones de exportación.",
            ),
            PageBreak(),
            p("5. Metodología estadística", "h1"),
            p(
                "Los cálculos se realizan sobre los valores numéricos válidos de la variable. "
                "No se modifican los registros originales. La varianza principal se presenta "
                "como poblacional porque se describe la totalidad del archivo cargado; también "
                "se ofrece la versión muestral para otros contextos.",
            ),
            styled_table(
                [
                    ["Indicador", "Expresión aplicada", "Interpretación"],
                    ["Media", "suma(xi) / n", "Centro aritmético."],
                    ["Mediana", "Percentil 50", "Centro resistente a extremos."],
                    ["Moda", "Valor con mayor frecuencia", "Valor más repetido."],
                    ["Rango", "máximo - mínimo", "Amplitud total."],
                    ["Desviación media", "promedio(|xi - media|)", "Distancia absoluta media."],
                    ["Varianza poblacional", "suma((xi - media)^2) / n", "Dispersión cuadrática."],
                    ["Desviación estándar", "raíz(varianza)", "Dispersión en unidades originales."],
                    ["CV", "desv. estándar / |media| x 100", "Variabilidad relativa."],
                    ["Atípicos", "< Q1 - 1,5 RIC o > Q3 + 1,5 RIC", "Observaciones alejadas."],
                ],
                [3.4 * cm, 5.7 * cm, 7.3 * cm],
                font_size=7.8,
            ),
            p("5.1 Distribución de frecuencias", "h2"),
            p(
                "Para variables con hasta 15 valores distintos, cada valor constituye una "
                "clase. Para variables continuas se aplica la regla de Sturges "
                "(k = 1 + 3,322 log10(n)), con un límite práctico de 5 a 20 intervalos para "
                "mantener la legibilidad. Se calculan frecuencia absoluta, relativa, "
                "porcentual y acumulada.",
            ),
            p("5.2 Criterios de interpretación", "h2"),
            p(
                "El coeficiente de variación se clasifica de forma orientativa como bajo "
                "(menor a 15 %), moderado (15 % a menos de 30 %) o alto (30 % o más). "
                "La asimetría se interpreta junto con la comparación media-mediana y los "
                "gráficos. Estas reglas sirven como apoyo descriptivo, no como decisiones "
                "automáticas definitivas.",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("6. Funcionalidades implementadas", "h1"),
            styled_table(
                [
                    ["Funcionalidad", "Implementación y validación"],
                    ["Carga y visualización", "CSV/XLSX, detección de codificación, tabla de hasta 500 filas."],
                    ["Perfil del dataset", "Filas, columnas, tipos, nulos, duplicados y memoria."],
                    ["Frecuencias", "Tabla dinámica por valor o por intervalos de Sturges."],
                    ["Tendencia central", "Media, mediana y moda con explicación automática."],
                    ["Dispersión", "Rango, desviación media, varianzas, desviaciones y CV."],
                    ["Gráficos", "Histograma, barras, polígono, curva acumulada y boxplot."],
                    ["Atípicos", "Detección mediante 1,5 RIC y reporte de límites."],
                    ["Interpretación", "Centro, dispersión, forma, atípicos y comparación de CV."],
                    ["Exportación", "Frecuencias a CSV y reporte individual a PDF."],
                    ["Manejo de errores", "Formato, archivo vacío, columnas duplicadas y falta de numéricas."],
                ],
                [4.2 * cm, 12.2 * cm],
                font_size=8,
            ),
            p("6.1 Diseño y usabilidad", "h2"),
            p(
                "La interfaz agrupa el flujo en cinco pestañas: Resumen, Datos, Frecuencias, "
                "Gráficos e Interpretación. La fuente de datos y la selección de variable "
                "permanecen visibles en la barra lateral, de modo que todas las vistas se "
                "actualizan de forma coherente. La paleta oscura, los acentos azules, las "
                "tarjetas de indicadores y las tablas con encabezados contrastados mantienen "
                "una jerarquía visual uniforme.",
            ),
            callout(
                "Funcionalidad adicional",
                "Además de los mínimos solicitados, se incluyen boxplot, cuartiles, rango "
                "intercuartílico, asimetría, curtosis, coeficiente de variación, ranking "
                "comparativo y exportación de reportes.",
                color=VIOLET,
            ),
            PageBreak(),
            p("7. Capturas de pantalla", "h1"),
            p(
                "Las siguientes capturas muestran la ejecución con el dataset de demostración "
                "y la variable Rented Bike Count.",
            ),
            capture(
                CAPTURE_DIR / "01_resumen.png",
                "Figura 1. Resumen del dataset y métricas de la variable seleccionada.",
            ),
            PageBreak(),
            capture(
                CAPTURE_DIR / "02_frecuencias.png",
                "Figura 2. Tabla de frecuencias agrupada automáticamente mediante Sturges.",
            ),
            PageBreak(),
            capture(
                CAPTURE_DIR / "03_graficos.png",
                "Figura 3. Histograma, barras, polígono y curva de frecuencia acumulada.",
            ),
            PageBreak(),
            capture(
                CAPTURE_DIR / "04_interpretacion.png",
                "Figura 4. Interpretación automática del comportamiento estadístico.",
            ),
            PageBreak(),
        ]
    )

    m = result.metrics
    results_rows = [
        ["Indicador", "Resultado"],
        ["Datos válidos", f"{int(m['Datos válidos']):,}"],
        ["Mínimo / máximo", f"{m['Mínimo']:.2f} / {m['Máximo']:.2f}"],
        ["Media", f"{m['Media']:.2f}"],
        ["Mediana", f"{m['Mediana']:.2f}"],
        ["Moda", str(m["Moda"])],
        ["Rango", f"{m['Rango']:.2f}"],
        ["Desviación media", f"{m['Desviación media']:.2f}"],
        ["Varianza poblacional", f"{m['Varianza poblacional']:.2f}"],
        ["Desviación estándar", f"{m['Desviación estándar']:.2f}"],
        ["Coeficiente de variación", f"{m['Coeficiente de variación']:.2f} %"],
        ["Asimetría", f"{m['Asimetría']:.2f}"],
        ["Atípicos por 1,5 RIC", f"{int(m['Valores atípicos'])}"],
    ]
    story.extend(
        [
            p("8. Resultados e interpretación", "h1"),
            p(
                "La variable principal representa la demanda horaria de bicicletas. Los "
                "resultados calculados por StatLab son los siguientes:",
            ),
            styled_table(results_rows, [8.4 * cm, 8.0 * cm], alignments=["LEFT", "RIGHT"]),
            p("8.1 Tendencia central y forma", "h2"),
            p(
                f"La media es {m['Media']:.2f} bicicletas por hora y la mediana "
                f"{m['Mediana']:.2f}. Como la media supera ampliamente a la mediana y la "
                f"asimetría es {m['Asimetría']:.2f}, la distribución presenta una cola hacia "
                "la derecha. El histograma confirma que la mayor concentración se encuentra "
                "en los intervalos bajos, mientras una proporción menor alcanza valores altos.",
            ),
            p(
                "La moda igual a 0 debe interpretarse con el contexto operativo. El dataset "
                "incluye 295 horas marcadas como días no funcionales y en todas ellas el "
                "conteo es cero; por ello, el cero no representa necesariamente ausencia "
                "espontánea de demanda.",
            ),
            p("8.2 Dispersión y atípicos", "h2"),
            p(
                f"La desviación estándar es {m['Desviación estándar']:.2f} y el coeficiente "
                f"de variación {m['Coeficiente de variación']:.2f} %, por lo que la demanda "
                "es heterogénea. Se detectaron "
                f"{int(m['Valores atípicos'])} valores atípicos mediante el criterio de "
                "1,5 RIC. No deben eliminarse automáticamente: pueden corresponder a horas "
                "reales de demanda excepcional.",
            ),
            callout(
                "Conclusión del indicador principal",
                "El promedio por sí solo no resume adecuadamente la demanda. La mediana, la "
                "dispersión y la forma de la distribución deben presentarse en conjunto.",
            ),
            PageBreak(),
            p("8.3 Comparaciones contextuales", "h2"),
        ]
    )

    seasonal_rows = [["Estación", "n", "Media", "Mediana", "Desv. estándar"]]
    for season, row in seasonal.iterrows():
        seasonal_rows.append(
            [
                str(season),
                f"{int(row['count']):,}",
                f"{row['mean']:.2f}",
                f"{row['median']:.2f}",
                f"{row['std']:.2f}",
            ]
        )
    story.extend(
        [
            p(
                "La media estacional más alta corresponde a verano y la más baja a invierno. "
                "Esta comparación es descriptiva; no separa el efecto de temperatura, horas "
                "de luz, feriados u otras variables.",
            ),
            styled_table(
                seasonal_rows,
                [4.2 * cm, 2.2 * cm, 3.3 * cm, 3.3 * cm, 3.6 * cm],
                alignments=["LEFT", "RIGHT", "RIGHT", "RIGHT", "RIGHT"],
            ),
            Spacer(1, 0.25 * cm),
            p("Correlaciones lineales con Rented Bike Count", "h2"),
        ]
    )
    correlation_rows = [["Variable", "Correlación de Pearson"]]
    for variable, value in correlations.items():
        correlation_rows.append([str(variable), f"{value:.3f}"])
    story.append(
        styled_table(
            correlation_rows,
            [10.5 * cm, 5.9 * cm],
            alignments=["LEFT", "RIGHT"],
            font_size=8,
        )
    )
    story.extend(
        [
            p(
                "La temperatura muestra la asociación positiva más alta (r = "
                f"{correlations['Temperature_C']:.3f}); la humedad presenta una asociación "
                f"negativa débil (r = {correlations['Humidity_pct']:.3f}). Correlación no "
                "implica causalidad y las relaciones podrían no ser lineales.",
            ),
            p("8.4 Variabilidad entre variables", "h2"),
        ]
    )
    ranking_rows = [["Variable", "Media", "Desv. estándar", "CV (%)"]]
    for _, row in ranking.head(6).iterrows():
        ranking_rows.append(
            [
                str(row["Variable"]),
                f"{row['Media']:.3f}",
                f"{row['Desviación estándar']:.3f}",
                f"{row['CV (%)']:.2f}",
            ]
        )
    story.extend(
        [
            styled_table(
                ranking_rows,
                [6.4 * cm, 3.3 * cm, 3.5 * cm, 3.2 * cm],
                alignments=["LEFT", "RIGHT", "RIGHT", "RIGHT"],
                font_size=7.8,
            ),
            p(
                "Lluvia y nieve tienen los CV más altos porque sus medias son muy pequeñas "
                "y contienen muchos ceros. Esto demuestra por qué el CV debe interpretarse "
                "con cautela cuando el promedio se aproxima a cero.",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            p("9. Validación y pruebas", "h1"),
            p(
                "El motor se verificó con pruebas unitarias y con el dataset real. Las pruebas "
                "comparan media, mediana, moda, varianza, desviación estándar y desviación "
                "media contra resultados de referencia; también verifican que las frecuencias "
                "sumen n, que las relativas sumen 1 y que las porcentuales sumen 100.",
            ),
            styled_table(
                [
                    ["Prueba", "Criterio", "Resultado"],
                    ["Carga CSV", "8.760 filas y 14 columnas", "Aprobada"],
                    ["Requisitos mínimos", ">=300 filas, >=5 columnas, >=3 numéricas", "Aprobada"],
                    ["Tendencia central", "Coincide con pandas", "Aprobada"],
                    ["Dispersión", "Coincide con fórmulas poblacionales", "Aprobada"],
                    ["Frecuencias", "Suma f=n, suma fr=1, suma %=100", "Aprobada"],
                    ["Atípicos", "Criterio Q1/Q3 y 1,5 RIC", "Aprobada"],
                    ["Variable constante", "Rango y desviación iguales a 0", "Aprobada"],
                    ["Generación PDF", "Archivo legible con resultados y gráficos", "Aprobada"],
                ],
                [4.4 * cm, 8.3 * cm, 3.7 * cm],
                font_size=8,
            ),
            p("9.1 Manejo de errores", "h2"),
            p(
                "La aplicación informa si el archivo no existe, está vacío, tiene un formato "
                "no admitido, contiene nombres de columnas duplicados o no posee variables "
                "numéricas. Para CSV prueba codificaciones UTF-8, CP1252 y Latin-1 y detecta "
                "el separador. Los valores no numéricos no se fuerzan salvo que al menos el "
                "95 % de una columna de texto sea convertible.",
            ),
            p("9.2 Limitaciones", "h2"),
            p(
                "Las interpretaciones automáticas usan reglas generales y no conocen todas "
                "las particularidades del dominio. Los umbrales de variabilidad son "
                "orientativos. La vista previa limita la tabla a 500 registros para conservar "
                "fluidez, aunque los cálculos utilizan todo el dataset.",
            ),
            PageBreak(),
            p("10. Conclusiones", "h1"),
            p(
                "StatLab cumple el objetivo de analizar datasets tabulares sin codificar "
                "nombres ni valores específicos. La arquitectura modular permite reemplazar "
                "el dataset de demostración y conservar el mismo flujo de trabajo.",
            ),
            p(
                "El sistema integra las medidas solicitadas, las cuatro representaciones "
                "gráficas obligatorias y una interpretación que relaciona centro, dispersión, "
                "asimetría y atípicos. Las funciones adicionales - boxplot, CV, cuartiles, "
                "curtosis, ranking y exportación - enriquecen la experiencia del usuario.",
            ),
            p(
                "En el caso estudiado, la demanda de bicicletas es asimétrica y altamente "
                "variable. La media es mayor que la mediana, existen 158 atípicos y el verano "
                "presenta el promedio estacional más alto. Los resultados ilustran que una "
                "decisión informada requiere combinar métricas y gráficos.",
            ),
            p("10.1 Recomendaciones", "h2"),
        ]
    )
    recommendations = [
        "Conservar junto con la entrega la referencia y la aprobación del dataset.",
        "Realizar la demostración en el mismo equipo que se usará para la sustentación.",
        "No eliminar atípicos sin revisar su significado operativo.",
        "Como trabajo futuro, incorporar filtros por categoría y análisis bivariado interactivo.",
    ]
    story.extend([p("• " + item) for item in recommendations])
    story.extend(
        [
            PageBreak(),
            p("11. Bibliografía", "h1"),
            p(
                "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. "
                "<i>Computing in Science & Engineering, 9</i>(3), 90-95. "
                "https://doi.org/10.1109/MCSE.2007.55",
                "bibliography",
            ),
            p(
                "McKinney, W. (2010). Data structures for statistical computing in Python. "
                "En <i>Proceedings of the 9th Python in Science Conference</i> (pp. 56-61). "
                "https://doi.org/10.25080/Majora-92bf1922-00a",
                "bibliography",
            ),
            p(
                "Python Software Foundation. (2026). <i>Python 3 documentation</i>. "
                "https://docs.python.org/3/",
                "bibliography",
            ),
            p(
                "Seoul Bike Sharing Demand [Dataset]. (2020). "
                "<i>UCI Machine Learning Repository</i>. "
                "https://doi.org/10.24432/C5F62R",
                "bibliography",
            ),
            p(
                "The pandas development team. (2026). <i>pandas documentation</i>. "
                "https://pandas.pydata.org/docs/",
                "bibliography",
            ),
            p(
                "Tukey, J. W. (1977). <i>Exploratory data analysis</i>. "
                "Addison-Wesley.",
                "bibliography",
            ),
            Spacer(1, 0.6 * cm),
            callout(
                "Declaración de reproducibilidad",
                "El código fuente, el dataset, las pruebas y el generador de este informe "
                "se entregan juntos. Los indicadores del capítulo 8 se recalculan desde el "
                "CSV cada vez que se ejecuta generar_informe.py.",
                color=colors.HexColor("#16A34A"),
            ),
        ]
    )

    doc.multiBuild(story)
    return OUTPUT_PATH


if __name__ == "__main__":
    try:
        path = build_report()
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"No se pudo generar el informe: {exc}") from exc
    print(f"Informe generado: {path}")

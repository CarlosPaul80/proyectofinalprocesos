"""Motor de estadística descriptiva y distribuciones de frecuencia."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AnalysisResult:
    variable: str
    series: pd.Series
    frequency_table: pd.DataFrame
    metrics: dict[str, float | int | str]
    outliers: pd.Series
    lower_fence: float
    upper_fence: float
    grouped: bool


def _clean_numeric(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    clean = clean[np.isfinite(clean)].astype(float)
    if clean.empty:
        raise ValueError("La variable no contiene valores numéricos válidos.")
    return clean


def _frequency_table(series: pd.Series) -> tuple[pd.DataFrame, bool]:
    n = len(series)
    unique_count = int(series.nunique())
    grouped = unique_count > 15

    if not grouped:
        counts = series.value_counts().sort_index()
        table = pd.DataFrame(
            {
                "Clase": [f"{value:g}" for value in counts.index],
                "Límite inferior": counts.index.astype(float),
                "Límite superior": counts.index.astype(float),
                "Marca de clase": counts.index.astype(float),
                "Frecuencia absoluta": counts.values.astype(int),
            }
        )
    elif float(series.min()) == float(series.max()):
        value = float(series.iloc[0])
        table = pd.DataFrame(
            {
                "Clase": [f"{value:g}"],
                "Límite inferior": [value],
                "Límite superior": [value],
                "Marca de clase": [value],
                "Frecuencia absoluta": [n],
            }
        )
        grouped = False
    else:
        # Regla de Sturges, limitada para conservar legibilidad visual.
        bin_count = min(20, max(5, math.ceil(1 + 3.322 * math.log10(n))))
        bin_count = min(bin_count, unique_count)
        edges = np.linspace(float(series.min()), float(series.max()), bin_count + 1)
        counts, edges = np.histogram(series.to_numpy(), bins=edges)
        lower = edges[:-1]
        upper = edges[1:]
        marks = (lower + upper) / 2
        labels = [
            f"[{lo:.2f}, {hi:.2f}{']' if i == len(lower) - 1 else ')'}"
            for i, (lo, hi) in enumerate(zip(lower, upper))
        ]
        table = pd.DataFrame(
            {
                "Clase": labels,
                "Límite inferior": lower,
                "Límite superior": upper,
                "Marca de clase": marks,
                "Frecuencia absoluta": counts.astype(int),
            }
        )

    table["Frecuencia relativa"] = table["Frecuencia absoluta"] / n
    table["Frecuencia porcentual"] = table["Frecuencia relativa"] * 100
    table["Frecuencia acumulada"] = table["Frecuencia absoluta"].cumsum()
    table["Porcentaje acumulado"] = table["Frecuencia porcentual"].cumsum()
    return table, grouped


def analyze_variable(data: pd.DataFrame, variable: str) -> AnalysisResult:
    """Calcula métricas, tabla de frecuencias y atípicos para una variable."""
    if variable not in data.columns:
        raise KeyError(f"No existe la variable '{variable}'.")

    original = data[variable]
    series = _clean_numeric(original)
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    outliers = series[(series < lower_fence) | (series > upper_fence)]

    mode_values = series.mode()
    if mode_values.empty:
        mode_text = "Sin moda"
    else:
        displayed = ", ".join(f"{value:g}" for value in mode_values.iloc[:5])
        mode_text = displayed + ("…" if len(mode_values) > 5 else "")

    mean = float(series.mean())
    std_population = float(series.std(ddof=0))
    coefficient_variation = (
        abs(std_population / mean) * 100 if not math.isclose(mean, 0.0) else math.nan
    )
    metrics: dict[str, float | int | str] = {
        "Registros totales": int(len(original)),
        "Datos válidos": int(len(series)),
        "Datos faltantes": int(original.isna().sum()),
        "Mínimo": float(series.min()),
        "Máximo": float(series.max()),
        "Rango": float(series.max() - series.min()),
        "Media": mean,
        "Mediana": float(series.median()),
        "Moda": mode_text,
        "Desviación media": float(np.mean(np.abs(series - mean))),
        "Varianza poblacional": float(series.var(ddof=0)),
        "Varianza muestral": float(series.var(ddof=1)) if len(series) > 1 else math.nan,
        "Desviación estándar": std_population,
        "Desviación estándar muestral": (
            float(series.std(ddof=1)) if len(series) > 1 else math.nan
        ),
        "Coeficiente de variación": coefficient_variation,
        "Primer cuartil": q1,
        "Tercer cuartil": q3,
        "Rango intercuartílico": iqr,
        "Asimetría": float(series.skew()) if len(series) > 2 else math.nan,
        "Curtosis": float(series.kurt()) if len(series) > 3 else math.nan,
        "Valores atípicos": int(len(outliers)),
    }
    frequency_table, grouped = _frequency_table(series)
    return AnalysisResult(
        variable=variable,
        series=series,
        frequency_table=frequency_table,
        metrics=metrics,
        outliers=outliers,
        lower_fence=lower_fence,
        upper_fence=upper_fence,
        grouped=grouped,
    )


def variability_ranking(data: pd.DataFrame) -> pd.DataFrame:
    """Ordena variables por variabilidad relativa cuando el promedio lo permite."""
    rows: list[dict[str, float | str]] = []
    for column in data.select_dtypes(include="number").columns:
        series = _clean_numeric(data[column])
        mean = float(series.mean())
        std = float(series.std(ddof=0))
        cv = abs(std / mean) * 100 if not math.isclose(mean, 0.0) else math.nan
        rows.append(
            {
                "Variable": str(column),
                "Media": mean,
                "Desviación estándar": std,
                "CV (%)": cv,
            }
        )
    return (
        pd.DataFrame(rows)
        .dropna(subset=["CV (%)"])
        .sort_values("CV (%)", ascending=False)
        .reset_index(drop=True)
    )

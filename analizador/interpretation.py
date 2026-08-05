"""Generación automática de interpretaciones estadísticas en español."""

from __future__ import annotations

import math

import pandas as pd

from .statistics_engine import AnalysisResult, variability_ranking


def _fmt(value: float | int | str) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    if math.isnan(float(value)):
        return "no calculable"
    return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_interpretation(
    result: AnalysisResult, data: pd.DataFrame
) -> list[tuple[str, str]]:
    """Devuelve secciones con explicaciones contextualizadas y prudentes."""
    m = result.metrics
    mean = float(m["Media"])
    median = float(m["Mediana"])
    std = float(m["Desviación estándar"])
    cv = float(m["Coeficiente de variación"])
    skew = float(m["Asimetría"])
    n = int(m["Datos válidos"])
    outliers = int(m["Valores atípicos"])

    overview = (
        f"La variable «{result.variable}» contiene {_fmt(n)} observaciones válidas. "
        f"Los valores se extienden desde {_fmt(m['Mínimo'])} hasta {_fmt(m['Máximo'])}, "
        f"con una amplitud total de {_fmt(m['Rango'])}."
    )

    central_gap = abs(mean - median)
    tolerance = max(std * 0.1, 1e-12)
    if central_gap <= tolerance:
        central_message = (
            "La media y la mediana son cercanas, lo que sugiere un centro relativamente "
            "estable y poca influencia global de valores extremos."
        )
    elif mean > median:
        central_message = (
            "La media supera a la mediana; los valores altos ejercen mayor influencia "
            "sobre el promedio y apuntan a una cola hacia la derecha."
        )
    else:
        central_message = (
            "La media es menor que la mediana; los valores bajos influyen en el promedio "
            "y apuntan a una cola hacia la izquierda."
        )
    central = (
        f"La media es {_fmt(mean)}, la mediana {_fmt(median)} y la moda "
        f"{_fmt(m['Moda'])}. {central_message}"
    )

    if math.isnan(cv):
        variability_level = (
            "El coeficiente de variación no es interpretable porque la media es cero "
            "o demasiado cercana a cero; se usa la desviación estándar absoluta."
        )
    elif cv < 15:
        variability_level = "La variabilidad relativa es baja: los datos son homogéneos."
    elif cv < 30:
        variability_level = (
            "La variabilidad relativa es moderada: existe dispersión apreciable sin "
            "dominar completamente al promedio."
        )
    else:
        variability_level = (
            "La variabilidad relativa es alta: los valores son heterogéneos y el promedio "
            "debe interpretarse con cautela."
        )
    dispersion = (
        f"La desviación estándar poblacional es {_fmt(std)}, la varianza es "
        f"{_fmt(m['Varianza poblacional'])} y el coeficiente de variación es "
        f"{_fmt(cv)} %. {variability_level}"
    )

    if math.isnan(skew) or abs(skew) < 0.5:
        shape = "La distribución presenta una asimetría leve o aproximadamente equilibrada."
    elif skew > 0:
        shape = (
            "La distribución tiene asimetría positiva: la cola derecha contiene valores "
            "más alejados."
        )
    else:
        shape = (
            "La distribución tiene asimetría negativa: la cola izquierda contiene valores "
            "más alejados."
        )
    distribution = (
        f"El coeficiente de asimetría es {_fmt(skew)}. {shape} El histograma y el "
        "polígono permiten verificar visualmente dónde se concentra la frecuencia, "
        "mientras la curva acumulada muestra qué proporción queda por debajo de cada clase."
    )

    outlier_pct = (outliers / n * 100) if n else 0
    if outliers:
        outlier_message = (
            f"Se detectaron {_fmt(outliers)} observaciones atípicas ({_fmt(outlier_pct)} %) "
            f"mediante el criterio de 1,5 RIC, fuera del intervalo "
            f"[{_fmt(result.lower_fence)}, {_fmt(result.upper_fence)}]. Deben revisarse "
            "en su contexto antes de eliminarlas, pues pueden representar eventos reales."
        )
    else:
        outlier_message = (
            "No se detectaron valores atípicos con el criterio de 1,5 veces el rango "
            "intercuartílico."
        )

    ranking = variability_ranking(data)
    if len(ranking) >= 2:
        highest = ranking.iloc[0]
        lowest = ranking.iloc[-1]
        comparison = (
            f"Entre las variables con media distinta de cero, «{highest['Variable']}» "
            f"presenta la mayor variabilidad relativa (CV = {_fmt(highest['CV (%)'])} %), "
            f"mientras «{lowest['Variable']}» presenta la menor "
            f"(CV = {_fmt(lowest['CV (%)'])} %). Esta comparación es relativa a la escala "
            "y no implica por sí sola una relación causal."
        )
    else:
        comparison = (
            "No existen suficientes variables con media distinta de cero para comparar "
            "la variabilidad relativa."
        )

    conclusion = (
        f"En síntesis, «{result.variable}» se caracteriza por un centro cercano a "
        f"{_fmt(median)}, una dispersión estándar de {_fmt(std)} y "
        f"{'presencia' if outliers else 'ausencia'} de atípicos según el criterio RIC. "
        "Las conclusiones describen este conjunto de datos; no prueban causalidad ni "
        "deben extrapolarse sin considerar cómo se recolectaron los registros."
    )

    return [
        ("Comportamiento general", overview),
        ("Tendencia central", central),
        ("Dispersión", dispersion),
        ("Forma y representaciones", distribution),
        ("Valores atípicos", outlier_message),
        ("Comparación entre variables", comparison),
        ("Conclusión descriptiva", conclusion),
    ]

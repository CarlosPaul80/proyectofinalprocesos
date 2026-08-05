"""Pruebas automáticas del motor estadístico."""

from __future__ import annotations

from pathlib import Path
import math
import tempfile
import unittest
from unittest.mock import patch

from matplotlib.figure import Figure
import pandas as pd
from PIL import Image as PILImage

from analizador.data_loader import load_dataset, profile_dataset
from analizador.reporting import export_variable_report
from analizador.statistics_engine import analyze_variable, variability_ranking
from analizador.visualizations import BG_COLOR


PROJECT_DIR = Path(__file__).resolve().parents[1]


class StatisticsEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = pd.DataFrame(
            {
                "x": [1, 2, 2, 3, 4, 100, None],
                "y": [10, 10, 10, 10, 10, 10, 10],
                "group": list("AABBBCC"),
            }
        )

    def test_central_and_dispersion_metrics(self) -> None:
        result = analyze_variable(self.data, "x")
        valid = pd.Series([1, 2, 2, 3, 4, 100], dtype=float)
        self.assertAlmostEqual(result.metrics["Media"], valid.mean())
        self.assertAlmostEqual(result.metrics["Mediana"], valid.median())
        self.assertEqual(result.metrics["Moda"], "2")
        self.assertAlmostEqual(
            result.metrics["Varianza poblacional"], valid.var(ddof=0)
        )
        self.assertAlmostEqual(
            result.metrics["Desviación estándar"], valid.std(ddof=0)
        )
        expected_mad = (valid - valid.mean()).abs().mean()
        self.assertAlmostEqual(result.metrics["Desviación media"], expected_mad)

    def test_frequency_totals(self) -> None:
        result = analyze_variable(self.data, "x")
        table = result.frequency_table
        self.assertEqual(table["Frecuencia absoluta"].sum(), 6)
        self.assertAlmostEqual(table["Frecuencia relativa"].sum(), 1.0)
        self.assertAlmostEqual(table["Frecuencia porcentual"].sum(), 100.0)
        self.assertEqual(table["Frecuencia acumulada"].iloc[-1], 6)

    def test_outlier_detection(self) -> None:
        result = analyze_variable(self.data, "x")
        self.assertIn(100.0, result.outliers.tolist())

    def test_constant_variable(self) -> None:
        result = analyze_variable(self.data, "y")
        self.assertEqual(result.metrics["Rango"], 0)
        self.assertEqual(result.metrics["Desviación estándar"], 0)
        self.assertTrue(math.isclose(result.frequency_table.iloc[0]["Frecuencia absoluta"], 7))

    def test_variability_ranking(self) -> None:
        ranking = variability_ranking(self.data)
        self.assertEqual(ranking.iloc[0]["Variable"], "x")


class DatasetIntegrationTests(unittest.TestCase):
    def test_demo_dataset_meets_project_requirements(self) -> None:
        path = PROJECT_DIR / "data" / "SeoulBikeData.csv"
        data = load_dataset(path)
        profile = profile_dataset(data)
        self.assertGreaterEqual(profile.rows, 300)
        self.assertGreaterEqual(profile.columns, 5)
        self.assertGreaterEqual(len(profile.numeric_columns), 3)

    def test_xlsx_loading(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.xlsx"
            pd.DataFrame(
                {"a": [1, 2, 3], "b": [4.5, 5.5, 6.5], "group": ["x", "y", "z"]}
            ).to_excel(path, index=False)
            loaded = load_dataset(path)
            self.assertEqual(loaded.shape, (3, 3))
            self.assertEqual(len(profile_dataset(loaded).numeric_columns), 2)

    def test_pdf_export(self) -> None:
        data = pd.DataFrame({"value": list(range(1, 51)), "other": list(range(51, 101))})
        result = analyze_variable(data, "value")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "analysis.pdf"
            export_variable_report(path, "sample.csv", data, result)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 10_000)

    def test_pdf_export_preserves_dark_chart_background(self) -> None:
        data = pd.DataFrame({"value": list(range(1, 51))})
        result = analyze_variable(data, "value")
        rendered_backgrounds: list[tuple[int, int, int]] = []
        savefig = Figure.savefig

        def savefig_and_capture(
            figure: Figure, path: str | Path, *args, **kwargs
        ) -> None:
            savefig(figure, path, *args, **kwargs)
            with PILImage.open(path) as image:
                rendered_backgrounds.append(image.convert("RGB").getpixel((0, 0)))

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "analysis-dark.pdf"
            with patch.object(
                Figure,
                "savefig",
                autospec=True,
                side_effect=savefig_and_capture,
            ):
                export_variable_report(path, "sample.csv", data, result)

        expected_background = tuple(
            int(BG_COLOR[index : index + 2], 16) for index in (1, 3, 5)
        )
        self.assertEqual(rendered_backgrounds, [expected_background] * 2)


if __name__ == "__main__":
    unittest.main()

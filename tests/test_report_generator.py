"""Pruebas del generador del informe técnico."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from generar_informe import load_report_config


class ReportGeneratorTests(unittest.TestCase):
    def test_cover_placeholders_are_rejected(self) -> None:
        config = {
            "institucion": "NOMBRE DE LA INSTITUCIÓN",
            "carrera": "Desarrollo de Software",
            "asignatura": "Probabilidad y Procesos Estocásticos",
            "titulo": "Informe",
            "nombre_aplicacion": "StatLab",
            "integrantes": ["NOMBRE DEL ESTUDIANTE 1"],
            "docente": "NOMBRE DEL DOCENTE",
            "ciudad": "Ecuador",
            "fecha": "Julio de 2026",
        }
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "config_informe.json"
            config_path.write_text(
                json.dumps(config, ensure_ascii=False),
                encoding="utf-8",
            )
            with patch("generar_informe.CONFIG_PATH", config_path):
                with self.assertRaisesRegex(ValueError, "marcadores sin reemplazar"):
                    load_report_config()


if __name__ == "__main__":
    unittest.main()

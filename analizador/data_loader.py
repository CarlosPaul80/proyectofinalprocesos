"""Carga, validación y perfilado general de archivos tabulares."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_object_dtype, is_string_dtype


SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


class DataLoadError(ValueError):
    """Error legible para el usuario durante la carga de datos."""


@dataclass(frozen=True)
class DatasetProfile:
    rows: int
    columns: int
    numeric_columns: tuple[str, ...]
    categorical_columns: tuple[str, ...]
    missing_values: int
    duplicated_rows: int
    memory_mb: float


def _load_csv(path: Path) -> pd.DataFrame:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(
                path,
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="error",
            )
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            errors.append(f"{encoding}: {exc}")
    raise DataLoadError(
        "No se pudo interpretar el CSV. Verifique el separador y la codificación.\n"
        + "\n".join(errors[-2:])
    )


def load_dataset(file_path: str | Path) -> pd.DataFrame:
    """Carga CSV/Excel y aplica validaciones mínimas sin alterar los datos."""
    path = Path(file_path)
    if not path.exists():
        raise DataLoadError(f"El archivo no existe:\n{path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise DataLoadError("Formato no compatible. Use CSV o XLSX.")

    try:
        if path.suffix.lower() == ".csv":
            data = _load_csv(path)
        else:
            data = pd.read_excel(path)
    except DataLoadError:
        raise
    except Exception as exc:
        raise DataLoadError(f"No fue posible cargar el archivo: {exc}") from exc

    if data.empty:
        raise DataLoadError("El archivo no contiene registros.")

    data.columns = [
        str(column).strip() or f"Columna_{index + 1}"
        for index, column in enumerate(data.columns)
    ]
    duplicate_names = data.columns[data.columns.duplicated()].tolist()
    if duplicate_names:
        raise DataLoadError(
            "Existen nombres de columnas duplicados: " + ", ".join(duplicate_names)
        )

    # Convierte columnas de texto que son casi totalmente numéricas.
    for column in data.columns:
        if is_numeric_dtype(data[column]) or not (
            is_object_dtype(data[column]) or is_string_dtype(data[column])
        ):
            continue
        converted = pd.to_numeric(data[column], errors="coerce")
        original_non_null = int(data[column].notna().sum())
        if original_non_null and converted.notna().sum() / original_non_null >= 0.95:
            data[column] = converted

    if len(data.select_dtypes(include="number").columns) == 0:
        raise DataLoadError(
            "El archivo debe contener al menos una variable numérica analizable."
        )
    return data


def profile_dataset(data: pd.DataFrame) -> DatasetProfile:
    numeric = tuple(data.select_dtypes(include="number").columns.astype(str))
    categorical = tuple(column for column in data.columns if column not in numeric)
    return DatasetProfile(
        rows=int(data.shape[0]),
        columns=int(data.shape[1]),
        numeric_columns=numeric,
        categorical_columns=categorical,
        missing_values=int(data.isna().sum().sum()),
        duplicated_rows=int(data.duplicated().sum()),
        memory_mb=float(data.memory_usage(deep=True).sum() / (1024**2)),
    )

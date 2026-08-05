"""Punto de entrada de StatLab."""

from __future__ import annotations

import argparse
import ctypes
import customtkinter

from analizador.ui import StatisticalApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aplicación de escritorio para análisis estadístico descriptivo."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Carga automáticamente el dataset de demostración.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")
    
    args = parse_args()
    app = StatisticalApp(load_demo=args.demo)
    app.mainloop()

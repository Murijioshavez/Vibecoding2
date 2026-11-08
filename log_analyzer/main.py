"""Punto de entrada para el analizador de logs."""

from __future__ import annotations

import argparse
from pathlib import Path

from log_analyzer import LogFileError, analyze_file, format_summary


class FileDialogUnavailableError(Exception):
    """El selector gráfico no está disponible en el entorno actual."""


def select_file_with_dialog() -> Path | None:
    """Abre el selector gráfico y devuelve None si el usuario cancela."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as error:
        raise FileDialogUnavailableError("tkinter no está instalado") from error

    try:
        root = tk.Tk()
    except tk.TclError as error:
        raise FileDialogUnavailableError("no hay una interfaz gráfica disponible") from error
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askopenfilename(
            title="Selecciona un archivo de logs",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
    finally:
        root.destroy()
    return Path(selected) if selected else None


def request_file_path() -> Path | None:
    """Alternativa por consola para entornos sin interfaz gráfica."""
    try:
        entered_path = input("Escribe la ruta del archivo de logs (o deja vacío para cancelar): ").strip()
    except EOFError:
        return None
    return Path(entered_path.strip('"')) if entered_path else None


def get_file_path(argument_path: str | None) -> Path | None:
    if argument_path:
        return Path(argument_path)
    try:
        return select_file_with_dialog()
    except FileDialogUnavailableError as error:
        print(f"No se pudo abrir el selector gráfico ({error}). Se usará la consola.")
        return request_file_path()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analiza un archivo de logs UTF-8.")
    parser.add_argument("path", nargs="?", help="Ruta opcional; evita abrir el selector gráfico.")
    args = parser.parse_args(argv)

    path = get_file_path(args.path)
    if path is None:
        print("No se seleccionó ningún archivo.")
        return 1

    try:
        print(format_summary(analyze_file(path)))
    except LogFileError as error:
        print(f"Error: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

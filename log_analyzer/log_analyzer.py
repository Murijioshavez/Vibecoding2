"""Funciones para leer y validar registros de eventos simples."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
from typing import Iterable


VALID_SEVERITIES = ("INFO", "WARNING", "ERROR")
_LINE_PATTERN = re.compile(r"^\[(?P<severity>[A-Za-z]+)\](?:\s+(?P<body>.*))?$")
_ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATE_LIKE_PATTERN = re.compile(r"^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$")


class LogFileError(Exception):
    """Indica que un archivo de logs no pudo ser leído."""


@dataclass
class LineAnalysis:
    """Resultado del análisis de una línea física del archivo."""

    line_number: int
    original: str
    severity: str | None = None
    date: str | None = None
    is_blank: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def is_event(self) -> bool:
        return not self.is_blank

    @property
    def is_valid(self) -> bool:
        return self.is_event and not self.errors


@dataclass
class AnalysisSummary:
    """Estadísticas agregadas de todas las líneas analizadas."""

    source_name: str
    total_lines: int
    total_events: int
    blank_lines: int
    valid_lines: int
    malformed_lines: int
    severity_counts: Counter[str]
    error_counts: Counter[str]
    line_results: list[LineAnalysis]

    @property
    def valid_percentage(self) -> float:
        if self.total_events == 0:
            return 0.0
        return (self.valid_lines / self.total_events) * 100


def validate_date(value: str) -> bool:
    """Comprueba que *value* sea una fecha ISO real, no solo una cadena con forma de fecha."""
    if not _ISO_DATE_PATTERN.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def analyze_line(line: str, line_number: int = 1) -> LineAnalysis:
    """Analiza una línea según la política de validación del proyecto."""
    content = line.strip()
    result = LineAnalysis(line_number=line_number, original=line.rstrip("\r\n"))

    if not content:
        result.is_blank = True
        return result

    match = _LINE_PATTERN.fullmatch(content)
    if not match:
        result.errors.append("Severidad ausente o con formato inválido")
        return result

    candidate_severity = match.group("severity")
    if candidate_severity in VALID_SEVERITIES:
        result.severity = candidate_severity
    else:
        result.errors.append(f"Severidad desconocida: {candidate_severity}")

    body = (match.group("body") or "").strip()
    if not body:
        result.errors.extend(["Fecha ausente", "Mensaje ausente"])
        return result

    first_token, *remaining = body.split(maxsplit=1)
    message = remaining[0].strip() if remaining else ""

    if _ISO_DATE_PATTERN.fullmatch(first_token):
        result.date = first_token
        if not validate_date(first_token):
            result.errors.append(f"Fecha imposible: {first_token}")
        if not message:
            result.errors.append("Mensaje ausente")
    elif _DATE_LIKE_PATTERN.fullmatch(first_token):
        result.errors.append(f"Formato de fecha no admitido: {first_token}")
        if not message:
            result.errors.append("Mensaje ausente")
    else:
        # El contenido existe y se conserva como mensaje, pero no se encontró una fecha al inicio.
        result.errors.append("Fecha ausente")

    return result


def analyze_lines(lines: Iterable[str], source_name: str = "<contenido>") -> AnalysisSummary:
    """Analiza una colección de líneas sin cargar reglas de presentación en el parser."""
    results = [analyze_line(line, number) for number, line in enumerate(lines, start=1)]
    severity_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()

    for result in results:
        if result.severity:
            severity_counts[result.severity] += 1
        error_counts.update(result.errors)

    total_events = sum(result.is_event for result in results)
    blank_lines = sum(result.is_blank for result in results)
    valid_lines = sum(result.is_valid for result in results)
    malformed_lines = total_events - valid_lines

    return AnalysisSummary(
        source_name=source_name,
        total_lines=len(results),
        total_events=total_events,
        blank_lines=blank_lines,
        valid_lines=valid_lines,
        malformed_lines=malformed_lines,
        severity_counts=severity_counts,
        error_counts=error_counts,
        line_results=results,
    )


def read_log_file(path: str | Path) -> list[str]:
    """Lee un archivo UTF-8 y transforma los errores de E/S en un error explicable."""
    log_path = Path(path)
    try:
        with log_path.open("r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError as error:
        raise LogFileError(f"El archivo no existe: {log_path}") from error
    except PermissionError as error:
        raise LogFileError(f"No hay permiso para leer el archivo: {log_path}") from error
    except UnicodeDecodeError as error:
        raise LogFileError(f"El archivo no está codificado en UTF-8: {log_path}") from error
    except OSError as error:
        raise LogFileError(f"No fue posible leer el archivo: {log_path} ({error})") from error


def analyze_file(path: str | Path) -> AnalysisSummary:
    """Lee un archivo y devuelve su resumen de validación."""
    log_path = Path(path)
    return analyze_lines(read_log_file(log_path), source_name=log_path.name)


def format_summary(summary: AnalysisSummary) -> str:
    """Construye un resumen de consola estable y fácil de revisar."""
    lines = [
        "RESUMEN DEL ANÁLISIS",
        "=" * 24,
        f"Archivo analizado: {summary.source_name}",
        f"Total de líneas físicas: {summary.total_lines}",
        f"Total de eventos (no vacíos): {summary.total_events}",
        f"Líneas vacías: {summary.blank_lines}",
        f"Eventos INFO: {summary.severity_counts['INFO']}",
        f"Eventos WARNING: {summary.severity_counts['WARNING']}",
        f"Eventos ERROR: {summary.severity_counts['ERROR']}",
        f"Líneas correctamente formateadas: {summary.valid_lines}",
        f"Líneas mal formateadas: {summary.malformed_lines}",
        f"Porcentaje de eventos válidos: {summary.valid_percentage:.1f}%",
    ]
    if summary.error_counts:
        lines.extend(["", "Errores encontrados:"])
        lines.extend(f"- {error}: {count}" for error, count in summary.error_counts.items())
    return "\n".join(lines)

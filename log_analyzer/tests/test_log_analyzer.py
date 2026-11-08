from __future__ import annotations

from pathlib import Path
import sys
from unittest import TestCase, main
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from log_analyzer import (  # noqa: E402
    LogFileError,
    analyze_file,
    analyze_line,
    analyze_lines,
    format_summary,
    read_log_file,
    validate_date,
)
from main import FileDialogUnavailableError, get_file_path  # noqa: E402


LOGS = PROJECT_ROOT / "test_logs"


class DateValidationTests(TestCase):
    def test_validate_date_distinguishes_real_and_impossible_dates(self):
        self.assertTrue(validate_date("2024-02-29"))
        self.assertFalse(validate_date("2025-02-29"))
        self.assertFalse(validate_date("10/01/2025"))


class LineAnalysisTests(TestCase):
    def test_complete_line_is_valid(self):
        result = analyze_line("[INFO] 2025-01-10 User logged in\n", 3)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.severity, "INFO")
        self.assertEqual(result.date, "2025-01-10")

    def test_line_without_date_keeps_its_message_and_reports_missing_date(self):
        result = analyze_line("[WARNING] Invalid password attempt")
        self.assertEqual(result.severity, "WARNING")
        self.assertEqual(result.errors, ["Fecha ausente"])

    def test_line_can_report_multiple_problems(self):
        result = analyze_line("[UNKNOWN] 31/12/2025")
        self.assertIn("Severidad desconocida: UNKNOWN", result.errors)
        self.assertIn("Formato de fecha no admitido: 31/12/2025", result.errors)
        self.assertIn("Mensaje ausente", result.errors)

    def test_blank_line_is_not_an_event_or_malformed_event(self):
        result = analyze_line("   \n")
        self.assertTrue(result.is_blank)
        self.assertFalse(result.is_event)
        self.assertFalse(result.is_valid)


class FileAnalysisTests(TestCase):
    def test_valid_fixture_summary(self):
        summary = analyze_file(LOGS / "logs_validos.txt")
        self.assertEqual(summary.total_events, 4)
        self.assertEqual(summary.valid_lines, 4)
        self.assertEqual(summary.malformed_lines, 0)
        self.assertEqual(dict(summary.severity_counts), {"INFO": 2, "WARNING": 1, "ERROR": 1})

    def test_error_fixture_summary(self):
        summary = analyze_file(LOGS / "logs_con_errores.txt")
        self.assertEqual(summary.total_events, 7)
        self.assertEqual(summary.valid_lines, 0)
        self.assertEqual(summary.malformed_lines, 7)
        self.assertEqual(summary.severity_counts["INFO"], 2)
        self.assertEqual(summary.severity_counts["WARNING"], 1)
        self.assertEqual(summary.severity_counts["ERROR"], 1)

    def test_empty_content_has_zero_percent_validity(self):
        summary = analyze_lines([], "vacío.txt")
        self.assertEqual(summary.total_lines, 0)
        self.assertEqual(summary.total_events, 0)
        self.assertEqual(summary.valid_percentage, 0.0)
        self.assertIn("0.0%", format_summary(summary))

    def test_single_line_file(self):
        summary = analyze_lines(["[ERROR] 2025-01-10 One event"], "una_linea.txt")
        self.assertEqual(summary.total_events, 1)
        self.assertEqual(summary.valid_lines, 1)

    def test_large_but_reasonable_input(self):
        summary = analyze_lines(["[INFO] 2025-01-10 Event\n"] * 2_000, "grande.txt")
        self.assertEqual(summary.total_events, 2_000)
        self.assertEqual(summary.valid_lines, 2_000)

    def test_missing_file_has_clear_error(self):
        with self.assertRaisesRegex(LogFileError, "no existe"):
            read_log_file(LOGS / "does_not_exist.txt")

    def test_invalid_utf8_has_clear_error(self):
        invalid_file = LOGS / "temporal_no_utf8.bin"
        invalid_file.write_bytes(b"\xff\xfe\x00")
        try:
            with self.assertRaisesRegex(LogFileError, "UTF-8"):
                read_log_file(invalid_file)
        finally:
            invalid_file.unlink(missing_ok=True)

    def test_permission_error_is_reported_when_reading_fails(self):
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(LogFileError, "permiso"):
                read_log_file(LOGS / "logs_validos.txt")


class FileSelectionTests(TestCase):
    def test_cancelling_the_dialog_does_not_request_a_console_path(self):
        with patch("main.select_file_with_dialog", return_value=None), patch(
            "main.request_file_path"
        ) as request_path:
            self.assertIsNone(get_file_path(None))
            request_path.assert_not_called()

    def test_unavailable_dialog_uses_console_fallback(self):
        expected = Path("manual.txt")
        with patch(
            "main.select_file_with_dialog",
            side_effect=FileDialogUnavailableError("sin pantalla"),
        ), patch("main.request_file_path", return_value=expected), patch("builtins.print"):
            self.assertEqual(get_file_path(None), expected)


if __name__ == "__main__":
    main()

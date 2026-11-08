# Evidencias de pruebas ejecutadas

Fecha de ejecución: 8 de noviembre de 2026. Los resultados de este documento proceden de ejecuciones reales dentro del workspace, no de resultados supuestos.

## Archivos de prueba

| Archivo | Contenido cubierto | Resultado comprobado |
| --- | --- | --- |
| `test_logs/logs_validos.txt` | 4 eventos completos; INFO, WARNING, ERROR y un 29 de febrero válido de 2024 | 4 eventos, 4 válidos, 0 mal formados; INFO=2, WARNING=1, ERROR=1 |
| `test_logs/logs_con_errores.txt` | Fecha imposible, severidad desconocida, fecha ausente, mensaje ausente, severidad ausente, formato de fecha no admitido y corchete incompleto | 7 eventos, 0 válidos y 7 mal formados; INFO=2, WARNING=1, ERROR=1 |
| `test_logs/logs_edge_cases.txt` | Dos líneas vacías, espacios extra, fecha imposible, símbolos, mensaje ausente, varios fallos en una línea y carácter UTF-8 | 8 líneas físicas, 6 eventos, 2 vacías, 3 válidos y 3 mal formados; INFO=2, WARNING=1, ERROR=2 |

## Suite automatizada

Se ejecutó desde la carpeta `log_analyzer`:

```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
```

Resultado real: **15 pruebas ejecutadas en 0.031 segundos; todas terminaron en `OK`**.

La suite comprueba validación de fechas reales, líneas completas, fecha ausente, errores múltiples, líneas vacías, los archivos de ejemplo, contenido vacío, una sola línea, 2,000 eventos, archivo inexistente, UTF-8 inválido y un error de permisos simulado con `unittest.mock`. La simulación de permisos es deliberada: cambiar permisos reales de forma portable, sobre todo en Windows, puede depender de privilegios de la cuenta.

También se ejecutó:

```powershell
python -m py_compile main.py log_analyzer.py tests\test_log_analyzer.py
python main.py .\test_logs\logs_validos.txt
python main.py .\test_logs\logs_con_errores.txt
```

La compilación no produjo errores. La ejecución de consola mostró 100.0% de eventos válidos para el archivo válido y 0.0% para el archivo intencionalmente incorrecto, con el desglose de los siete problemas.

## Hallazgo y corrección reales

En la primera versión, `get_file_path` usaba el ingreso por consola tanto cuando la interfaz no podía abrirse como cuando la persona cancelaba la ventana. Esto mezclaba dos resultados distintos: cancelar no es un fallo de `tkinter`.

Se corrigió introduciendo `FileDialogUnavailableError`. Ahora la cancelación devuelve `None` y termina con el mensaje “No se seleccionó ningún archivo”; solo un fallo al importar o iniciar `tkinter` ofrece la alternativa por consola. Se añadieron dos pruebas para ambos caminos. Esta corrección fue detectada durante la revisión del flujo de control y es verificable en `main.py` y en `tests/test_log_analyzer.py`.

## Limitaciones conocidas

- La política solo admite archivos UTF-8 y fechas ISO `YYYY-MM-DD`; es una regla intencional que debe ser aprobada por el estudiante.
- El programa procesa el archivo completo en memoria mediante `readlines()`. Es apropiado para la actividad y los tamaños probados, no para logs enormes de producción.
- La ventana gráfica depende de que `tkinter` y una sesión gráfica estén disponibles. El modo de ruta por consola cubre esa situación.

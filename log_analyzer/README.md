# Analizador de logs: IA como herramienta, no como autor

Programa en Python para seleccionar o indicar un archivo de texto UTF-8, revisar cada evento y presentar un resumen en consola. Identifica severidad, fecha ISO válida, mensaje, líneas incompletas y errores de lectura.

## Tecnologías

- Python 3 y biblioteca estándar.
- `re` para reconocer la estructura de las líneas.
- `datetime` para comprobar fechas reales.
- `tkinter` para el selector gráfico de archivos.
- `unittest` para las pruebas automatizadas.

## Ejecutar el programa

Desde la carpeta del proyecto:

```powershell
python main.py
```

Se abrirá una ventana para elegir un `.txt`. Si la ventana no puede abrirse, el programa pedirá la ruta por consola. Para probar directamente sin ventana:

```powershell
python main.py .\test_logs\logs_validos.txt
```

## Ejecutar las pruebas

```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
```

## Reglas principales

La propuesta actual exige `[INFO|WARNING|ERROR] YYYY-MM-DD Mensaje`. Los detalles, alternativas y decisiones pendientes están en [docs/decisiones_tecnicas.md](docs/decisiones_tecnicas.md).

## Estructura

```text
log_analyzer/
├── main.py
├── log_analyzer.py
├── tests/test_log_analyzer.py
├── test_logs/
└── docs/
```

## Ejemplo breve

Para `logs_validos.txt` se esperan cuatro eventos válidos: dos `INFO`, uno `WARNING` y uno `ERROR`. Los resultados ejecutados se registran en `docs/evidencias_pruebas.md`.

## Uso consciente de IA

La IA apoyó con la estructura inicial, propuestas de validación, pruebas y documentación. Las reglas no se presentan como decisiones automáticas del estudiante: se señalan como propuestas que el estudiante debe revisar antes de entregar. La trazabilidad y el borrador de reflexión están en `docs/`.

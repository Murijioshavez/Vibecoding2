# Decisiones técnicas y reglas de validación

Este documento registra una propuesta inicial generada durante el desarrollo asistido con IA. No sustituye la revisión del estudiante.

## Política implementada

Una línea válida tiene esta estructura:

```text
[INFO|WARNING|ERROR] YYYY-MM-DD Mensaje no vacío
```

- Solo se aceptan las severidades escritas exactamente como `INFO`, `WARNING` y `ERROR`.
- La fecha debe ser el primer elemento después de la severidad y usar `YYYY-MM-DD`.
- La expresión regular comprueba la forma de la fecha y `datetime.strptime` comprueba que exista realmente. Así, `2025-02-30` no pasa aunque tenga la forma correcta.
- Los espacios externos y varios espacios entre campos se permiten, porque no cambian el contenido del evento.
- Un mensaje puede contener números, símbolos y caracteres UTF-8; debe tener al menos un carácter que no sea espacio.
- Una línea vacía se cuenta como línea física vacía, pero no como evento ni como evento mal formado. Esto evita que un separador visual altere las estadísticas de eventos.
- Una línea no vacía con cualquier campo requerido ausente o inválido se considera un evento mal formado. Puede acumular varios errores para mostrar la causa real.
- La severidad reconocida se contabiliza incluso si la fecha o el mensaje de esa misma línea fallan. Una severidad desconocida no se asigna a ninguno de los tres contadores.
- Un archivo vacío es válido como entrada, pero contiene cero eventos y muestra 0.0% de eventos válidos.
- El archivo debe poder leerse en UTF-8. Archivo inexistente, permisos insuficientes y codificación inválida producen un mensaje claro y no un resumen engañoso.

## Alternativas consideradas

| Tema | Alternativa | Consecuencia | Recomendación inicial |
| --- | --- | --- | --- |
| Fecha | Aceptar varios formatos | Más flexible, pero menos predecible y más reglas | Aceptar solo ISO `YYYY-MM-DD` |
| Fecha imposible | Validar solo con regex | `2025-02-30` se aceptaría por error | Regex más `datetime` |
| Línea sin fecha | Ignorarla por completo | Se pierde la evidencia de un evento incompleto | Contarla como mal formada y explicar que falta fecha |
| Línea vacía | Contarla como error | Puede penalizar separadores visuales | Reportarla aparte |
| Severidad minúscula | Normalizar con `.upper()` | Oculta un formato inconsistente | Exigir mayúsculas exactas |
| Errores múltiples | Detenerse en el primer error | Da mensajes más cortos pero incompletos | Acumular errores por línea |

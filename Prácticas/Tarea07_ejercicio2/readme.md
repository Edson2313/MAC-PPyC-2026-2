# Análisis de Latencia en Sistemas Concurrentes: APIs REST

## Descripción

Este proyecto tiene como objetivo analizar la diferencia de rendimiento entre una ejecución **secuencial** y una **concurrente** al consumir múltiples APIs REST.

Se utiliza la API de Open-Meteo para obtener información del clima de distintas ciudades y se comparan los tiempos de respuesta en ambos enfoques.

---

## Objetivos

- Ejecutar consultas a APIs de forma secuencial como se pidio en el archivo.
- Implementar concurrencia usando `threading.Thread`.
- Medir y comparar tiempos de ejecución.
- Analizar el impacto de la concurrencia en operaciones I/O.

---

## Ciudades Analizadas

- CDMX
- Nueva York
- Londres
- Tokio

---

## Tecnologías utilizadas

- Python 3
- Librerías:
  - `requests`
  - `threading`
  - `time`

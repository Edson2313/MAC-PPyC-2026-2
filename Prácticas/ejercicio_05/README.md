# Práctica 5: Patrón Arquitectónico Productor-Consumidor - Equilibrio de Cargas

## Descripción

Esta práctica implementa el patrón arquitectónico **Productor-Consumidor** para demostrar el equilibrio de cargas en sistemas concurrentes. Utiliza una cola thread-safe (`queue.Queue`) para comunicar productores y consumidores de forma segura.

### Objetivos
- Implementar múltiples productores que generan datos (chistes) desde una API REST
- Implementar múltiples consumidores que procesan los datos y los persisten en archivos
- Utilizar una cola compartida con capacidad limitada para equilibrar la carga
- Coordinar la detención del sistema mediante tiempo máximo o cantidad máxima de items
- Muestra el rendimiento del programa


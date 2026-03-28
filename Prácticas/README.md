# Ejercicio 2: Condiciones de Carrera y Sincronización: Exclusión Mutua

## Descripción

Este ejercicio demuestra el problema de las condiciones de carrera en sistemas concurrentes y cómo puede resolverse mediante sincronización usando `threading.Lock()`.

Una condición de carrera ocurre cuando múltiples hilos acceden y modifican una variable compartida al mismo tiempo, provocando resultados inconsistentes.

Para ilustrar este problema, se simula un sistema de venta de boletos donde varios hilos intentan descontar boletos de un inventario compartido.

---

## Objetivo

- Comprender cómo se producen las condiciones de carrera en programas concurrentes.
- Observar cómo múltiples hilos pueden interferir al modificar un recurso compartido.
- Aplicar exclusión mutua utilizando `threading.Lock()` para proteger la sección crítica.
- Verificar que el resultado final sea consistente cuando se utiliza sincronización.

---

## Funcionamiento del Programa

El programa realiza dos simulaciones:

### 1. Simulación sin sincronización (sin Lock)

En esta versión, los hilos acceden simultáneamente a la variable compartida `boletos_disponibles`.

Pasos de la primera simulación:

1. Se inicia un inventario con 1000 boletos.
2. Se crean 100 hilos, cada uno intenta vender 10 boletos.
3. Los hilos leen el valor del inventario, esperan una pequeña latencia (`sleep`) y luego actualizan el valor.

Debido a que los hilos trabajan al mismo tiempo, algunos pueden sobrescribir los cambios de otros, provocando un resultado incorrecto.

Resultado esperado:

- Inventario final diferente de 0.
- Se detecta una condición de carrera.

---

### 2. Simulación con sincronización (con Lock)

En esta versión se utiliza `threading.Lock()` para proteger la sección crítica donde se modifica el inventario.

El Lock garantiza que:

- Solo un hilo a la vez pueda acceder a la sección crítica.
- Los demás hilos deben esperar su turno.

Resultado esperado:

- Inventario final correcto (0 boletos).
- No hay inconsistencias en los datos.

---


## Resultados Esperados

Al ejecutar el programa se observará una salida similar a la siguiente:
```
SIMULACIÓN SIN LOCK
Boletos restantes: 40
Condición de carrera detectada

SIMULACIÓN CON LOCK
Boletos restantes: 0
Sincronización exitosa
```

El número de boletos restantes en la primera simulación puede variar en cada ejecución debido a la naturaleza de la concurrencia.

---

## Conceptos de Concurrencia Aplicados

- Threading
- Condición de carrera
- Sección crítica
- Exclusión mutua
- threading.Lock()

---

## Conclusión

Este ejercicio demuestra cómo la ejecución concurrente puede provocar inconsistencias cuando múltiples hilos acceden a un recurso compartido sin control.

El uso de mecanismos de sincronización como Locks permite garantizar la integridad de los datos y evitar condiciones de carrera en aplicaciones concurrentes.
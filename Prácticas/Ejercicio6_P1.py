import requests
import threading
import time
import os

archivos = [
    ("https://www.gutenberg.org/cache/epub/11/pg11.txt",   "pg11_alice.txt"),
    ("https://www.gutenberg.org/cache/epub/84/pg84.txt",   "pg84_frankenstein.txt"),
    ("https://www.gutenberg.org/cache/epub/1342/pg1342.txt", "pg1342_pride.txt"),
    ("https://www.gutenberg.org/cache/epub/1661/pg1661.txt", "pg1661_sherlock.txt"),
    ("https://www.gutenberg.org/cache/epub/98/pg98.txt",   "pg98_two_cities.txt"),
]

def descargar_archivo(url, nombre_salida):
    """Descarga un archivo desde `url` y lo guarda en `nombre_salida`."""
    respuesta = requests.get(url, stream=True, timeout=30)
    respuesta.raise_for_status()
    with open(nombre_salida, "wb") as archivo:
        for chunk in respuesta.iter_content(chunk_size=1024):
            if chunk:
                archivo.write(chunk)

# Secuencial
def descargar_secuencial(archivos):
    """Descarga los archivos uno por uno y devuelve el tiempo total."""
    print("\n=== Descarga SECUENCIAL ===")
    inicio = time.time()

    for url, nombre in archivos:
        print(f"  Descargando: {nombre}...")
        descargar_archivo(url, nombre)
        kb = os.path.getsize(nombre) / 1024
        print(f"  ✓ {nombre} ({kb:.1f} KB)")

    duracion = time.time() - inicio
    print(f"  Tiempo total secuencial: {duracion:.2f}s")
    return duracion

# Con hilos (concurrente)
def descargar_con_hilos(archivos):
    """Descarga todos los archivos en paralelo usando un hilo por URL."""
    print("\n=== Descarga CONCURRENTE (hilos) ===")
    inicio = time.time()

    hilos = []
    for url, nombre in archivos:
        hilo = threading.Thread(
            target=descargar_archivo,
            args=(url, nombre),
            name=f"Hilo-{nombre}"
        )
        hilos.append((hilo, nombre))

    # Lanzar todos los hilos simultáneamente
    for hilo, _ in hilos:
        hilo.start()
        print(f"  Hilo iniciado: {hilo.name}")

    # Esperar a que todos terminen
    for hilo, nombre in hilos:
        hilo.join()
        kb = os.path.getsize(nombre) / 1024
        print(f"  ✓ {nombre} ({kb:.1f} KB)")

    duracion = time.time() - inicio
    print(f"  Tiempo total concurrente: {duracion:.2f}s")
    return duracion

# Verificación de archivos descargados
def verificar_descargas(archivos):
    print("\n=== Verificación de archivos ===")
    todos_ok = True
    for _, nombre in archivos:
        if os.path.exists(nombre) and os.path.getsize(nombre) > 0:
            kb = os.path.getsize(nombre) / 1024
            print(f"  ✓ {nombre:35s} {kb:8.1f} KB")
        else:
            print(f"  ✗ {nombre} – NO encontrado o vacío")
            todos_ok = False
    return todos_ok


if __name__ == "__main__":
    print("Descarga Concurrente de Múltiples Archivos")
    print("=" * 45)

    # Descarga secuencial
    t_sec = descargar_secuencial(archivos)

    # Descarga concurrente
    t_con = descargar_con_hilos(archivos)

    # Verificación
    verificar_descargas(archivos)

    # Comparación
    print("\n=== Comparación de tiempos ===")
    print(f"  Secuencial : {t_sec:.2f}s")
    print(f"  Concurrente: {t_con:.2f}s")
    mejora = (t_sec - t_con) / t_sec * 100
    speedup = t_sec / t_con
    print(f"  Mejora     : {mejora:.1f}%  (speedup ×{speedup:.1f})")

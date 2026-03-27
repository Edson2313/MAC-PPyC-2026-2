import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

paginas = [
    "scanme.nmap.org",
    "testphp.vulnweb.com",
    "example.com",
    "google.com"
]

MODOS = {
    "1": ("Puertos importantes (0 - 1024)",  range(0, 1025)),
    "2": ("Rango completo      (0 - 65535)", range(0, 65536)),
}


def verificar_puerto(host, puerto):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            resultado = s.connect_ex((host, puerto))
            if resultado == 0:
                return (host, puerto, True)
    except socket.gaierror:
        pass
    except Exception:
        pass
    return (host, puerto, False)


def escanear_paginas(paginas, puertos, modo_nombre, max_workers=200):
    """
    Puertos abiertos y tiempo de ejecución.
    """
    print()
    print("=" * 55)
    print("       ESCÁNER DE PUERTOS PARALELO")
    print("=" * 55)
    print(f"  Modo     : {modo_nombre}")
    print(f"  Páginas  : {len(paginas)}")
    print(f"  Puertos  : {len(puertos)}")
    print(f"  Workers  : {max_workers}")
    print(f"  Tareas   : {len(paginas) * len(puertos):,}")
    print("=" * 55)
    print()

    tareas = [(host, puerto) for host in paginas for puerto in puertos]
    resultados_abiertos = []

    inicio = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(verificar_puerto, host, puerto): (host, puerto)
            for host, puerto in tareas
        }
        for futuro in as_completed(futuros):
            host, puerto, abierto = futuro.result()
            if abierto:
                resultados_abiertos.append((host, puerto))

    fin = time.perf_counter()
    tiempo_total = fin - inicio

    resultados_abiertos.sort(key=lambda x: (x[0], x[1]))

    if resultados_abiertos:
        host_actual = None
        for host, puerto in resultados_abiertos:
            if host != host_actual:
                if host_actual is not None:
                    print()
                print(f"  {host}")
                print(f"  {'-' * len(host)}")
                host_actual = host
            print(f"    puerto {puerto:>5}  -->  ABIERTO")
        print()
    else:
        print("  No se encontraron puertos abiertos.")
        print()

    print("=" * 55)
    print(f"  Total puertos abiertos : {len(resultados_abiertos)}")
    print(f"  Tiempo de ejecución    : {tiempo_total:.2f} segundos")
    print("=" * 55)
    print()


def seleccionar_modo():
    print()
    print("=" * 55)
    print("       ESCÁNER DE PUERTOS — MENÚ")
    print("=" * 55)
    for clave, (nombre, _) in MODOS.items():
        print(f"  [{clave}] {nombre}")
    print("=" * 55)

    while True:
        opcion = input("  Selecciona una opción (1 o 2): ").strip()
        if opcion in MODOS:
            return MODOS[opcion]  #nombre y rango
        print("  Opción inválida. Ingresa 1 o 2.")


if __name__ == "__main__":
    modo_nombre, puertos = seleccionar_modo()
    escanear_paginas(paginas, puertos, modo_nombre, max_workers=200)


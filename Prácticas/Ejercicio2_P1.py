import requests
from PIL import Image
import numpy as np
import io
import threading
import time

url_img = (
    "https://images.unsplash.com/"
    "photo-1506748686214-e9df14d4d9d0?w=1080"
)
response = requests.get(url_img)
img = Image.open(io.BytesIO(response.content))
matriz_original = np.array(img)  # Matriz de píxeles (Height, Width, Channels)

print(f"Imagen cargada: {matriz_original.shape[1]}x{matriz_original.shape[0]} px")


def escala_grises_secuencial(matriz):
    """Convierte la imagen a escala de grises píxel por píxel (un solo hilo)."""
    alto, ancho, canales = matriz.shape
    for i in range(alto):
        for j in range(ancho):
            r, g, b = matriz[i, j]
            # Ecuación de luminancia CIE 1931
            gris = int(0.299 * r + 0.587 * g + 0.114 * b)
            matriz[i, j] = [gris, gris, gris]
    return matriz


def convertir_franja(matriz, fila_inicio, fila_fin, hilo_id):
    """
    Tarea de cada hilo: convierte a gris solo las filas [fila_inicio, fila_fin).
    Opera directamente sobre la matriz compartida (numpy es thread-safe para
    escrituras en regiones disjuntas).
    """
    for i in range(fila_inicio, fila_fin):
        for j in range(matriz.shape[1]):
            r, g, b = matriz[i, j]
            gris = int(0.299 * r + 0.587 * g + 0.114 * b)
            matriz[i, j] = [gris, gris, gris]
    print(f"  [Hilo {hilo_id}] Filas {fila_inicio}-{fila_fin-1} completadas ✓")


def escala_grises_paralela(matriz, N=4):
    """
    Divide la imagen en N franjas horizontales y lanza un hilo por franja.

    Parámetros:
        matriz : np.ndarray — imagen RGB compartida (se modifica in-place)
        N      : int        — número de hilos / franjas (ej. 4 u 8)
    """
    alto = matriz.shape[0]
    hilos = []

    indices = np.array_split(range(alto), N)

    print(f"\nParticionando imagen en {N} franjas horizontales:")
    for k, idx in enumerate(indices):
        fila_inicio = idx[0]
        fila_fin    = idx[-1] + 1          # rango exclusivo
        print(f"  Franja {k}: filas {fila_inicio} → {fila_fin - 1}  "
              f"({fila_fin - fila_inicio} filas)")

        hilo = threading.Thread(
            target=convertir_franja,
            args=(matriz, fila_inicio, fila_fin, k),
            name=f"Hilo-{k}"
        )
        hilos.append(hilo)

    print("\nLanzando hilos...")
    t0 = time.perf_counter()

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    t1 = time.perf_counter()
    print(f"\nTodos los hilos terminaron en {t1 - t0:.2f} s")
    return matriz


def main():
    N_HILOS = 4   

    # — Secuencial —
    mat_sec = matriz_original.copy()
    print("\n=== VERSIÓN SECUENCIAL ===")
    t0 = time.perf_counter()
    escala_grises_secuencial(mat_sec)
    t_sec = time.perf_counter() - t0
    print(f"Tiempo secuencial: {t_sec:.2f} s")
    Image.fromarray(mat_sec.astype(np.uint8)).save("gris_secuencial.png")
    print("Guardada: gris_secuencial.png")

    # — Paralela —
    mat_par = matriz_original.copy()
    print(f"\n=== VERSIÓN PARALELA ({N_HILOS} hilos) ===")
    t0 = time.perf_counter()
    escala_grises_paralela(mat_par, N=N_HILOS)
    t_par = time.perf_counter() - t0
    print(f"Tiempo paralelo:   {t_par:.2f} s")
    Image.fromarray(mat_par.astype(np.uint8)).save("gris_paralelo.png")
    print("Guardada: gris_paralelo.png")

    # — Resumen —
    speedup = t_sec / t_par if t_par > 0 else float('inf')
    print(f"\n{'─'*40}")
    print(f"Speedup (sec/par): {speedup:.2f}x")
    print(f"¿Imágenes idénticas? "
          f"{'SÍ ✓' if np.array_equal(mat_sec, mat_par) else 'NO ✗'}")

    print("Para paralelismo real en CPU-bound usa multiprocessing.")


if __name__ == "__main__":
    main()
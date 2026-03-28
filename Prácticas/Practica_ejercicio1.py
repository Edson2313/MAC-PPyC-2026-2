import time
import requests
import threading

ciudades = [
    {"nombre": "CDMX", "lat": 19.43, "lon": -99.13},
    {"nombre": "NY", "lat": 40.71, "lon": -74.00},
    {"nombre": "Londres", "lat": 51.50, "lon": -0.12},
    {"nombre": "Tokio", "lat": 35.68, "lon": 139.69}
]

def obtener_clima(lat, lon):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = f"?latitude={lat}&longitude={lon}&current_weather=true"
    url = base_url + params
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        return respuesta.json()['current_weather']
    return None


# =========================
# 🔹 1. Secuencial
# =========================
resultados_seq = {}

inicio_seq = time.time()

for ciudad in ciudades:
    clima = obtener_clima(ciudad['lat'], ciudad['lon'])
    resultados_seq[ciudad['nombre']] = clima

tiempo_seq = time.time() - inicio_seq

print("Resultados secuencial:")
for ciudad, clima in resultados_seq.items():
    print(ciudad, "->", clima)

print(f"\nTiempo secuencial: {tiempo_seq:.4f} segundos")


# =========================
# 🔹 2. Concurrente
# =========================
resultados_conc = {}
lock = threading.Lock()  # para evitar conflictos

def tarea(ciudad):
    clima = obtener_clima(ciudad['lat'], ciudad['lon'])
    
    # Sección crítica
    with lock:
        resultados_conc[ciudad['nombre']] = clima

hilos = []
inicio_conc = time.time()

for ciudad in ciudades:
    hilo = threading.Thread(target=tarea, args=(ciudad,))
    hilos.append(hilo)
    hilo.start()

# Esperar a todos los hilos
for hilo in hilos:
    hilo.join()

tiempo_conc = time.time() - inicio_conc

print("\nResultados concurrente:")
for ciudad, clima in resultados_conc.items():
    print(ciudad, "->", clima)

print(f"\nTiempo concurrente: {tiempo_conc:.4f} segundos")


# =========================
# 🔹 3. Comparación
# =========================
print("\nComparación:")
print(f"Secuencial: {tiempo_seq:.4f} s")
print(f"Concurrente: {tiempo_conc:.4f} s")
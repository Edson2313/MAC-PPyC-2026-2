import threading
import time

boletos_disponibles = 1000

cerrojo = threading.Lock()

# 1 VERSIÓN SIN LOCK (INCORRECTA)

def vender_boletos_sin_lock(id_hilo, cantidad):
    global boletos_disponibles

    temp = boletos_disponibles
    time.sleep(0.0001)  
    boletos_disponibles = temp - cantidad


def simulacion_sin_lock():
    global boletos_disponibles
    boletos_disponibles = 1000

    hilos = []

    print("\n==============================")
    print("SIMULACIÓN SIN LOCK")
    print("==============================")

    for i in range(100):
        t = threading.Thread(target=vender_boletos_sin_lock, args=(i, 10))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print(f"Boletos restantes: {boletos_disponibles}")

    if boletos_disponibles != 0:
        print("❌ Condición de carrera detectada: el inventario es incorrecto.")
    else:
        print("Resultado correcto (pero fue por casualidad).")

# 2 VERSIÓN CON LOCK (CORRECTA)

def vender_boletos_con_lock(id_hilo, cantidad):
    global boletos_disponibles

    with cerrojo:
        temp = boletos_disponibles
        time.sleep(0.0001)
        boletos_disponibles = temp - cantidad


def simulacion_con_lock():
    global boletos_disponibles
    boletos_disponibles = 1000

    hilos = []

    print("\n==============================")
    print("SIMULACIÓN CON LOCK")
    print("==============================")

    for i in range(100):
        t = threading.Thread(target=vender_boletos_con_lock, args=(i, 10))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    print(f"Boletos restantes: {boletos_disponibles}")

    if boletos_disponibles == 0:
        print("✅ Sincronización exitosa: el inventario es correcto.")
    else:
        print("❌ Error en sincronización.")


# EJECUCIÓN
if __name__ == "__main__":

    simulacion_sin_lock()

    simulacion_con_lock()
import requests
import queue
import threading
import time
import json
from datetime import datetime

# Configuración del sistema
MAX_ITEMS = 50  # Cantidad máxima de chistes a procesar
TIEMPO_MAXIMO = 5  # Tiempo máximo de ejecución en segundos
MAX_QUEUE_SIZE = 20  # Tamaño máximo de la cola

# Cola thread-safe para compartir los chistes entre productores y consumidores
cola_chistes = queue.Queue(maxsize=MAX_QUEUE_SIZE)

# Evento para señalar que el sistema debe detenerse
detener_sistema = threading.Event()

# Contadores compartidos
total_chistes_producidos = 0
total_chistes_consumidos = 0
chistes_guardados = []

# Locks para proteger los contadores compartidos
lock_producidos = threading.Lock()
lock_consumidos = threading.Lock()
lock_guardados = threading.Lock()

def obtener_chiste(productor_id):
    """
    Obtiene un chiste aleatorio de la API de Chuck Norris
    """
    try:
        endpoint = "https://api.chucknorris.io/jokes/random"
        respuesta = requests.get(endpoint, timeout=10)
        if respuesta.status_code == 200:
            chiste = respuesta.json()['value']
            return chiste
        else:
            return None
    except Exception as e:
        print(f"[Productor {productor_id}] Error al obtener chiste: {e}")
        return None

def productor(productor_id):
    """
    Productor: Genera chistes y los coloca en la cola
    """
    global total_chistes_producidos
    
    print(f"[Productor {productor_id}] Iniciado")
    
    while not detener_sistema.is_set():
        try:
            # Obtener un chiste
            chiste = obtener_chiste(productor_id)
            
            if chiste:
                # Intentar colocar el chiste en la cola (con timeout)
                try:
                    cola_chistes.put((productor_id, chiste, time.time()), timeout=1)
                    
                    # Incrementar contador de chistes producidos
                    with lock_producidos:
                        total_chistes_producidos += 1
                        producidos_actual = total_chistes_producidos
                    
                    print(f"[Productor {productor_id}] Produjo chiste #{producidos_actual}")
                    
                    # Verificar si alcanzamos el máximo de items
                    if producidos_actual >= MAX_ITEMS:
                        print(f"[Productor {productor_id}] Se alcanzó el máximo de {MAX_ITEMS} items")
                        detener_sistema.set()
                        break
                        
                except queue.Full:
                    print(f"[Productor {productor_id}] Cola llena, esperando...")
                    time.sleep(0.1)
            else:
                # Si no se pudo obtener chiste, esperar un poco
                time.sleep(0.5)
                
        except Exception as e:
            print(f"[Productor {productor_id}] Error: {e}")
            time.sleep(1)
    
    print(f"[Productor {productor_id}] Terminado")

def consumidor(consumidor_id):
    """
    Consumidor: Toma chistes de la cola y los guarda en archivo
    """
    global total_chistes_consumidos, chistes_guardados
    
    print(f"[Consumidor {consumidor_id}] Iniciado")
    
    # Cada consumidor tiene su propio archivo para evitar conflictos
    archivo = f"chistes_consumidor_{consumidor_id}.txt"
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(f"=== Chistes procesados por Consumidor {consumidor_id} ===\n")
        f.write(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        while not detener_sistema.is_set() or not cola_chistes.empty():
            try:
                # Intentar obtener un chiste de la cola (con timeout)
                productor_id, chiste, timestamp = cola_chistes.get(timeout=1)
                
                # Procesar el chiste (guardarlo en archivo)
                numero_chiste = None
                with lock_consumidos:
                    total_chistes_consumidos += 1
                    numero_chiste = total_chistes_consumidos
                
                # Guardar en archivo
                f.write(f"Chiste #{numero_chiste} (Productor {productor_id}):\n")
                f.write(f"{chiste}\n")
                f.write(f"Timestamp: {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}\n")
                f.write("-" * 60 + "\n\n")
                f.flush()  # Forzar escritura en disco
                
                # Guardar también en lista compartida para estadísticas
                with lock_guardados:
                    chistes_guardados.append({
                        'numero': numero_chiste,
                        'productor': productor_id,
                        'consumidor': consumidor_id,
                        'chiste': chiste,
                        'timestamp': timestamp
                    })
                
                print(f"[Consumidor {consumidor_id}] Consumió chiste #{numero_chiste}")
                
                # Marcar como completado en la cola
                cola_chistes.task_done()
                
            except queue.Empty:
                # Si la cola está vacía y el sistema debe detenerse, salir
                if detener_sistema.is_set():
                    break
                # Si no, esperar un poco
                time.sleep(0.1)
            except Exception as e:
                print(f"[Consumidor {consumidor_id}] Error: {e}")
                time.sleep(0.5)
        
        f.write(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"[Consumidor {consumidor_id}] Terminado - Procesó {total_chistes_consumidos} chistes")

def version_concurrente():
    """
    Versión concurrente: 2 productores y 3 consumidores con cola thread-safe
    """
    global total_chistes_producidos, total_chistes_consumidos, chistes_guardados
    total_chistes_producidos = 0
    total_chistes_consumidos = 0
    chistes_guardados = []
    detener_sistema.clear()
    
    # Vaciar la cola por si acaso
    while not cola_chistes.empty():
        try:
            cola_chistes.get_nowait()
            cola_chistes.task_done()
        except queue.Empty:
            break
    
    print("\n" + "="*60)
    print("VERSIÓN CONCURRENTE (2 Productores + 3 Consumidores)")
    print("="*60)
    
    inicio = time.time()
    
    # Crear productores
    productores = []
    for i in range(1, 3):  # 2 productores
        hilo = threading.Thread(target=productor, args=(i,))
        productores.append(hilo)
        hilo.start()
    
    # Crear consumidores
    consumidores = []
    for i in range(1, 4):  # 3 consumidores
        hilo = threading.Thread(target=consumidor, args=(i,))
        consumidores.append(hilo)
        hilo.start()
    
    # Monitorear el sistema
    tiempo_inicio = time.time()
    try:
        while not detener_sistema.is_set():
            # Verificar si se alcanzó el tiempo máximo
            if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
                print(f"\n[Sistema] Tiempo máximo ({TIEMPO_MAXIMO}s) alcanzado")
                detener_sistema.set()
                break
            
            # Verificar si se alcanzó la cantidad máxima de items
            with lock_producidos:
                if total_chistes_producidos >= MAX_ITEMS:
                    print(f"\n[Sistema] Cantidad máxima ({MAX_ITEMS} items) alcanzada")
                    detener_sistema.set()
                    break
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n[Sistema] Interrupción manual")
        detener_sistema.set()
    
    # Esperar a que todos los hilos terminen
    print("\n[Sistema] Esperando que terminen los hilos...")
    
    for hilo in productores:
        hilo.join(timeout=2)
    
    for hilo in consumidores:
        hilo.join(timeout=2)
    
    tiempo_total = time.time() - inicio
    
    print(f"\n--- ESTADÍSTICAS VERSIÓN CONCURRENTE ---")
    print(f"Tiempo total: {tiempo_total:.4f} segundos")
    print(f"Total chistes producidos: {total_chistes_producidos}")
    print(f"Total chistes consumidos: {total_chistes_consumidos}")
    print(f"Items en cola al final: {cola_chistes.qsize()}")
    
    # Crear archivo resumen
    with open("chistes_concurrente_resumen.txt", 'w', encoding='utf-8') as f:
        f.write("=== Sistema Productor-Consumidor (Versión Concurrente) ===\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tiempo ejecución: {tiempo_total:.4f} segundos\n")
        f.write(f"Productores: 2 | Consumidores: 3\n")
        f.write(f"Tamaño máximo cola: {MAX_QUEUE_SIZE}\n\n")
        
        f.write("=== ESTADÍSTICAS ===\n")
        f.write(f"Total chistes producidos: {total_chistes_producidos}\n")
        f.write(f"Total chistes consumidos: {total_chistes_consumidos}\n")
        f.write(f"Items en cola al final: {cola_chistes.qsize()}\n\n")
        
        f.write("=== DISTRIBUCIÓN POR CONSUMIDOR ===\n")
        consumidor_counts = {}
        for item in chistes_guardados:
            cid = item['consumidor']
            consumidor_counts[cid] = consumidor_counts.get(cid, 0) + 1
        
        for cid, count in sorted(consumidor_counts.items()):
            f.write(f"Consumidor {cid}: {count} chistes\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("=== APÉNDICE: DETALLE DE ARCHIVOS POR CONSUMIDOR ===\n")
        f.write("="*60 + "\n")
        # Unimos el contenido de los 3 archivos de los consumidores
        for i in range(1, 4):  # Para consumidor 1, 2 y 3
            nombre_archivo_consumidor = f"chistes_consumidor_{i}.txt"
            try:
                with open(nombre_archivo_consumidor, 'r', encoding='utf-8') as archivo_c:
                    contenido = archivo_c.read()
                    f.write(f"\n--- RECOPILACIÓN DE: {nombre_archivo_consumidor} ---\n")
                    f.write(contenido)
                    f.write("\n" + "-"*40 + "\n")
            except FileNotFoundError:
                f.write(f"\n[Error] No se encontró el archivo del Consumidor {i}\n")
    
    return tiempo_total

def mostrar_estadisticas_archivos():
    """
    Muestra estadísticas de los archivos generados
    """
    print("\n" + "="*60)
    print("ARCHIVOS GENERADOS")
    print("="*60)
    
    archivos = [
        "chistes_concurrente_resumen.txt",
        "chistes_consumidor_1.txt",
        "chistes_consumidor_2.txt",
        "chistes_consumidor_3.txt"
    ]
    
    import os
    for archivo in archivos:
        if os.path.exists(archivo):
            tamaño = os.path.getsize(archivo) / 1024  # KB
            print(f"✓ {archivo} ({tamaño:.1f} KB)")
        else:
            print(f"✗ {archivo} (no encontrado)")

if __name__ == "__main__":
    print("="*70)
    print("PRÁCTICA 5: Patrón Arquitectónico Productor-Consumidor - Equilibrio de Cargas")
    print("="*70)
    
    print("\nInformación del sistema:")
    print(f"• Máximo de items: {MAX_ITEMS}")
    print(f"• Tiempo máximo: {TIEMPO_MAXIMO} segundos")
    print(f"• Tamaño máximo de cola: {MAX_QUEUE_SIZE}")
    print(f"• API: https://api.chucknorris.io/jokes/random")
    
    # Pequeña pausa para no saturar la API
    time.sleep(2)
    
    # Ejecutar versión concurrente
    tiempo_conc = version_concurrente()
    
    # Comparación de rendimiento
    print("\n" + "="*60)
    print("RENDIMIENTO")
    print("="*60)
    print(f"Versión concurrente:  {tiempo_conc:.4f} segundos")
    
    
    # Mostrar archivos generados
    mostrar_estadisticas_archivos()
    
    print("\n" + "="*60)
    print("CONCLUSIONES DEL PATRÓN PRODUCTOR-CONSUMIDOR")
    print("="*60)
    print("• queue.Queue: Cola thread-safe que permite comunicación segura entre hilos")
    print("• Productores: Generan datos y los colocan en la cola")
    print("• Consumidores: Extraen datos de la cola y los procesan")
    print("• Separación de responsabilidades: producción y consumo son independientes")
    print("• Equilibrio de cargas: Múltiples consumidores trabajan en paralelo")
    print("• El sistema se detiene por tiempo máximo o cantidad máxima de items")
    print("• Los consumidores guardan en archivos separados para evitar conflictos")
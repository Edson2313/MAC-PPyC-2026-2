import urllib.request
from collections import Counter
from threading import Thread
from queue import Queue
import re
import time

# URLs de los libros a descargar
libros = [
    ("https://www.gutenberg.org/cache/epub/1342/pg1342.txt", "Orgullo y Prejuicio"),
    ("https://www.gutenberg.org/cache/epub/84/pg84.txt", "Frankenstein"),
    ("https://www.gutenberg.org/cache/epub/11/pg11.txt", "Alicia en el país de las maravillas")
]


def contar_palabras(url):
    try:
        print(f"[MAP] Descargando: {url}")
        respuesta = urllib.request.urlopen(url, timeout=10)
        texto = respuesta.read().decode('utf-8').lower()
        
        # Extraer solo palabras (remover puntuación y números)
        palabras = re.findall(r'\b[a-z]+\b', texto)
        
        # Filtrar palabras muy cortas y palabras comunes (stopwords)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why',
            'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'de', 'que', 'el', 'la', 'y', 'o', 'un',
            'una', 'unos', 'unas', 'lo', 'su', 'sus', 'se', 'le', 'les', 'es',
            'fue', 'son', 'está', 'están', 'era', 'eran', 'ser', 'estar', 'tener'
        }
        
        palabras_filtradas = [p for p in palabras if len(p) > 3 and p not in stopwords]
        
        contador = Counter(palabras_filtradas)
        print(f"[MAP] Completado: {len(palabras_filtradas)} palabras procesadas")
        return contador
        
    except Exception as e:
        print(f"[ERROR] No se pudo descargar {url}: {e}")
        return Counter()


def map_phase(libros, resultados_queue):
    hilos = []
    
    def procesar_libro(url, nombre):
        """Función para ejecutar en cada hilo"""
        print(f"\n[HILO] Iniciando procesamiento de: {nombre}")
        contador = contar_palabras(url)
        resultados_queue.put(contador)
        print(f"[HILO] {nombre} finalizado")
    
    # Lanzar un hilo por libro
    print("=" * 60)
    print("FASE MAP: Descargando y procesando libros en paralelo")
    print("=" * 60)
    
    inicio = time.time()
    
    for url, nombre in libros:
        hilo = Thread(target=procesar_libro, args=(url, nombre))
        hilo.start()
        hilos.append(hilo)
    
    # Esperar a que terminen todos los hilos
    for hilo in hilos:
        hilo.join()
    
    tiempo_map = time.time() - inicio
    print(f"\n[MAP] Fase completada en {tiempo_map:.2f} segundos")


def reduce_phase(resultados_queue):
    print("\n" + "=" * 60)
    print("FASE REDUCE: Fusionando resultados")
    print("=" * 60)
    
    contador_final = Counter()
    
    # Extraer todos los Counters de la cola y fusionarlos
    while not resultados_queue.empty():
        contador_parcial = resultados_queue.get()
        contador_final.update(contador_parcial)
    
    print(f"[REDUCE] Total de palabras únicas: {len(contador_final)}")
    print(f"[REDUCE] Total de palabras procesadas: {sum(contador_final.values())}")
    
    return contador_final


def mostrar_resultados(contador_final, top_n=20):
    print("\n" + "=" * 60)
    print(f"TOP {top_n} PALABRAS MÁS FRECUENTES")
    print("=" * 60)
    
    palabras_populares = contador_final.most_common(top_n)
    
    print(f"\n{'Ranking':<8} {'Palabra':<20} {'Frecuencia':<12} {'%':<8}")
    print("-" * 50)
    
    total_palabras = sum(contador_final.values())
    
    for i, (palabra, frecuencia) in enumerate(palabras_populares, 1):
        porcentaje = (frecuencia / total_palabras) * 100
        print(f"{i:<8} {palabra:<20} {frecuencia:<12} {porcentaje:.2f}%")


def main():
    print("\n" + "=" * 60)
    print("ANÁLISIS MAP-REDUCE DE TEXTOS DISTRIBUIDOS")
    print("=" * 60 + "\n")
    
    # Cola compartida para guardar resultados parciales
    resultados_queue = Queue()
    
    # Fase 1: MAP - Procesar libros en paralelo
    inicio_total = time.time()
    map_phase(libros, resultados_queue)
    
    # Fase 2: REDUCE - Fusionar todos los conteos
    contador_final = reduce_phase(resultados_queue)
    
    # Fase 3: Mostrar resultados
    mostrar_resultados(contador_final, top_n=20)
    
    tiempo_total = time.time() - inicio_total
    print("\n" + "=" * 60)
    print(f"  TIEMPO TOTAL DE EJECUCIÓN: {tiempo_total:.2f} segundos")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

"""
Script para migrar datos de SQLite a PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2 import sql

PG_CONFIG = {
    'host': 'localhost',
    'database': 'sp500_db',
    'user': 'postgres',
    'password': 'postgres',  # Cambiar si es diferente
    'port': '5432'
}

SQLITE_DB = "sp500_inversiones.db"

def migrate_to_postgres():
    
    try:
        # Conexión a PostgreSQL
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        
        # Crear tabla en PostgreSQL
        pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS inversiones (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL UNIQUE,
                precio VARCHAR(50),
                fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        pg_conn.commit()
        print("✓ Tabla 'inversiones' creada en PostgreSQL\n")
        
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        
        sqlite_cursor.execute("SELECT symbol, precio FROM inversiones")
        registros = sqlite_cursor.fetchall()
        total = len(registros)
                
        # Insertar datos en PostgreSQL
        insertados = 0
        errores = 0
        
        for i, (symbol, precio) in enumerate(registros, 1):
            try:
                pg_cursor.execute("""
                    INSERT INTO inversiones (symbol, precio, fecha_consulta)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (symbol) DO UPDATE 
                    SET precio = EXCLUDED.precio
                """, (symbol, precio))
                
                insertados += 1
                if i % 50 == 0:
                    pg_conn.commit()
                    print(f"  ✓ {i}/{total} registros procesados")
                    
            except Exception as e:
                errores += 1
                print(f"  ✗ Error con {symbol}: {str(e)[:50]}")
        
        pg_conn.commit()
        sqlite_conn.close()
        
        print(f"\n{'='*70}")
        print(f"  RESUMEN DE MIGRACIÓN")
        print(f"{'='*70}")
        print(f"  ✓ Insertados/actualizados: {insertados}")
        print(f"  ✗ Errores: {errores}")
        print(f"{'='*70}\n")
        
        pg_cursor.execute("SELECT COUNT(*) FROM inversiones")
        total_pg = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("""
            SELECT COUNT(*) FROM inversiones 
            WHERE precio NOT LIKE '%Error%' 
            AND precio NOT LIKE '%HTTP%'
            AND precio != 'N/A'
        """)
        validos_pg = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("""
            SELECT symbol, precio 
            FROM inversiones 
            ORDER BY fecha_consulta DESC 
            LIMIT 15
        """)
        
        for row in pg_cursor.fetchall():
            print(f"{row[0]:<10} {str(row[1]):<15}")
        
        pg_cursor.close()
        pg_conn.close()
                
    except psycopg2.OperationalError as e:
        print(f"Eror de conexión a PostgreSQL:")
        
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    migrate_to_postgres()


import os
import sys
import psycopg2
from decimal import Decimal, InvalidOperation

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "datamart"),
    "user": os.getenv("DB_USER", "datamart_user"),
    "password": os.getenv("DB_PASSWORD")
}

ARCHIVO_RESULTADOS = "/data/output/ingresos/part-00000"


def cargar_resultados():
    if not os.path.isfile(ARCHIVO_RESULTADOS):
        print(f"No se encontro el archivo: {ARCHIVO_RESULTADOS}")
        sys.exit(1)

    conexion = psycopg2.connect(**DB_CONFIG)
    cursor = conexion.cursor()

    insertados = 0

    try:
        with open(ARCHIVO_RESULTADOS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split("\t")

                if len(partes) != 3:
                    continue

                try:
                    hora = int(partes[0])
                    categoria = partes[1].strip()
                    ingreso = Decimal(partes[2])

                    if not 0 <= hora <= 23 or not categoria:
                        continue

                    clave = f"{hora}-{categoria}"

                    cursor.execute("""
                        INSERT INTO resultados
                            (clave, hora, categoria, ingreso_total)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (clave)
                        DO UPDATE SET
                            ingreso_total = EXCLUDED.ingreso_total
                    """, (clave, hora, categoria, ingreso))

                    insertados += 1

                except (ValueError, InvalidOperation):
                    continue

        conexion.commit()
        print(f"Resultados cargados correctamente: {insertados}")

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    cargar_resultados()

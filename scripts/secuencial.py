
import csv
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation
from collections import defaultdict

ARCHIVO_ENTRADA = "ventas_125052348.csv"
ARCHIVO_SALIDA = "scripts/resultados_secuencial.tsv"

def procesar():
    inicio = time.perf_counter()

    totales = defaultdict(Decimal)
    registros_validos = 0
    registros_invalidos = 0

    with open(ARCHIVO_ENTRADA, "r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)

        for fila in lector:
            try:
                fecha = datetime.strptime(
                    fila["fecha_hora"].strip(),
                    "%Y-%m-%d %H:%M:%S"
                )

                hora = fecha.hour
                categoria = fila["categoria"].strip()
                cantidad = Decimal(fila["cantidad"])
                precio = Decimal(fila["precio_unitario"])

                if not categoria:
                    raise ValueError("Categoría vacía")

                ingreso = cantidad * precio
                clave = (hora, categoria)

                totales[clave] += ingreso
                registros_validos += 1

            except (ValueError, InvalidOperation, TypeError, KeyError):
                registros_invalidos += 1

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8", newline="") as salida:
        for (hora, categoria), total in sorted(totales.items()):
            salida.write(f"{hora:02d}\t{categoria}\t{total}\n")

    fin = time.perf_counter()
    duracion = fin - inicio

    print("PROCESAMIENTO SECUENCIAL FINALIZADO")
    print(f"Registros validos: {registros_validos}")
    print(f"Registros invalidos: {registros_invalidos}")
    print(f"Grupos generados: {len(totales)}")
    print(f"Tiempo de ejecucion: {duracion:.2f} segundos")
    print(f"Archivo generado: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    procesar()

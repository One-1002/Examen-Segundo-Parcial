
import sys
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation


for linea in sys.stdin:
    try:
        fila = next(csv.reader([linea]))

        # Ignorar encabezado
        if not fila or fila[0].strip().lower() == "id":
            continue

        # Obtener columnas del CSV
        fecha_hora = fila[1].strip()
        categoria = fila[3].strip()
        cantidad = Decimal(fila[5].strip())
        precio_unitario = Decimal(fila[6].strip())

        # Extraer hora
        fecha = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
        hora = fecha.hour

        # Calcular ingreso
        ingreso = cantidad * precio_unitario

        # Emitir clave y valor
        clave = f"{hora:02d}|{categoria}"
        print(f"{clave}\t{ingreso}")

    except (IndexError, ValueError, InvalidOperation, TypeError):
        # Ignorar registros inválidos
        continue

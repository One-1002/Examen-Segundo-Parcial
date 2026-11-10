
import csv
from decimal import Decimal

ARCHIVO_SECUENCIAL = "scripts/resultados_secuencial.tsv"
ARCHIVO_MAPREDUCE = "scripts/resultados_mapreduce.tsv"


def leer_resultados(ruta):
    resultados = {}

    with open(ruta, "r", encoding="utf-8") as archivo:
        lector = csv.reader(archivo, delimiter="\t")

        for fila in lector:
            if len(fila) != 3:
                continue

            hora = int(fila[0])
            categoria = fila[1]
            ingreso = Decimal(fila[2])

            resultados[(hora, categoria)] = ingreso

    return resultados


secuencial = leer_resultados(ARCHIVO_SECUENCIAL)
mapreduce = leer_resultados(ARCHIVO_MAPREDUCE)

coinciden = secuencial == mapreduce

print("COMPARACION DE RESULTADOS")
print(f"Grupos secuenciales: {len(secuencial)}")
print(f"Grupos MapReduce: {len(mapreduce)}")
print(f"Coincidencia exacta: {'SI' if coinciden else 'NO'}")

if not coinciden:
    diferencias = set(secuencial) ^ set(mapreduce)

    for clave in diferencias:
        print(f"Grupo faltante: {clave}")

    for clave in set(secuencial) & set(mapreduce):
        if secuencial[clave] != mapreduce[clave]:
            print(
                f"Diferencia en {clave}: "
                f"secuencial={secuencial[clave]}, "
                f"MapReduce={mapreduce[clave]}"
            )
else:
    print("Los dos metodos generaron exactamente los mismos ingresos.")

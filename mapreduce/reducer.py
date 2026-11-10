
import sys
from decimal import Decimal, InvalidOperation

clave_actual = None
total = Decimal("0")


def emitir(clave, ingreso_total):
    if clave is not None:
        hora, categoria = clave.split("|", 1)
        print(f"{hora}\t{categoria}\t{ingreso_total}")


for linea in sys.stdin:
    try:
        clave, valor = linea.rstrip("\n").split("\t", 1)
        ingreso = Decimal(valor)

        if clave == clave_actual:
            total += ingreso
        else:
            emitir(clave_actual, total)
            clave_actual = clave
            total = ingreso

    except (ValueError, InvalidOperation):
        continue

emitir(clave_actual, total)

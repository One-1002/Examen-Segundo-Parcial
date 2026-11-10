
import os
import time
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuracion de PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "datamart"),
    "user": os.getenv("DB_USER", "datamart_user"),
    "password": os.getenv("DB_PASSWORD")
}


def conectar_db():
    return psycopg2.connect(**DB_CONFIG)


def inicializar_db():
    # Esperar a que PostgreSQL este disponible
    for intento in range(30):
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resultados (
                    clave VARCHAR(150) PRIMARY KEY,
                    hora INTEGER NOT NULL CHECK (hora BETWEEN 0 AND 23),
                    categoria VARCHAR(100) NOT NULL,
                    ingreso_total NUMERIC(15,2) NOT NULL
                );
            """)

            conexion.commit()
            cursor.close()
            conexion.close()

            print("Base de datos inicializada correctamente.")
            return

        except psycopg2.OperationalError:
            print(f"Esperando PostgreSQL... intento {intento + 1}/30")
            time.sleep(2)

    raise RuntimeError("No fue posible conectar con PostgreSQL.")


def generar_clave(hora, categoria):
    return f"{hora}-{categoria}"


# Comprobar que la API funciona
@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "API de resultados funcionando",
        "estado": "OK"
    })


# Consultar todos los resultados
@app.route("/resultados", methods=["GET"])
def obtener_resultados():
    conexion = conectar_db()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM resultados ORDER BY hora, categoria")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    for registro in datos:
        registro["ingreso_total"] = float(registro["ingreso_total"])

    return jsonify(datos)


# Consultar un resultado por clave
@app.route("/resultados/<path:clave>", methods=["GET"])
def obtener_resultado(clave):
    conexion = conectar_db()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM resultados WHERE clave = %s",
        (clave,)
    )

    registro = cursor.fetchone()

    cursor.close()
    conexion.close()

    if registro is None:
        return jsonify({"error": "Resultado no encontrado"}), 404

    registro["ingreso_total"] = float(registro["ingreso_total"])

    return jsonify(registro)


# Insertar un resultado
@app.route("/resultados", methods=["POST"])
def insertar_resultado():
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se requiere un JSON valido"}), 400

    try:
        hora = int(datos["hora"])
        categoria = str(datos["categoria"]).strip()
        ingreso = Decimal(str(datos["ingreso_total"]))

        if not 0 <= hora <= 23 or not categoria:
            raise ValueError()

        clave = generar_clave(hora, categoria)

    except (KeyError, ValueError, TypeError, ArithmeticError):
        return jsonify({"error": "Datos invalidos"}), 400

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO resultados
            (clave, hora, categoria, ingreso_total)
            VALUES (%s, %s, %s, %s)
        """, (clave, hora, categoria, ingreso))

        conexion.commit()

    except psycopg2.IntegrityError:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"error": "El resultado ya existe"}), 409

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Resultado insertado correctamente",
        "clave": clave
    }), 201


# Actualizar un resultado
@app.route("/resultados/<path:clave>", methods=["PUT"])
def actualizar_resultado(clave):
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se requiere un JSON valido"}), 400

    try:
        hora = int(datos["hora"])
        categoria = str(datos["categoria"]).strip()
        ingreso = Decimal(str(datos["ingreso_total"]))

        if not 0 <= hora <= 23 or not categoria:
            raise ValueError()

    except (KeyError, ValueError, TypeError, ArithmeticError):
        return jsonify({"error": "Datos invalidos"}), 400

    nueva_clave = generar_clave(hora, categoria)

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE resultados
            SET clave = %s, hora = %s,
                categoria = %s, ingreso_total = %s
            WHERE clave = %s
        """, (nueva_clave, hora, categoria, ingreso, clave))

        actualizado = cursor.rowcount
        conexion.commit()

    except psycopg2.IntegrityError:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"error": "La nueva clave ya existe"}), 409

    cursor.close()
    conexion.close()

    if actualizado == 0:
        return jsonify({"error": "Resultado no encontrado"}), 404

    return jsonify({"mensaje": "Resultado actualizado correctamente"})


# Eliminar un resultado
@app.route("/resultados/<path:clave>", methods=["DELETE"])
def eliminar_resultado(clave):
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM resultados WHERE clave = %s",
        (clave,)
    )

    eliminado = cursor.rowcount
    conexion.commit()

    cursor.close()
    conexion.close()

    if eliminado == 0:
        return jsonify({"error": "Resultado no encontrado"}), 404

    return jsonify({"mensaje": "Resultado eliminado correctamente"})


if __name__ == "__main__":
    inicializar_db()
    app.run(host="0.0.0.0", port=5000, debug=False)

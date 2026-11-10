
# Examen P2 - Procesamiento de Big Data

## 1. Descripción del proyecto

Sistema de procesamiento de datos de ventas mediante Hadoop Streaming, PostgreSQL y una API REST desarrollada con Flask.

El objetivo es calcular el ingreso total por hora del día (0 a 23) y categoría de producto, utilizando la fórmula:

**Ingreso = cantidad × precio_unitario**

Se procesan 5 millones de registros del archivo CSV `ventas_125052348.csv`.

## 2. Tecnologías utilizadas

- Python 3.11
- Hadoop 3.4.1
- Hadoop Streaming
- Docker y Docker Compose
- PostgreSQL 16
- Flask 3.1.2
- PowerShell
- OpenSSH con autenticación por llave

## 3. Arquitectura del sistema

El proyecto está compuesto por tres servicios:

### Hadoop
Procesa el archivo CSV mediante MapReduce:
- Mapper: lee los registros, extrae la hora y categoría, y calcula el ingreso individual.
- Reducer: agrupa los ingresos por hora y categoría y obtiene los totales.

### PostgreSQL
Almacena los 240 resultados generados por Hadoop.

### API Flask
Permite consultar y administrar los resultados mediante operaciones HTTP.

## 4. Estructura del proyecto

```text
Examen-P2/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── cargar_resultados.py
├── evidencias/
├── hadoop/
│   ├── Dockerfile
│   └── start-hadoop.sh
├── mapreduce/
│   ├── mapper.py
│   └── reducer.py
├── scripts/
│   ├── secuencial.py
│   ├── comparar.py
│   ├── resultados_secuencial.tsv
│   └── resultados_mapreduce.tsv
├── .env.example
├── .gitignore
├── docker-compose.yml
├── generar_dataset.py
└── README.md
```

El archivo CSV y el archivo `.env` no se incluyen en el repositorio.

## 5. Configuración y ejecución

### Requisitos
- Docker Desktop con motor Linux y WSL2.
- Python 3 instalado.
- Archivo CSV original en la raíz del proyecto.

### Variables de entorno

Crear un archivo `.env` a partir de `.env.example` y configurar las credenciales de PostgreSQL y el puerto de la API.

### Construir las imágenes

```powershell
docker compose build
```

### Iniciar los servicios

```powershell
docker compose up -d
```

### Verificar los contenedores

```powershell
docker compose ps
```

### Ejecutar Hadoop Streaming

```powershell
docker exec -u hadoop datamart-hadoop hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar -files /app/mapreduce/mapper.py,/app/mapreduce/reducer.py -mapper "python3 mapper.py" -reducer "python3 reducer.py" -input /data/input/ventas_125052348.csv -output /data/output/ingresos
```

### Consultar los resultados

```powershell
docker exec -u hadoop datamart-hadoop head -n 5 /data/output/ingresos/part-00000
```

### Cargar resultados en PostgreSQL

```powershell
docker exec datamart-api python cargar_resultados.py
```

### Consultar la API

```powershell
Invoke-RestMethod http://localhost:5000/resultados
```

## 6. Endpoints de la API

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Verificar disponibilidad de la API |
| GET | `/resultados` | Consultar todos los resultados |
| GET | `/resultados/<clave>` | Consultar un resultado específico |
| POST | `/resultados` | Crear un registro |
| PUT | `/resultados/<clave>` | Actualizar un registro |
| DELETE | `/resultados/<clave>` | Eliminar un registro |

## 7. Resultados obtenidos

| Indicador | Resultado |
|---|---:|
| Registros válidos | 5,000,000 |
| Registros inválidos | 0 |
| Grupos generados | 240 |
| Tiempo secuencial | 42.99 s |
| Tiempo Hadoop | 49.12 s |
| Resultados coincidentes | 240 de 240 |

La comparación confirmó que ambos métodos producen exactamente los mismos ingresos por hora y categoría.

En esta ejecución Hadoop tardó más debido a la sobrecarga de ejecución en un entorno local de un solo contenedor. Esto no representa una comparación de rendimiento contra un clúster distribuido de varios nodos.

## 8. Persistencia

PostgreSQL utiliza un volumen Docker denominado `postgres_data`.

La persistencia se comprobó deteniendo los contenedores con:

```powershell
docker compose down
```

Y levantándolos nuevamente con:

```powershell
docker compose up -d
```

Después del reinicio, los 240 registros continuaron disponibles.

**Importante:** no utilizar `docker compose down -v`, ya que elimina los volúmenes.

## 9. Seguridad

- El archivo `.env` contiene credenciales y no debe publicarse.
- El archivo CSV está excluido del repositorio.
- El acceso SSH entre la API y Hadoop utiliza autenticación mediante llave.
- El dataset se monta en el contenedor Hadoop como solo lectura.
- La API monta los resultados de Hadoop como solo lectura.

## 10. Consideraciones

La implementación utiliza Hadoop Streaming en modo local dentro de un contenedor. Aunque se utiliza el motor MapReduce de Hadoop, no se implementó un clúster multinodo con HDFS distribuido.

La solución demuestra el procesamiento MapReduce, la integración con PostgreSQL, la exposición de resultados mediante API REST y la persistencia de información.

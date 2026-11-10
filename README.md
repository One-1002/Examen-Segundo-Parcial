
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

## 11. Respuestas
Diferencia entre los modos standalone, pseudo-distribuido y totalmente distribuido de Hadoop. ¿En cuál se usa HDFS?
 Standalone: Hadoop funciona en una sola máquina, utilizando el sistema de archivos local y sin ejecutar servicios HDFS.
 Pseudo-distribuido: los servicios de Hadoop se ejecutan en una sola máquina como procesos independientes y se utiliza HDFS.
 Totalmente distribuido: Hadoop trabaja en varias máquinas conectadas, distribuyendo el almacenamiento y procesamiento de datos.
 HDFS se utiliza en los modos pseudo-distribuido y totalmente distribuido.

¿Por qué el dataset se monta como volumen y no se copia dentro de la imagen con COPY?

Montar el dataset como volumen permite separar los datos de la imagen del contenedor, evitando reconstruirla cada vez que cambia el archivo. Además, facilita trabajar con archivos grandes sin aumentar innecesariamente el tamaño de la imagen. También permite compartir los datos con el contenedor y establecer permisos de solo lectura para proteger el archivo original.


 ¿Qué ocurre con los datos de la base de datos al ejecutar docker compose down? ¿Y con docker compose down -v?

Al ejecutar docker compose down, los contenedores y la red se eliminan, pero los volúmenes nombrados permanecen, por lo que los datos de PostgreSQL se conservan. En cambio, al ejecutar docker compose down -v, también se eliminan los volúmenes asociados al proyecto, provocando la pérdida de los datos persistidos en PostgreSQL y de los demás volúmenes nombrados.


¿Por qué MapReduce no siempre es más rápido que un script secuencial con un archivo de 400 MB? ¿A partir de qué condiciones conviene?

MapReduce introduce sobrecarga por la inicialización de procesos, distribución de tareas, transferencia de datos y combinación de resultados. Para archivos relativamente pequeños, un script secuencial puede ser más rápido porque evita esos costos. MapReduce conviene cuando se procesan grandes volúmenes de datos, existen varios nodos disponibles y el trabajo puede dividirse en tareas paralelas que aprovechen los recursos distribuidos.

Diferencia entre CMD y ENTRYPOINT, y entre COPY y ADD.
CMD: establece el comando o los argumentos predeterminados que ejecutará el contenedor; puede reemplazarse al iniciar el contenedor.
 ENTRYPOINT: define el ejecutable principal del contenedor y normalmente se mantiene incluso cuando se proporcionan argumentos adicionales.
COPY: copia archivos o directorios desde el contexto de construcción hacia la imagen.
ADD: realiza funciones similares a COPY, pero también permite descargar recursos desde URL y extraer automáticamente archivos comprimidos locales compatibles.

## Reproducción del proyecto desde cero

### Requisitos
- Docker Desktop con WSL2.
- Python 3 instalado.
- Git.

### Instalación y ejecución

1. Clonar el repositorio.
2. Crear el archivo de configuración:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Editar `.env` y establecer una contraseña propia para PostgreSQL.
4. Generar el dataset:
   ```powershell
   python generar_dataset.py 125052348
   ```
5. Construir e iniciar los servicios:
   ```powershell
   docker compose up --build -d
   ```

El generador crea cinco millones de registros y utiliza la matrícula como semilla para obtener datos reproducibles. El archivo CSV y las credenciales no se incluyen en GitHub.

### Respuestas teóricas

**1. ¿Cuáles son los modos de ejecución de Hadoop?**

- Standalone: ejecuta Hadoop en una sola máquina y utiliza el sistema de archivos local. No requiere HDFS.
- Pseudo-distribuido: ejecuta los servicios de Hadoop como procesos independientes en una misma máquina y utiliza HDFS.
- Totalmente distribuido: utiliza varias máquinas para distribuir almacenamiento y procesamiento mediante HDFS y YARN.

Este proyecto utiliza el modo Standalone para ejecutar Hadoop Streaming dentro de un contenedor.

**2. ¿Cuál es la diferencia entre utilizar un volumen y COPY en Docker?**

COPY incorpora archivos dentro de la imagen durante su construcción. Un volumen permite almacenar y compartir datos fuera del ciclo de vida de los contenedores, conservando la información aunque estos se eliminen. Para este proyecto se utilizan volúmenes para persistir PostgreSQL y los resultados, mientras que el CSV se monta en modo de solo lectura.

**3. ¿Qué sucede al ejecutar docker compose down y docker compose down -v?**

`docker compose down` elimina los contenedores y la red, pero conserva los volúmenes nombrados. `docker compose down -v` también elimina los volúmenes, por lo que se pierde la información persistida en PostgreSQL.

**4. ¿Por qué MapReduce no siempre es más rápido que el procesamiento secuencial?**

MapReduce incorpora costos de inicialización, distribución de tareas, ordenamiento, transferencia de datos y reducción. En conjuntos pequeños o entornos de una sola máquina, estos costos pueden superar los beneficios del procesamiento paralelo. Su ventaja se observa principalmente con grandes volúmenes de información y múltiples nodos.

**5. ¿Cuál es la diferencia entre CMD y ENTRYPOINT, y entre COPY y ADD?**

- CMD define el comando o los argumentos predeterminados de un contenedor y puede ser reemplazado al ejecutarlo.
- ENTRYPOINT define el ejecutable principal del contenedor.
- COPY copia archivos y directorios locales hacia la imagen.
- ADD también permite funcionalidades adicionales, como extraer archivos comprimidos locales y utilizar ciertas fuentes remotas. Se recomienda COPY cuando solamente se necesita copiar archivos.

### Resultados de ejecución

- Registros procesados: 5,000,000.
- Grupos generados: 240.
- Registros inválidos: 0.
- Tiempo secuencial: 42.99 segundos.
- Tiempo MapReduce: 49.12 segundos.
- Coincidencia entre resultados: 100%.

Ambos métodos generaron exactamente los mismos 240 grupos y los mismos ingresos totales.
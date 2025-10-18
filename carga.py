"""
Procesos necesarios para la carga de dataset de pandas en Postgres (AWS)
"""

import os
from psycopg2 import OperationalError, ProgrammingError, connect
from psycopg2.extras import execute_values


def conexion():
    """
    Establece una conexión a la base de datos PostgreSQL usando las variables
    de entorno HOST, PORT, DATABASE, USER y PASSWORD.
    """
    try:
        conn = connect(
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD")
        )
        print("Conectado a postgres (AWS)")
        return conn
    except OperationalError as e:
        print("Error de conexión:", e)
    except ProgrammingError as e:
        print("Error de programación:", e)


def crear_schema(conn, archivo_sql):
    """
    Crea las tablas necesarias leyendo un archivo SQL línea por línea.
    """
    cur = conn.cursor()
    try:
        with open(archivo_sql, "r",  encoding="utf-8") as f:
            sql = f.read()

        # Divide por ';' y ejecuta cada comando
        for comando in sql.split(";"):
            comando = comando.strip()
            if comando:  # evita ejecutar líneas vacías
                cur.execute(comando)

        conn.commit()
        print("Schema creado en AWS")
    except OperationalError as e:
        print("Error de conexión:", e)
    except ProgrammingError as e:
        print("Error de programación:", e)
        conn.rollback()
    finally:
        cur.close()


def insertar(conn, df, tabla):
    """
    Funcion para isertar el dataframe de pandas en las tablas del schema ya creado
    """
    cur = conn.cursor()
    columnas = list(df.columns)
    valores = df.values.tolist()
    sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES %s"
    try:
        execute_values(cur, sql, valores)
        conn.commit()
        print(f"{len(df)} filas insertadas en {tabla}")
    except OperationalError as e:
        print("Error de conexión:", e)
    except ProgrammingError as e:
        print("Error de programación:", e)
        conn.rollback()
    finally:
        cur.close()


def cargar_AWS(products, purchases, purchase_products):
    """
    Funcion para cargar la base de datos en AWS (PostGres SQL)
    """
    conn_aws = conexion()
    ruta_actual = os.path.dirname(__file__)
    archivo_sql = os.path.join(ruta_actual, "schema", "schema.sql")
    crear_schema(conn_aws, archivo_sql=archivo_sql)
    # cargar datos
    insertar(conn_aws, products, "products")
    insertar(conn_aws, purchases, "purchases")
    insertar(conn_aws, purchase_products, "purchase_products")
    conn_aws.close()
    print("PostGres Cargado con la informacion")

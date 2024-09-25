from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
from datetime import datetime
import pathlib
import pyodbc
from os import listdir
import os

# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}_{inicio.month}_{inicio.year}_{inicio.hour}{inicio.minute}{inicio.second}'
file_log = f'logs_{inicio.day}_{inicio.month}_{inicio.year}'
log_path = fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Segmentacion_Hanna\Logs\{file_log}"

# ======================= Modificar aquí ==================================================
rutas = {
    "otras": r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fuentes_Segmentacion"
}

# ======================= Modificar aquí ==================================================
access_files = [
    'Grupo_familiar.accdb'
]

# ======================= Modificar aquí ==================================================
access_tables = [
    'TB_grupo_familiar'
]

# Diccionario vacío que se llena con el listado de tablas y campos de las tablas de access
table_columns = {}

# Nombre del controlador.
DRIVER_NAME = "{Microsoft Access Driver (*.mdb, *.accdb)}"

# Ciclo para recorrer los archivos de access que haya en cada ruta especificada
for ruta in rutas:
    print(ruta)
    print(listdir(rutas[ruta]))

    # Captura el nombre del archivo
    archivos = (listdir(rutas[ruta]))

    for file in archivos:
        # Ruta completa del archivo adquiriendo el valor de 'ruta'.
        DB_PATH = fr"{rutas[ruta]}\{file}"
        extension = pathlib.Path(rutas[ruta] + file).suffix
        if extension == '.accdb' and file in access_files:
            conn = pyodbc.connect("DRIVER=" + DRIVER_NAME + ";DBQ=" + DB_PATH)
            tablas = []

            # Creación de cursor para listar tablas en la BD Access
            crsr = conn.cursor()
            for table_info in crsr.tables(tableType='TABLE'):
                # Si la tabla está dentro de las tablas ingresadas en la variable with_tables
                if table_info.table_name in access_tables:
                    tablas.append(table_info.table_name)

            # Listar las columnas de una tabla. Elimina los espacios y convierte todo a Mayúsculas
            for table in tablas:
                cols = []
                columnas = crsr.columns(table=table)
                for row in columnas:
                    cols.append(row[3].replace(" ", "").upper())
                # Agrega al diccionario table_columns la clave (Nombre de la tabla) y el valor (las columnas)
                table_columns[f"{table}"] = cols

            # Creación del cursor para ejecutar consultas sql por medio de un ciclo que recorre las tablas seleccionadas
            for table in tablas:
                data = []
                # ================ Si es necesario, Modificar Query aquí =============================================
                Query = f"SELECT * FROM {table}"
                crsr.execute(Query)

                # Guarda los encabezados de las tablas en un arreglo
                headers = table_columns[table]

                # Ciclo para extraer los registros de las tablas en formato lista y guardarlos en el arreglo data
                for row in crsr.fetchall():
                    reg = [*row]
                    data.append(reg)
                df = pd.DataFrame(data, columns=headers)


## Credenciales SAP - Hana Database

db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')


## Conexión con la base de datos
cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

if cc:
    print("Success <3<3<3<3")

dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                pandas_df=df,
                                                schema='COLSUBSIDIO_IDN',
                                                table_name='TBL_GRUPO_FAMILIAR_SEGM',
                                                drop_exist_tab=False,
                                                force=True,
                                                append=False
                                               )
cc.close()

# Crea archivo Log
if os.path.exists(log_path):
    pass
else:
    os.mkdir(log_path)

with open(fr"{log_path}\log_{access_tables[0]}_{hora_archivo}.txt", "w") as file:
    file.write(f"Hola inicio: {inicio} \n")
    file.write(f'Archivo txt: {access_tables[0]} \n')
    file.write(f'Total registros: {df.shape[0]} \n')
    file.write(f'Muestra: \n {df.head(10)} \n')
    file.write(f'Hora fin: {datetime.now()}')
    file.close()

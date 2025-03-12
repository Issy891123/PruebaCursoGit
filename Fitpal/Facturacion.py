import unicodedata
from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
from datetime import datetime
import os


# ======================= Modificar aquí ==================================================
path = r"C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\Betterfly"
file_txt = "Facturacion_Usuarios activos"
path_file = path + '\\' + file_txt + ".xlsx"
table_name = 'TBL_BETTERFLY_PARA_FACTURACION'

# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}-{inicio.month}-{inicio.year}'
file_log = f'logs_{inicio.day}_{inicio.month}_{inicio.year}'
log_path = fr"C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\Betterfly\Logs\{file_log}"

# Encabezados del archivo
# Define una función para eliminar tildes y reemplazar espacios por "_"
def limpiar_nombre(nombre):
    nombre = nombre.upper()  # Convertir a mayúsculas
    nombre = nombre.replace(" ", "_")  # Reemplazar espacios por "_"
    nombre = ''.join((c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn'))  # Eliminar tildes
    return nombre


# Leer el archivo xlsx en dataframe de pandas
df = pd.read_excel(path_file, sheet_name='Export', dtype='object')
nombres_originales = df.columns.tolist()
# Genera los nuevos nombres de las columnas
nuevos_nombres = {nombre: limpiar_nombre(nombre) for nombre in nombres_originales}

# Renombra las columnas del DataFrame
df.rename(columns=nuevos_nombres, inplace=True)
df['FECHA_CARGUE'] = hora_archivo


# Validaciones
print(f'Archivo txt: {file_txt}')
print(f'Total registros: {df.count(axis=1)}')
print(df.head(10))


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
                                                table_name=table_name,
                                                drop_exist_tab=False,
                                                # force=True,
                                                append=True)
cc.close()

# Crea archivo Log
if os.path.exists(log_path):
    pass
else:
    os.mkdir(log_path)

with open(fr"{log_path}\log_{file_txt}_{hora_archivo}.txt", "w") as file:
    file.write(f"Hola inicio: {inicio} \n")
    file.write(f'Archivo txt: {file_txt} \n')
    file.write(f'Total registros: {df.shape[0]} \n')
    # file.write(f'Muestra: \n {df.head(10)} \n')
    file.write(f'Hora fin: {datetime.now()}')
    file.close()
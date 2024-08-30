from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
import os
import sys

from hdbcli import dbapi

from Validador import validar_csv
from datetime import datetime


def extraer_primeros_caracteres(cadena):
    return str(cadena)[:4999]

# ======================= Modificar aquí ==================================================
path = r"C:\Users\estegomhin\Downloads\CC_Bases"
file_txt = "CamCom_BasesConsolidadas"
path_file = path + '\\' + file_txt + ".csv"


# Leer el archivo txt en dataframe de pandas
df_final = pd.read_csv(path_file, sep=',', encoding="latin_1", low_memory=False)
df_final = df_final.drop(['Contiene Proponente'], axis=1)

# Iterar sobre las columnas del DataFrame
for columna in df_final.columns:
    # Verificar si el tipo de datos de la columna es 'object'
    if df_final[columna].dtype == 'object':
        # Aplicar la función solo a las columnas de tipo 'object'
        df_final[columna] = df_final[columna].apply(extraer_primeros_caracteres)


# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
#pd.set_option('display.max_rows', None)

# Validaciones
print(f'Archivo txt: {file_txt}')
print(f'Total registros: {df_final.shape[0]}')
print(df_final.head(10))



## Credenciales SAP - Hana Database

db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = "linamargal"
db_pwd = "Lina1595*"

# Conexión con la base de datos
cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

if cc:
    print("Success <3<3<3<3")

try:
    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                    pandas_df=df_final,
                                                    schema='COLSUBSIDIO_IDN',
                                                    table_name='TBL_CAM_COMERCIO_CONSOLIDADA',
                                                    drop_exist_tab=False,
                                                    # force=True)
                                                    append=True)
except dbapi.IntegrityError as e:
    print(e)
    pass



cc.close()

from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
import pyreadr
import os


# ======================= Modificar aquí ==================================================
path = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fuentes_Segmentacion"
file_txt = "Base_afiliados_acces"
path_file = path + '\\' + file_txt + ".rds"


# Leer el archivo txt en dataframe de pandas
dfr = pyreadr.read_r(path_file)
print(dfr.keys())
df = dfr[None]
# df = pd.DataFrame([dfr])

# Validaciones
print(f'Archivo txt: {file_txt}')
print(f'Total registros: {df.count(axis=0)}')
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
                                                table_name='TBL_BASEAFILIADOS_RDS_SEGM',
                                                drop_exist_tab=False,
                                                force=True,
                                                append=False)
cc.close()

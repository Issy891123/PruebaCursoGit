from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from datetime import datetime, timedelta
import sys
import pandas as pd

# Variables
tabla = 'V_SEGMENTACION'
tabla_insert = 'TBL_V_SEGMENTACION_HD'
hoy = datetime.now()
hoy1 = str(hoy.strftime('%Y-%m-%d'))

## Parámetros de conexión
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')
schema_name = "COLSUBSIDIO_IDN"

## Crear una conexión
cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")
if cc:
    print("Success <3<3<3<3")

# Query para validar si el día ya está cargado
query_val = str(f'''
SELECT MAX(TO_DATE(FECHA, 'YYYY-MM-DD')) AS FECHA_MAS_RECIENTE
FROM {schema_name}.{tabla_insert};
''')
val_fecha = cc.sql(query_val)
val_fecha = val_fecha.collect()
fecha_mas_reciente = str(val_fecha.iloc[0,0])

if hoy1 == fecha_mas_reciente:
    print(f'Ya se cargó información del día de hoy {hoy1}')
    sys.exit()

# Extracción de datos de la vista de hana para anexar a la tabla que contiene el histórico
query = f'select * from "{schema_name}"."{tabla}" '
df = cc.sql(query)
pandas_df = df.collect()
pandas_df['FECHA'] = hoy1
print(f'Insertará {pandas_df.shape[0]} filas')

dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                pandas_df=pandas_df,
                                                schema=schema_name,
                                                table_name=tabla_insert,
                                                drop_exist_tab=False,
                                                # force=True,
                                                append=True)
cc.close()

from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from datetime import datetime

inicio = datetime.now()
hora_archivo = f'{inicio.day}{inicio.month}{inicio.year}'

tabla1 = 'TBL_HISTORIAL_BETTERFLY_VAL'
tabla2 = 'TBL_HISTORIAL_BAJAS_BETTERFLY'
schema1 = 'COLSUBSIDIO_IDN'


db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")


query_cargues = f'''
    SELECT
        ID_EMP_FILIAL,TIPO_DOCUMENTO_AFILAIDO,NUMERO_DOCUMENTO_AFILIADO,PRIMER_APELLIDO,SEGUNDO_APELLIDO,NOMBRE_COMPLETO,FECHA_NACIMIENTO,GENERO,ID_PERSONA,RAZON_SOCIAL,RANGO_EDAD,CATEGORIA,SEGMENTO_POBLACIONAL,MES,ACTIVO
    FROM {schema1}.{tabla1}
'''

query_bajas = f'''
    SELECT *
    FROM {schema1}.{tabla2}
'''

# Exporta historial cargues
df = cc.sql(query_cargues)
df_cargues = df.collect()
df_cargues = df_cargues.astype(str)

df_cargues.to_excel(r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Cargue Masivo\Hostorial Solicitudes\BD_HistorialBetterfly.xlsx")

# Exporta historial bajas
df = cc.sql(query_bajas)
df_bajas = df.collect()
df_bajas = df_bajas.astype(str)

df_bajas.to_excel(r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Cargue Masivo\Hostorial Solicitudes\BD_HistorialBajasBetterfly.xlsx")


cc.close()


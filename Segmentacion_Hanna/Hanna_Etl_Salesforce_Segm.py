from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
from datetime import datetime
import os
import json

# ======================= Modificar aquí ==================================================
path = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fuentes_Segmentacion"
file_txt = "EmpSFCordAsesor"
path_file = path + '\\' + file_txt + ".csv"

# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}_{inicio.month}_{inicio.year}_{inicio.hour}{inicio.minute}{inicio.second}'
file_log = f'logs_{inicio.day}_{inicio.month}_{inicio.year}'
log_path = fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Segmentacion_Hanna\Logs\{file_log}"

# Encabezados del archivo
headers = ['Tipo de Identificacion', 'Numero de Identificacion', 'Identificador Unico Empresas',
           'Propietario de la cuenta', 'Jefe Inmediato', 'Ultima Carta de Riesgo Recibida',
           'Fecha Radicacion Ultima Carta', 'Cluster Empresarial Grupo', 'Cluster Individual',
           'Estado de Afiliacion', 'Fecha de Afiliacion', 'Tipo de registro de cuenta', 'Codigo CIIU',
           'Sector Economico Comercial'
           ]

# Leer el archivo txt en dataframe de pandas
df = pd.read_csv(path_file, sep=';', header=None, names=headers, dtype="object", encoding="latin_1", low_memory=False)

# Validaciones
print(f'Archivo txt: {file_txt}')
print(f'Total registros: {df.count(axis=1)}')
print(df.head(10))

## Credenciales SAP - Hana Database
loginInfo = json.load(open(r'C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\PycharmProjects\Segmentacion_Hanna\login-prd.json'))
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = loginInfo['DB_USER']
db_pwd = loginInfo['DB_PASSWORD']

## Conexión con la base de datos
cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

if cc:
    print("Success <3<3<3<3")

dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                pandas_df=df,
                                                schema='COLSUBSIDIO_IDN',
                                                table_name='TBL_EMPSFCORDASESOR_SEGM',
                                                drop_exist_tab=False,
                                                force=True,
                                                append=False)
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
    file.write(f'Muestra: \n {df.head(10)} \n')
    file.write(f'Hora fin: {datetime.now()}')
    file.close()

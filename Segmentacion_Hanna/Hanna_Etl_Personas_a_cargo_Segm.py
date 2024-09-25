from hana_ml.dataframe import ConnectionContext, create_dataframe_from_pandas
import pandas as pd
import hana_ml.dataframe as dataframe
from datetime import datetime
import os
import json
import sys
from Validador import validar_csv

# ======================= Modificar aquí ==================================================
path = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fuentes_Segmentacion"
file_txt = "PAC"
path_file = path + '\\' + file_txt + ".txt"

# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}_{inicio.month}_{inicio.year}_{inicio.hour}{inicio.minute}{inicio.second}'
file_log = f'logs_{inicio.day}_{inicio.month}_{inicio.year}'
log_path = fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Segmentacion_Hanna\Logs\{file_log}"

# Crea carpeta del día para los archivos log
if os.path.exists(log_path):
    pass
else:
    os.mkdir(log_path)

# Encabezados del archivo
headers = ["TIP_IDENTIFICACION", "NUM_IDENTIFICACION_EMPRESA", "TIP_IDENTIFICACION_AFILIADO",
           "NUM_IDENTIFICACION_AFILIADO", "TIP_IDENTIFICACION_PERSONA_A_CARGO", "NUM_IDENTIFICACION_PERSONA_A_CARGO",
           "PRI_NOMBRE_PERSONA_A_CARGO", "SEG_NOMBRE_PERSONA_A_CARGO",
           "PRI_APELLIDO_PERSONA_A_CARGO", "SEG_APELLIDO_PERSONA_A_CARGO", "FEC_NACIMIENTO_PERSONA_A_CARGO",
           "GEN_PERSONA_A_CARGO", "PAR_PERSONA_A_CARGO", "DISC_PERSONA_A_CARGO", "TIP_CUOTA_MONETARIA_PERSONA_A_CARGO",
           "VAL_CUOTA_MONETARIA_PERSONA_A_CARGO", "NUM_CUOTAS_PAGADAS", "NUM_PERIODOS_PAGADAS", "INDEFINIDA"
           ]

# Se pasa el archivo por la función para validar el número de columnas y el delimitador
info_csv = validar_csv(path_file)
if info_csv['num_columnas'] > 1 and info_csv['num_columnas'] != len(headers) - 1:
    print(f"El archivo CSV no coincide con la estructura definida, tiene {info_csv['num_columnas']} y debería tener {len(headers)} columnas. Está delimitado por: '{info_csv['delimitador']}'")
    with open(fr"{log_path}\Error_log_{file_txt}_{hora_archivo}.txt", "w") as file:
        file.write(f"El archivo CSV no coincide con la estructura definida, tiene {info_csv['num_columnas']} y debería tener {len(headers)} columnas. Está delimitado por: '{info_csv['delimitador']}' \n")
        file.close
        sys.exit()
elif info_csv['delimitador'] != '\t':
    print(f"El archivo CSV no está delimitado por ';', tiene {info_csv['num_columnas']} columnas y el delimitador es: '{info_csv['delimitador']}'")
    with open(fr"{log_path}\Error_log_{file_txt}_{hora_archivo}.txt", "w") as file:
        file.write(f"El archivo CSV no está delimitado por ';', tiene {info_csv['num_columnas']} columnas y el delimitador es: '{info_csv['delimitador']}'\n")
        file.close
        sys.exit()
elif info_csv['num_columnas'] > 1 and info_csv['num_columnas'] == len(headers) - 1 and info_csv['delimitador'] == '\t':
    print("El archivo coincide con la estructura definida")
else:
    print("No se pudo determinar el delimitador o el archivo tiene menos de 2 columnas.")
    with open(fr"{log_path}\Error_log_{file_txt}_{hora_archivo}.txt", "w") as file:
        file.write(f"No se pudo determinar el delimitador o el archivo tiene menos de 2 columnas. \nHora: {inicio} \n")
        file.close
        sys.exit()


# Leer el archivo txt en dataframe de pandas
df = pd.read_csv(path_file, sep='\t', header=None, names=headers, dtype="object", encoding="latin_1", low_memory=False)
df = df.drop(['INDEFINIDA'], axis=1)

# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

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
                                                table_name='TBL_PERSONAS_A_CARGO_SEGM',
                                                drop_exist_tab=False,
                                                force=True,
                                                append=False)
cc.close()

# Crea archivo Log
with open(fr"{log_path}\log_{file_txt}_{hora_archivo}.txt", "w") as file:
    file.write(f"Hola inicio: {inicio} \n")
    file.write(f'Archivo txt: {file_txt} \n')
    file.write(f'Total registros: {df.shape[0]} \n')
    file.write(f'Muestra: \n {df.head(10)} \n')
    file.write(f'Hora fin: {datetime.now()}')
    file.close()

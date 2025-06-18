import openpyxl
import os
import re
import pandas as pd
import paramiko
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from hdbcli import dbapi
from datetime import datetime

inicio = datetime.now()
hora_archivo = inicio.strftime('%d%m%Y')


def extract_digits_dv(id_empresa):
    # Eliminar todos los caracteres que no son números
    digits_only = re.sub(r'[^0-9]', '', id_empresa)
    # Tomar los primeros 10 caracteres
    return digits_only[:10]


# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

# Diccionario para tener el nombre de los meses
meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
         9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

tabla1 = 'T_IDN_TR_FITPAL_CARGUES'
tabla2 = 'CV_PERFIL_PERSONA_FULL'
tabla3 = 'T_IDN_TR_ALTAS_BAJAS_FITPAL'

schema1 = 'COLSUBSIDIO_APG'
schema2 = 'COLSUBSIDIO_DA'
nitdv = None

# Sftp Config
sftp_host = '192.168.100.207'
sftp_port = 22
sftp_username = os.environ.get('SFTP_USER')
sftp_password = os.environ.get('SFTP_PASS')
sftp_remote_path = '/sftp/FITPAL/Altas_y_bajas/2025'

total_altas = 0
empresas_con_altas = 0
nits_procesados = []

path_altas = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fitpal\AltasYBajas"
new_path_altas = fr'{path_altas}\Altas y bajas_{hora_archivo}'
name_file = fr'{new_path_altas}\{meses[inicio.month]}_{inicio.year}_Cargas y bajas_{hora_archivo}.csv'
path_logs = r"C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\PycharmProjects\Fitpal\Logs"
print(new_path_altas)

try:
    os.mkdir(fr'{new_path_altas}')
    print("Directorio creado exitosamente.")
except:
    print("Directorio ya está creado")

db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

with open(fr"{path_logs}\Logs_altas_{hora_archivo}_{inicio.hour}_{inicio.minute}_{inicio.second}.csv", "w") as file:
    file.write(f"{inicio} \n")
    file.write("Nit; RazonSocial; altas\n")
    file.close()

query_list_emp = f'''
    SELECT DISTINCT ID_EMPRESA FROM {schema1}.{tabla1}
'''

list_emp = cc.sql(query_list_emp)
list_emp = list_emp.collect()
list_emp = list_emp["ID_EMPRESA"].tolist()
list_emp_sql = ",".join(f"'{item}'" for item in list_emp)
print(list_emp)
print(list_emp_sql)

## ==== Query altas ============
query_altas = f'''
    SELECT -- Query para bajas
        FC.NOMBRE,
        FC.APELLIDO,
        FC.TIPO_IDENTIFICACION_AFILIADO,
        FC.NUM_IDENTIFICACION_AFILIADO,
        FC.ID_EMPRESA,
        FC.ID_PADRE,
        'NA' AS AREA,
        'BAJAS' AS ORIGEN,
        PP.ESTADO_AFILIACION,
        PP.FECHA_RETIRO
    FROM COLSUBSIDIO_APG.T_IDN_TR_FITPAL_CARGUES FC
    LEFT JOIN {schema2}.{tabla2} PP
        ON FC.TIPO_IDENTIFICACION_AFILIADO || FC.NUM_IDENTIFICACION_AFILIADO || FC.ID_EMPRESA = 
            PP.TIPO_IDENTIFICACION_AFILIADO || TO_VARCHAR(PP.NUM_IDENTIFICACION_AFILIADO) || PP.ID_EMPRESA
    WHERE PP.ID_EMPRESA IN ({list_emp_sql})
        AND PP.ESTADO_AFILIACION = 'Retirada(o)'
        
UNION ALL
    SELECT -- Query para altas
        PP.PRIMER_NOMBRE || ' ' || PP.SEGUNDO_NOMBRE AS NOMBRE,
        PP.PRIMER_APELLIDO || ' ' || PP.SEGUNDO_APELLIDO AS APELLIDO,
        PP.TIPO_IDENTIFICACION_AFILIADO,
        PP.NUM_IDENTIFICACION_AFILIADO,	    
        PP.ID_EMPRESA,
        EU.ID_PADRE,
        'NA' AS AREA,
        'ALTAS' AS ORIGEN,
        PP.ESTADO_AFILIACION,
        PP.FECHA_AFILIACION	    
    FROM {schema2}.{tabla2} PP
    LEFT JOIN {schema1}.{tabla1} FC
        ON TO_VARCHAR(PP.NUM_IDENTIFICACION_AFILIADO) = FC.NUM_IDENTIFICACION_AFILIADO 
    LEFT JOIN 
		(SELECT DISTINCT FC.ID_EMPRESA,
			FC.ID_PADRE				
		FROM COLSUBSIDIO_APG.T_IDN_TR_FITPAL_CARGUES FC			
		) EU
		ON EU.ID_EMPRESA = PP.ID_EMPRESA	    
    WHERE PP.ID_EMPRESA IN ({list_emp_sql})
        AND PP.ESTADO_AFILIACION = 'Afiliada(o)'	    
        AND FC.NUM_IDENTIFICACION_AFILIADO IS NULL
    '''

# Para exportar altas
print(query_altas)
# Ejecutar el query y convertir a un dataframe de pandas
df = cc.sql(query_altas)
df_result = df.collect()
df_result = pd.DataFrame(df_result)
print(df_result.head(10))
df_csv = df_result.iloc[:, :-2]  # Elimina las últimas dos columnas
df_csv['ID_EMPRESA'] = df_csv['ID_EMPRESA'].apply(extract_digits_dv)
# Calcular el conteo para "ALTAS" y "BAJAS"
count_altas = df_result[df_result['ORIGEN'] == 'ALTAS'].shape[0]
count_bajas = df_result[df_result['ORIGEN'] == 'BAJAS'].shape[0]
total_registros = count_bajas + count_altas

if total_registros > 0:
    df_csv.to_csv(rf"{name_file}", index=False, header=False, sep=";")
    print(df_csv.head(10))
    empresas_con_altas += 1

# Conectar al servidor SFTP y subir el archivo
try:
    # Crear cliente SSH
    transport = paramiko.Transport((sftp_host, sftp_port))
    transport.connect(username=sftp_username, password=sftp_password)

    # Crear cliente SFTP
    sftp = paramiko.SFTPClient.from_transport(transport)
    # Obtener solo el nombre del archivo
    file_name = os.path.basename(name_file)
    # Subir el archivo CSV al SFTP
    remote_file_path = f"{sftp_remote_path}/{file_name}"
    sftp.put(name_file, remote_file_path)

    # Verificar si el archivo se subió
    archivos_remotos = sftp.listdir(sftp_remote_path)
    print(f"Archivos en el SFTP después de la subida: {archivos_remotos}")

    # Cerrar conexión
    sftp.close()
    transport.close()

except Exception as e:
    print(f"Error al subir el archivo al SFTP: {str(e)}")

# Segmento de código para insertar a la tabla de cargues las altas que salieron
query_insert_altas = f'''
SELECT -- Query para altas
    PP.PRIMER_NOMBRE || ' ' || PP.SEGUNDO_NOMBRE AS NOMBRE,
    PP.PRIMER_APELLIDO || ' ' || PP.SEGUNDO_APELLIDO AS APELLIDO,
    PP.TIPO_IDENTIFICACION_AFILIADO,
    PP.NUM_IDENTIFICACION_AFILIADO,
    'NA' AS AREA,  
    PP.ID_EMPRESA,
    CURRENT_TIMESTAMP AS FECHA_CARGUE,
    'ALTAS' AS ORIGEN,
    EU.ID_PADRE                           
FROM {schema2}.{tabla2} PP
LEFT JOIN {schema1}.{tabla1} FC
    ON TO_VARCHAR(PP.NUM_IDENTIFICACION_AFILIADO) = FC.NUM_IDENTIFICACION_AFILIADO
LEFT JOIN 
		(
		SELECT DISTINCT FC.ID_EMPRESA,
			FC.ID_PADRE				
		FROM COLSUBSIDIO_APG.T_IDN_TR_FITPAL_CARGUES FC			
		) EU
	ON EU.ID_EMPRESA = PP.ID_EMPRESA
WHERE PP.ID_EMPRESA IN ({list_emp_sql})
    AND PP.ESTADO_AFILIACION = 'Afiliada(o)'	    
    AND FC.NUM_IDENTIFICACION_AFILIADO IS NULL
'''

df_query_altas = cc.sql(query_insert_altas)
df_insert = df_query_altas.collect()
df_insert = pd.DataFrame(df_insert)

try:
    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                    pandas_df=df_insert,
                                                    schema=schema1,
                                                    table_name=tabla1,
                                                    drop_exist_tab=False,
                                                    # force=True,
                                                    append=True)
except dbapi.IntegrityError as e:
    print(e)
    pass

print(f"Datos de ALTAS insertados correctamente en la tabla {schema1}.{tabla1}.")

# Segmento de código para insertar a la tabla de historial de altas y bajas
df_result = df_result.drop(columns=['ID_PADRE'])
df_result['FECHA_CARGUE'] = str(inicio)
try:
    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                    pandas_df=df_result,
                                                    schema=schema1,
                                                    table_name=tabla3,
                                                    drop_exist_tab=False,
                                                    # force=True,
                                                    append=True)
except dbapi.IntegrityError as e:
    print(e)
    pass

print(f"Total altas: {count_altas}\n")
print(f"Total bajas: {count_bajas}\n")
print(f"Total empresas: {len(list_emp)} \n")

with open(fr"{path_logs}\Logs_altas_{hora_archivo}_{inicio.hour}_{inicio.minute}_{inicio.second}.csv", "a") as file:
    file.write(f"Total altas: {count_altas}\n")
    file.write(f"Total bajas: {count_bajas}\n")
    file.write(f"Total empresas: {len(list_emp)} \n")
    file.write(f"Finalizó {datetime.now()} \n")
    file.close()

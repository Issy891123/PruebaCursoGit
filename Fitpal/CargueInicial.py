import openpyxl
import os
import re
from hdbcli import dbapi
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from datetime import datetime
import pandas as pd
import paramiko

# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
#pd.set_option('display.max_rows', None)

inicio = datetime.now()
hora_archivo = inicio.strftime('%d%m%Y')

def extract_digits(id_empresa):
    # Eliminar todos los caracteres que no son números
    digits_only = re.sub(r'[^0-9]', '', id_empresa)
    # Tomar los primeros 9 caracteres
    return digits_only[:9]

def extract_digits_dv(id_empresa):
    # Eliminar todos los caracteres que no son números
    digits_only = re.sub(r'[^0-9]', '', id_empresa)
    # Tomar los primeros 10 caracteres
    return digits_only[:10]

tabla1 = 'CV_PERFIL_PERSONA_FULL'
tablains = 'T_IDN_TR_FITPAL_CARGUES'
# tabla3 = 'V_GRC_ALL_USERS'

schema1 = 'COLSUBSIDIO_DA'
schemains = 'COLSUBSIDIO_APG'

# Sftp Config
sftp_host = '192.168.100.207'
sftp_port = 22
sftp_username = os.environ.get('SFTP_USER')
sftp_password = os.environ.get('SFTP_PASS')
sftp_remote_path = '/sftp/FITPAL/cargue_inicial/2025'

total_registros = 0
cant_registros_sin = 0
con_reg = 0
sin_reg = 0
empresas_sin = []

path_cargues = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fitpal\SolicitudCargues"
path_solicitud = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Fitpal"
file = "Fitpal_SolicitudCargue"
path_file = path_solicitud + '\\' + file + ".xlsx"
new_path = os.path.join(path_cargues, f"Cargue_{hora_archivo}")
path_logs = r"C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\PycharmProjects\Fitpal\Logs"
print(new_path)

try:
    os.mkdir(new_path)
    print("Directorio creado exitosamente.")
except FileExistsError:
    print("El directorio ya está creado.")


book = openpyxl.load_workbook(path_file, data_only=True)
hoja = book.active
celdas = hoja['A2':'D100000']

db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

with open(fr"{path_logs}\Logs_{hora_archivo}_{inicio.hour}_{inicio.minute}_{inicio.second}.csv", "w") as file:
    file.write(f"{inicio} \n")
    file.write("Nit; RazonSocial; Cantidad; sin_nombres; total_enviados \n")
    file.close()

for fila in celdas:
    nit = None
    nitdv = None
    razon_social = None
    id_padre = None
    for celda in fila:
        if celda.value is not None:
            print(f'{fila} ---->> {celda.column_letter}')
            if celda.column_letter == 'A':
                nit = extract_digits(celda.value)
                nitdv = extract_digits_dv(celda.value)
            elif celda.column_letter == 'B':
                razon_social = celda.value
            elif celda.column_letter == 'D':
                id_padre = celda.value
                print(f'Nit: {nit} -------> Razon Social: {razon_social} ID_PADRE ==> {id_padre}')
                query_todo = f'''
                    SELECT PRIMER_NOMBRE || ' ' || SEGUNDO_NOMBRE AS NOMBRE,
                        PRIMER_APELLIDO || ' ' || SEGUNDO_APELLIDO AS APELLIDO,
                        TIPO_IDENTIFICACION_AFILIADO,
                        NUM_IDENTIFICACION_AFILIADO,
                        'NA' AS AREA,
                        ID_EMPRESA
                    FROM {schema1}.{tabla1}
                    WHERE SUBSTRING(REPLACE_REGEXPR('[^0-9]' IN ID_EMPRESA WITH ''), 1, 9) = '{nit}'
                        AND ESTADO_AFILIACION = 'Afiliada(o)'
                '''


                ini_rows = cc.sql(query_todo).count()
                print(query_todo)
                df = cc.sql(query_todo)
                pandas_df = df.collect()
                total_registros += ini_rows
                print(f'Cantidad registros archivo {nit} {razon_social}: {pandas_df.shape[0]} \nTotal Registros: {total_registros}')

                if ini_rows == 0:
                    sin_reg += 1
                    empresas_sin.append(f'{razon_social}')
                else:
                    # Ruta local del archivo CSV para el sftp
                    # if inicio.day < 10:
                        # remote_file_name = f"{id_padre}_{razon_social}_0{hora_archivo[:7]}.csv"
                    # else:
                    remote_file_name = f"{id_padre}_{razon_social}_{hora_archivo[:8]}.csv"

                    local_file_path = rf"{new_path}\{remote_file_name}"
                    con_reg += 1
                    df = pandas_df.iloc[:, :-1]
                    df['ID_EMPRESA'] = nitdv
                    df.to_csv(rf"{local_file_path}", index=False, sep=";", header=False)
                    print(pandas_df.head(10))

                    #Validar que ya ecista el archivo
                    if os.path.exists(local_file_path):
                        print(f"El archivo local {local_file_path} existe.")
                    else:
                        print(f"El archivo local {local_file_path} NO existe.")

                    # Conectar al servidor SFTP y subir el archivo
                    try:
                        # Crear cliente SSH
                        transport = paramiko.Transport((sftp_host, sftp_port))
                        transport.connect(username=sftp_username, password=sftp_password)

                        # Crear cliente SFTP
                        sftp = paramiko.SFTPClient.from_transport(transport)

                        # Subir el archivo CSV al SFTP
                        remote_file_path = f"{sftp_remote_path}/{remote_file_name}"
                        sftp.put(local_file_path, remote_file_path)

                        # Verificar si el archivo se subió
                        archivos_remotos = sftp.listdir(sftp_remote_path)
                        print(f"Archivos en el SFTP después de la subida: {archivos_remotos}")

                        # Cerrar conexión
                        sftp.close()
                        transport.close()

                    except Exception as e:
                        print(f"Error al subir el archivo al SFTP: {str(e)}")

                print(f"Empresas con registros: {con_reg} \nEmpresas sin registros: {sin_reg}")
                pandas_df = pandas_df.astype(str)
                print(df.dtypes)

                with open(fr"{path_logs}\Logs_{hora_archivo}_{inicio.hour}_{inicio.minute}_{inicio.second}.csv", "a") as file:
                    file.write(f'{nit}; {razon_social}; {ini_rows}\n')

                pandas_df['FECHA_CARGUE'] = str(inicio)
                pandas_df['ORIGEN'] = 'CARGUES'
                pandas_df['ID_PADRE'] = f'{id_padre}'
                try:
                    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                                    pandas_df=pandas_df,
                                                                    schema=schemains,
                                                                    table_name=tablains,
                                                                    drop_exist_tab=False,
                                                                    # force=True,
                                                                    append=True)
                except dbapi.IntegrityError as e:
                    print(e)
                    continue
        else:
            break

print(empresas_sin)
with open(fr"{path_logs}\Logs_{hora_archivo}_{inicio.hour}_{inicio.minute}_{inicio.second}.csv", "a") as file:
    file.write(f"Empresas con registros: {con_reg} \nEmpresas sin registros: {sin_reg} \n")
    file.write(f"Total registros: {total_registros} \n")
    file.write(f"Finalizó {datetime.now()} \n")

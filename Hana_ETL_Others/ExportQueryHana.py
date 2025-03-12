import openpyxl
import os
import pandas as pd
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from hdbcli import dbapi
from datetime import datetime
import subprocess

inicio = datetime.now()
hora_archivo = inicio.strftime('%Y-%m-%d_%H-%M-%S')  # Formato: YYYY-MM-DD_HH-MM-SS

tabla4 = 'TBL_HISTORIAL_BETTERFLY_VAL'
tabla5 = 'TBL_HISTORIAL_BAJAS_BETTERFLY'

schema1 = 'COLSUBSIDIO_IDN'
total_bajas = 0
empresas_con_bajas = 0

path_bajas = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Bajas"
new_path_bajas = fr'{path_bajas}\Bajas_{hora_archivo}'

try:
    os.mkdir(fr'{new_path_bajas}')
except:
    print("Directorio ya está creado")


headers = ['NIT empresa empleadora', 'Tipo de documento de identidad CC CE PPT',
           'Número de identificación   Ciudadania CC o de Extranjería CE, debe ingresarse así: 8 a 10 Digitos (XXXXXXXXXX).',
           'Primer apellido                     máximo 30 caracteres',
           'Segundo apellido                 máximo 30 caracteres           ',
           'Nombre                 máximo 30 caracteres           ',
           'Email                                                        máximo 30 caracteres ej: mail@mail.com           ',
           'Fecha de nacimiento              fecha en formato: dd-mm-aaaa           ',
           'Género                                       ingresar F, M u O           ',
           'Celular                                       Opcional          ',
           'FECHA_REPORTADO'
           ]



db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_bajas_{hora_archivo}.csv", "w") as file:
    file.write(f"{inicio} \n")
    file.write("Nit; RazonSocial; bajas \n")
    file.close()

query_list_emp = f'''
    SELECT DISTINCT ID_EMP_FILIAL, RAZON_SOCIAL FROM {schema1}.{tabla4}
'''

list_emp = cc.sql(query_list_emp)
list_emp = list_emp.collect()
list_emp = list_emp[["ID_EMP_FILIAL", "RAZON_SOCIAL"]].to_dict(orient='records')

# Convertir la lista de diccionarios a un DataFrame
df = pd.DataFrame(list_emp)

# Establecer la columna 'ID_EMP_FILIAL' como índice y convertir a un solo diccionario
list_emp = df.set_index('ID_EMP_FILIAL')['RAZON_SOCIAL'].to_dict()
print(list_emp)

for clave in list_emp:
    print(clave)
    print(list_emp[clave])

    print(f'Nit: {clave} -------> Razon Social: {list_emp[clave]}')
    query_bajas = f'''
        SELECT 
            --HB.ACTIVO, 
            --HBB.FECHA_REPORTADO,
            --HB.MES,
            HB.ID_EMP_FILIAL, HB.TIPO_DOCUMENTO_AFILAIDO, HB.NUMERO_DOCUMENTO_AFILIADO,
            HB.PRIMER_APELLIDO, HB.SEGUNDO_APELLIDO, HB.NOMBRE_COMPLETO, HB.CORREO_ELECTRONICO_1,
            HB.FECHA_NACIMIENTO, HB.GENERO,TELEFONO_CELULAR_1     
        FROM {schema1}.{tabla4} HB
        LEFT JOIN {schema1}.{tabla5} hbb 
            ON HB.ID_EMP_FILIAL = HBB.ID_EMP_FILIAL 
            AND HB.NUMERO_DOCUMENTO_AFILIADO = HBB.NUMERO_DOCUMENTO_AFILIADO 
        WHERE HB.ACTIVO = 0
            AND HB.ID_EMP_FILIAL = '{clave}'
            AND HBB.FECHA_REPORTADO IS NULL
    '''


    # Para exportar las bajas
    cant_bajas = cc.sql(query_bajas).count()
    print(query_bajas)
    df_bajas = cc.sql(query_bajas)
    df_bajas = df_bajas.collect()
    total_bajas += cant_bajas

    # Inserta hora de ejecución al df para que quede la fecha de reporte
    df_bajas['FECHA_REPORTADO'] = pd.Timestamp.now()

    #Borra campos que no van en el historial de bajas
    columnas_a_eliminar = ['CORREO_ELECTRONICO_1', 'TELEFONO_CELULAR_1']
    df_bajas_hana = df_bajas.drop(columns=columnas_a_eliminar)

    # Inserta los datos en el historial de bajas
    try:
        dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                        pandas_df=df_bajas_hana,
                                                        schema=schema1,
                                                        table_name=tabla5,
                                                        drop_exist_tab=False,
                                                        # force=True,
                                                        append=True)
    except dbapi.IntegrityError as e:
        print(e)
        continue


    print(f'Cantidad registros archivo {clave} {list_emp[clave]}: Bajas = {cant_bajas}')

    if cant_bajas > 0:
        df_bajas.to_excel(rf"{new_path_bajas}\{list_emp[clave]}_{clave}_{hora_archivo}.xlsx", index=False, header=headers)
        print(df_bajas.head(10))
        empresas_con_bajas += 1

    with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_bajas_{hora_archivo}.csv", "a") as file:
        file.write(f'{clave}; {list_emp[clave]}; {cant_bajas}\n')
        file.close()


with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_bajas_{hora_archivo}.csv", "a") as file:
    file.write(f"Total bajas: {total_bajas} \n")
    file.write(f"Total empresas: {empresas_con_bajas} \n")
    file.write(f"Finalizó {datetime.now()} \n")
    file.close()

# Cuando finaliza el script de bajas, ejecuta el script de altas

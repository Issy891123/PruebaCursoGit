import openpyxl
import os
import pandas as pd
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from hdbcli import dbapi
from datetime import datetime

inicio = datetime.now()
hora_archivo = inicio.strftime('%Y-%m-%d_%H-%M-%S')  # Formato: YYYY-MM-DD_HH-MM-SS

tabla1 = 'V_CONSOLIDACION_SEGM'
tabla2 = 'V_LIST_EMPRESAS_SEGM'
# tabla3 = 'V_GRC_ALL_USERS'
tabla4 = 'TBL_HISTORIAL_BETTERFLY_VAL'

schema1 = 'COLSUBSIDIO_IDN'
schema2 = 'COLSUBSIDIO_GRC'
total_altas = 0

empresas_con_altas = 0
nits_procesados = []

path_altas = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Altas"
new_path_altas = fr'{path_altas}\Altas_{hora_archivo}'

try:
    os.mkdir(fr'{new_path_altas}')
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
           'Celular                                       Opcional          '
           ]



db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_altas_{hora_archivo}.csv", "w") as file:
    file.write(f"{inicio} \n")
    file.write("Nit; RazonSocial; altas\n")
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


flag = False
while not flag:
    try:
        for clave in list_emp:
            print(clave)
            print(list_emp[clave])

            if clave in nits_procesados:
                pass
            else:
                ## ==== Query altas ============
                query_altas = f'''
                    WITH CTE AS (
                    SELECT LE.ID_EMP_FILIAL, AF.TIPO_DOCUMENTO_AFILIADO, AF.NUMERO_DOCUMENTO_AFILIADO,
                        AF.PRIMER_APELLIDO, AF.SEGUNDO_APELLIDO, 
                        AF.PRIMER_NOMBRE || ' ' || CASE WHEN AF.SEGUNDO_NOMBRE IS NULL THEN ' ' ELSE AF.SEGUNDO_NOMBRE END AS NOMBRE_COMPLETO, 
                        'DC.EMAIL' AS CORREO_ELECTRONICO_1, 
                        SUBSTRING(AF.FECHA_NACIMIENTO,9,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,6,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,1,4) AS FECHA_NACIMIENTO,
                        AF.GENERO,
                        'DC.CELL_PHONE' AS TELEFONO_CELULAR_1
                    FROM {schema1}.{tabla1} AF
                    LEFT JOIN {schema1}.{tabla2} AS LE
                        ON AF.NUMERO_ID_EMPRESA_SD = LE.NIT_SIN_DIGITO_FILIAL                    
                    WHERE LE.ID_EMP_FILIAL = '{clave}'              
                    ORDER BY 'DC.EMAIL' DESC
                )
                SELECT DISTINCT CTE.* --, HB.RAZON_SOCIAL 
                FROM CTE
                LEFT JOIN {schema1}.{tabla4} HB
                    ON CTE.ID_EMP_FILIAL = HB.ID_EMP_FILIAL 
                    AND HB.NUMERO_DOCUMENTO_AFILIADO = CTE.NUMERO_DOCUMENTO_AFILIADO
                WHERE HB.RAZON_SOCIAL IS NULL OR HB.RAZON_SOCIAL = ''
                    AND CTE.NOMBRE_COMPLETO IS NOT NULL
                    '''


                # Para exportar altas
                print(query_altas)
                cant_altas = cc.sql(query_altas).count()
                print(cant_altas)
                df_altas = cc.sql(query_altas)
                df_altas = df_altas.collect()
                total_altas += cant_altas

                print(f'Cantidad registros archivo {clave} {list_emp[clave]}: Altas =: {cant_altas}')


                if cant_altas > 0:
                    df_altas.to_excel(rf"{new_path_altas}\{list_emp[clave]}_{clave}_{hora_archivo}.xlsx", index=False, header=headers)
                    print(df_altas.head(10))
                    empresas_con_altas += 1

                    # Query para subir a la tabla de hana las altas que salieron y que se enviaron
                    query_up_hist = f'''
                            WITH ALTASYBAJAS AS (
                                WITH CTE AS (
                                    SELECT LE.ID_EMP_FILIAL, AF.TIPO_DOCUMENTO_AFILIADO, AF.NUMERO_DOCUMENTO_AFILIADO,
                                        AF.PRIMER_APELLIDO, AF.SEGUNDO_APELLIDO, 
                                        AF.PRIMER_NOMBRE || ' ' || CASE WHEN AF.SEGUNDO_NOMBRE IS NULL THEN ' ' ELSE AF.SEGUNDO_NOMBRE END AS NOMBRE_COMPLETO, 
                                        'DC.EMAIL' AS CORREO_ELECTRONICO_1, 
                                        SUBSTRING(AF.FECHA_NACIMIENTO,9,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,6,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,1,4) AS FECHA_NACIMIENTO,
                                        AF.GENERO,
                                        'DC.CELL_PHONE' AS TELEFONO_CELULAR_1
                                    FROM {schema1}.{tabla1} AF
                                    LEFT JOIN {schema1}.{tabla2} AS LE
                                        ON AF.NUMERO_ID_EMPRESA_SD = LE.NIT_SIN_DIGITO_FILIAL                                    
                                    WHERE LE.ID_EMP_FILIAL = '{clave}'                             
                                )
                                SELECT DISTINCT CTE.* --, HB.RAZON_SOCIAL 
                                FROM CTE
                                LEFT JOIN {schema1}.{tabla4} HB
                                    ON CTE.ID_EMP_FILIAL = HB.ID_EMP_FILIAL 
                                    AND HB.NUMERO_DOCUMENTO_AFILIADO = CTE.NUMERO_DOCUMENTO_AFILIADO
                                WHERE HB.RAZON_SOCIAL IS NULL OR HB.RAZON_SOCIAL = ''
                                    AND CTE.NOMBRE_COMPLETO IS NOT NULL
                            )
                            SELECT 
                                AB.*, 
                                CS.ID_PERSONA, CS.RAZON_SOCIAL, CS.RANGO_EDAD, CS.CATEGORIA, CS.SEGMENTO_POBLACIONAL, CURRENT_TIMESTAMP AS MES, 1 AS ACTIVO
                            FROM ALTASYBAJAS AS AB
                            LEFT JOIN {schema1}.{tabla1} CS	 
                                ON AB.NUMERO_DOCUMENTO_AFILIADO = CS.NUMERO_DOCUMENTO_AFILIADO
                                AND AB.ID_EMP_FILIAL = CS.ID_EMPRESA        
                        '''
                    df_hist = cc.sql(query_up_hist)
                    df_hist = df_hist.collect()
                    df_hist = df_hist.astype(str)

                    try:
                        dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                                        pandas_df=df_hist,
                                                                        schema=schema1,
                                                                        table_name=tabla4,
                                                                        drop_exist_tab=False,
                                                                        # force=True,
                                                                        append=True)
                    except dbapi.IntegrityError as e:
                        print(e)
                        continue

                with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_altas_{hora_archivo}.csv", "a") as file:
                    file.write(f'{clave}; {list_emp[clave]}; {cant_altas}\n')
                    file.close()

                nits_procesados.append(clave)
                if len(list_emp) == len(nits_procesados):
                    flag = True

    except Exception as e:
        print(f'Se presentó un error durante el proceso. {e}')

with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_altas_{hora_archivo}.csv", "a") as file:
    file.write(f"Total altas: {total_altas}\n")
    file.write(f"Total empresas: {empresas_con_altas} \n")
    file.write(f"Finalizó {datetime.now()} \n")
    file.close()


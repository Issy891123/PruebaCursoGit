import openpyxl
import os
import hdbcli
from hdbcli import dbapi
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from datetime import datetime

inicio = datetime.now()
hora_archivo = inicio.strftime('%Y-%m-%d_%H-%M-%S')  # Formato: YYYY-MM-DD_HH-MM-SS

tabla1 = 'V_CONSOLIDACION_SEGM'
tabla2 = 'V_LIST_EMPRESAS_SEGM'
# tabla3 = 'V_GRC_ALL_USERS'

schema1 = 'COLSUBSIDIO_IDN'
# schema2 = 'COLSUBSIDIO_GRC'
total_registros = 0
cant_registros_sin = 0
con_reg = 0
sin_reg = 0
empresas_sin = []

path = r"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Cargue Masivo"
file = "Betterfly_SolicitudCargue"
path_file = path + '\\' + file + ".xlsx"
new_path = fr'{path}\Cargue_Masivo_{hora_archivo}'

try:
    os.mkdir(fr'{new_path}')
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

book = openpyxl.load_workbook(path_file, data_only=True)
hoja = book.active
celdas = hoja['A2':'B100000']

db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_{hora_archivo}.csv", "w") as file:
    file.write(f"{inicio} \n")
    file.write("Nit; RazonSocial; Cantidad; sin_nombres; total_enviados \n")
    file.close()

for fila in celdas:
    for celda in fila:
        if celda.value is not None:
            print(f'{fila} ---->> {celda.column_letter}')
            if celda.column_letter == 'A':
                nit = celda.value
            elif celda.column_letter == 'B':
                razon_social = celda.value
                print(f'Nit: {nit} -------> Razon Social: {razon_social}')
                query_todo = f'''
                    SELECT LE.ID_EMP_FILIAL, AF.TIPO_DOCUMENTO_AFILIADO, AF.NUMERO_DOCUMENTO_AFILIADO,
                    AF.PRIMER_APELLIDO, AF.SEGUNDO_APELLIDO, 
                    AF.PRIMER_NOMBRE || ' ' || CASE WHEN AF.SEGUNDO_NOMBRE IS NULL THEN ' ' ELSE AF.SEGUNDO_NOMBRE END AS NOMBRE_COMPLETO, 
                    'DC.EMAIL' AS CORREO_ELECTRONICO_1, 
                    SUBSTRING(AF.FECHA_NACIMIENTO,9,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,6,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,1,4) AS FECHA_NACIMIENTO,
                    AF.GENERO,
                    'DC.CELL_PHONE' AS TELEFONO_CELULAR_1
                    FROM {schema1}.{tabla1} AF
                    LEFT JOIN {schema1}.{tabla2} AS LE
                        ON NUMERO_ID_EMPRESA_SD = LE.NIT_SIN_DIGITO_FILIAL                    
                    WHERE LE.ID_EMP_FILIAL = '{nit}'
                '''

                ## ==== Query validar registros sin nombres ============
                query_sin_nombres = f'''
                    SELECT LE.ID_EMP_FILIAL, AF.TIPO_DOCUMENTO_AFILIADO, AF.NUMERO_DOCUMENTO_AFILIADO,
                    AF.PRIMER_APELLIDO, AF.SEGUNDO_APELLIDO, 
                    AF.PRIMER_NOMBRE || ' ' || CASE WHEN AF.SEGUNDO_NOMBRE IS NULL THEN ' ' ELSE AF.SEGUNDO_NOMBRE END AS NOMBRE_COMPLETO, 
                    'DC.EMAIL' AS CORREO_ELECTRONICO_1, 
                    SUBSTRING(AF.FECHA_NACIMIENTO,9,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,6,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,1,4) AS FECHA_NACIMIENTO,
                    AF.GENERO,
                    'DC.CELL_PHONE' AS TELEFONO_CELULAR_1
                    FROM {schema1}.{tabla1} AF
                    LEFT JOIN {schema1}.{tabla2} AS LE
                        ON NUMERO_ID_EMPRESA_SD = LE.NIT_SIN_DIGITO_FILIAL                    
                    WHERE LE.ID_EMP_FILIAL = '{nit}'
                        AND AF.PRIMER_NOMBRE IS NULL	                    
                    '''

                ini_rows = cc.sql(query_todo).count()
                print(query_sin_nombres)
                df = cc.sql(query_todo)
                pandas_df = df.collect()
                # Elimino del dataframe los reguistros que no tengan nombre
                pandas_df = pandas_df.dropna(subset=["NOMBRE_COMPLETO"])
                cant_registros_sin = cc.sql(query_sin_nombres).count()
                total_registros += ini_rows - cant_registros_sin
                print(f'Cantidad registros archivo {nit} {razon_social}: {pandas_df["ID_EMP_FILIAL"].count()} \nTotal Registros: {total_registros}')

                if ini_rows == 0:
                    sin_reg += 1
                    empresas_sin.append(f'{razon_social}')
                else:
                    con_reg += 1
                    pandas_df.to_excel(rf"{new_path}\{razon_social}_{nit}_{hora_archivo}.xlsx", index=False, header=headers)
                    print(pandas_df.head(10))

                print(f"Empresas con registros: {con_reg} \nEmpresas sin registros: {sin_reg}")

                with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_{hora_archivo}.csv", "a") as file:
                    file.write(f'{nit}; {razon_social}; {ini_rows}; {cant_registros_sin}; {ini_rows - cant_registros_sin}\n')

                # ================================== Query para completar campos para el  tablero de Juanita ============================

                query_complete = f'''
                    WITH CTE AS(
                        SELECT LE.ID_EMP_FILIAL, AF.TIPO_DOCUMENTO_AFILIADO, AF.NUMERO_DOCUMENTO_AFILIADO,
                            AF.PRIMER_APELLIDO, AF.SEGUNDO_APELLIDO, 
                            AF.PRIMER_NOMBRE || ' ' || CASE WHEN AF.SEGUNDO_NOMBRE IS NULL THEN ' ' ELSE AF.SEGUNDO_NOMBRE END AS NOMBRE_COMPLETO, 
                            'DC.EMAIL' AS CORREO_ELECTRONICO_1, 
                            SUBSTRING(AF.FECHA_NACIMIENTO,9,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,6,2) || '-' || SUBSTRING(AF.FECHA_NACIMIENTO,1,4) AS FECHA_NACIMIENTO,
                            AF.GENERO,
                            'DC.CELL_PHONE' AS TELEFONO_CELULAR_1
                        FROM {schema1}.{tabla1} AF
                        LEFT JOIN {schema1}.{tabla2} AS LE
                            ON NUMERO_ID_EMPRESA_SD = LE.NIT_SIN_DIGITO_FILIAL                        
                        WHERE LE.ID_EMP_FILIAL = '{nit}'                            	                                               
                    )
                    SELECT 
                        HB.*, 
                        CS.ID_PERSONA, CS.RAZON_SOCIAL, CS.RANGO_EDAD, CS.CATEGORIA, CS.SEGMENTO_POBLACIONAL, CURRENT_TIMESTAMP AS MES, 1 AS ACTIVO
                    FROM CTE AS HB
                    LEFT JOIN {schema1}.{tabla1} CS	 
                        ON HB.NUMERO_DOCUMENTO_AFILIADO = CS.NUMERO_DOCUMENTO_AFILIADO
                        AND HB.ID_EMP_FILIAL = CS.ID_EMPRESA
                    WHERE HB.NOMBRE_COMPLETO IS NOT NULL
                '''
                print(f'Query para completar campos para el  tablero de Juanita: \n {query_complete}')

                df_complete = cc.sql(query_complete)
                pd_df_complete = df_complete.collect()
                pd_df_complete = pd_df_complete.astype(str)

                try:
                    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                                    pandas_df=pd_df_complete,
                                                                    schema='COLSUBSIDIO_IDN',
                                                                    table_name='TBL_HISTORIAL_BETTERFLY_VAL',
                                                                    drop_exist_tab=False,
                                                                    # force=True,
                                                                    append=True)
                except dbapi.IntegrityError as e:
                    print(e)
                    continue
        else:
            break

print(empresas_sin)
with open(fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\Betterfly\Logs\Logs_{hora_archivo}.csv", "a") as file:
    file.write(f"Empresas con registros: {con_reg} \nEmpresas sin registros: {sin_reg} \n")
    file.write(f"Total registros: {total_registros} \n")
    file.write(f"Finalizó {datetime.now()} \n")

import os
import pandas as pd
from datetime import datetime, timedelta
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from concurrent.futures import ThreadPoolExecutor
from hdbcli import dbapi


def extraer_primeros_caracteres(cadena):
    return str(cadena)[:4999]

# Función que concatena los valores de todas las columnas según el formato requerido
def concatenar_campos(row):
    return f"{row['NUR']}|{row['CAMARA_C']}|{row['Matricula']}|{row['Tipo_Identific']}|{row['Identificacion']}|{row['Razon_Social']}|{row['Organizacion_Juridica']}|{row['Categoria']}|{row['Estado_Mat']}|{row['Fecha_Constitucion']}|{row['Fecha_Matricula']}|{row['Fec_Ultima_Renov']}|{row['Ultimo_AnoRenovado']}|{row['Direccion']}|{row['Ciudad_Mpio']}|{row['Zona_Postal']}|{row['Barrio']}|{row['Localidad']}|{row['Imp_Exp']}|{row['Telefono1']}|{row['Telefono2']}|{row['Telefono3']}|{row['Fax']}|{row['Celular']}|{row['E_mail']}|{row['Pagina_Web']}|{row['CIIU']}|{row['Descripcion_CIIU']}|{row['Sector_Economico']}|{row['Tipo_ID_Represe_Legal']}|{row['ID_Represe_Legal']}|{row['Representante_legal']}|{row['Personal']}|{row['Clasificacion']}|{row['Activo_Total']}|{row['Activo_Sin_Ajuste']}|{row['Activo_Corriente']}|{row['Activo_Fijo']}|{row['Valoracion_Activo']}|{row['Otro_Activo']}|{row['Pasivo_Corriente']}|{row['Obliga_LargoPlz']}|{row['Pasivo_Total']}|{row['Patrimonio']}|{row['Pasivo+Patrimonio']}|{row['Ventas_Netas']}|{row['Costo_Ventas']}|{row['Util_Perdida_Oper']}|{row['Util_Perdida_Neta']}|{row['Gastos_Admon']}|{row['Ingresos AO']}|{row['Costo Ventas']}|{row['Guanacia Bruta']}|{row['Otros Ingreso']}|{row['Gastos Ventas']}|{row['Gastos Admin']}|{row['Otros Gastos']}|{row['Otras Ganancias']}|{row['Ganancia x AO']}|{row['Diferencia EILDILA']}|{row['Ganancias SBCA']}|{row['Ingresos Finan']}|{row['Costos Finan']}|{row['Participacion GAN']}|{row['Otros Ing SEC']}|{row['Ganancias SDIV']}|{row['Ganancia CGPPRC']}|{row['Ganancias ADI']}|{row['Ingreso x Imp']}|{row['Ganancia POC']}|{row['Ganancia POD']}|{row['Ganancia Perdida']}"


# Función que agrega el nombre del archivo a todos los archivos descargados
def procesar_archivo(file):
    if file.endswith('.xlsx') and hora_archivo in file[:8]:
        archivo_completo = os.path.join(directorio, file)
        dfexcel = pd.read_excel(archivo_completo, skiprows=1)
        dfexcel['Archivo'] = file
        dfexcel['LLAVE'] = dfexcel.apply(concatenar_campos, axis=1)
        dfexcel['Fecha_Ejecucion'] = fecha_cargue
        return dfexcel

directorio = r'C:\Users\estegomhin\Downloads'
contenido = os.listdir(directorio)

# Configuración de fechas
inicio = datetime.now() - timedelta(days=5)
fecha_cargue = inicio
# fecha_cargue = fecha_cargue.strftime('%Y-%m-%d_%H-%M-%S')

# Cuando se ejecuta un reproceso se quema la fecha # '20231010' # , sino, se deja la función
if inicio.month < 10:
    if inicio.day < 10:
        hora_archivo = f'{inicio.year}0{inicio.month}0{inicio.day}'
    else:
        hora_archivo = f'{inicio.year}0{inicio.month}{inicio.day}'
else:
    hora_archivo = f'{inicio.year}{inicio.month}{inicio.day}'
# hora_archivo = ''

# Procesar archivos en paralelo y combinarlos en un solo DataFrame
with ThreadPoolExecutor() as executor:
    dataframes = list(executor.map(procesar_archivo, contenido))
df_final = pd.concat([df for df in dataframes if df is not None])

# Guardar el DataFrame combinado
df_final.to_csv(os.path.join(directorio, 'CC_Bases', 'CamCom_BasesConsolidadas.csv'), index=False, encoding='utf-8-sig')


# Iterar sobre las columnas del DataFrame
for columna in df_final.columns:
    # Verificar si el tipo de datos de la columna es 'object'
    if df_final[columna].dtype == 'object':
        # Aplicar la función solo a las columnas de tipo 'object'
        df_final[columna] = df_final[columna].apply(extraer_primeros_caracteres)


# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
#pd.set_option('display.max_rows', None)

headers = ['NUR', 'CAMARA_C', 'Matricula', 'Tipo_Identific', 'Identificacion', 'Razon_Social', 'Organizacion_Juridica',
           'Categoria', 'Estado_Mat', 'Fecha_Constitucion', 'Fecha_Matricula', 'Fec_Ultima_Renov', 'Ultimo_AnoRenovado',
           'Direccion', 'Ciudad_Mpio', 'Zona_Postal', 'Barrio', 'Localidad', 'Imp_Exp', 'Telefono1', 'Telefono2',
           'Telefono3', 'Fax', 'Celular', 'E_mail', 'Pagina_Web', 'CIIU', 'Descripcion_CIIU', 'Sector_Economico',
           'Tipo_ID_Represe_Legal', 'ID_Represe_Legal', 'Representante_legal', 'Personal', 'Clasificacion', 'Activo_Total', 'Activo_Sin_Ajuste',
           'Activo_Corriente', 'Activo_Fijo', 'Valoracion_Activo', 'Otro_Activo', 'Pasivo_Corriente', 'Obliga_LargoPlz',
           'Pasivo_Total', 'Patrimonio', 'Pasivo+Patrimonio', 'Ventas_Netas', 'Costo_Ventas', 'Util_Perdida_Oper',
           'Util_Perdida_Neta', 'Gastos_Admon', 'Ingresos AO', 'Costo Ventas', 'Guanacia Bruta', 'Otros Ingreso',
           'Gastos Ventas', 'Gastos Admin', 'Otros Gastos', 'Otras Ganancias', 'Ganancia x AO', 'Diferencia EILDILA',
           'Ganancias SBCA', 'Ingresos Finan', 'Costos Finan', 'Participacion GAN', 'Otros Ing SEC', 'Ganancias SDIV',
           'Ganancia CGPPRC', 'Ganancias ADI', 'Ingreso x Imp', 'Ganancia POC', 'Ganancia POD', 'Ganancia Perdida',
           'Archivo', 'LLAVE'
           ]

# Leer el archivo txt en dataframe de pandas
# df = pd.read_csv(fr'{directorio}\CC_Bases\CamCom_BasesConsolidadas.csv', sep=',', skiprows=1, header=None, names=headers, dtype="object",
#                  encoding="utf-8-sig", low_memory=False)

df_final.drop(df_final[(df_final['NUR'] == "NUR") & (df_final['CAMARA_C'] == 'CAMARA_C')].index, inplace=True)
df_final.drop_duplicates(subset=["NUR", "CAMARA_C", "Matricula", "Identificacion", "Razon_Social"], keep='last')
df_final = df_final.drop(['Contiene Proponente'], axis=1)

# Validaciones
print(f'Total registros a cargar: {df_final.shape[0]}')
print(df_final.head(10))

# Credenciales SAP - Hana Database
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = "ESTEGOMHIN"
db_pwd = "Poison0624*"

# Conexión con la base de datos
cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

if cc:
    print("Success <3<3<3<3")

try:
    dfhana = dataframe.create_dataframe_from_pandas(connection_context=cc,
                                                    pandas_df=df_final,
                                                    schema='COLSUBSIDIO_IDN',
                                                    table_name='TBL_CAM_COMERCIO_CONSOLIDADA',
                                                    drop_exist_tab=False,
                                                    # force=True)
                                                    append=True)
except dbapi.IntegrityError as e:
    print(e)
    pass



cc.close()

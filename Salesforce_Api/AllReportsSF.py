import json
import os
import pandas as pd
import requests
from io import StringIO
import unicodedata
from simple_salesforce import Salesforce, SalesforceLogin, SFType
import hana_ml as hana
import logging
from datetime import datetime

# Guardar hora de inicio ejecución
inicio = datetime.now()
hora_archivo = inicio.strftime('%Y-%m-%d_%H-%M-%S')  # Formato: YYYY-MM-DD_HH-MM-SS

# Conexión a Hana
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd = os.environ.get('DB_PASSWORD')
schema = 'COLSUBSIDIO_IDN'

# ========================== funciones para crear tabla o insertar =================================
# Función para limpiar los nombres de los encabezados porque vienen con tildes y espacios
def limpiar_nombre(nombre):
    nombre = nombre.upper()  # Convertir a mayúsculas
    nombre = nombre.replace(" ", "_")  # Reemplazar espacios por "_"
    nombre = ''.join((c for c in unicodedata.normalize('NFD', nombre) if unicodedata.category(c) != 'Mn'))  # Eliminar tildes
    return nombre

def conectar(url, port, user, pwd):
    try:
        cc = hana.ConnectionContext(url, port, user, pwd, encrypt="true", sslValidateCertificate="false")
        if cc:
            print("¡Conexión exitosa!")
        return cc
    except Exception as e:
        print(f"Error al conectar con SAP HANA: {e}")
        return None

def appen_data(dataframe, schema, table):
    cc = conectar(db_url, db_port, db_user, db_pwd)
    dfhana = hana.dataframe.create_dataframe_from_pandas(
        connection_context=cc,
        pandas_df=dataframe,
        schema=schema,
        table_name=table,
        drop_exist_tab=False,
        # force=True,
        append=True
    )

def truncate_data(dataframe, schema, table):
    cc = conectar(db_url, db_port, db_user, db_pwd)
    dfhana = hana.dataframe.create_dataframe_from_pandas(
        connection_context=cc,
        pandas_df=dataframe,
        schema=schema,
        table_name=table,
        drop_exist_tab=True,
        force=True,
        append=False
    )

# Truncate para tablas a las que no se debe cambiar el nombre de las columnas
def truncate_data_keepnames(dataframe, schema, table):
    cc = conectar(db_url, db_port, db_user, db_pwd)
    dfhana = hana.dataframe.create_dataframe_from_pandas(
        connection_context=cc,
        pandas_df=dataframe,
        schema=schema,
        table_name=table,
        drop_exist_tab=False,
        force=True,
        append=False
    )

def eliminar_datos_tablas(esquema, tabla):
    query_count = f'''
        SELECT * FROM {esquema}."{tabla}"
        WHERE TO_TIMESTAMP(FECHA_CARGUE, 'YYYY-MM-DD_HH24-MI-SS') < (SELECT MAX(TO_TIMESTAMP(FECHA_CARGUE, 'YYYY-MM-DD_HH24-MI-SS')) FROM {esquema}."{reporte}");
    '''
    cc = conectar(db_url, db_port, db_user, db_pwd)
    print(query_count)
    result_count = cc.sql(query_count).count()

    query_delete = f'''
            DELETE FROM {esquema}."{tabla}" WHERE TO_TIMESTAMP(FECHA_CARGUE, 'YYYY-MM-DD_HH24-MI-SS') < (SELECT MAX(TO_TIMESTAMP(FECHA_CARGUE, 'YYYY-MM-DD_HH24-MI-SS')) FROM {esquema}."{reporte}");
        '''

    filas_eliminadas = result_count
    print(f'Se eliminan {filas_eliminadas} registros')
    cc.execute_sql(query_delete)
    print(f'DELETE: {query_delete} >>>>> ejecutado correctamente')


# ======================================================================================================

# Función para extraer los primeros 4999 caracteres de una cadena
def extraer_primeros_caracteres(cadena):
    return str(cadena)[:4999]

## =========================================================================================


# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
#pd.set_option('display.max_rows', None)

loginInfo = json.load(open(r'C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\PycharmProjects\Salesforce_Api\login-prd.json'))
username = loginInfo['username']
password = loginInfo['password']
securityToken = loginInfo['token']
reports_id = {
    'TBL_EVENTOS_ASISTENTES_SF': '00OTS000000I7JB2A0',
    'TBL_EVENTOS_EMPRESAS_SF': '00OTS000000aeBp2AI',
    'TBL_VARIABLES_VITALES_SALESFORCE': '00OTS000000MTRZ2A4',
    'TBL_VENTA_EMPRESARIAL_LECTURA_SF': '00O5a000007dl9yEAA',
    'TBL_ALIADOS_SF': '00OTS000000Upmf2AC',
    'TBL_CAMPAÑAS_CORPORATIVAS_SF': '00OTS000000Uphp2AC',
    'TBL_CAMPAÑAS_EMPRESARIALES_SF': '00OTS000000Upuj2AC',
    'TBL_DESARROLLO_EMPRESARIAL_SF': '00OTS000000UpzZ2AS',
    'TBL_EMPLEABILIDAD_SF': '00O5a000007dlA3EAI',
    'TBL_FORMACION_EMP_FOSFEC_SF': '00OTS000000UqAr2AK',
    'TBL_LICITACION_SF': '00OTS000000UrlF2AS',
    'TBL_VENTA_INDIVIDUAL_COTIZACION_SF': '00OTS000000Urq52AC',
    'TBL_CUENTAS_SF': '00OTS000000YAcr2AG',
    'TBL_CUENTAS_PERSONAL_SF': '00OTS000000YEyD2AW',
    # 'TBL_CONTACTOS_SF':'00OTS000000YDfZ2AW',
    'TBL_RIESGO_SF': '00OTS000000YF9V2AW',
    'TBL_ATRACCION_VISITAS_SF': '00OTS000000YDsT2AW',
    ###'TBL_CARTERIZACION_SF': '00O5a000007dlAIEAY', Después del 15 de Mayo 2024 se podría borrar
    # 'T_CARTERIZACION_SF_STG': '00OTS000000svZB2AY',
    'TBL_PROPIETARIOS_DE_CUENTA_SF': '00OTS000001jyib2AA',
    'TBL_PAZYSALVOS_FUGA_SF': '00OTS000000lg0b2AA',
    'TBL_FORMACION_FOSFEC_SF': '00OTS000001nVJp2AM'
}


# for reporte in reports_id:
#     eliminar_datos_tablas(schema, reporte)

logging.basicConfig(filename=rf'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\Salesforce_Api\Logs\log_api_SF_{hora_archivo}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sf = Salesforce(username=username,password=password,security_token=securityToken)

# Basic report URL structure:
orgParams = 'https://colsubsidio.my.salesforce.com/' # you can see this in your Salesforce URL
exportParams = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'

# Downloading the report:
for reporte in reports_id:
    print(reporte)
    print(reports_id[reporte])
    reportId = reports_id[reporte] # You find this in the URL of the report in question between "Report/" and "/view"
    reportUrl = orgParams + reportId + exportParams
    reportReq = requests.get(reportUrl, headers=sf.headers, cookies={'sid': sf.session_id})
    reportData = reportReq.content.decode('utf-8')
    reportDf = pd.read_csv(StringIO(reportData), low_memory=False)
    nombres_originales = reportDf.columns.tolist()
    nuevos_nombres = {nombre: limpiar_nombre(nombre) for nombre in nombres_originales}

    # Iterar sobre las columnas del DataFrame
    for columna in reportDf.columns:
        # Verificar si el tipo de datos de la columna es 'object'
        print(columna, ': ', type(columna))
        if reportDf[columna].dtype == 'object':
            reportDf[columna] = reportDf[columna].fillna('0')
            # Aplicar la función solo a las columnas de tipo 'object'
            reportDf[columna] = reportDf[columna].apply(extraer_primeros_caracteres)
        elif reportDf[columna].dtype == int or reportDf[columna].dtype == float:
            reportDf[columna] = reportDf[columna].fillna(0)

    reportDf.to_csv(rf'ReportsExcel\{reporte}.csv', index=False)


    # if reporte == 'TBL_VARIABLES_VITALES_SALESFORCE':
    #     reportDf['Fecha de Pago'] = reportDf['Fecha de Pago'].astype('object')
    #     # Lidiar con los valores no válidos (por ejemplo, reemplazar NaN con cero)
    #     reportDf['Valor Aportes'] = reportDf['Valor Aportes'].fillna(0)
    #     reportDf['Valor Aportes'] = reportDf['Valor Aportes'].astype('object')
    #     reportDf['Valor Subsidio'] = reportDf['Valor Subsidio'].fillna(0)
    #     reportDf['Valor Subsidio'] = reportDf['Valor Subsidio'].astype('object')
    #     reportDf['Fecha de Ciclo de Pago'] = pd.to_datetime(reportDf['Fecha de Ciclo de Pago'])
    #     reportDf['Posición Ranking Grupo'] = reportDf['Posición Ranking Grupo'].fillna(0)
    #     reportDf['Posición Ranking Grupo'] = reportDf['Posición Ranking Grupo'].astype('int64')
    #     reportDf['Posición Ranking Empresa'] = reportDf['Posición Ranking Empresa'].fillna(0)
    #     reportDf['Posición Ranking Empresa'] = reportDf['Posición Ranking Empresa'].str.replace(',', '.').astype(float)
    #
    # elif reporte == 'TBL_ATRACCION_VISITAS_SF':
    #     reportDf['Comentarios'] = reportDf['Comentarios'].str.slice(0, 4900)
    #
    # elif reporte == 'T_CARTERIZACION_SF_STG':
    #     columnas_a_eliminar = ['Fecha estado de atraccion anterior',
    #                             'Dirección',
    #                             'Motivos de No Interesado',
    #                             'Cúal Motivo No interesado?',
    #                             # 'Fecha Motivo No Interesado'
    #                            ]
    #     reportDf = reportDf.drop(columns=columnas_a_eliminar)
    #     reportDf['FECHA_CARGUE'] = hora_archivo
    #     print(reportDf.head(10))
    #     # truncate_data_keepnames(reportDf, schema, reporte)
    #     # print(f'La tabla {reporte} presentó error en su esquema. **Se eliminó** y se creó nuevamente con {reportDf.shape[0]} registros.')
    #     # logging.info(f'La tabla {reporte} presentó error en su esquema. **Se eliminó** y se creó nuevamente con {reportDf.shape[0]} registros.')
    #
    # elif reporte == 'TBL_PROPIETARIOS_DE_CUENTA_SF':
    #     reportDf['Número de cédula'] = reportDf['Número de cédula'].astype('object')
    #
    # else:
    #     # Renombra las columnas del DataFrame
    #     reportDf.rename(columns=nuevos_nombres, inplace=True)
    #     # reportDf['FECHA_CARGUE'] = hora_archivo
    #     print(reportDf.head(10))
    #
    # reportDf.to_csv(rf'ReportsExcel\{reporte}.csv', index= False)

    #     # try:
    #     #     appen_data(reportDf, schema, reporte)
    #     #     print(f'Se anexó correctamente datos a la tabla {reporte} con {reportDf.shape[0]} registros.')
    #     #     logging.info(f'Se anexó correctamente datos a la tabla {reporte} con {reportDf.shape[0]} registros.')
    #     # except:
    # try:
    #     truncate_data(reportDf, schema, reporte)
    #     print(f'La tabla {reporte} presentó error en su esquema. **Se eliminó** y se creó nuevamente con {reportDf.shape[0]} registros.')
    #     logging.info(f'La tabla {reporte} presentó error en su esquema. **Se eliminó** y se creó nuevamente con {reportDf.shape[0]} registros.')
    # except Exception as e:
    #     truncate_data(reportDf, schema, reporte)
    #     print(f'La tabla {reporte} presentó error en su esquema. **NO SE CARGÓ** {e}')
    #     logging.info(f'La tabla {reporte} presentó error en su esquema. **NO SE CARGÓ** {e}')
    #     pass
import json
import pandas as pd
from hdbcli import dbapi
import requests
from io import StringIO
from simple_salesforce import Salesforce, SalesforceLogin, SFType
import hana_ml as hana

loginInfo = json.load(open('login-prd.json'))
username = loginInfo['username']
password = loginInfo['password']
securityToken = loginInfo['token']

sf = Salesforce(username=username,password=password,security_token=securityToken)

# Basic report URL structure:
orgParams = 'https://colsubsidio.my.salesforce.com/' # you can see this in your Salesforce URL
exportParams = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'

# Downloading the report:
reportId = '00OTS000000MTRZ2A4' # You find this in the URL of the report in question between "Report/" and "/view"
reportUrl = orgParams + reportId + exportParams
reportReq = requests.get(reportUrl, headers=sf.headers, cookies={'sid': sf.session_id})
reportData = reportReq.content.decode('utf-8')
reportDf = pd.read_csv(StringIO(reportData), low_memory=False)
# reportDf.iloc[:, 8] = reportDf.iloc[:, 8].astype('int64')
reportDf['Fecha de Pago'] = reportDf['Fecha de Pago'].astype('object')
# Lidiar con los valores no válidos (por ejemplo, reemplazar NaN con cero)
reportDf['Valor Aportes'] = reportDf['Valor Aportes'].fillna(0)
reportDf['Valor Aportes'] = reportDf['Valor Aportes'].astype('object')
reportDf['Valor Subsidio'] = reportDf['Valor Subsidio'].fillna(0)
reportDf['Valor Subsidio'] = reportDf['Valor Subsidio'].astype('object')
reportDf['Fecha de Ciclo de Pago'] = pd.to_datetime(reportDf['Fecha de Ciclo de Pago'])
reportDf['Posición Ranking Grupo'] = reportDf['Posición Ranking Grupo'].fillna(0)
reportDf['Posición Ranking Grupo'] = reportDf['Posición Ranking Grupo'].astype('int64')
reportDf['Posición Ranking Empresa'] = reportDf['Posición Ranking Empresa'].fillna(0)
reportDf['Posición Ranking Empresa'] = reportDf['Posición Ranking Empresa'].str.replace(',', '.').astype(float)


# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
print(reportDf.dtypes)
print(reportDf.head(10))

# Conexión a Hana
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = "ESTEGOMHIN"
db_pwd = "Poison0624*"

cc = hana.ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")
if cc:
    print("Success <3<3<3<3")

try:
    dfhana = hana.dataframe.create_dataframe_from_pandas(
        connection_context=cc,
        pandas_df=reportDf,
        schema='COLSUBSIDIO_IDN',
        table_name='TBL_VARIABLES_VITALES_SALESFORCE',
        drop_exist_tab=False,
        # force=True,
        append=True
        )
except dbapi.IntegrityError as e:
    print(e)
    pass
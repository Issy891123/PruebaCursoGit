import json
import pandas as pd
import csv
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
reportId = '00OTS000000ehXh2AI' # You find this in the URL of the report in question between "Report/" and "/view"
reportUrl = orgParams + reportId + exportParams
reportReq = requests.get(reportUrl, headers=sf.headers, cookies={'sid': sf.session_id})
reportData = reportReq.content.decode('utf-8')
reportDf = pd.read_csv(StringIO(reportData))
print(reportDf.head(10))

# Conexión a Hana
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = "ESTEGOMHIN"
db_pwd = "Poison0624*"

cc = hana.ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")
if cc:
    print("Success <3<3<3<3")

dfhana = hana.dataframe.create_dataframe_from_pandas(
    connection_context=cc,
    pandas_df=reportDf,
    schema='COLSUBSIDIO_IDN',
    table_name='TBL_EVENTOS_SALESFORCE',
    drop_exist_tab=True,
    force=True,
    append=False
)
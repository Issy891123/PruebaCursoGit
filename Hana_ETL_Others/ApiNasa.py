import requests
import pandas as pd
import os
from sqlalchemy import create_engine
from hana_ml.dataframe import ConnectionContext
import hana_ml.dataframe as dataframe
from hdbcli import dbapi

# Configuración de la API de la NASA
NASA_API_KEY = "DEMO_KEY"
NASA_PROJECTS_URL = f"https://api.nasa.gov/techtransfer/patent/?api_key={NASA_API_KEY}"

TEST_URL = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
response = requests.get(TEST_URL)
print(response.status_code, response.text)

Api = None
# Función para extraer datos desde la API
def extract_data():
    response = requests.get(NASA_PROJECTS_URL)
    if response.status_code == 200:
        data = response.json()
        Api = 'MAIN'
        print(f'Conectado a la Api: {Api}')
        return data, Api
    elif response.status_code == 500:
        print(f'error en la Api principal {response.status_code}')
        response = requests.get(TEST_URL)
        data = response.json()
        Api = 'TEST'
        print(f'Conectado a la Api: {Api}')
        return data, Api
    else:
        raise Exception(f"Error en la API: {response.status_code}")


# Transformar datos
def transform_data(data):
    projects = []
    for project in data.get('results', []):
        project_id = project[0]
        title = project[1]
        description = project[2]
        url = project[3]

        projects.append({"project_id": project_id, "title": title, "description": description, "url": url})

    df_projects = pd.DataFrame(projects)
    return df_projects

# Función que transforma data alternativa por si la api principal no funciona
def transform_alternate_data(data):
    """ Transforma los datos en un DataFrame de Pandas """
    df = pd.DataFrame([{
        "date": data["date"],
        "title": data["title"],
        "explanation": data["explanation"],
        "media_type": data["media_type"],
        "hdurl": data.get("hdurl", ""),  # Algunos pueden no tener HD URL
        "url": data["url"]
    }])
    return df

# Conexión flexible a BD (SAP HANA, AWS RDS, Azure)
def load_data(df, db_type="sap_hana"):
    if db_type == "sap_hana":
        print("==>> Conectando a SAP HANA...")
        db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
        db_port = 443
        db_user = os.environ.get('DB_USER')
        db_pwd = os.environ.get('DB_PASSWORD')
        conn = ConnectionContext(address=db_url, port=db_port, user=db_user, password=db_pwd)

        try:
            dfhana = dataframe.create_dataframe_from_pandas(connection_context=conn,
                                                            pandas_df=df,
                                                            schema='COLSUBSIDIO_APG',
                                                            table_name='T_TEST_API_NASA',
                                                            drop_exist_tab=True,
                                                            # force=True,
                                                            append=True)
        except dbapi.IntegrityError as e:
            print(e)
            pass
        print("✅ Datos cargados en SAP HANA")

    elif db_type == "aws_rds":
        print("🔗 Conectando a AWS RDS...")
        engine = create_engine(
            f'postgresql://{os.environ["AWS_USER"]}:{os.environ["AWS_PASSWORD"]}@{os.environ["AWS_HOST"]}/{os.environ["AWS_DB"]}')
        df.to_sql('projects', engine, if_exists='replace', index=False)
        print("✅ Datos cargados en AWS RDS")

    elif db_type == "azure_sql":
        print("🔗 Conectando a Azure SQL...")
        engine = create_engine(
            f'mysql+pymysql://{os.environ["AZURE_USER"]}:{os.environ["AZURE_PASSWORD"]}@{os.environ["AZURE_HOST"]}/{os.environ["AZURE_DB"]}')
        df.to_sql('projects', engine, if_exists='replace', index=False)
        print("✅ Datos cargados en Azure SQL")


# 🚀 Ejecutar la ETL


try:
    print("🛰️ Extrayendo datos desde la API de la NASA...")
    raw_data, api_type = extract_data()

    print("🔄 Transformando datos...")
    if api_type == 'MAIN':
        transformed_data = transform_data(raw_data)
    elif api_type == 'TEST':
        transformed_data = transform_alternate_data(raw_data)

    print("🛢️ Cargando datos en la base seleccionada...")
    load_data(transformed_data, db_type="sap_hana")  # Cambiar "aws_rds" o "azure_sql" según sea necesario

except Exception as e:
    print(f"❌ Error en la ETL: {str(e)}")

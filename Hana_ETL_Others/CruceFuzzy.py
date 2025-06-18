import os
import re
import pandas as pd
from hana_ml.dataframe import ConnectionContext

# 1. Configuración y conexión a HANA
db_url  = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = os.environ.get('DB_USER')
db_pwd  = os.environ.get('DB_PASSWORD')

cc = ConnectionContext(
    address=db_url,
    port=db_port,
    user=db_user,
    password=db_pwd,
    encrypt="true",
    sslValidateCertificate="false"
)

# 2. Leer el Excel desde Downloads (ajusta el nombre de archivo)
file_path = r"C:\Users\estegomhin\Downloads\Cio_Fontanar_Entrega_ID_CRISTHIAN CAMILO BUI.xlsx"
df = pd.read_excel(file_path, sheet_name='Consolida')

# 3. Crear campos adicionales con expresiones regulares
# 3.1 RAZON_SOCIAL_LIMPIA: eliminar caracteres especiales (. , - / * & etc)
df['RAZON_SOCIAL_LIMPIA'] = (
    df['NAME1']
      .astype(str)
      .str.upper()
      .str.replace(r'[^A-Z0-9 ]', '', regex=True)
)

# 3.2 RAZON_SOCIAL_SIN_ESPACIOS: quitar todos los espacios
df['RAZON_SOCIAL_SIN_ESPACIOS'] = (
    df['RAZON_SOCIAL_LIMPIA']
      .str.replace(r'\s+', '', regex=True)
)

# 4. Traer la tabla de HANA a pandas
hana_df = (
    cc.table("CV_IDN_LIMPIA_Y_CONSOLIDA_EMPRESAS", "COLSUBSIDIO_LT")
      .collect()
)

print("Antes de normalizar:", hana_df.columns.tolist())

# 5. Función auxiliar para hacer merge y marcar coincidencia
def merge_with_mark(local_df, remote_df, left_on, right_on, mark_label):
    m = local_df.merge(
        remote_df,
        how='left',
        left_on=left_on,
        right_on=right_on,
        suffixes=('', '_emp')
    )
    # sólo conservar las filas que realmente coincidieron en este join
    matched = m[~m[right_on].isna()].copy()
    matched['MATCH_FIELD'] = mark_label
    return matched

# 6. Realizar los 3 cruces en orden de prioridad
# 6.1 Por RAZON_SOCIAL_ORIGINAL (suponiendo que en la tabla remota se llama así)
step1 = merge_with_mark(
    df, hana_df,
    left_on='NAME1', right_on='RAZON_SOCIAL_ORGINAL',
    mark_label='ORIGINAL'
)

# 6.2 Por RAZON_SOCIAL_LIMPIA (local) vs RAZON_SOCIAL_LIMPIA (remota)
#    sólo los que no coincidieron en step1
remaining = df[~df.index.isin(step1.index)]
step2 = merge_with_mark(
    remaining, hana_df,
    left_on='RAZON_SOCIAL_LIMPIA', right_on='RAZON_SOCIAL_LIMPIA',
    mark_label='LIMPIA'
)

# 6.3 Por RAZON_SOCIAL_SIN_ESPACIOS
remaining = remaining[~remaining.index.isin(step2.index)]
step3 = merge_with_mark(
    remaining, hana_df,
    left_on='RAZON_SOCIAL_SIN_ESPACIOS', right_on='RAZON_SOCIAL_SIN_ESPACIOS',
    mark_label='SIN_ESPACIOS'
)

# 7. Unir los resultados
result = pd.concat([step1, step2, step3], ignore_index=True, sort=False)

# 8. Para los que no coincidieron en ninguno, si los quieres identificar:
no_match = df[~df['NAME1'].isin(result['NAME1'])]
no_match['MATCH_FIELD'] = 'NO_MATCH'

# 9. Combinar todo
final_df = pd.concat([result, no_match], ignore_index=True, sort=False)

# 10. Guardar o procesar
final_df.to_excel(r"C:\Users\estegomhin\Downloads\resultado_cruce.xlsx", index=False)
print("Cruce completado. Resultado en 'resultado_cruce.xlsx'.")

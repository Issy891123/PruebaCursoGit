# Este archivo usa el encoding: utf-8
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from selenium import webdriver
from hana_ml.dataframe import ConnectionContext
from selenium.common import NoAlertPresentException, ElementClickInterceptedException, NoSuchElementException, \
    StaleElementReferenceException, NoSuchDriverException, WebDriverException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from datetime import datetime
import pandas as pd
import time
from selenium.webdriver.support.wait import WebDriverWait
from ConsultaIdsParaMascara import id_afiliados


# Función para validar y tomar el dato de la columna que sí tiene el dato
def valpar(numero):
    if numero % 2 == 0:
        return True
    else:
        return False

# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}_{inicio.month}_{inicio.year}_{inicio.hour}{inicio.minute}{inicio.second}'
ruta_archivo = r'C:\Users\estegomhin\OneDrive - colsubsidio.com (1)\PycharmProjects\Hana_ETL_Others\Outputs'

## Parámetros de conexión
db_url = "548b50f4-1fe9-4725-baea-e9f96bb4f092.hana.prod-us10.hanacloud.ondemand.com"
db_port = 443
db_user = "ESTEGOMHIN"
db_pwd = "Poison0624*"

cc = ConnectionContext(db_url, db_port, db_user, db_pwd, encrypt="true", sslValidateCertificate="false")

# query_afiliados = f'''
#     WITH CTE AS (
#         SELECT DISTINCT TIPO_DOCUMENTO_AFILIADO,
#             NO_DOCUMENTO_PERSONA,
#             ROW_NUMBER () OVER (PARTITION BY TIPO_DOCUMENTO_AFILIADO ORDER BY TIPO_DOCUMENTO_AFILIADO) AS VAL
#         FROM COLSUBSIDIO_IDN.TBL_AFILIADO_EMPRESA_SEGM
#     )
#     SELECT TIPO_DOCUMENTO_AFILIADO,
#         NO_DOCUMENTO_PERSONA
#     FROM CTE
#     --WHERE VAL <= 10
#     WHERE NO_DOCUMENTO_PERSONA IN ('80243275')
#     ORDER BY TIPO_DOCUMENTO_AFILIADO, VAL
# '''
#
# print(query_afiliados)
#
# id_afiliados = cc.sql(query_afiliados)
# id_afiliados = id_afiliados.collect()


# Id_afiliados se quema con los valores a consultar cuando no se sabe si la persona es afiliada o no
print(id_afiliados.head(15))

# Quitar comentario cuando se deban consultar en hana sino, dejarlos quemados como lista
# id_afiliados_list = id_afiliados["NUM_IDENTIFICACION_AFILIADO"].tolist()
id_afiliados_list = []

df_documentos_encontrados = id_afiliados["NO_DOCUMENTO_PERSONA"].tolist()
# Encontrar los elementos faltantes y guardarlos en una lista
faltantes = [id_afiliado for id_afiliado in id_afiliados_list if id_afiliado not in df_documentos_encontrados]
# Crear el diccionario con los elementos faltantes
diccionario_faltantes = {id_afiliado: 'CC' for id_afiliado in faltantes}
# Crea diccionario con lo que encontró en el query
id_afiliados_dict = id_afiliados[["TIPO_DOCUMENTO_AFILIADO", "NO_DOCUMENTO_PERSONA"]].to_dict(orient='records')

id_validados = []
# Convertir la lista de diccionarios a un DataFrame
df = pd.DataFrame(id_afiliados_dict)


# Establecer la columna 'ID_EMP_FILIAL' como índice y convertir a un solo diccionario
id_afiliados_dict = df.set_index('NO_DOCUMENTO_PERSONA')['TIPO_DOCUMENTO_AFILIADO'].to_dict()

# Unir los dos diccionarios para completar todos los documentos, los que vienen sin tipo de doc por defecto se mandan con CC
id_afiliados_dict.update(diccionario_faltantes)
print(id_afiliados_dict)

url_bd = 'http://sapmasclnx.colsubsidio.com:8080/ConsultaUsuarios/index.xhtml'

chrome_driver = webdriver.Chrome()
chrome_driver.get(url_bd)
actions = ActionChains(chrome_driver)
chrome_driver.maximize_window()
WebDriverWait(chrome_driver, 5).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'ul.ui-selectonemenu-items.ui-selectonemenu-list.ui-widget-content.ui-widget.ui-corner-all.ui-helper-reset')))

# Xpath tablas a extraer
datos_afiliado = '/html/body/div[1]/div[2]/form/table[1]/tbody/tr[3]/td/div/div[2]/table[contains(.,"Nombre")]'
datos_afiliacion = '/html/body/div[1]/div[2]/form/table[1]/tbody/tr[4]/td/div/div[2]/table[contains(.,"Tipo Aporte Afiliado")]'
grilla_datos_afiliacion = '/html/body/div[1]/div[2]/form/table[1]/tbody/tr[4]/td/div/div[2]/div/div/table[contains(.,"Código")]'
grupo_familiar = '/html/body/div[1]/div[2]/form/table[1]/tbody/tr[5]/td/div/div[2]/div/div/table[contains(.,"Tipo Documento")]'
datos_empresa = '/html/body/div[1]/div[2]/form/table[2]/tbody/tr/td/div/div[2]/div/div/table[contains(.,"Razón Social")]'
tipos_documento = {
    'CC': 'Cédula De Ciudadanía',
    'CD': 'Carnet Diplomatico',
    'CE': 'Cedula Extranjeria',
    'CV': 'Permiso Especial de Permanencia',
    'PAS': 'Pasaporte',
    'PT': 'Permiso Protección Temporal',
    'TI': 'Tarjeta Identidad'
}
name_displayed = ''
name_appened = ''

encabezados_csv = 'Tipo_Documento, Documento, Nombre, Fecha_Nacimiento, Fecha_Ingreso_Empresa, Fecha_Afiliacion, Estado_Afiliado, Fecha_Retiro, Categoria, Tipo_Trabajador, Numero_Tarjeta, GP, Estado_Tarjeta, Fecha_Entrega_Tarjeta, Valor_ultimo_Subsidio, Ultimo_ciclo_pagado, Via_de_Pago, Motivo_Bloqueo, Tipo_Afiliacion, Tipo_Aporte_Afiliado, Porcentaje_Aporte_Afiliado, Mas_DAtos_afiliado, Grupo_Familiar, Datos_empresa'


# Crea el archivo plano con los encabezados
with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "w") as csv:
    csv.write(f"{encabezados_csv}\n")
    csv.close()

# Por cada documento afiliado que extrajo del query_afiliados
for clave in id_afiliados_dict:
    # Valida si el número de documento ya ha sido validado
    if clave not in id_validados:
        # Valida el tipo de documento para cambiar el filtro
        flag = False
        while not flag:
            try:
                # Ciclo for por si hay algún error al seleccionar el tipo de documento. Recorre hasta que coincide
                for valor in tipos_documento:
                    xpath = f"//label[text()='{tipos_documento[valor]}']"
                    tipo_de_documento = tipos_documento[id_afiliados_dict[clave]]
                    try:
                        chrome_driver.find_element(By.XPATH, xpath).click()
                        break
                    except:
                        pass

                tipo_ident = chrome_driver.find_element(By.CSS_SELECTOR, 'ul.ui-selectonemenu-items.ui-selectonemenu-list.ui-widget-content.ui-widget.ui-corner-all.ui-helper-reset')
                opcion = tipo_ident.find_elements(By.CSS_SELECTOR, "li.ui-selectonemenu-item.ui-selectonemenu-list-item.ui-corner-all")
                for op in opcion:
                    print('===========================================================================')
                    if op.text == tipo_de_documento:
                        print(f'Selecciona: {op.text} = {clave}')
                        op.click()
                        WebDriverWait(chrome_driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")))
                        break

                try:
                    doc = chrome_driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")
                    id_elemento = doc.get_attribute("id")
                    doc = chrome_driver.find_element(By.ID, id_elemento)
                    doc.send_keys(clave)
                    doc.send_keys(Keys.ENTER)

                    try:
                        WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located(
                            (By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label')))
                    except:
                        elemento = WebDriverWait(chrome_driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "ui-growl-title"))
                        )
                        # Verificar si el texto contiene "La consulta no arrojó resultados"
                        if "Atención: La consulta no arrojó resultados de afiliados" in elemento.text:
                            print("El texto 'La consulta no arrojó resultados' está presente en la página.")
                            doc = chrome_driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")
                            doc.send_keys(Keys.CONTROL + 'a')
                            doc.send_keys(Keys.BACKSPACE)
                            chrome_driver.refresh()
                            WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located(
                                (By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")))
                            flag = True
                            break
                        else:
                            print("El texto 'La consulta no arrojó resultados' no está presente en la página.")
                        print("El elemento no está presente en la página.")

                    # Validar si los datos ya se actualizaron en las tablas. A veces se queda pegado y cuando se da enter al buscar el
                    # documento la página no carga rápido y sigue arrojando los datos del documento anterior- consultado
                    if name_appened == '':
                        name_displayed = chrome_driver.find_element(By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label').text
                    else:
                        name_displayed = chrome_driver.find_element(By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label').text
                        while name_displayed == name_appened:
                            # WebDriverWait(chrome_driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label')))
                            name_displayed = chrome_driver.find_element(By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label').text

                    # Datos del afiliado
                    print('====Datos Afiliado======')
                    tabla_dtaf = chrome_driver.find_element(By.XPATH, datos_afiliado)
                    filas = tabla_dtaf.find_elements(By.TAG_NAME, "tr")
                    with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                        csv.write(id_afiliados_dict[clave] + "," + clave + ",")
                        try:
                            notif = chrome_driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/form/table[1]/tbody/tr[1]/td/div/div/ul/li/span[2]")
                            csv.write(f"{notif.text} ")
                        except:
                            pass

                    for fila in filas:
                        columnas = fila.find_elements(By.TAG_NAME, "td")
                        i = 1
                        for columna in columnas:
                            dato = columna.text + ","
                            print(dato)
                            if valpar(i):
                                if tipos_documento[id_afiliados_dict[clave]] in dato or clave in dato:
                                    continue
                                else:
                                    with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                        csv.write(dato)
                            i += 1

                    # Datos de afiliación
                    print('====Datos Afiliación======')
                    tabla_dtafcion = chrome_driver.find_element(By.XPATH, datos_afiliacion)
                    filas = tabla_dtafcion.find_elements(By.TAG_NAME, "tr")

                    for fila in filas:
                        columnas = fila.find_elements(By.TAG_NAME, "td")
                        i = 1
                        for columna in columnas:
                            dato = columna.text + ","
                            print(dato)
                            if valpar(i):
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write(dato)
                            i += 1

                    # Grilla más datos afiliación (Si los tiene)
                    try:
                        tabla_dtgrafcion = chrome_driver.find_element(By.XPATH, grilla_datos_afiliacion)
                        filas = tabla_dtgrafcion.find_elements(By.TAG_NAME, "tr")

                        for fila in filas:
                            columnas = fila.find_elements(By.TAG_NAME, "td")
                            if 'Código' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("{")
                                print("{")
                            for columna in columnas:
                                dato = columna.text + " - "
                                print(dato)
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write(dato)
                            if 'Código' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("} / ")
                                print("} / ")
                        with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                            csv.write(", ")
                    except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException):
                        print('No tiene más datos de afiliación')
                        with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                            csv.write(",")

                    # Grupo familiar
                    print('====Grupo Familiar======')
                    try:
                        tabla_dtgrfam = chrome_driver.find_element(By.XPATH, grupo_familiar)
                        filas = tabla_dtgrfam.find_elements(By.TAG_NAME, "tr")

                        for fila in filas:
                            columnas = fila.find_elements(By.TAG_NAME, "td")
                            if 'Tipo Documento' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("{")
                                print("{")
                            for columna in columnas:
                                dato = columna.text + " - "
                                print(dato)
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write(dato)
                            if 'Tipo Documento' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("} / ")
                                print("} / ")
                        with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                            csv.write(", ")
                        print(", ")
                    except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException):
                        print('No tiene datos de grupo familiar')
                        with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                            csv.write(",")

                    # Datos empresa
                    print('====Datos Empresa======')
                    try:
                        tabla_dtafcion = chrome_driver.find_element(By.XPATH, datos_empresa)
                        filas = tabla_dtafcion.find_elements(By.TAG_NAME, "tr")

                        for fila in filas:
                            columnas = fila.find_elements(By.TAG_NAME, "td")
                            if 'Razón Social' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("{")
                                print("{")
                            for columna in columnas:
                                dato = columna.text + " - "
                                print(dato)
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write(dato)
                            if 'Razón Social' not in fila.text:
                                with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                                    csv.write("} / ")
                                print("} / ")
                        with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                            csv.write(", ")
                        print(", ")
                    except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException):
                        print('No tiene datos de Empresa')

                    with open(fr"{ruta_archivo}\Afiliados_{hora_archivo}.csv", "a") as csv:
                        csv.write("\n")

                    id_validados.append(clave)

                    # Guarda el nombre de la persona que se acabó de consultar
                    name_appened = chrome_driver.find_element(By.XPATH, '//*[@id="j_idt16:j_idt42_content"]/table/tbody/tr[1]/td[2]/label').text

                    # Borrar número de documento para poder ingresar el siguiente, de lo contrario se pega seguido
                    doc = chrome_driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")
                    doc.send_keys(Keys.CONTROL + 'a')
                    doc.send_keys(Keys.BACKSPACE)
                    chrome_driver.refresh()
                    WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")))
                    flag = True

                except NoSuchElementException:
                    print('No hay datos para el documento')
                    doc = chrome_driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")
                    doc.send_keys(Keys.CONTROL + 'a')
                    doc.send_keys(Keys.BACKSPACE)
                    chrome_driver.refresh()
                    WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/form/div/div[2]/table/tbody/tr[3]/td[2]/input")))
                    flag = True
            except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException) as e:
                print(f'******No cargó bien, se vuelve a intentar****** {e}')
            except TimeoutException as time:
                print(f'******Hubo un problema de red, se vuelve a intentar****** {time}')
                chrome_driver.refresh()
                # Esperar hasta 10 segundos para que aparezca el elemento
                try:
                    elemento = WebDriverWait(chrome_driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ui-growl-title"))
                    )
                    # Verificar si el texto contiene "La consulta no arrojó resultados"
                    if "Atención: La consulta no arrojó resultados de afiliados" in elemento.text:
                        print("El texto 'La consulta no arrojó resultados' está presente en la página.")
                        flag = True
                    else:
                        print("El texto 'La consulta no arrojó resultados' no está presente en la página.")
                except:
                    print("El elemento no está presente en la página.")

time.sleep(2)




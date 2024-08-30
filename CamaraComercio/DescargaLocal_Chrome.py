from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common import NoAlertPresentException, ElementClickInterceptedException, NoSuchElementException, \
    StaleElementReferenceException, NoSuchDriverException, WebDriverException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from loginCCB import iniciar_sesion
import os
from datetime import datetime
import time

# Hora inicio
inicio = datetime.now()
if inicio.month < 10:
    if inicio.day < 10:
        hora_archivo = f'{inicio.year}0{inicio.month}0{inicio.day}'
    else:
        hora_archivo = f'{inicio.year}0{inicio.month}{inicio.day}'
else:
    hora_archivo = f'{inicio.year}{inicio.month}{inicio.day}'


# Variables para marcar los archivos que se descarguen
cant_archivos = 0
url_bd = 'https://sico.ccb.org.co/Sico/Paginas/frm_SolicitudInfo.aspx'
ruta_log = r'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs'
usuario = os.environ.get('usuario')
password = os.environ.get('password')


# Primer Flag para loguearse hasta que ingrese. A veces salen mensajes de alerta de que no se puede iniciar sesión.
iniciar_sesion(usuario, password)
chrome_driver = iniciar_sesion.chrome_driver

chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_menu_BDn2"]/table/tbody/tr/td/a').click()

# Conteo de filas de la tabla descargas
filas = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr')
cells = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[1]/th')


pagina = 1
flag_pag = False
while not flag_pag:
    try:
        i = 2
        for dato in range(2, len(filas)):
            # Espera a que la tabla esté disponible
            WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')))
            espera_tabla = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')
            # Desplázate hasta el elemento
            chrome_driver.execute_script("arguments[0].scrollIntoView(true);", espera_tabla)
            dato = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')
            dato_usuario = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[3]')
            name_file = dato.text
            correo = dato_usuario.text
            print(f'{name_file} ----->> {usuario}')
            val_ini_name = name_file[:8]
            if "andres.juliono@colsubsidio.com" in correo and name_file.startswith("20240620"):
                print("Archivo nuestro")
                # flag = False
                # while not flag:
                try:
                    descargar = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes_lnkDescargarDB_{i - 2}"]')
                    # if texto != '':
                    descargar.click()
                    time.sleep(1)
                    # Espera a que la tabla esté disponible
                    WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')))
                    espera_tabla = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')
                    chrome_driver.execute_script("arguments[0].scrollIntoView(true);", espera_tabla)
                    if espera_tabla:
                        flag = True
                        # Se asegura de que muestre la fila con los números de página
                        siguiente_pagina = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[12]/td/table/tbody/tr')
                        # Desplázate hasta el elemento
                        chrome_driver.execute_script("arguments[0].scrollIntoView(true);", siguiente_pagina)
                    else:
                        # Espera a que la tabla esté disponible
                        WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')))
                        espera_tabla = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')
                        chrome_driver.execute_script("arguments[0].scrollIntoView(true);", espera_tabla)
                        if espera_tabla:
                            flag = True
                            siguiente_pagina = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[12]/td/table/tbody/tr')
                            # Desplázate hasta el elemento
                            chrome_driver.execute_script("arguments[0].scrollIntoView(true);", siguiente_pagina)
                except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                    time.sleep(2)

                cant_archivos += 1
                with open(fr"{ruta_log}\Logs_DescargaLocal_{hora_archivo}.txt", "a") as file:
                    file.write(f'Archivo descargado: {name_file}\nArchivos descargados al corte: {cant_archivos}\n')

            i += 1

            siguiente_pagina = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[12]/td/table/tbody/tr')
            # Desplázate hasta el elemento
            chrome_driver.execute_script("arguments[0].scrollIntoView(true);", siguiente_pagina)

            if i == len(filas):
                pagina += 1
                try:
                    siguiente_pagina = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[12]/td/table/tbody/tr/td[{pagina}]/a')
                    # Desplázate hasta el elemento
                    chrome_driver.execute_script("arguments[0].scrollIntoView(true);", siguiente_pagina)
                    siguiente_pagina.click()

                    # Espera a que la tabla esté disponible
                    WebDriverWait(chrome_driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody')))
                    # Conteo de filas de la tabla descargas
                    filas = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr')
                    with open(fr"{ruta_log}\Logs_DescargaLocal_{hora_archivo}.txt", "a") as file:
                        file.write(f'==========> Avanza a la página {pagina} <============')
                except NoSuchElementException:
                    print("No hay más páginas")
                    flag_pag = True

    except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
        if cant_archivos > 80:
            with open(fr"{ruta_log}\Logs_DescargaLocal_{hora_archivo}.txt", "a") as file:
                print(f"La cantidad de archivos descargados es {cant_archivos}. Es posible que el error se haya "
                      f"generado porque el proceso ya terminó. Por favor revisar")
                file.write(f"La cantidad de archivos descargados es {cant_archivos}. Es posible que el error se haya "
                           f"generado porque el proceso ya terminó. Por favor revisar \n")
            flag_pag = True
        else:
            with open(fr"{ruta_log}\Logs_DescargaLocal_{hora_archivo}.txt", "a") as file:
                print(f"Ocurrió un error con la página. Se reinicia")
                file.write(f"Ocurrió un error con la página. Se reinicia \n")
            chrome_driver.quit()
            # Primer Flag para loguearse hasta que ingrese. A veces salen mensajes de alerta de que no se puede iniciar sesión.
            iniciar_sesion(usuario, password)
            WebDriverWait(chrome_driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_menu_BDn2"]/table/tbody/tr/td/a')))
            chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_menu_BDn2"]/table/tbody/tr/td/a').click()
            siguiente_pagina = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[12]/td/table/tbody/tr/td[{pagina}]/a')
            # Desplázate hasta el elemento
            chrome_driver.execute_script("arguments[0].scrollIntoView(true);", siguiente_pagina)
            siguiente_pagina.click()

            # Conteo de filas de la tabla descargas
            filas = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr')


with open(fr"{ruta_log}\Logs_DescargaLocal_{hora_archivo}.txt", "a") as file:
    print(f"Total archivos descargados: {cant_archivos}")
    file.write(f"Total archivos descargados: {cant_archivos}\n")

time.sleep(300)


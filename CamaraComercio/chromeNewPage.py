#!/usr/bin/python3
# Este archivo usa el encoding: utf-8
from selenium.common import NoAlertPresentException, ElementClickInterceptedException, NoSuchElementException, \
    StaleElementReferenceException, NoSuchDriverException, WebDriverException, TimeoutException, \
    UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from datetime import datetime
import inspect
import time
import os
import logging
from selenium.webdriver.support.wait import WebDriverWait
from loginCCB import crear_archivo, iniciar_sesion, extraer_ciudades_desde_archivo_mas_reciente, seleccionar_opcion_ciudad


# Hora inicio
inicio = datetime.now()
hora_archivo = f'{inicio.day}_{inicio.month}_{inicio.year}_{inicio.hour}{inicio.minute}{inicio.second}'


# Arrays para guardar valoresde filtros
ciudades = []
ciiu = []
año_matr = []
ciudades_descargadas = []

# Variables para marcar los archivos que se descarguen
vciudad = ''
vciiu = ''
vañomatr = ''
usuario = os.environ.get('usuario')
password = os.environ.get('password')
ruta_archivo = fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs"
archivo_log = crear_archivo(ruta_archivo)
# Directorio donde se encuentran los archivos log con las ciudades descargadas
log_ciudades_desc = r'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs\LogCiudadesDescargadas'
ciudades_descargadas = extraer_ciudades_desde_archivo_mas_reciente(log_ciudades_desc)
# Le ingresa al nuevo Log las ciudades descargadas
logging.basicConfig(filename=rf'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs\LogCiudadesDescargadas\log_ciudades_descargadas_{hora_archivo}.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
if ciudades_descargadas:
    for ciudad in ciudades_descargadas:
        logging.info(ciudad)

# Primer Flag para loguearse hasta que ingrese. A veces salen mensajes de alerta de que no se puede iniciar sesión.
iniciar_sesion(usuario, password)

chrome_driver = iniciar_sesion.chrome_driver
archivo_log.write(f"Hora inicio: {inicio} \n")

flag_alert = False
while not flag_alert:
    try:
        text = chrome_driver.switch_to.alert.text
        archivo_log.write(f"{text}\n")
        if text == '':
            time.sleep(2)
        else:
            chrome_driver.switch_to.alert.accept()
            flag_alert = True
    except NoAlertPresentException:
        print('No salió alerta de ingreso a la página de generación de bases')
        archivo_log.write('No salió alerta de ingreso a la página de generación de bases \n')
        inicia = WebDriverWait(iniciar_sesion.chrome_driver, 15).until(expected_conditions.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")))
        if inicia:
            flag_alert = True
            print('Ingresó a la página correctamente sin alertas')
        time.sleep(2)


# Llena el arreglo con las ciudades que hay en el filtro
list_ciudades = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCamaras")
opctO = list_ciudades.find_elements(By.TAG_NAME, "option")
for opcion in opctO:
    ciudades.append(opcion.text)
# ciudb = ciudades[5:10]

# Llena el arreglo de año de matrícula según los valores que hay en el filtro
list_am = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstAniosMatricula")
cant_años_mat = 0
opcam = list_am.find_elements(By.TAG_NAME, "option")
for opcion in opcam:
    cant_años_mat += 1


# Variables para validaciones
val_total_ciudad = 1
contador = 0
contador_ciiu = 0
option = 1
Descargar = False
flag_añomat = False
total_acumulado = 0
segundos = 0

# Segundo flag indica que el proceso no ha terminado y debe continuar
terminado = False
while not terminado:
    try:
        # Comenzar a seleccionar valores para los filtros
        for ciudad in ciudades:
            if ciudad in ciudades_descargadas: ## Valida que la ciudad que está descargando no esté descargada aún
                pass
            else:
                # Crea archivo de logs para seguimiento
                flag_ciiu = False
                while not flag_ciiu:

                    vciudad = seleccionar_opcion_ciudad(chrome_driver, ciudad, ciudades, archivo_log)

                    # list_ciu = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCamaras")
                    # opciu =  list_ciu.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_lstCamaras"]/option[{ciudades.index(ciudad) + 1}]')
                    # opciu.click()
                    # print(f"Opción seleccionada: {ciudades.index(ciudad) + 1} de {len(ciudades) - 1} ciudades")
                    # archivo_log.write(f"Opción seleccionada: {ciudades.index(ciudad) + 1} de {len(ciudades) - 1} ciudades\n")
                    # vciudad = opciu.text
                    # print(vciudad)
                    # archivo_log.write(f"{vciudad} \n")
                    # add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCamara")
                    # add.click()

                    flag_alert = False
                    while not flag_alert:
                        try:
                            text = chrome_driver.switch_to.alert.text
                            archivo_log.write(f"{text}\n")
                            if text == '':
                                time.sleep(2)
                                segundos += 2
                            else:
                                chrome_driver.switch_to.alert.accept()
                                segundos = 0
                                flag_alert = True
                        except NoAlertPresentException:
                            print('No salió alerta de adición de ciudad')
                            archivo_log.write('No salió alerta de adición de ciudad \n')
                            time.sleep(2)
                            segundos += 2
                            if segundos > 60:
                                # Refrescar página para evitar que se quede pegada
                                print("Excedió el minuto de espera. Se vuelve a recargar")
                                chrome_driver.refresh()
                                flag_alert = False
                                while not flag_alert:
                                    try:
                                        text = chrome_driver.switch_to.alert.text
                                        if text == '':
                                            time.sleep(2)
                                        else:
                                            chrome_driver.switch_to.alert.accept()
                                            flag_alert = True
                                    except NoAlertPresentException:
                                        print('No había alerta')
                                        time.sleep(2)

                                vciudad = seleccionar_opcion_ciudad(chrome_driver, ciudad, ciudades, archivo_log)

                                # list_ciu = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCamaras")
                                # opciu = list_ciu.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_lstCamaras"]/option[{ciudades.index(ciudad) + 1}]')
                                # opciu.click()
                                # chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCamara").click()
                                # add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCamara")
                                # add.click()

                                print("La alerta de adición de ciudad se demoró. Se vuelve a dar click en el botón de add ciudad")
                                archivo_log.write("La alerta de adición de ciudad se demoró. Se vuelve a dar click en el botón de add ciudad")
                                segundos = 0


                    sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                    reg_sel = int(sel.text)
                    val_total_ciudad = reg_sel

                    # Selecciona la opción letras para desplegar la tabla de CIIU
                    select_list_ciud = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_ddlCIIU")
                    selct = Select(select_list_ciud)
                    selct.select_by_visible_text(('Letras'))
                    time.sleep(2)
                    # Conteo de filas de la tabla de CIIU
                    rows = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr')
                    cells = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[1]/th')
                    print(len(rows))
                    print("Checkpoint 1 Conteo de filas de la tabla de Ciiu")
                    archivo_log.write("Checkpoint 1. Conteo de filas de la tabla de Ciiu\n")

                    if reg_sel <= 50000:
                        total_acumulado += reg_sel

                        print("Checkpoint 2. Descarga sin filtros")
                        archivo_log.write("Checkpoint 2. Descarga sin filtros\n")

                        flag_bott = False
                        while not flag_bott:
                            try:
                                # Encuentra el botón
                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]')
                                # Desplázate hasta el elemento
                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]').click() # Generar
                                #Validar si el botón de la siguiente página ya está disponible
                                try:
                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                    if semuestra == "Siguiente":
                                        flag_bott = True
                                except:
                                    time.sleep(5)
                            except:
                                print("no encontró el botón para generar base. Se vuelve a intentar")
                                archivo_log.write("no encontró el botón para generar base. Se vuelve a intentar\n")
                                try:
                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                    if semuestra == "Siguiente":
                                        flag_bott = True
                                except:
                                    time.sleep(5)


                        avanzar = False
                        while not avanzar:
                            try:
                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                if semuestra == "Siguiente":
                                    avanzar = True
                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').click()
                            except (NoSuchElementException, StaleElementReferenceException):
                                time.sleep(2)

                        avanzar = False
                        while not avanzar:
                            try:
                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').accessible_name  # Excluír
                                if semuestra == "Siguiente":
                                    avanzar = True
                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').click()
                            except (NoSuchElementException, StaleElementReferenceException):
                                time.sleep(2)

                        avanzar = False
                        while not avanzar:
                            try:
                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').accessible_name  # Límite registros
                                if semuestra == "Siguiente":
                                    avanzar = True
                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').click()  # Límite registros
                            except (NoSuchElementException, StaleElementReferenceException):
                                time.sleep(2)

                        avanzar = False
                        while not avanzar:
                            try:
                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').accessible_name  # Procesar BD
                                if semuestra == "Procesar Base de Datos":
                                    avanzar = True
                            except (NoSuchElementException, StaleElementReferenceException):
                                time.sleep(2)

                        name_bd = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_NombreDB")
                        name_bd.send_keys(f"{vciudad}Completo")

                        # Procesar base de datos
                        flag_bott = False
                        while not flag_bott:
                            try:
                                # Encuentra el botón
                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]')
                                # Desplázate hasta el elemento
                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').click()
                                # Validar si el botón de la siguiente página ya está disponible
                                try:
                                    text = chrome_driver.switch_to.alert.text
                                    archivo_log.write(f"{text}\n")
                                    print(text)
                                    if '¿Desea continuar con el procesamiento de esta base de datos?' in text:
                                        chrome_driver.switch_to.alert.accept()
                                        flag_bott = True
                                except NoAlertPresentException:
                                    print('NO hay alerta en procesamiento de base')
                            except:
                                print("no encontró el botón para procesamiento de base. Se vuelve a intentar")
                                archivo_log.write("no encontró el botón para procesamiento de base. Se vuelve a intentar\n")
                        # Procesar BD

                        # flag_alert = False
                        # while not flag_alert:
                        #     try:
                        #         text = chrome_driver.switch_to.alert.text
                        #         archivo_log.write(f"{text}\n")
                        #         print(text)
                        #         if text == '':
                        #             time.sleep(2)
                        #         else:
                        #             chrome_driver.switch_to.alert.accept()
                        #             flag_alert = True
                        #     except NoAlertPresentException:
                        #         print('No salió alerta de generación de base')
                        #         archivo_log.write('No salió alerta de generación de base \n')
                        #         time.sleep(2)

                        segundos = 0
                        flag_alert = False
                        while not flag_alert:
                            try:
                                text = chrome_driver.switch_to.alert.text
                                archivo_log.write(f"{text}\n")
                                print(text)
                                if text == '':
                                    time.sleep(2)
                                elif text != '' and segundos < 60:
                                    chrome_driver.switch_to.alert.accept()
                                    flag_alert = True
                                elif segundos > 60:
                                    chrome_driver.refresh()
                                    segundos = 0
                            except NoAlertPresentException:
                                print('No salió alerta de confirmación de generación de base')
                                archivo_log.write('No salió alerta de confirmación generación de base \n')
                                time.sleep(2)
                                segundos += 2
                                if segundos > 60:
                                    chrome_driver.refresh()
                                    segundos = 0

                        segundos = 0
                        flag_alert = False
                        while not flag_alert:
                            try:
                                text = chrome_driver.switch_to.alert.text
                                if text == '':
                                    time.sleep(2)
                                elif text != '':
                                    chrome_driver.switch_to.alert.accept()
                                    flag_alert = True
                                elif segundos > 60:
                                    chrome_driver.refresh()
                                    segundos = 0
                            except NoAlertPresentException:
                                print('No salió alerta de ingreso a la página de BD')
                                archivo_log.write('No salió alerta de ingreso a la página de BD \n')
                                time.sleep(2)
                                segundos += 2
                                if segundos > 60:
                                    chrome_driver.refresh()
                                    segundos = 0

                        option += 1
                        flag_ciiu = True
                        print(f"Descarga total ciudad sin filtros. Total registros: {reg_sel} \n *** Total acumulado: {total_acumulado} ***")
                        archivo_log.write(f"Descarga total ciudad sin filtros. Total registros: {reg_sel} \n *** Total acumulado: {total_acumulado} ***\n")
                        # Agregar la ciudad a la lista de ciudades descargadas para no volverlas a descargar
                        if vciudad not in ciudades_descargadas:
                            ciudades_descargadas.append(vciudad)
                            logging.info(vciudad)

                    esperar = 0
                    while reg_sel > 50000:
                        print("Entró a mayor a 50mil")
                        esperar += 1
                        # Conteo de filas de la tabla de CIIU
                        rows = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr')
                        cells = chrome_driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[1]/th')
                        # Validar si ya hay algún ciiu o año matricula seleccionado
                        list_ciudades_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                        opcion_ciuu = list_ciudades_fill.find_elements(By.TAG_NAME, "option")
                        list_años = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstAniosMatriculaFil")
                        opcion_años = list_años.find_elements(By.TAG_NAME, "option")

                        if len(año_matr) > 0 and len(opcion_ciuu) == 0:
                            ActionChains(chrome_driver).send_keys(Keys.ESCAPE).perform()
                            dato = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[{len(ciiu) + 1}]/td[{1}]')
                            inputs = dato.find_elements(By.TAG_NAME, "input")
                            for inp in inputs:
                                # Desplázate hasta el elemento
                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                                inp.click()

                            # Para Validar si el numero de ciiu seleccionadas ya aumentó
                            list_ciiu_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                            opcion_ciuu = list_ciiu_fill.find_elements(By.TAG_NAME, "option")
                            cant_ini = len(opcion_ciuu)

                            # Click en el botón de agregar ciiu
                            add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCIIU")
                            add.click()
                            time.sleep(1)

                            # Para Validar si el número de ciiu seleccionadas ya aumentó. Espera el span y presiona escape
                            print("Entra a Validar si el número de ciiu seleccionadas ya aumentó. Espera el span y presiona escape")
                            cant_fin = 0
                            segundos = 0
                            while cant_fin <= cant_ini:
                                time.sleep(2)
                                segundos += 2
                                if segundos > 60:
                                    print("La alerta de adición de Ciiu se demoró. Se vuelve a dar click en el botón de add Ciiu")
                                    archivo_log.write("La alerta de adición de Ciiu se demoró. Se vuelve a dar click en el botón de add Ciiu")
                                    dato = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[{len(ciiu) + 1}]/td[{1}]')
                                    inputs = dato.find_elements(By.TAG_NAME, "input")
                                    for inp in inputs:
                                        if not inp.is_selected():
                                            # Desplázate hasta el elemento
                                            chrome_driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                                            inp.click()
                                        else:
                                            pass
                                    chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCIIU").click()
                                    segundos = 0
                                try:
                                    list_ciudades_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                                    opcion_ciuu = list_ciudades_fill.find_elements(By.TAG_NAME, "option")
                                    cant_fin = len(opcion_ciuu)
                                except StaleElementReferenceException:
                                    print("No encontró el elemento")
                                    archivo_log.write("No encontró el elemento. Esperando adicionar ciiu\n")

                            ActionChains(chrome_driver).send_keys(Keys.ESCAPE).perform()
                            vciiu = ciiu[len(ciiu) - 1]
                            sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                            val_total_ciiu = int(sel.text)


                        elif len(opcion_ciuu) == 0 and len(opcion_años) == 0:
                            for r in range(len(ciiu) + 2, len(rows) + 2):
                                # Ingresa al filtro por letras de CIIU
                                # Valida en donde quedó desde la última descarga, si continua donde quedó o empieza de nuevo
                                if not flag_ciiu and not Descargar and len(año_matr) == 0:
                                    if r > 23:
                                        Descargar = True
                                        pass
                                        sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                        reg_sel = int(sel.text)
                                        contador += reg_sel
                                        total_acumulado += reg_sel

                                        print(f"Procede a descargar con 2 filtros. Ciudad y Ciiu. Línea {inspect.currentframe().f_lineno}")
                                        archivo_log.write(f"Procede a descargar con 2 filtros. Ciudad y Ciiu. Línea {inspect.currentframe().f_lineno}")

                                        flag_bott = False
                                        while not flag_bott:
                                            try:
                                                # Encuentra el botón
                                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]')
                                                # Desplázate hasta el elemento
                                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]').click()  # Generar
                                                # Validar si el botón de la siguiente página ya está disponible
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                    if semuestra == "Siguiente":
                                                        flag_bott = True
                                                except:
                                                    time.sleep(5)
                                            except:
                                                print("no encontró el botón para generar base. Se vuelve a intentar")
                                                archivo_log.write(
                                                    "no encontró el botón para generar base. Se vuelve a intentar\n")
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                    if semuestra == "Siguiente":
                                                        flag_bott = True
                                                except:
                                                    time.sleep(5)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').click()
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').accessible_name  # Excluír
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').click()
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').accessible_name  # Límite registros
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').click()  # Límite registros
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').accessible_name  # Procesar BD
                                                if semuestra == "Procesar Base de Datos":
                                                    avanzar = True
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        name_bd = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_NombreDB")
                                        name_bd.send_keys(f"{vciudad}{ciiu[0]}Hasta{ciiu[-1]}")

                                        # Procesar base de datos
                                        flag_bott = False
                                        while not flag_bott:
                                            try:
                                                # Encuentra el botón
                                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]')
                                                # Desplázate hasta el elemento
                                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').click()
                                                # Validar si el botón de la siguiente página ya está disponible
                                                try:
                                                    text = chrome_driver.switch_to.alert.text
                                                    archivo_log.write(f"{text}\n")
                                                    print(text)
                                                    if '¿Desea continuar con el procesamiento de esta base de datos?' in text:
                                                        chrome_driver.switch_to.alert.accept()
                                                        flag_bott = True
                                                except NoAlertPresentException:
                                                    print('NO hay alerta en procesamiento de base')
                                            except:
                                                print("no encontró el botón para procesamiento de base. Se vuelve a intentar")
                                                archivo_log.write("no encontró el botón para procesamiento de base. Se vuelve a intentar\n")
                                        # Procesar BD

                                        # flag_alert = False
                                        # while not flag_alert:
                                        #     try:
                                        #         text = chrome_driver.switch_to.alert.text
                                        #         archivo_log.write(f"{text}\n")
                                        #         print(text)
                                        #         if text == '':
                                        #             time.sleep(2)
                                        #         else:
                                        #             chrome_driver.switch_to.alert.accept()
                                        #             flag_alert = True
                                        #     except NoAlertPresentException:
                                        #         print('No salió alerta de generación de base')
                                        #         archivo_log.write('No salió alerta de generación de base \n')
                                        #         time.sleep(2)

                                        segundos = 0
                                        flag_alert = False
                                        while not flag_alert:
                                            try:
                                                text = chrome_driver.switch_to.alert.text
                                                archivo_log.write(f"{text}\n")
                                                print(text)
                                                if text == '':
                                                    time.sleep(2)
                                                elif text != '' and segundos < 60:
                                                    chrome_driver.switch_to.alert.accept()
                                                    flag_alert = True
                                                elif segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0
                                            except NoAlertPresentException:
                                                print('No salió alerta de confirmación de generación de base')
                                                archivo_log.write('No salió alerta de confirmación generación de base \n')
                                                time.sleep(2)
                                                segundos += 2
                                                if segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0

                                        segundos = 0
                                        flag_alert = False
                                        while not flag_alert:
                                            try:
                                                text = chrome_driver.switch_to.alert.text
                                                if text == '':
                                                    time.sleep(2)
                                                elif text != '':
                                                    chrome_driver.switch_to.alert.accept()
                                                    flag_alert = True
                                                elif segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0
                                            except NoAlertPresentException:
                                                print('No salió alerta de ingreso a la página de BD')
                                                archivo_log.write('No salió alerta de ingreso a la página de BD \n')
                                                time.sleep(2)
                                                segundos += 2
                                                if segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0

                                        print(f"\n ------>>>> Descarga con 2 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)}. \n Registros en esta descarga {reg_sel} <<<<------ \n *** Total acumulado: {total_acumulado} ***")
                                        archivo_log.write(f"\n ------>>>> Descarga con 2 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)}. \n Registros en esta descarga {reg_sel} <<<<------ \n *** Total acumulado: {total_acumulado} ***\n")
                                        Descargar = False
                                        # Agregar la ciudad a la lista de ciudades descargadas para no volverlas a descargar
                                        if vciudad not in ciudades_descargadas:
                                            ciudades_descargadas.append(vciudad)
                                            logging.info(vciudad)

                                        if contador == val_total_ciudad or r == 23:
                                            print(f"Total registros: {contador}")
                                            archivo_log.write(f"Total registros: {contador}")
                                            flag_ciiu = True
                                            option += 1
                                            contador = 0
                                            val_total_ciudad = 1
                                            ciiu.clear()
                                        break
                                    #################################################################################################

                                    ActionChains(chrome_driver).send_keys(Keys.ESCAPE).perform()
                                    dato = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[{r}]/td[{1}]')
                                    ciiu.append(chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_grdCIIULetras"]/tbody/tr[{r}]/td[{2}]').text)
                                    inputs = dato.find_elements(By.TAG_NAME, "input")
                                    # Desplázate hacia abajo 100 píxeles
                                    chrome_driver.execute_script("window.scrollBy(0, 50);")
                                    for inp in inputs:
                                        # Desplázate hasta el elemento
                                        chrome_driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                                        inp.click()

                                    # Para Validar si el numero de ciiu seleccionadas ya aumentó
                                    list_ciiu_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                                    opcion_ciuu = list_ciiu_fill.find_elements(By.TAG_NAME, "option")
                                    cant_ini = len(opcion_ciuu)

                                    # Click en el botón de agregar ciiu
                                    add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCIIU")
                                    add.click()

                                    # Para Validar si el número de ciiu seleccionadas ya aumentó. Espera el span y presiona escape
                                    cant_fin = 0
                                    segundos = 0
                                    while cant_fin <= cant_ini:
                                        time.sleep(2)
                                        segundos += 2
                                        if segundos > 60:
                                            print("La alerta de adición de Ciiu se demoró. Se vuelve a dar click en el botón de add Ciiu")
                                            archivo_log.write("La alerta de adición de Ciiu se demoró. Se vuelve a dar click en el botón de add Ciiu")
                                            chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCIIU").click()
                                            segundos = 0
                                        try:
                                            list_ciudades_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                                            opcion_ciuu = list_ciudades_fill.find_elements(By.TAG_NAME, "option")
                                            cant_fin = len(opcion_ciuu)
                                        except StaleElementReferenceException:
                                            print("No encontró el elemento")
                                            archivo_log.write("No encontró el elemento. Esperando adicionar ciiu\n")

                                    ActionChains(chrome_driver).send_keys(Keys.ESCAPE).perform()
                                    vciiu = ciiu[len(ciiu) - 1]
                                    sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                    reg_sel = int(sel.text)
                                    val_total_ciiu = int(sel.text)
                                    print("Checkpoint Add Ciius")
                                    archivo_log.write("Checkpoint Add Ciius\n")

                                if reg_sel < 50000 and len(ciiu) < 22 and not Descargar:
                                    pass
                                elif reg_sel > 50000:
                                    break

                        ########################################################################################
                        elif len(año_matr) >= 0 and len(opcion_ciuu) > 0:
                            # Elimina la última opción que se anexó al filtro de CIUU para validar que vuelva a ser menor o igual
                            # a 50Mil; sino es el caso entonces accede al filtro de año matrícula
                            list_ciudades_fill = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCIIUFil")
                            opcion_ciuu = list_ciudades_fill.find_elements(By.TAG_NAME, "option")
                            if len(opcion_ciuu) == 1:
                                # Filtro año matrícula
                                for año in range(1, cant_años_mat):
                                    if not Descargar:
                                        año = len(año_matr) + 1
                                        if len(año_matr) > 93:
                                            Descargar = True
                                            pass
                                        else:
                                            list_am = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstAniosMatricula")
                                            opcam = list_am.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_lstAniosMatricula"]/option[{año}]')
                                            opcam.click()
                                            año_matr.append(opcam.text)
                                            add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddFecMat")
                                            add.click()

                                            segundos = 0
                                            flag_alert = False
                                            while not flag_alert:
                                                try:
                                                    text = chrome_driver.switch_to.alert.text
                                                    print(f"El texto del mensaje de alerta de año matricula dice: {text}")
                                                    archivo_log.write(f"El texto del mensaje de alerta de año matricula dice: {text}\n")
                                                    if text == '' and segundos < 60:
                                                        time.sleep(2)
                                                        segundos += 2
                                                    elif text != '':
                                                        chrome_driver.switch_to.alert.accept()
                                                        flag_alert = True
                                                except NoAlertPresentException:
                                                    print('No había alerta de agregación de año matricula')
                                                    archivo_log.write('No había alerta de agregación de año matricula\n')
                                                    time.sleep(2)
                                                    segundos += 2
                                                    if segundos > 60:
                                                        print("La alerta de adición de año matrícula se demoró. Se vuelve a dar click en el botón de add año matrícula")
                                                        archivo_log.write("La alerta de adición de año matrícula se demoró. Se vuelve a dar click en el botón de año matrícula")
                                                        segundos = 0
                                                        chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddFecMat").click()

                                            sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                            reg_sel = int(sel.text)


                                    if reg_sel < 50000 and len(año_matr) < 93 and not Descargar and (contador_ciiu + reg_sel) < val_total_ciiu:
                                        print("Checkpoint 5 ------->> año matricula menor a 50mil")
                                        archivo_log.write("Checkpoint 5 ------->> año matricula menor a 50mil\n")
                                        pass
                                    elif reg_sel > 50000 or reg_sel == 0:
                                        list_años = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstAniosMatriculaFil")
                                        opcion_años = list_años.find_elements(By.TAG_NAME, "option")
                                        # Valida que los años seleccionados no excedan los 50000 registros, en caso tal,
                                        # elimina el último año seleccionado
                                        for opcion in opcion_años:
                                            if opcion_años.index(opcion) == len(opcion_años) - 1:
                                                opcion.click()
                                                chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnRemFecMat").click()

                                                flag_alert = False
                                                while not flag_alert:
                                                    try:
                                                        alert = WebDriverWait(chrome_driver,10).until(EC.alert_is_present())
                                                        text = chrome_driver.switch_to.alert.text
                                                        print(f"El texto del mensaje de alerta dice: {text}")
                                                        archivo_log.write(f"El texto del mensaje de alerta dice: {text}\n")
                                                        alert.accept()
                                                        flag_alert = True
                                                    except (TimeoutException, NoAlertPresentException):
                                                        print('No había alerta de eliminación de año de matricula')
                                                        archivo_log.write('No había alerta de eliminación de año de matricula\n')


                                                año_matr.pop()
                                                sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                                reg_sel = int(sel.text)
                                                Descargar = True
                                                break

                                    elif len(año_matr) >= 93 or Descargar or (contador_ciiu + reg_sel) == val_total_ciiu:
                                        sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                        reg_sel = int(sel.text)
                                        contador += reg_sel
                                        contador_ciiu += reg_sel
                                        val_total_ciudad += reg_sel
                                        total_acumulado += reg_sel

                                        print(f"Procede a generar base con 3 filtros. Línea {inspect.currentframe().f_lineno}")
                                        archivo_log.write(f"Procede a generar base con 3 filtros. Línea {inspect.currentframe().f_lineno}")

                                        flag_bott = False
                                        while not flag_bott:
                                            try:
                                                # Encuentra el botón
                                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]')
                                                # Desplázate hasta el elemento
                                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]').click()  # Generar
                                                # Validar si el botón de la siguiente página ya está disponible
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                    if semuestra == "Siguiente":
                                                        flag_bott = True
                                                except:
                                                    time.sleep(5)
                                            except:
                                                print("no encontró el botón para generar base. Se vuelve a intentar")
                                                archivo_log.write(
                                                    "no encontró el botón para generar base. Se vuelve a intentar\n")
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                    if semuestra == "Siguiente":
                                                        flag_bott = True
                                                except:
                                                    time.sleep(5)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').click()
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)


                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').accessible_name  # Excluír
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').click()
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').accessible_name  # Límite registros
                                                if semuestra == "Siguiente":
                                                    avanzar = True
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').click()  # Límite registros
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        avanzar = False
                                        while not avanzar:
                                            try:
                                                semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').accessible_name  # Procesar BD
                                                if semuestra == "Procesar Base de Datos":
                                                    avanzar = True
                                            except (NoSuchElementException, StaleElementReferenceException):
                                                time.sleep(2)

                                        name_bd = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_NombreDB")
                                        name_bd.send_keys(f"{vciudad}{ciiu[-1]}{año_matr[0]}Hasta{año_matr[-1]}")

                                        # Procesar base de datos
                                        flag_bott = False
                                        while not flag_bott:
                                            try:
                                                # Encuentra el botón
                                                generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]')
                                                # Desplázate hasta el elemento
                                                chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').click()
                                                # Validar si el botón de la siguiente página ya está disponible
                                                try:
                                                    text = chrome_driver.switch_to.alert.text
                                                    archivo_log.write(f"{text}\n")
                                                    print(text)
                                                    if '¿Desea continuar con el procesamiento de esta base de datos?' in text:
                                                        chrome_driver.switch_to.alert.accept()
                                                        flag_bott = True
                                                except NoAlertPresentException:
                                                    print('NO hay alerta en procesamiento de base')
                                            except:
                                                print("no encontró el botón para procesamiento de base. Se vuelve a intentar")
                                                archivo_log.write("no encontró el botón para procesamiento de base. Se vuelve a intentar\n")
                                        # Procesar BD

                                        # flag_alert = False
                                        # while not flag_alert:
                                        #     try:
                                        #         text = chrome_driver.switch_to.alert.text
                                        #         archivo_log.write(f"{text}\n")
                                        #         print(text)
                                        #         if text == '':
                                        #             time.sleep(2)
                                        #         else:
                                        #             chrome_driver.switch_to.alert.accept()
                                        #             flag_alert = True
                                        #     except NoAlertPresentException:
                                        #         print('No salió alerta de generación de base')
                                        #         archivo_log.write('No salió alerta de generación de base \n')
                                        #         time.sleep(2)

                                        segundos = 0
                                        flag_alert = False
                                        while not flag_alert:
                                            try:
                                                text = chrome_driver.switch_to.alert.text
                                                archivo_log.write(f"{text}\n")
                                                print(text)
                                                if text == '':
                                                    time.sleep(2)
                                                elif text != '' and segundos < 60:
                                                    chrome_driver.switch_to.alert.accept()
                                                    flag_alert = True
                                                elif segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0
                                            except NoAlertPresentException:
                                                print('No salió alerta de confirmación de generación de base')
                                                archivo_log.write('No salió alerta de confirmación generación de base \n')
                                                time.sleep(2)
                                                segundos += 2
                                                if segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0

                                        segundos = 0
                                        flag_alert = False
                                        while not flag_alert:
                                            try:
                                                text = chrome_driver.switch_to.alert.text
                                                if text == '':
                                                    time.sleep(2)
                                                elif text != '':
                                                    chrome_driver.switch_to.alert.accept()
                                                    flag_alert = True
                                                elif segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0
                                            except NoAlertPresentException:
                                                print('No salió alerta de ingreso a la página de BD')
                                                archivo_log.write('No salió alerta de ingreso a la página de BD \n')
                                                time.sleep(2)
                                                segundos += 2
                                                if segundos > 60:
                                                    chrome_driver.refresh()
                                                    segundos = 0

                                        print(f"\n----->>>> Descarga con 3 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)} y año matricula {', '.join(año_matr)}.\n Registros en esta descarga: {reg_sel} <<<<<--------\n *** Total acumulado: {total_acumulado} ***")
                                        archivo_log.write(f"\n----->>>> Descarga con 3 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)} y año matricula {', '.join(año_matr)}.\n Registros en esta descarga: {reg_sel} <<<<<--------\n *** Total acumulado: {total_acumulado} ***\n")
                                        Descargar = False
                                        # Agregar la ciudad a la lista de ciudades descargadas para no volverlas a descargar
                                        if vciudad not in ciudades_descargadas:
                                            ciudades_descargadas.append(vciudad)
                                            logging.info(vciudad)

                                        if contador_ciiu == val_total_ciiu or len(año_matr) == 93:
                                            print(f"Total registros: {contador_ciiu + reg_sel}")
                                            archivo_log.write(f"Total registros: {contador_ciiu + reg_sel}\n")
                                            flag_añomat = True
                                            año_matr.clear()
                                            r = len(ciiu) + 2
                                            contador_ciiu = 0
                                            val_total_ciiu = 1
                                        break
                                break

                            elif len(opcion_ciuu) > 1:
                                # eliminar la última letra que se agregó al filtro de CIIU
                                for opcion in opcion_ciuu:
                                    if opcion_ciuu.index(opcion) == len(opcion_ciuu) - 1:
                                        opcion.click()
                                        chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnRemCIIU").click()
                                        flag_alert = False
                                        while not flag_alert:
                                            try:
                                                text = chrome_driver.switch_to.alert.text
                                                print(text)
                                                archivo_log.write(f"{text}\n")
                                                if text == '':
                                                    time.sleep(2)
                                                else:
                                                    chrome_driver.switch_to.alert.accept()
                                                    flag_alert = True
                                            except NoAlertPresentException:
                                                print('No había alerta de eliminación de Ciiu')
                                                archivo_log.write('No había alerta de eliminación de Ciiu')
                                                time.sleep(2)

                                        ciiu.pop()
                                        sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                        reg_sel = int(sel.text)
                                        Descargar = True
                                        pass

                                        if len(ciiu) >= 22 or Descargar:
                                            sel = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")
                                            reg_sel = int(sel.text)
                                            contador += reg_sel
                                            total_acumulado += reg_sel

                                            print(f"Procede a descargar con 2 filtros. Ciudad y Ciiu. Línea {inspect.currentframe().f_lineno}")
                                            archivo_log.write(f"Procede a descargar con 2 filtros. Ciudad y Ciiu. Línea {inspect.currentframe().f_lineno}")

                                            flag_bott = False
                                            while not flag_bott:
                                                try:
                                                    # Encuentra el botón
                                                    generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]')
                                                    # Desplázate hasta el elemento
                                                    chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BD"]').click()  # Generar
                                                    # Validar si el botón de la siguiente página ya está disponible
                                                    try:
                                                        semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                        if semuestra == "Siguiente":
                                                            flag_bott = True
                                                    except:
                                                        time.sleep(5)
                                                except:
                                                    print("no encontró el botón para generar base. Se vuelve a intentar")
                                                    archivo_log.write("no encontró el botón para generar base. Se vuelve a intentar\n")
                                                    try:
                                                        semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                        if semuestra == "Siguiente":
                                                            flag_bott = True
                                                    except:
                                                        time.sleep(5)

                                            avanzar = False
                                            while not avanzar:
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').accessible_name  # Ordenar
                                                    if semuestra == "Siguiente":
                                                        avanzar = True
                                                        chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC1"]').click()
                                                except (NoSuchElementException, StaleElementReferenceException):
                                                    time.sleep(2)

                                            avanzar = False
                                            while not avanzar:
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').accessible_name  # Excluír
                                                    if semuestra == "Siguiente":
                                                        avanzar = True
                                                        chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC3"]').click()
                                                except (NoSuchElementException, StaleElementReferenceException):
                                                    time.sleep(2)

                                            avanzar = False
                                            while not avanzar:
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').accessible_name  # Límite registros
                                                    if semuestra == "Siguiente":
                                                        avanzar = True
                                                        chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_BtnSiguienteC2"]').click()  # Límite registros
                                                except (NoSuchElementException, StaleElementReferenceException):
                                                    time.sleep(2)

                                            avanzar = False
                                            while not avanzar:
                                                try:
                                                    semuestra = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').accessible_name  # Procesar BD
                                                    if semuestra == "Procesar Base de Datos":
                                                        avanzar = True
                                                except (NoSuchElementException, StaleElementReferenceException):
                                                    time.sleep(2)

                                            name_bd = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_NombreDB")
                                            name_bd.send_keys(f"{vciudad}{ciiu[0]}Hasta{ciiu[-1]}")

                                            # Procesar base de datos
                                            flag_bott = False
                                            while not flag_bott:
                                                try:
                                                    # Encuentra el botón
                                                    generar_bd_button = chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]')
                                                    # Desplázate hasta el elemento
                                                    chrome_driver.execute_script("arguments[0].scrollIntoView(true);", generar_bd_button)
                                                    chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_Generar_BaseDatos"]').click()
                                                    # Validar si el botón de la siguiente página ya está disponible
                                                    try:
                                                        text = chrome_driver.switch_to.alert.text
                                                        archivo_log.write(f"{text}\n")
                                                        print(text)
                                                        if '¿Desea continuar con el procesamiento de esta base de datos?' in text:
                                                            chrome_driver.switch_to.alert.accept()
                                                            flag_bott = True
                                                    except NoAlertPresentException:
                                                        print('NO hay alerta en procesamiento de base')
                                                except:
                                                    print("no encontró el botón para procesamiento de base. Se vuelve a intentar")
                                                    archivo_log.write("no encontró el botón para procesamiento de base. Se vuelve a intentar\n")
                                            # Procesar BD

                                            # flag_alert = False
                                            # while not flag_alert:
                                            #     try:
                                            #         text = chrome_driver.switch_to.alert.text
                                            #         archivo_log.write(f"{text}\n")
                                            #         print(text)
                                            #         if text == '':
                                            #             time.sleep(2)
                                            #         else:
                                            #             chrome_driver.switch_to.alert.accept()
                                            #             flag_alert = True
                                            #     except NoAlertPresentException:
                                            #         print('No salió alerta de generación de base')
                                            #         archivo_log.write('No salió alerta de generación de base \n')
                                            #         time.sleep(2)

                                            segundos = 0
                                            flag_alert = False
                                            while not flag_alert:
                                                try:
                                                    text = chrome_driver.switch_to.alert.text
                                                    archivo_log.write(f"{text}\n")
                                                    print(text)
                                                    if text == '':
                                                        time.sleep(2)
                                                    elif text != '' and segundos < 60:
                                                        chrome_driver.switch_to.alert.accept()
                                                        flag_alert = True
                                                    elif segundos > 60:
                                                        chrome_driver.refresh()
                                                        segundos = 0
                                                except NoAlertPresentException:
                                                    print('No salió alerta de confirmación de generación de base')
                                                    archivo_log.write('No salió alerta de confirmación generación de base \n')
                                                    time.sleep(2)
                                                    segundos += 2
                                                    if segundos > 60:
                                                        chrome_driver.refresh()
                                                        segundos = 0

                                            segundos = 0
                                            flag_alert = False
                                            while not flag_alert:
                                                try:
                                                    text = chrome_driver.switch_to.alert.text
                                                    if text == '':
                                                        time.sleep(2)
                                                    elif text != '':
                                                        chrome_driver.switch_to.alert.accept()
                                                        flag_alert = True
                                                    elif segundos > 60:
                                                        chrome_driver.refresh()
                                                        segundos = 0
                                                except NoAlertPresentException:
                                                    print('No salió alerta de ingreso a la página de BD')
                                                    archivo_log.write('No salió alerta de ingreso a la página de BD \n')
                                                    time.sleep(2)
                                                    segundos += 2
                                                    if segundos > 60:
                                                        chrome_driver.refresh()
                                                        segundos = 0

                                            print(f"\n ------>>>> Descarga con 2 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)}. \n Registros en esta descarga {reg_sel} <<<<------ \n *** Total acumulado: {total_acumulado} ***")
                                            archivo_log.write(f"\n ------>>>> Descarga con 2 filtros; Ciudad {ciudad} y ciiu {', '.join(ciiu)}. \n Registros en esta descarga {reg_sel} <<<<------ \n *** Total acumulado: {total_acumulado} ***\n")
                                            Descargar = False
                                            # Agregar la ciudad a la lista de ciudades descargadas para no volverlas a descargar
                                            if vciudad not in ciudades_descargadas:
                                                ciudades_descargadas.append(vciudad)
                                                logging.info(vciudad)

                                            if contador == val_total_ciudad or r == 23:
                                                print(f"Total registros: {contador}")
                                                archivo_log.write(f"Total registros: {contador}\n")
                                                flag_ciiu = True
                                                option += 1
                                                contador = 0
                                                val_total_ciudad = 1
                                                ciiu.clear()
                                            break

                                        elif flag_añomat and not flag_ciiu and not Descargar:
                                            flag_añomat = False
                                            break
                            elif esperar > 60:
                                chrome_driver.refresh()
                                esperar = 0


                    # Hora fin
                    fin = datetime.now()
                    archivo_log.write(f"Hora finalización: {fin} \n")

        terminado = True

    except (NoSuchElementException, StaleElementReferenceException, UnexpectedAlertPresentException):
        print("******** Un error ocurrió durante el proceso. Por culpa de la página. Se reinicia**********")
        archivo_log.write("******** Un error ocurrió durante el proceso. Por culpa de la página. Se reinicia**********")
        chrome_driver.quit()

        if ciudades_descargadas[-1] == vciudad:
            ciudades_descargadas.pop()



    # Vuelve a loguearse hasta que ingrese. A veces salen mensajes de alerta de que no se puede iniciar sesión.
    if not terminado:
        iniciar_sesion(usuario, password)

# Hora fin
print(f"El proceso finalizó con exito a las: {datetime.now()}")
archivo_log.close()
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
import re

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

texto = """
[Archivo descargado: 20250408054326853_VILLAVICENCIOAHastaX.xlsx
Archivos descargados al corte: 1
Archivo descargado: 20250408054334173_VILLAVICENCIOAHastaH.xlsx
Archivos descargados al corte: 2
Archivo descargado: 20250408054138409_VALLEDUPARCompleto.xlsx
Archivos descargados al corte: 3
Archivo descargado: 20250408053948893_URABACompleto.xlsx
Archivos descargados al corte: 4
Archivo descargado: 20250408054324131_TUNJACompleto.xlsx
Archivos descargados al corte: 5
Archivo descargado: 20250408053640615_TUMACOCompleto.xlsx
Archivos descargados al corte: 6
Archivo descargado: 20250408053811095_SUR Y ORIENTE DEL TOLIMACompleto.xlsx
Archivos descargados al corte: 7
Archivo descargado: 20250408053458131_SINCELEJOCompleto.xlsx
Archivos descargados al corte: 8
Archivo descargado: 20250408053336525_SEVILLACompleto.xlsx
Archivos descargados al corte: 9
Archivo descargado: 20250408053322955_SANTA ROSA DE CABALCompleto.xlsx
Archivos descargados al corte: 10
==========> Avanza a la página 2 <============Archivo descargado: 20250408054326853_VILLAVICENCIOAHastaX.xlsx
Archivos descargados al corte: 11
Archivo descargado: 20250408053534534_SANTA MARTAAHastaL.xlsx
Archivos descargados al corte: 12
Archivo descargado: 20250408053140469_RIOHACHACompleto.xlsx
Archivos descargados al corte: 13
Archivo descargado: 20250408052924972_QUIBDOCompleto.xlsx
Archivos descargados al corte: 14
Archivo descargado: 20250408052952372_PUTUMAYOCompleto.xlsx
Archivos descargados al corte: 15
Archivo descargado: 20250408053542223_PEREIRACompleto.xlsx
Archivos descargados al corte: 16
Archivo descargado: 20250408053330897_PASTOCompleto.xlsx
Archivos descargados al corte: 17
Archivo descargado: 20250408052656562_PALMIRACompleto.xlsx
Archivos descargados al corte: 18
Archivo descargado: 20250408052713942_ORIENTE ANTIOQUENOCompleto.xlsx
Archivos descargados al corte: 19
Archivo descargado: 20250408052329372_OCANACompleto.xlsx
Archivos descargados al corte: 20
==========> Avanza a la página 3 <============Archivo descargado: 20250408053210245_SANTA MARTAAHastaX.xlsx
Archivos descargados al corte: 21
Archivo descargado: 20250408052510593_NEIVAAHastaL.xlsx
Archivos descargados al corte: 22
Archivo descargado: 20250408052156761_MEDELLINAHastaX.xlsx
Archivos descargados al corte: 23
Archivo descargado: 20250408052456167_MEDELLINAHastaQ.xlsx
Archivos descargados al corte: 24
Archivo descargado: 20250408051935154_MEDELLINAHastaK.xlsx
Archivos descargados al corte: 25
Archivo descargado: 20250408051727926_MEDELLING2029Hasta1952.xlsx
Archivos descargados al corte: 26
Archivo descargado: 20250408051505557_MEDELLING2029Hasta2018.xlsx
Archivos descargados al corte: 27
Archivo descargado: 20250408051259104_MEDELLINAHastaF.xlsx
Archivos descargados al corte: 28
Archivo descargado: 20250408105316159_MEDELLING2029Hasta1952.xlsx
Archivos descargados al corte: 29
Archivo descargado: 20250408104913442_MEDELLING2029Hasta2018.xlsx
Archivos descargados al corte: 30
==========> Avanza a la página 4 <============Archivo descargado: 20250408052316536_NEIVAAHastaX.xlsx
Archivos descargados al corte: 31
Archivo descargado: 20250408104519238_MANIZALESCompleto.xlsx
Archivos descargados al corte: 32
Archivo descargado: 20250408104238600_MAGDALENA MEDIOCompleto.xlsx
Archivos descargados al corte: 33
Archivo descargado: 20250408104224611_MAGANGUECompleto.xlsx
Archivos descargados al corte: 34
Archivo descargado: 20250408104210888_IPIALESCompleto.xlsx
Archivos descargados al corte: 35
Archivo descargado: 20250408104047957_IBAGUEAHastaX.xlsx
Archivos descargados al corte: 36
Archivo descargado: 20250408104351067_IBAGUEAHastaR.xlsx
Archivos descargados al corte: 37
Archivo descargado: 20250408103734966_HONDACompleto.xlsx
Archivos descargados al corte: 38
Archivo descargado: 20250408103740749_GIRARDOTCompleto.xlsx
Archivos descargados al corte: 39
Archivo descargado: 20250408103743140_FLORENCIACompleto.xlsx
Archivos descargados al corte: 40
==========> Avanza a la página 5 <============Archivo descargado: 20250408104712888_MEDELLINAHastaF.xlsx
Archivos descargados al corte: 41
Archivo descargado: 20250408103517017_DUITAMACompleto.xlsx
Archivos descargados al corte: 42
Archivo descargado: 20250408103346298_DOSQUEBRADASCompleto.xlsx
Archivos descargados al corte: 43
Archivo descargado: 20250408103345782_CUCUTAAHastaX.xlsx
Archivos descargados al corte: 44
Archivo descargado: 20250408103721759_CUCUTAAHastaI.xlsx
Archivos descargados al corte: 45
Archivo descargado: 20250408103113104_CUCUTAAHastaF.xlsx
Archivos descargados al corte: 46
Archivo descargado: 20250408102719012_CHINCHINACompleto.xlsx
Archivos descargados al corte: 47
Archivo descargado: 20250408103348019_CAUCACompleto.xlsx
Archivos descargados al corte: 48
Archivo descargado: 20250408102918086_CASANARECompleto.xlsx
Archivos descargados al corte: 49
Archivo descargado: 20250408102606053_CARTAGOCompleto.xlsx
Archivos descargados al corte: 50
==========> Avanza a la página 6 <============Archivo descargado: 20250408104054693_FACATATIVACompleto.xlsx
Archivos descargados al corte: 51
Archivo descargado: 20250408102742707_CARTAGENAAHastaH.xlsx
Archivos descargados al corte: 52
Archivo descargado: 20250408102541686_CALIAHastaX.xlsx
Archivos descargados al corte: 53
Archivo descargado: 20250408102157154_CALIAHastaM.xlsx
Archivos descargados al corte: 54
Archivo descargado: 20250408101855502_CALIG2029Hasta1945.xlsx
Archivos descargados al corte: 55
Archivo descargado: 20250408101743099_CALIG2029Hasta2015.xlsx
Archivos descargados al corte: 56
Archivo descargado: 20250408101557657_CALIAHastaF.xlsx
Archivos descargados al corte: 57
Archivo descargado: 20250408101404980_BUGACompleto.xlsx
Archivos descargados al corte: 58
Ocurrió un error con la página. Se reinicia 
==========> Avanza a la página 2 <============Ocurrió un error con la página. Se reinicia 
==========> Avanza a la página 2 <======================> Avanza a la página 3 <======================> Avanza a la página 4 <======================> Avanza a la página 5 <======================> Avanza a la página 6 <============Archivo descargado: 20250408102748740_CARTAGENAAHastaX.xlsx
Archivos descargados al corte: 1
Archivo descargado: 20250408101306810_BUENAVENTURACompleto.xlsx
Archivos descargados al corte: 2
Archivo descargado: 20250408101444337_BUCARAMANGAAHastaX.xlsx
Archivos descargados al corte: 3
==========> Avanza a la página 7 <============Archivo descargado: 20250408101444478_BUCARAMANGAAHastaH.xlsx
Archivos descargados al corte: 4
Archivo descargado: 20250408101019292_BUCARAMANGAAHastaF.xlsx
Archivos descargados al corte: 5
Archivo descargado: 20250408100830540_BOGOTAAHastaX.xlsx
Archivos descargados al corte: 6
Archivo descargado: 20250408100545471_BOGOTAAHastaR.xlsx
Archivos descargados al corte: 7
Archivo descargado: 20250408100442032_BOGOTAAHastaP.xlsx
Archivos descargados al corte: 8
Archivo descargado: 20250408100146034_BOGOTAM2029Hasta1972.xlsx
Archivos descargados al corte: 9
Archivo descargado: 20250408095604785_BOGOTAM2029Hasta2017.xlsx
Archivos descargados al corte: 10
Archivo descargado: 20250408095254302_BOGOTAAHastaL.xlsx
Archivos descargados al corte: 11
Archivo descargado: 20250408095138529_BOGOTAAHastaK.xlsx
Archivos descargados al corte: 12
Archivo descargado: 20250408094937447_BOGOTAI2029Hasta1972.xlsx
Archivos descargados al corte: 13
==========> Avanza a la página 8 <============Archivo descargado: 20250408094426427_BOGOTAI2029Hasta2020.xlsx
Archivos descargados al corte: 14
Archivo descargado: 20250408094158500_BOGOTAAHastaH.xlsx
Archivos descargados al corte: 15
Archivo descargado: 20250408094147716_BOGOTAG2029Hasta1972.xlsx
Archivos descargados al corte: 16
Archivo descargado: 20250408093716315_BOGOTAG2029Hasta2009.xlsx
Archivos descargados al corte: 17
Archivo descargado: 20250408093846173_BOGOTAG2029Hasta2017.xlsx
Archivos descargados al corte: 18
Archivo descargado: 20250408093556884_BOGOTAG2029Hasta2020.xlsx
Archivos descargados al corte: 19
Archivo descargado: 20250408093457678_BOGOTAG2029Hasta2022.xlsx
Archivos descargados al corte: 20
Archivo descargado: 20250408093259479_BOGOTAG2029Hasta2024.xlsx
Archivos descargados al corte: 21
Archivo descargado: 20250408092643299_BOGOTAAHastaF.xlsx
Archivos descargados al corte: 22
Archivo descargado: 20250408092434512_BOGOTAC2029Hasta1972.xlsx
Archivos descargados al corte: 23
==========> Avanza a la página 9 <============Archivo descargado: 20250408091754431_BOGOTAC2029Hasta2019.xlsx
Archivos descargados al corte: 24
Archivo descargado: 20250408091409362_BOGOTAAHastaB.xlsx
Archivos descargados al corte: 25
Archivo descargado: 20250408091216354_BARRANQUILLAAHastaX.xlsx
Archivos descargados al corte: 26
Archivo descargado: 20250408091209430_BARRANQUILLAAHastaQ.xlsx
Archivos descargados al corte: 27
Archivo descargado: 20250408090934431_BARRANQUILLAG2029Hasta1943.xlsx
Archivos descargados al corte: 28
Archivo descargado: 20250408090748350_BARRANQUILLAG2029Hasta2005.xlsx
Archivos descargados al corte: 29
Archivo descargado: 20250408090436488_BARRANQUILLAAHastaF.xlsx
Archivos descargados al corte: 30
Archivo descargado: 20250408085205394_BARRANQUILLAAHastaF.xlsx
Archivos descargados al corte: 31
Archivo descargado: 20250408085102922_BARRANCABERMEJACompleto.xlsx
Archivos descargados al corte: 32
Archivo descargado: 20250408085044636_ARMENIACompleto.xlsx
Archivos descargados al corte: 33
Ocurrió un error con la página. Se reinicia 
]
"""

# Usamos una expresión regular para buscar solo los nombres que empiezan con 2025 y terminan en .xlsx
archivos = re.findall(r'2025\d+.*?\.xlsx', texto)

# Mostramos la lista
print(archivos)


# Primer Flag para loguearse hasta que ingrese. A veces salen mensajes de alerta de que no se puede iniciar sesión.
iniciar_sesion(usuario, password)
chrome_driver = iniciar_sesion.chrome_driver

chrome_driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_menu_BDn4"]/table/tbody/tr/td/a').click()

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
            archivos_a_buscar = ['20250408']
            if "andres.juliono@colsubsidio.com" in correo and val_ini_name in archivos_a_buscar and name_file not in archivos:
                print("Archivo nuestro")
                # flag = False
                # while not flag:
                try:
                    descargar = chrome_driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes_lnkDescargarDB_{i - 2}"]')
                    # if texto != '':
                    descargar.click()
                    time.sleep(2)
                    # Espera a que la tabla esté disponible
                    WebDriverWait(chrome_driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH, f'//*[@id="ContentPlaceHolder1_GrdSolicitudes"]/tbody/tr[{i}]/td[1]')))
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
                archivos.append(name_file)
                print(archivos)
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
                    time.sleep(3)

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


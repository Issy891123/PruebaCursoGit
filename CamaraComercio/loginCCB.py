import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, NoSuchDriverException, \
    WebDriverException, UnexpectedAlertPresentException, TimeoutException
from datetime import datetime
import os


# Hora inicio
inicio = datetime.now()
hora_actual = inicio.strftime("%Y-%m-%d_%H-%M-%S")

url_bd = 'https://sico.ccb.org.co/Sico/Paginas/frm_SolicitudInfo.aspx'
archivo_log = fr"C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs\Log_{hora_actual}.txt"
ruta_archivo = fr'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs'


def crear_archivo(ruta_archivo):
    hora_actual = inicio.strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo_log = f"Log_{hora_actual}.txt"
    ruta_completa = os.path.join(ruta_archivo, nombre_archivo_log)
    archivo_log = None  # Variable para almacenar el objeto de archivo

    # Intenta abrir el archivo en modo de append, si no existe, lo crea
    try:
        archivo_log = open(ruta_completa, "a")
        archivo_log.write(f"Hora inicio: {hora_actual}\n")
        print(f"Accediendo a archivo de log: {ruta_completa}")
    except FileNotFoundError:
        archivo_log = open(ruta_completa, "w")
        archivo_log.write(f"Hora inicio: {hora_actual}\n")
        print(f"Archivo de log creado: {ruta_completa}")

    return archivo_log  # Retorna el objeto de archivo para uso futuro


def iniciar_sesion(user, key, max_intentos=5, espera=10):
    if not hasattr(iniciar_sesion, 'chrome_driver'):
        iniciar_sesion.chrome_driver = None

    flag = False
    while not flag:
        try:
            iniciar_sesion.chrome_driver = webdriver.Chrome()
            iniciar_sesion.chrome_driver.get(url_bd)
            iniciar_sesion.chrome_driver.maximize_window()

            correo = iniciar_sesion.chrome_driver.find_element(By.ID, "txtUsuario")
            correo.send_keys(user)

            passw = iniciar_sesion.chrome_driver.find_element(By.ID, "txtPassword")
            passw.send_keys(key)
            passw.send_keys(Keys.ENTER)

            # Asume que si llegas a este punto, la alerta está presente
            iniciar_sesion.chrome_driver.switch_to.alert.accept()
        except (NoSuchElementException, UnexpectedAlertPresentException) as e:
            print(f"Ocurrió un error, vuelvo a intentar ---- {e}")
            # Asumiendo que crear_archivo_log es una función modificada que retorna el objeto de archivo
            with crear_archivo(ruta_archivo) as archivo_log:
                archivo_log.write(f"Ocurrió un error, vuelvo a intentar ---- {e}\n")
            iniciar_sesion.chrome_driver.close()
            iniciar_sesion.chrome_driver = None  # Reinicia chrome_driver a None para reintentar
        except NoAlertPresentException:
            if "504 Gateway Time-out" in iniciar_sesion.chrome_driver.page_source:
                flag_na = False
                intentos = 0
                while intentos < max_intentos and not flag_na:
                    try:
                        iniciar_sesion.chrome_driver.get(url_bd)
                        # Espera un tiempo para ver si la página carga completamente
                        # time.sleep(5)  # Espera 5 segundos para dar tiempo a la página a cargar
                        if "504 Gateway Time-out" in iniciar_sesion.chrome_driver.page_source:
                            raise TimeoutException("Error 504 Gateway Time-out")
                            iniciar_sesion.chrome_driver.refresh()
                        else:
                            flag_na = True

                    except TimeoutException as e:
                        with crear_archivo(ruta_archivo) as archivo_log:
                            archivo_log.write(f"Intento {intentos + 1}: La página no cargó correctamente. Error: {e}\n")
                        print(f"Intento {intentos + 1}: La página no cargó correctamente. Error: {e}")
                        intentos += 1
                        iniciar_sesion.chrome_driver.refresh()
                        time.sleep(espera)  # Espera antes de reintentar

            print("Sin alertas")
            with crear_archivo(ruta_archivo) as archivo_log:
                archivo_log.write("Sin alertas\n")
            # Asume que la sesión se inicia correctamente si no hay alerta
            try:
                iniciar_sesion.chrome_driver.switch_to.window(iniciar_sesion.chrome_driver.window_handles[1])
            except:
                pass

            try:
                text = iniciar_sesion.chrome_driver.switch_to.alert.text
                if text == '':
                    inicia = WebDriverWait(iniciar_sesion.chrome_driver, 15).until(expected_conditions.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")))
                    if inicia:
                        flag = True
                        print('Ingresó a la página correctamente sin alertas')
                        time.sleep(10)
                    else:
                        iniciar_sesion.chrome_driver.refresh()
                else:
                    iniciar_sesion.chrome_driver.switch_to.alert.accept()
                    iniciar_sesion.chrome_driver.get(url_bd)
                    # Asume que si llegas a este punto, la alerta está presente
                    inicia = WebDriverWait(iniciar_sesion.chrome_driver, 15).until(expected_conditions.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")))
                    if inicia:
                        flag = True
                        print('Ingresó a la página correctamente sin alertas')
                        time.sleep(10)
                    else:
                        iniciar_sesion.chrome_driver.refresh()
            except:
                iniciar_sesion.chrome_driver.get(url_bd)
                # Asume que si llegas a este punto, la alerta está presente
                iniciar_sesion.chrome_driver.switch_to.alert.accept()
                inicia = WebDriverWait(iniciar_sesion.chrome_driver, 15).until(expected_conditions.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")))
                if inicia:
                    flag = True
                    print('Ingresó a la página correctamente sin alertas')
                    time.sleep(10)
                else:
                    iniciar_sesion.chrome_driver.refresh()

        except (NoSuchDriverException, WebDriverException):
            print("No reconoció el Driver")
            with crear_archivo(ruta_archivo) as archivo_log:
                archivo_log.write("No reconoció el Driver\n")
            return None  # Retorna None si el driver no puede ser inicializado

    try:
        inicia = WebDriverWait(iniciar_sesion.chrome_driver, 15).until(expected_conditions.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblFloatSeleccionados")))
        if inicia:
            flag = True
            print('Ingresó a la página correctamente sin alertas')
            time.sleep(10)
            return iniciar_sesion.chrome_driver  # Retorna el driver para uso futuro
    except:
        iniciar_sesion.chrome_driver.refresh()





# ================================================================================

def seleccionar_opcion_ciudad(chrome_driver, ciudad, ciudades, archivo_log):
    """
        Esta función selecciona una opción de ciudad en una página web y hace clic en el botón de agregar.

        Parámetros:
            chrome_driver (WebDriver): El objeto del controlador de Chrome.
            ciudad (str): La ciudad que se va a seleccionar en la lista desplegable.
            ciudades (list): La lista de todas las ciudades disponibles en la lista desplegable.
            archivo_log (file): El archivo de registro donde se escribirán los mensajes.
        """
    list_ciu = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_lstCamaras")
    opciu =  list_ciu.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_lstCamaras"]/option[{ciudades.index(ciudad) + 1}]')
    opciu.click()
    print(f"Opción seleccionada: {ciudades.index(ciudad) + 1} de {len(ciudades) - 1} ciudades")
    archivo_log.write(f"Opción seleccionada: {ciudades.index(ciudad) + 1} de {len(ciudades) - 1} ciudades\n")
    vciudad = opciu.text
    print(vciudad)
    archivo_log.write(f"{vciudad} \n")
    add = chrome_driver.find_element(By.ID, "ContentPlaceHolder1_BtnAddCamara")
    add.click()
    return vciudad

# Funciones para extraer ciudades descargadas del log
def obtener_ciudad(linea):
    # Dividir la línea por el guion ("-")
    partes = linea.split('-')
    # Obtener el elemento que está después del segundo guion y eliminar los espacios en blanco al inicio y al final
    ciudad = partes[4].strip()
    return ciudad

def obtener_archivo_mas_reciente(ruta):
    # Obtener la lista de archivos en la ruta especificada
    archivos = os.listdir(ruta)
    # Inicializar variables para almacenar el nombre del archivo más reciente y su fecha de modificación
    archivo_mas_reciente = None
    fecha_modificacion_mas_reciente = 0
    # Iterar sobre cada archivo en la lista
    for archivo in archivos:
        # Obtener la ruta completa del archivo
        ruta_completa = os.path.join(ruta, archivo)
        # Verificar si el archivo es un archivo regular (no un directorio)
        if os.path.isfile(ruta_completa):
            # Obtener la fecha de modificación del archivo
            fecha_modificacion = os.path.getmtime(ruta_completa)
            # Verificar si esta fecha de modificación es más reciente que la actual más reciente
            if fecha_modificacion > fecha_modificacion_mas_reciente:
                # Actualizar el archivo más reciente y su fecha de modificación
                archivo_mas_reciente = ruta_completa
                fecha_modificacion_mas_reciente = fecha_modificacion
    return archivo_mas_reciente


def extraer_ciudades_desde_archivo_mas_reciente(ruta_directorio):
    # Obtener el archivo más reciente en la ruta especificada
    archivo_mas_reciente = obtener_archivo_mas_reciente(ruta_directorio)
    # Verificar si se encontró un archivo más reciente
    if archivo_mas_reciente:
        # Leer el archivo más reciente y obtener las ciudades
        ciudades = []
        with open(archivo_mas_reciente, 'r') as archivo:
            lineas = archivo.readlines()
            for linea in lineas:
                ciudad = obtener_ciudad(linea)
                if 'Retrying (' not in ciudad:
                    ciudades.append(ciudad)
            if len(ciudades) > 0:
                ciudades.pop()
        return ciudades
    else:
        print("No se encontraron archivos en la ruta especificada.")
        return None

# Directorio donde se encuentran los archivos
directorio = r'C:\Users\ESTEGOMHIN\OneDrive - colsubsidio.com (1)\PycharmProjects\CamaraComercio\Logs\LogCiudadesDescargadas'
# Obtener y extraer ciudades desde el archivo más reciente en el directorio
ciudades = extraer_ciudades_desde_archivo_mas_reciente(directorio)

# Imprimir las ciudades obtenidas
if ciudades:
    for ciudad in ciudades:
        print(ciudad)

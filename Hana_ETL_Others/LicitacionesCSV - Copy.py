import pandas as pd

#   Este comentario es para validar el git fetch
#   Algunas empresas del archivo de Nina cruzan con el SECOP pero la fecha y la descripción de la oportunidad no coinciden
#   Debemos buscar manual a ver si algunas de las descripciones coinciden
#   Comparar con cuantas empresas que están en el SECOP hemos tenido licitaciones
#   Revisar si para todas las licitaciones del SECOP puede aplicar colsubsidio
#   En el SECOP Colsubsidio aparece bajo otras modalidades de contratación pero no como licitación

#   Descargar archivo solo con adjudicaciones a cajas de compensación sin importar el tipo de contratación
#   Descargar archivo completo y analizar todos los registros que tengan que ver con bienestar
#   Licitaciones que tengan que ver con cajas de compensación y/o bienestar (Quienes licitan, cuántas, valor por nits)

df = pd.read_csv("./Inputs/SECOPII_Licitaciones.csv", dtype={1: str})

# Configurar Pandas para mostrar todas las columnas y filas sin truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
print(df.head(15))


import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Credenciales del remitente
smtp_server = "smtp.hostinger.com"
port = 587  # Puerto para SSL
sender_email = "databi@leasyingenieria.com"
password = os.environ.get('PASS')

# Lista de destinatarios
emails = [
    "VMPISCIOTTI@YAHOO.COM",
    # "CONTABILIDAD@HERMOSAYASOCIADOS.COM.CO",
    # "YYOROZCO@IPINNOVATECH.CO",
    # "ESPANAELECT@SPAINAUDIO-ONLINE.COM",
    # "ADMINISTRACION@SISTEM.NET.CO",
    # "CONTABILIDAD@ORTOPEDICAMERICANA.COM",
    # "PAOLA@ARON.COM.CO",
    # "GERENCIA@ALMACENSANTANGEL.COM",
    # "GERENCIA@ATELELECTRIC.COM",
    # "HECTOR@INNOVABRAND.COM"
]

# Asunto y cuerpo genérico del correo
subject = "Impulsa tu empresa con Ingeniería de Datos y BI"

# Cuerpo del mensaje en HTML
body_html = f"""
<html>
  <body>
    <p>Hola,</p>
    <p>En un entorno empresarial cada vez más competitivo, implementar soluciones de <strong>Ingeniería de Datos y BI</strong> ya no es un lujo, sino una necesidad.</p>
    <p>Las organizaciones que estructuran, limpian y analizan sus datos son capaces de:</p>
    <ul>
      <li>Tomar decisiones basadas en evidencia.</li>
      <li>Anticiparse a riesgos y oportunidades.</li>
      <li>Optimizar procesos operativos y comerciales.</li>
    </ul>
    <p>En <strong>Leasy Ingeniería</strong>, te ayudamos a transformar tus datos en activos estratégicos. Te invitamos a conocer más sobre nuestro enfoque en:</p>
    <p><a href="https://leasyingenieria.com">https://leasyingenieria.com</a></p>
    <p>Y si deseas un diagnóstico más completo, por favor diligencia el formulario en:<br>
    <a href="https://leasyingenieria.com/diagnostico-empresarial">https://leasyingenieria.com/diagnostico-empresarial</a></p>
    <p>¡Estamos listos para acompañarte en tu transformación basada en datos!</p>
    <br>
    <p>Atentamente,<br>
    Leasy Ingeniería<br>
    3005218277 - 
    3107785029 -
    databi@leasyingenieria.com</p>
  </body>
</html>
"""

# Enviar correo a cada destinatario
context = ssl.create_default_context()

with smtplib.SMTP(smtp_server, port) as server:
    server.starttls(context=context)
    server.login(sender_email, password)
    for receiver_email in emails:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Bcc"] = 'linamartinez1995@outlook.com'

        part_html = MIMEText(body_html, "html")
        message.attach(part_html)

        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Correo enviado a {receiver_email}")

from moviepy.editor import VideoFileClip
from google.cloud import speech
import io

# Cargar el video Eliana CAmpos
video = VideoFileClip(r"C:\Users\estegomhin\Downloads\CONSUMOS B2B-20241021.mp4")

# Extraer el audio
audio = video.audio

# Guardar el audio en un archivo
audio_path_mp3 = r"C:/users/estegomhin/Downloads/CONSUMOS B2B-20241021.mp3"
audio.write_audiofile(audio_path_mp3)


# Configurar el cliente de Google Cloud
# client = speech.SpeechClient()
#
# # Cargar el archivo de audio
# with io.open(r"C:/users/estegomhin/Downloads/Informe Consumos B2B-20241008.mp3", "rb") as audio_file:
#     content = audio_file.read()
#
# audio = speech.RecognitionAudio(content=content)
# config = speech.RecognitionConfig(
#     encoding=speech.RecognitionConfig.AudioEncoding.MP3,
#     sample_rate_hertz=16000,
#     language_code="es-ES",
# )
#
# # Transcribir el audio
# response = client.recognize(config=config, audio=audio)
#
# for result in response.results:
#     print("Transcripción: {}".format(result.alternatives.transcript))

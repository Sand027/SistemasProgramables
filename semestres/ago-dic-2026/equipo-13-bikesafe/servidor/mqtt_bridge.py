# ============================================
# Proyecto:  BikeSafe — Candado inteligente portátil
# Archivo:   mqtt_bridge.py
# Objetivo:  Se suscribe a los tópicos de BikeSafe y muestra los datos en consola
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josué Talamantes Santiago (23240355)
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883


def al_conectar(cliente, userdata, flags, rc, properties=None):
    print("Conectado al broker, código:", rc)
    cliente.subscribe("bikesafe/#")


def al_recibir(cliente, userdata, msg):
    hora = datetime.now().strftime("%H:%M:%S")
    if msg.topic == "bikesafe/cam/frame":
        print(f"[{hora}] {msg.topic}: frame de {len(msg.payload)} bytes")
    else:
        print(f"[{hora}] {msg.topic}: {msg.payload.decode(errors='replace')}")


cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.on_connect = al_conectar
cliente.on_message = al_recibir
cliente.connect(BROKER, PUERTO)
cliente.loop_forever()

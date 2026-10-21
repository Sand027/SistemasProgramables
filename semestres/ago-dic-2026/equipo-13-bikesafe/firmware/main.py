# ============================================
# Proyecto:  BikeSafe — Candado inteligente portátil
# Archivo:   main.py
# Objetivo:  Conecta la ESP32 a WiFi/MQTT, publica 3 sensores y atiende 3 actuadores
# Equipo:    Oscar Sandoval Cabrera (L00000000),
#            Diego Josué Talamantes Santiago (L00000000)
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

import time
import network
from umqtt.simple import MQTTClient
from hal import sensores, actuadores

WIFI_SSID = "TU_RED"
WIFI_PASS = "TU_PASSWORD"
BROKER    = "192.168.1.100"   # IP de la PC con Mosquitto
CLIENT_ID = "bikesafe-esp32"
PERIODO_S = 2

TOPICOS_CMD = {
    b"bikesafe/a1/cmd": actuadores.actuador1,
    b"bikesafe/a2/cmd": actuadores.actuador2,
    b"bikesafe/a3/cmd": actuadores.actuador3,
}


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("WiFi OK:", wlan.ifconfig()[0])


def al_recibir(topico, mensaje):
    funcion = TOPICOS_CMD.get(topico)
    if funcion:
        funcion(mensaje.decode())


def main():
    conectar_wifi()
    cliente = MQTTClient(CLIENT_ID, BROKER)
    cliente.set_callback(al_recibir)
    cliente.connect()
    for t in TOPICOS_CMD:
        cliente.subscribe(t)
    print("MQTT OK")

    while True:
        cliente.publish(b"bikesafe/s1", str(sensores.leer_sensor1()))
        cliente.publish(b"bikesafe/s2", str(sensores.leer_sensor2()))
        cliente.publish(b"bikesafe/s3", str(sensores.leer_sensor3()))
        cliente.check_msg()
        time.sleep(PERIODO_S)


main()

# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   pruebas/e14_tapa_reed.py
# Objetivo:  Probar el interruptor magnetico (reed switch) de la tapa
#            en GPIO15
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
#
# CONEXION: el reed switch tiene 2 patitas (no tiene polaridad).
#   una patita -> D15      la otra -> GND
#   (no lleva resistencia: usamos la pull-up interna de la ESP32)
#
# OJO: el reed es una capsula de VIDRIO. No doblen las patitas pegado
# al vidrio porque se estrella; doblen a 3 mm del cuerpo.
#
# QUE DEBES VER: acerca el iman -> "TAPA CERRADA (iman cerca)".
# Alejalo -> "TAPA ABIERTA (iman lejos)". Sirve para encontrar la mejor
# posicion del iman en la tapa antes de pegarlo.

import time
from machine import Pin

reed = Pin(15, Pin.IN, Pin.PULL_UP)
anterior = None
cambios = 0
print("Acerca y aleja el iman del reed switch...")
while True:
    valor = reed.value()
    if valor != anterior:
        cambios += 1
        print("#{}  {}".format(cambios, "TAPA CERRADA (iman cerca)" if valor == 0
                               else "TAPA ABIERTA (iman lejos)"))
        anterior = valor
    time.sleep_ms(20)

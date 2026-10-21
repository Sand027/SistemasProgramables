# ============================================
# Proyecto:  BikeSafe — Candado inteligente portátil
# Archivo:   hal/sensores.py
# Objetivo:  Lectura de los 3 sensores del candado (capa HAL)
# Equipo:    Oscar Sandoval Cabrera (L00000000),
#            Diego Josué Talamantes Santiago (L00000000)
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

from machine import Pin

# TODO: cambiar GPIO y lógica según los sensores reales (ver Tabla HAL)
_s1 = Pin(34, Pin.IN)
_s2 = Pin(35, Pin.IN)
_s3 = Pin(32, Pin.IN)


def leer_sensor1():
    return _s1.value()


def leer_sensor2():
    return _s2.value()


def leer_sensor3():
    return _s3.value()

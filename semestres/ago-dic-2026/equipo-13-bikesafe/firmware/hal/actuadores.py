# ============================================
# Proyecto:  BikeSafe — Candado inteligente portátil
# Archivo:   hal/actuadores.py
# Objetivo:  Control de los 3 actuadores del candado (capa HAL)
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josué Talamantes Santiago (23240355)
# Materia:   Sistemas Programables — ISC TecNM León
# Semestre:  ago-dic-2026
# ============================================

from machine import Pin

# TODO: cambiar GPIO y lógica según los actuadores reales (ver Tabla HAL)
_a1 = Pin(25, Pin.OUT)
_a2 = Pin(26, Pin.OUT)
_a3 = Pin(27, Pin.OUT)


def _aplicar(pin, cmd, nombre):
    pin.value(1 if cmd.upper() == "ON" else 0)
    print(nombre, "->", cmd)


def actuador1(cmd):
    _aplicar(_a1, cmd, "A1")


def actuador2(cmd):
    _aplicar(_a2, cmd, "A2")


def actuador3(cmd):
    _aplicar(_a3, cmd, "A3")

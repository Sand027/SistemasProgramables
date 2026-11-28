# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   pruebas_pc/fakes/mfrc522.py
# Objetivo:  Falso del lector RFID RC522: las pruebas "acercan" tarjetas
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
VERSION = [0x92]
TARJETAS = []          # la prueba agrega UIDs aqui


class MFRC522:
    def __init__(self, sck, mosi, miso, rst, cs, bus=2):
        pass

    def version(self):
        return VERSION[0]

    def leer_uid(self):
        return TARJETAS.pop(0) if TARJETAS else None

# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   pruebas_pc/fakes_cam/cryptolib.py
# Objetivo:  Imita el modulo cryptolib de MicroPython (aes) con la
#            libreria cryptography, para probar cifrado.py tal como corre
#            en la Freenove
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class aes:
    def __init__(self, llave, modo, iv):
        assert modo == 2, "BikeSafe usa CBC (modo 2)"
        self._c = Cipher(algorithms.AES(bytes(llave)), modes.CBC(bytes(iv)))

    def encrypt(self, datos):
        e = self._c.encryptor()
        return e.update(bytes(datos)) + e.finalize()

    def decrypt(self, datos):
        d = self._c.decryptor()
        return d.update(bytes(datos)) + d.finalize()

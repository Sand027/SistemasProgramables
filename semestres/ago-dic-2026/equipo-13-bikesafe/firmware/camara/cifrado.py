# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   cifrado.py   (Freenove; el servidor usa ESTE MISMO archivo)
# Objetivo:  Cifrar las fotos antes de mandarlas por el broker MQTT
#            publico (AES-256-CBC + HMAC-SHA256) para proteger la
#            privacidad de las personas que salen en ellas
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
#
# PROBLEMA: broker.hivemq.com es publico. Cualquiera que se suscriba a
# bikesafe/cam/frame veria las fotos de quien pase junto a la bici.
#
# SOLUCION: la foto viaja cifrada. Sin la clave (MQTT_CLAVE, que nunca
# viaja por la red) solo se ven bytes sin sentido.
#
#   mensaje = "BS1" + iv (16 bytes) + foto cifrada + etiqueta (16 bytes)
#
#   - AES-256 en modo CBC con un iv al azar en CADA foto (dos fotos
#     iguales no se ven iguales cifradas).
#   - Etiqueta = HMAC-SHA256 del iv + foto cifrada ("cifrar y luego
#     firmar"): si alguien cambia un solo byte, o manda fotos falsas,
#     el servidor las rechaza.
#   - De la clave se sacan DOS llaves distintas (una para cifrar y otra
#     para firmar), como se recomienda.
#
# Funciona en MicroPython (modulo cryptolib) y en Python normal
# (libreria "cryptography", ver servidor/requirements.txt).

import hashlib
import os

try:                                         # MicroPython
    from cryptolib import aes as _aes
except ImportError:
    try:
        from ucryptolib import aes as _aes   # MicroPython viejo
    except ImportError:
        _aes = None
_cryptography = None
if _aes is None:
    try:                                     # Python en la laptop
        from cryptography.hazmat.primitives.ciphers import (
            Cipher, algorithms, modes)
        _cryptography = (Cipher, algorithms, modes)
    except ImportError:
        pass

MAGIA = b"BS1"
_BLOQUE = 16


def disponible():
    return _aes is not None or _cryptography is not None


def _b(x):
    return x if isinstance(x, (bytes, bytearray)) else str(x).encode()


def _llaves(clave):
    clave = _b(clave)
    return (hashlib.sha256(b"bikesafe-cifrado|" + clave).digest(),
            hashlib.sha256(b"bikesafe-firma|" + clave).digest())


def _hmac(llave, datos):
    """HMAC-SHA256 (RFC 2104); MicroPython no trae el modulo hmac."""
    llave = llave + b"\x00" * (64 - len(llave))
    interna = hashlib.sha256(bytes(b ^ 0x36 for b in llave))
    interna.update(datos)
    externa = hashlib.sha256(bytes(b ^ 0x5C for b in llave))
    externa.update(interna.digest())
    return externa.digest()


def _aes_cbc(llave, iv, datos, cifrar):
    if _aes is not None:
        motor = _aes(llave, 2, iv)                # 2 = modo CBC
        return motor.encrypt(datos) if cifrar else motor.decrypt(datos)
    Cipher, algorithms, modes = _cryptography
    c = Cipher(algorithms.AES(llave), modes.CBC(iv))
    hacer = c.encryptor() if cifrar else c.decryptor()
    return hacer.update(bytes(datos)) + hacer.finalize()


def cifrar(clave, datos):
    """bytes o texto -> mensaje cifrado y firmado (bytes)."""
    if not disponible():
        raise OSError("no hay AES en este firmware")
    k_cif, k_fir = _llaves(clave)
    datos = _b(datos)
    relleno = _BLOQUE - len(datos) % _BLOQUE          # PKCS#7
    datos = bytes(datos) + bytes([relleno]) * relleno
    iv = os.urandom(_BLOQUE)
    cuerpo = iv + _aes_cbc(k_cif, iv, datos, True)
    return MAGIA + cuerpo + _hmac(k_fir, cuerpo)[:16]


def descifrar(clave, mensaje):
    """Mensaje -> bytes originales. Lanza ValueError si no es nuestro,
    si lo modificaron o si la clave no coincide."""
    mensaje = bytes(mensaje)
    if not mensaje.startswith(MAGIA) or len(mensaje) < 3 + 16 + 16 + 16:
        raise ValueError("no es un mensaje cifrado de BikeSafe")
    k_cif, k_fir = _llaves(clave)
    cuerpo, etiqueta = mensaje[3:-16], mensaje[-16:]
    esperada = _hmac(k_fir, cuerpo)[:16]
    dif = 0
    for x, y in zip(etiqueta, esperada):        # comparacion en tiempo constante
        dif |= x ^ y
    if dif:
        raise ValueError("firma incorrecta (otra clave o datos alterados)")
    iv, cifrado = cuerpo[:16], cuerpo[16:]
    if len(cifrado) % _BLOQUE:
        raise ValueError("largo invalido")
    datos = _aes_cbc(k_cif, iv, cifrado, False)
    relleno = datos[-1]
    if not 1 <= relleno <= _BLOQUE:
        raise ValueError("relleno invalido")
    return bytes(datos[:-relleno])

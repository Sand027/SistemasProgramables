# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   hal/sensores.py
# Objetivo:  Una clase por cada sensor (acelerometro, ultrasonico,
#            lector RFID, interruptor magnetico de la tapa, cable de
#            sujecion y PIR) para que main.py solo pregunte
#            "que esta pasando"
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
#
# HAL = "capa de abstraccion de hardware". Es la capa que habla
# directamente con las piezas. main.py nunca toca un pin: le pide
# las cosas a estas clases.
#
# Los 3 sensores del proyecto:
#   1. Acelerometro MPU6050   -> toques, forcejeo e inclinacion
#   2. Ultrasonico HC-SR04    -> alguien parado junto a la bici
#   3. Lector RFID RC522      -> reconoce la tarjeta del DUENO
# Extras: reed switch (abrieron la caja), cable de sujecion anti-corte
# y PIR opcional.

import math
import time
from machine import Pin, I2C, time_pulse_us


def _estable(pin, valor, veces=3, espera_ms=2):
    """True si el pin lee 'valor' varias veces seguidas (quita ruido
    y rebotes de los contactos mecanicos)."""
    for _ in range(veces):
        if pin.value() != valor:
            return False
        time.sleep_ms(espera_ms)
    return True


# ---------------------------------------------------------------
#  1. ACELEROMETRO MPU6050
# ---------------------------------------------------------------
class Acelerometro:
    """Detecta si mueven o inclinan la bici.

    Idea: al empezar a vigilar guardamos "hacia donde apunta la
    gravedad" (la referencia). Despues comparamos cada lectura
    contra esa referencia:
      - cambio():      cuanto cambio la aceleracion (en g)
      - inclinacion(): cuantos grados se inclino
    """

    DIRECCION = 0x68

    def __init__(self, sda, scl):
        self._i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=400000)
        self._buf = bytearray(6)
        self._ref = (0.0, 0.0, 1.0)
        self.fallas = 0              # lecturas seguidas que fallaron
        self._despertar()

    def _despertar(self):
        # El MPU6050 arranca "dormido": escribir 0 en el registro
        # 0x6B lo despierta.
        self._i2c.writeto_mem(self.DIRECCION, 0x6B, b"\x00")
        time.sleep_ms(100)
        # Filtro interno (registro 0x1A) para quitar vibraciones
        # muy rapidas que no nos interesan.
        self._i2c.writeto_mem(self.DIRECCION, 0x1A, b"\x03")

    @staticmethod
    def _con_signo(alto, bajo):
        valor = (alto << 8) | bajo
        return valor - 65536 if valor > 32767 else valor

    def leer(self):
        """Regresa (ax, ay, az) en g. En reposo uno de los tres vale ~1.
        Si el cable I2C se suelta lanza OSError (main.py lo cuenta como
        posible sabotaje)."""
        try:
            self._i2c.readfrom_mem_into(self.DIRECCION, 0x3B, self._buf)
        except OSError:
            self.fallas += 1
            raise
        self.fallas = 0
        b = self._buf
        # 16384 cuentas = 1 g (escala de +-2 g, la de fabrica)
        return (self._con_signo(b[0], b[1]) / 16384,
                self._con_signo(b[2], b[3]) / 16384,
                self._con_signo(b[4], b[5]) / 16384)

    def promedio(self, muestras=20):
        sx = sy = sz = 0.0
        for _ in range(muestras):
            x, y, z = self.leer()
            sx += x
            sy += y
            sz += z
            time.sleep_ms(5)
        return (sx / muestras, sy / muestras, sz / muestras)

    def guardar_referencia(self):
        """Llamar cuando la bici ya esta quieta y el sistema empieza a vigilar."""
        self._ref = self.promedio()
        return self._ref

    def cambio(self, lectura=None):
        """Cuanto se aleja la lectura de la referencia, en g."""
        x, y, z = lectura if lectura else self.leer()
        rx, ry, rz = self._ref
        return math.sqrt((x - rx) ** 2 + (y - ry) ** 2 + (z - rz) ** 2)

    def inclinacion(self, lectura=None):
        """Angulo (grados) entre la posicion actual y la referencia."""
        x, y, z = lectura if lectura else self.leer()
        rx, ry, rz = self._ref
        m1 = math.sqrt(x * x + y * y + z * z)
        m2 = math.sqrt(rx * rx + ry * ry + rz * rz)
        if m1 == 0 or m2 == 0:
            return 0.0
        coseno = (x * rx + y * ry + z * rz) / (m1 * m2)
        coseno = max(-1.0, min(1.0, coseno))
        return math.degrees(math.acos(coseno))


# ---------------------------------------------------------------
#  2. SENSOR ULTRASONICO HC-SR04
# ---------------------------------------------------------------
class Ultrasonico:
    """Mide distancia con sonido: manda un 'clic' y cuenta cuanto
    tarda en regresar el eco.

    El HC-SR04 a veces da lecturas locas (un eco que rebota raro).
    Por eso guardamos las ultimas 3 y regresamos la de en medio
    (mediana): un valor loco aislado nunca gana."""

    def __init__(self, trig, echo):
        self._trig = Pin(trig, Pin.OUT, value=0)
        self._echo = Pin(echo, Pin.IN)
        self._ultimas = []

    def medir_una(self):
        """Una sola medicion en cm, o None si no hubo eco."""
        self._trig.value(0)
        time.sleep_us(3)
        self._trig.value(1)
        time.sleep_us(10)            # pulso de 10 microsegundos
        self._trig.value(0)
        # Esperamos el eco maximo 25 ms (unos 4 metros)
        duracion = time_pulse_us(self._echo, 1, 25000)
        if duracion < 0:
            return None
        # El sonido viaja a 0.0343 cm por microsegundo, ida y vuelta
        cm = duracion * 0.0343 / 2
        return cm if 2 <= cm <= 400 else None

    def distancia_cm(self):
        """Distancia filtrada (mediana de las ultimas 3 lecturas)."""
        self._ultimas.append(self.medir_una())
        self._ultimas = self._ultimas[-3:]
        validas = sorted(v for v in self._ultimas if v is not None)
        if not validas:
            return None
        return validas[len(validas) // 2]


# ---------------------------------------------------------------
#  3. LECTOR RFID RC522 (reconoce al dueno)
# ---------------------------------------------------------------
class LectorRFID:
    """Lee el numero (UID) de la tarjeta o llavero que se acerque.
    main.py compara ese numero contra TARJETAS_DUENO de config.py.

    Conexion (bus SPI por hardware de la ESP32):
        SDA(CS) -> D5   SCK -> D18   MOSI -> D23   MISO -> D19
        RST -> D4       3.3V -> 3V3 (NUNCA a 5 V)   GND -> GND
    """

    def __init__(self, sck, mosi, miso, sda, rst):
        from mfrc522 import MFRC522
        self._chip = MFRC522(sck=sck, mosi=mosi, miso=miso, rst=rst, cs=sda)
        self._ultimo_uid = None
        self._ultimo_ms = 0

    def version(self):
        return self._chip.version()

    def conectado(self):
        """True si el chip contesta (0x00 o 0xFF = no hay comunicacion
        por SPI: revisar cables, 3.3 V y soldaduras)."""
        return self.version() not in (0x00, 0xFF)

    def leer(self, ignorar_repetida_ms=2500):
        """Regresa el UID ("A1B2C3D4") solo UNA vez por pasada.
        Si dejas la tarjeta pegada, no la repite hasta que pasen
        'ignorar_repetida_ms' (asi no arma y desarma como loco)."""
        uid = self._chip.leer_uid()
        if uid is None:
            return None
        ahora = time.ticks_ms()
        repetida = (uid == self._ultimo_uid and
                    time.ticks_diff(ahora, self._ultimo_ms) < ignorar_repetida_ms)
        self._ultimo_uid = uid
        self._ultimo_ms = ahora
        return None if repetida else uid


# ---------------------------------------------------------------
#  INTERRUPTOR MAGNETICO DE LA TAPA (reed switch, extra)
# ---------------------------------------------------------------
class SensorTapa:
    """Un reed switch es un interruptor que se cierra cuando le acercas
    un iman. El reed va pegado en la pared de la caja y el iman en la
    tapa: si alguien abre la caja para desconectar la pila o arrancar
    los cables, el sistema lo sabe.

      tapa cerrada (iman cerca) -> contacto cerrado -> pin en 0
      tapa abierta (iman lejos) -> contacto abierto -> pin en 1

    Conexion: una patita del reed al pin, la otra a GND. Usamos la
    resistencia interna (pull-up), no lleva resistencia externa.
    """

    def __init__(self, pin, cerrada_es=0):
        self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._cerrada_es = cerrada_es

    def cerrada(self):
        return _estable(self._pin, self._cerrada_es)

    def abierta(self):
        return _estable(self._pin, 1 - self._cerrada_es)

    def texto(self):
        return "CERRADA" if self._pin.value() == self._cerrada_es else "ABIERTA"


# ---------------------------------------------------------------
#  CABLE DE SUJECION ANTI-CORTE (extra)
# ---------------------------------------------------------------
class LazoAntiCorte:
    """Un cable delgado que sale del pin, va junto al cable con el que
    la caja se amarra a la bici y al estacionamiento, y regresa a GND. Mientras este entero, el pin lee 0. Si lo
    cortan, la resistencia interna (pull-up) sube el pin a 1."""

    def __init__(self, pin):
        self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)

    def cortado(self):
        # Leemos 3 veces para no dar falsa alarma por ruido
        return _estable(self._pin, 1)


# ---------------------------------------------------------------
#  SENSOR DE MOVIMIENTO PIR HC-SR501 (opcional)
# ---------------------------------------------------------------
class SensorPIR:
    """Detecta el calor de una persona que se mueve cerca.
    Su pin OUT da 3.3 V cuando ve a alguien y 0 V cuando no."""

    def __init__(self, pin):
        self._pin = Pin(pin, Pin.IN)

    def hay_alguien(self):
        return self._pin.value() == 1

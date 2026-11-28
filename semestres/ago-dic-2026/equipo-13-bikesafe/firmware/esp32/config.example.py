# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   config.example.py
# Objetivo:  Guardar en UN solo lugar todo lo que se puede ajustar:
#            pines, tarjetas del dueno, piezas conectadas, umbrales,
#            WiFi y MQTT
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
#
# PLANTILLA: copien este archivo como config.py y llenen sus datos.
# config.py NO se sube a GitHub (esta en .gitignore).
#
# REGLA: si quieres cambiar algo del comportamiento de BikeSafe,
# casi siempre se cambia AQUI y no en main.py.

# ---------------------------------------------------------------
# 1. PINES DE LA ESP32 NORMAL (los numeros son GPIO)
# ---------------------------------------------------------------
# Acelerometro MPU6050 (bus I2C)
PIN_I2C_SDA = 21
PIN_I2C_SCL = 22

# Sensor ultrasonico HC-SR04
PIN_TRIG = 26
PIN_ECHO = 27          # OJO: pasa por el divisor de 1k + 2k

# Lector RFID RC522 (bus SPI por hardware). VCC a 3.3 V, NUNCA a 5 V.
PIN_RFID_SCK  = 18
PIN_RFID_MOSI = 23
PIN_RFID_MISO = 19
PIN_RFID_SDA  = 5      # tambien se llama SS o CS
PIN_RFID_RST  = 4

# Reed switch de la TAPA de la caja: una patita al pin y la otra a
# GND. El iman va pegado en la tapa.
PIN_REED = 15

# Actuadores
PIN_SERVO     = 13     # obturador de la camara
PIN_BUZZER    = 25     # (+) del buzzer directo a D25 (sin el 2N2222)

# LED RGB (cada color con su resistencia de 220 ohm)
PIN_RGB_R = 33         # el rojo va donde estaba el LED rojo
PIN_RGB_G = 32         # el verde va donde estaba el LED verde
PIN_RGB_B = 2          # el azul (el 19 ahora es del RFID)
# Nota: GPIO2 y GPIO15 son pines "de arranque". Funcionan bien para el
# LED azul y el reed; solo si algun dia la placa no deja instalar
# MicroPython, desconecten esos 2 cables un momento.
# Si todavia no tienen el RGB, se usan los 2 LEDs de antes:
PIN_LED_VERDE = 32
PIN_LED_ROJO  = 33

# Cable de sujecion anti-corte (un cable delgado de este pin a GND
# que acompana al cable con el que la caja se amarra a la bici)
PIN_LAZO = 14

# Sensor de movimiento PIR HC-SR501 (OUT), opcional
PIN_PIR = 34           # D34 solo sirve como entrada: perfecto para el PIR

# Enlace serie (UART2) con la placa de la camara
PIN_CAM_TX = 17        # ESP32 TX2 -> Freenove GPIO33 (RX)
PIN_CAM_RX = 16        # ESP32 RX2 <- Freenove GPIO32 (TX)

# ---------------------------------------------------------------
# 2. QUE PARTES ESTAN CONECTADAS
# ---------------------------------------------------------------
# Deja en False lo que todavia no tengas armado. Asi el programa
# principal funciona aunque falte una pieza.
USAR_ACELEROMETRO = True
USAR_ULTRASONICO  = True
USAR_RFID         = True   # 3er sensor: reconoce al dueno
USAR_SENSOR_TAPA  = True   # reed switch de la tapa (extra)
USAR_LAZO         = True
USAR_PIR          = False  # True cuando conecten el PIR
USAR_CAMARA       = True
USAR_WIFI_MQTT    = True   # False = funciona sin red (solo Telegram)
USAR_LED_RGB      = True   # False = LEDs verde y rojo de antes

# MODO PRUEBA: con True, empieza a vigilar solo 5 segundos despues
# de prender (para probar la alarma sin tarjeta ni Telegram).
ARMAR_AL_ARRANCAR = False

# ---------------------------------------------------------------
# TARJETAS DEL DUENO (RFID)
# ---------------------------------------------------------------
# Pasa tu tarjeta o llavero por el lector con Thonny abierto: sale
# "Tarjeta: A1B2C3D4". Copia ese numero aqui. Puede haber varias.
TARJETAS_DUENO = [
    "A1B2C3D4",
]
TARJETAS_PARA_ROBO = 3       # 3 tarjetas ajenas seguidas = ROBO
VENTANA_TARJETAS_MS = 60000  # ...dentro de 1 minuto

# ---------------------------------------------------------------
# 3. BUZZER, SERVO Y LED
# ---------------------------------------------------------------
# True  = buzzer ACTIVO  (suena solo al darle 5 V)
# False = buzzer PASIVO  (necesita que le generemos el tono)
BUZZER_ACTIVO = True

# Angulos del servo del obturador. Ajustalos con la caja armada:
# TAPADO = la tapita cubre la ventana de la camara.
SERVO_TAPADO = 0
SERVO_DESTAPADO = 90

# LED RGB: False = catodo comun (patita larga a GND)
#          True  = anodo comun  (patita larga a 3.3 V)
# Si al prender sale "al reves" (todo prendido menos un color),
# cambien este valor. Prueba: pruebas/e13_led_rgb.py
RGB_ANODO_COMUN = False

# ---------------------------------------------------------------
# 4. SENSIBILIDAD DE LA ALARMA (acelerometro)
# ---------------------------------------------------------------
# Todo se mide en "g" (1 g = la gravedad). Entre mas chico el
# numero, mas sensible.
UMBRAL_TOQUE_G   = 0.18   # cambio minimo para contarlo como "toque"
UMBRAL_INCLINA_GRADOS = 25  # si la inclinan mas que esto...
TIEMPO_INCLINA_MS = 1200  # ...durante este tiempo = ROBO

# Nivel 2 (robo): tantos toques dentro de una ventana de tiempo
TOQUES_PARA_ROBO = 4
VENTANA_TOQUES_MS = 6000

# ---------------------------------------------------------------
# 5. ULTRASONICO (foto preventiva)
# ---------------------------------------------------------------
DISTANCIA_CERCA_CM = 50     # alguien a menos de 50 cm...
TIEMPO_CERCA_MS    = 3000   # ...durante 3 segundos = foto
ESPERA_ENTRE_FOTOS_MS = 20000  # no tomar fotos mas seguido que esto

# ---------------------------------------------------------------
# 6. REED SWITCH DE LA TAPA
# ---------------------------------------------------------------
REED_CERRADO_ES = 0          # 0 = el pin lee 0 con el iman cerca
TIEMPO_TAPA_ABIERTA_MS = 500 # abierta asi de tiempo vigilando = ROBO

# ---------------------------------------------------------------
# 7. IA (la decision la toma ESTA placa, no la laptop)
# ---------------------------------------------------------------
# El servidor solo manda "vi una persona con 82 %". Aqui se decide:
IA_CONFIANZA_MINIMA = 0.45   # menos que esto se ignora
IA_VENTANA_MS = 120000       # se recuerdan las personas de 2 minutos
IA_PERSONAS_PARA_ROBO = 2    # 2 personas + la bici se movio = ROBO

# ---------------------------------------------------------------
# 8. ALARMA
# ---------------------------------------------------------------
DURACION_ALARMA_MS = 60000  # la sirena se calla sola al minuto
FOTOS_EXTRA_ROBO   = 2      # en un robo: 1 foto + estas extra
ESPERA_RAFAGA_MS   = 6000   # tiempo entre fotos de la rafaga
DURACION_BUSCAR_MS = 5000   # boton "Buscar": cuanto suena

# Reinicio automatico (watchdog). True SOLO para la exposicion: si
# algo se traba, la placa se reinicia sola. Con True, Thonny no podra
# detener el programa (la placa se reinicia 20 s despues de STOP).
USAR_WATCHDOG = False

# ---------------------------------------------------------------
# 9. WIFI Y MQTT (solo si USAR_WIFI_MQTT = True)
# ---------------------------------------------------------------
WIFI_SSID = "TU_RED"
WIFI_PASS = "TU_PASSWORD"       # "" si la red es abierta
MQTT_BROKER = "broker.hivemq.com"   # o la IP de la laptop con Mosquitto
MQTT_PUERTO = 1883
MQTT_CLIENTE = "bikesafe-esp32"
PERIODO_PUBLICAR_MS = 2000      # cada cuanto manda los sensores
# Clave secreta para FIRMAR los mensajes MQTT (ver firma.py). Debe
# ser IGUAL a la de servidor/clave_mqtt.txt y a la de la Freenove.
# Sin clave, no se acepta "desarmar" por MQTT (el broker publico lo
# ve cualquiera).
MQTT_CLAVE = ""
# Permitir desarmar desde el dashboard (solo con clave).
PERMITIR_DESARMAR_POR_MQTT = True

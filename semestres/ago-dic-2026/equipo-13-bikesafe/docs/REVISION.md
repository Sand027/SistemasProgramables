# 📋 Revisiones de la maestra: observaciones y cambios

## Revisión del 27 de noviembre (cambios solicitados en el PR + plática en clase)

Decisión acordada con la maestra: **BikeSafe deja de ser candado y es un sistema de vigilancia y alarma**. El dueño se reconoce con el **RFID** que nos prestó (con él se completan los 3 sensores), se usan los 3 actuadores, se conserva la caja impresa en 3D y el servo necesitaba una función real.

| # | Observación | Qué hicimos | Dónde verlo | Estado |
|---|---|---|---|---|
| 1 | **Un solo enfoque y un solo nombre** en todo el repo | Se eligió **vigilancia y alarma**. Estados `DESARMADO / VIGILANDO / ALARMA`; comandos `armar / desarmar`; se quitó "candado", "cerrojo", "asegurar" y "liberar" del código, `config.example.py`, encabezados, bot, dashboard, reglas, README y DEMO. `simular_candado.py` → `simular_placas.py`, `e14_cerrojo_reed.py` → `e14_tapa_reed.py` | Todo el repositorio | ✅ |
| 2 | **Función real del servo** | **Obturador de privacidad:** tapa la lente de la cámara cuando está desarmado y la destapa al vigilar (o 6 s para una foto pedida) | `Obturador` en `firmware/esp32/hal/actuadores.py` · `e02_servo.py` | ✅ Código · 🟡 pestaña en la caja |
| 3 | **RFID: explicar qué falló, con evidencia** y regresarlo | Historia completa con las mediciones (corto, `0x00`/`0xFF`, MISO "al aire", 8 combinaciones, 0.48 V en MOSI). El RC522 prestado se integra como **sensor 3**: tarjeta del dueño arma/desarma, una ajena desarmado solo pita, 3 ajenas en 1 min vigilando = ALARMA | [README › RFID](../README.md#-rfid-qué-falló-la-primera-vez-y-cómo-se-resolvió) · `LectorRFID` en `hal/sensores.py` | ✅ Código · 🟡 soldar y fotos |
| 4 | **Componente no convencional** | El **bot de Telegram** | [README › Bot](../README.md#-bot-de-telegram-componente-no-convencional) | ✅ |
| 5 | **Pines 18/19 ocupados por reed y LED** | El RC522 va en VSPI (18, 19, 23, 5, 4). El reed pasó a **GPIO15** y el azul del LED a **GPIO2** | README › HAL · `config.example.py` · [SOLDADURA.md](SOLDADURA.md) | ✅ |
| 6 | **Reed switch:** ¿para qué? | Ahora detecta si **abren la tapa de la caja**. No deja armar con la tapa abierta, y si la abren vigilando es ALARMA | `SensorTapa` · `e14_tapa_reed.py` | ✅ Código · 🟡 montaje |
| 7 | **¿Las fotos viajan por HiveMQ público? ¿Privacidad?** | Sí viajaban abiertas. Ahora van **cifradas (AES-256-CBC + HMAC-SHA256)**; si no hay clave, la Freenove no publica. Además: obturador, servidor web de la cámara apagado, Telegram por HTTPS solo al dueño y Firestore cerrado | [README › Seguridad y privacidad](../README.md#-seguridad-y-privacidad-de-las-fotos) · `firmware/camara/cifrado.py` | ✅ |
| 8 | **Evidencia física:** placa soldada, abrazadera real, caja cerrada, reed y RGB funcionando, demo sin laptop | Guion nuevo de demo sin laptop. Las fotos y el video los toma el equipo con la versión soldada | [DEMO.md](DEMO.md) · `media/` | 🟡 Equipo |
| 9 | **CODEOWNERS** con `@pendiente-talamantes` | Se pusieron los usuarios reales: `@Sand027` y `@josuegoku2203-creator` | `.github/CODEOWNERS` | ✅ |

### Pruebas después de los cambios

| Prueba | Resultado |
|---|---|
| Simulación de la ESP32 (RFID dueño/ajena, tapa, obturador, firma, replay, IA, cable, inclinación, presencia, RC522 sin comunicación) | 65 / 65 |
| Simulación de la Freenove (botones Armar/Desarmar, confirmación, extraños, **fotos cifradas**, reconexión, sin internet) | 20 / 20 |
| Punta a punta con broker real (foto cifrada → servidor la descifra → YOLO → resultado firmado → ESP32 decide; comandos del dashboard) | 19 / 19 |

---

## Revisión del 25 de noviembre

Respuesta punto por punto al plan de acción de la maestra (PR, equipo 13). *Nota: en esta revisión el proyecto todavía era "candado"; los nombres se cambiaron el 27 de noviembre.*

| # | Observación | Qué hicimos | Dónde verlo | Estado |
|---|---|---|---|---|
| 1 | **Soldadura y placa:** no depender de Dupont sueltos (vibración en la bici) | Plan de placa fenólica con headers hembra para la ESP32 y el MPU6050, rieles soldados, conectores para todo lo que sale a la carcasa y revisión con continuidad antes de energizar | [SOLDADURA.md](SOLDADURA.md) · [placa-perforada.png](../hardware/placa-perforada.png) | 🟡 Soldando (Diego) |
| 2 | **3 sensores + 3 actuadores** | **Sensores:** MPU6050, HC-SR04 y **reed switch** del cerrojo (nuevo). **Actuadores:** servo, buzzer y **LED RGB** (nuevo, prestado). El reed impide asegurar si el cable no está metido y dispara ROBO si lo sacan a la fuerza. El RGB muestra el estado con colores | `firmware/esp32/hal/` · pruebas `e13_led_rgb.py` y `e14_cerrojo_reed.py` | ✅ Código · 🟡 montaje |
| 3 | **Sujeción real a la bici** | Abrazadera sin fin inoxidable con hule alrededor del tubo del cuadro, en lugar de la cinta de los tenis. El alcance se redefinió como **sistema de alarma y bloqueo disuasorio**, con sus límites mecánicos explicados | [README › Alcance](../README.md#alcance-y-límites-mecánicos-honestos) | 🟡 Por comprar la abrazadera |
| 4a | **Detección de persona** (MobileNet-SSD / YOLO) en lugar de rostro | YuNet (caras) se reemplazó por **YOLOv5s (COCO, clase "person")** con `cv2.dnn`. MobileNet-SSD no se pudo usar porque OpenCV 5 ya no lee modelos Caffe. Con fotos reales de nuestra cámara detecta cuerpos y hasta una mano | `servidor/ia/detector.py` | ✅ |
| 4b | **La alarma no debe depender de la laptop** | El servidor ya **no** manda órdenes a los actuadores (`alerta_ia` se eliminó): solo publica el resultado firmado. La **ESP32 decide**: con 1 persona da un aviso morado; con 2 personas y la bici movida, ROBO. Sin laptop, la alarma, las fotos y Telegram siguen funcionando | `firmware/esp32/main.py` → `_resultado_ia()` | ✅ |
| 5a | **Firebase no solo para enlazar: guardar y escuchar en tiempo real** | **Guarda:** lecturas, alertas, eventos (historial con origen), eventos_ia y estado. **Escucha:** el dashboard usa `onSnapshot` en 6 consultas y el servidor usa `on_snapshot` sobre `comandos`. Los botones del dashboard → Firestore → servidor → MQTT firmado → ESP32, en menos de 1 s, y el estado del comando se ve en vivo | `servidor/nube.py` · `interfaz/index.html` | ✅ |
| 5b | **Cerrar las reglas de lectura pública (`".read": true`)** | `".read": true` es sintaxis de **Realtime Database**: el proyecto no la tiene creada, lo revisamos en la consola. Aun así dejamos `database.rules.json` con todo en `false`. Las reglas de **Firestore** se publicaron de nuevo el 25/nov: lectura solo para 2 UID, escritura solo para crear comandos validados y cualquier otra ruta cerrada | `interfaz/firestore.rules` · [captura](../media/firestore-reglas-publicadas.jpg) | ✅ |

## Mejoras extra que encontramos al revisar

- **Seguridad MQTT:** `broker.hivemq.com` es público, así que antes cualquiera podía publicar `liberar`. Ahora todo lo que entra a la ESP32 va **firmado con HMAC-SHA256** y lleva un contador anti-repetición guardado en la flash.
- **Conexión en vivo:** con el *last will* de MQTT, el dashboard sabe si la ESP32 se desconectó aunque ya no pueda avisar.
- **Ultrasónico filtrado** con la mediana de 3 lecturas, para que un eco raro no tome fotos falsas.
- **Autodiagnóstico:** si el MPU6050 deja de responder (cable suelto o arrancado), se avisa y se intenta reiniciarlo.
- **Bot:** si alguien ajeno le escribe, se le avisa al dueño. Si se abre desde el dashboard, el dueño recibe un mensaje en Telegram.
- **Cámara:** ping MQTT cada 30 s y reintento, para no perder fotos.
- **Una sola versión del código:** antes había 3 copias distintas (GitHub, OneDrive y las placas). Ahora el repositorio es la única fuente.

## Pruebas del 25 de noviembre

| Prueba | Resultado |
|---|---|
| Simulación de la ESP32 (máquina de estados, reed, IA, firma, replay, lazo, inclinación, presencia, buscar, LED) | 50 / 50 (versión del 25/nov) |
| Simulación de la Freenove (botones, confirmación, extraños, fotos, MQTT con reconexión, sin internet) | 17 / 17 |
| `telegram.py` (peticiones HTTP y lectura de `getUpdates`) | OK |
| Punta a punta con un broker real (placas simuladas + servidor con YOLO + comandos del dashboard) | 18 / 18 |
| Config viejo de la placa (sin los ajustes nuevos) | Arranca y funciona |

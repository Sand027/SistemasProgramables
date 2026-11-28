# 🎤 Guion de la demostración (5 minutos)

> La maestra pidió ver la demo **sin laptop**: los pasos 1 a 9 funcionan solo con las dos placas, la powerbank y el celular. La laptop (IA + dashboard) se enseña al final, aparte.

## Antes de entrar (checklist)

- [ ] Powerbank cargada y **cable USB "Y"** (o dos cables) para las dos placas
- [ ] WiFi con internet (escuela u hotspot con **"Maximizar compatibilidad"**), el mismo en los dos `config.py`
- [ ] Chat del bot abierto y **proyectado o a la vista** de la maestra
- [ ] Borrar `estado.txt` de la ESP32 para empezar en **DESARMADO**
- [ ] **Tarjeta del dueño** (su UID en `TARJETAS_DUENO`) y **otra tarjeta o llavero** que no esté registrado
- [ ] Caja **cerrada con sus 4 tornillos**, sujeta al cuadro con la abrazadera, y cable de sujeción conectado (**ENTERO**)
- [ ] Probar una vez **tarjeta → golpecito → tarjeta** antes de que les toque
- [ ] (Para el final) Laptop con `INICIAR_DEMO.bat` y sesión de Google en el dashboard

## Guion

| # | Qué hacen | Qué dicen | Qué se ve |
|---|---|---|---|
| 1 | Conectan la powerbank | "BikeSafe es un **sistema de vigilancia y alarma** que se sujeta al cuadro. No es un candado: vigila y avisa." | LED cian y luego verde parpadeando; llega "BikeSafe encendido" |
| 2 | Pasan la **tarjeta ajena** | "Solo reconoce al dueño. Otra tarjeta no hace nada, solo pita." | Pitido largo y LED rojo un momento; sigue DESARMADO |
| 3 | Pasan la **tarjeta del dueño** | "Con su tarjeta empieza a vigilar. El servo **destapa la cámara**." | 🛡 VIGILANDO en Telegram, LED **azul**, la pestaña se mueve |
| 4 | Un golpecito | "Un roce no dispara la sirena: es nivel 1." | 2 pitidos, LED amarillo, ⚠️ foto de AVISO |
| 5 | Se paran frente a la caja | "Si alguien se queda junto a la bici, toma foto." | 👀 foto de PRESENCIA, LED cian |
| 6 | Pasan la tarjeta ajena **3 veces** | "Alguien probando tarjetas es intento de robo." | Avisos y luego 🚨 sirena, LED **rojo**, ráfaga de 3 fotos |
| 7 | Tocan **Silenciar** en Telegram | "El **bot de Telegram** es nuestro componente no convencional: es el control y la pantalla." | Se calla, sigue VIGILANDO |
| 8 | Jalonean o inclinan la bici | "Forcejeo o levantarla = robo directo." | 🚨 sirena y fotos |
| 9 | **Desarmar → Sí, desarmar** (o la tarjeta del dueño) | "Al desarmar, el servo **tapa la cámara**: no graba al dueño ni a quien pasa." | 👋 DESARMADO, LED verde, la pestaña tapa la lente |
| 10 | Prenden la laptop y muestran el dashboard | "La IA confirma si hay una persona, pero **la ESP32 decide**. Las fotos viajan **cifradas**." | Foto con recuadro "persona", historial en vivo |
| 11 | Pican **Armar** en el dashboard | "Firebase va en las dos direcciones: el botón se guarda, el servidor lo escucha y se lo manda firmado a la ESP32." | El comando pasa a `enviado`; la ESP32 vigila |

## Preguntas probables

- **¿Por qué ya no es un candado?** Un servo SG90 no puede trabar una bici de verdad. Lo honesto es lo que sí hace bien: **vigilar, alarmar y avisar** con evidencia. Recomendamos usarlo junto con un candado.
- **¿Para qué sirve el servo?** Es un **obturador de privacidad**: tapa la cámara cuando está desarmado y la destapa al vigilar.
- **¿Qué falló con el RFID la primera vez?** El primer RC522 tuvo un corto por un puente de estaño y después nunca contestó por SPI (`0x00`/`0xFF` en 8 combinaciones; MISO "al aire"). Con el módulo que nos prestaron, soldado y en el SPI por hardware, sí funciona. Detalle en el README.
- **¿Y si no hay internet?** Sigue vigilando y sonando, porque eso no depende de la red. Las alertas se guardan y se mandan al volver la conexión. El RFID funciona sin internet.
- **¿Y si alguien más le escribe al bot?** Solo obedece el chat del dueño, y le avisa que alguien más escribió.
- **¿Y si alguien publica "desarmar" en el broker público?** Se rechaza: todo lo que entra a la ESP32 va firmado con HMAC-SHA256 y un contador que no se repite.
- **¿Cualquiera puede ver las fotos en el broker?** No: van cifradas con AES-256 y firmadas. A Telegram van por HTTPS solo al chat del dueño.
- **¿Por qué YOLO y no MobileNet-SSD?** OpenCV 5 ya no lee modelos Caffe; YOLOv5 en ONNX corre con `cv2.dnn` en OpenCV 4.8 y 5.
- **¿Por qué dos placas?** La cámara ocupa casi todos los pines de la Freenove. Así el cerebro tiene pines libres y, si la cámara falla, la alarma sigue funcionando.

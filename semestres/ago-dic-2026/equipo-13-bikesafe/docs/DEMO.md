# 🎤 Guion de la demostración (5 minutos)

## Antes de entrar (checklist)

- [ ] Powerbank cargada y **cable USB "Y"** (o dos cables) para las dos placas
- [ ] Hotspot del celular encendido con **"Maximizar compatibilidad"**, el mismo WiFi del `config.py`
- [ ] Chat del bot abierto y **proyectado o a la vista** de la maestra
- [ ] Borrar `estado.txt` de la ESP32 para empezar en **LIBRE**
- [ ] Interruptor del lazo en posición **ENTERO**
- [ ] Probar una vez **Cerrar → golpecito → Abrir** antes de que les toque
- [ ] (Si muestran la IA) Laptop en el mismo WiFi con `mosquitto -v`, `python mqtt_bridge.py` y el dashboard abierto
- [ ] (Opcional) `USAR_WATCHDOG = True` en los dos `config.py` para que se reinicien solas si algo se traba

## Guion

| # | Qué hacen | Qué dicen | Qué se ve |
|---|---|---|---|
| 1 | Conectan la powerbank | "BikeSafe es un candado que va en la mochila y se amarra a cualquier estacionamiento." | Llega "BikeSafe encendido" con los botones |
| 2 | Tocan **Cerrar** | "El dueño lo asegura desde Telegram. No necesita llaves ni otra app." | Servo cierra, LED verde fijo, "bici ASEGURADA" |
| 3 | Un golpecito al MPU6050 | "Un roce en el estacionamiento no dispara la sirena: es nivel 1, solo aviso." | 2 pitidos y ⚠️ foto de AVISO |
| 4 | Se paran frente al HC-SR04 | "Si alguien se queda junto a la bici, toma una foto preventiva." | 👀 foto de PRESENCIA |
| 5 | **4 jalones** o mueven el interruptor | "Esto ya es robo: forcejeo o cable cortado." | 🚨 Sirena, LED rojo y **3 fotos** |
| 6 | Tocan **Silenciar** | "El dueño calla la alarma desde donde esté; la bici sigue asegurada." | Se calla la sirena |
| 7 | Tocan **Estado** | "Puede revisar cómo está todo en cualquier momento." | Resumen con distancia, inclinación y conteos |
| 8 | Tocan **Buscar** | "En un estacionamiento lleno, la hace sonar para encontrarla." | Suena 5 s |
| 8b | (Con la laptop) Muestran el dashboard | "Cada foto pasa por una IA con OpenCV que confirma si hay una persona, y todo queda guardado en Firebase." | Evento `persona` con su confianza y la miniatura |
| 9 | Tocan **Abrir → Sí, abrir** | "Abrir siempre pide confirmación, para evitar accidentes." | Servo abre, "bici LIBERADA" |

## Preguntas probables

- **¿Por qué no usaron RFID?** Lo intentamos: el RC522 tuvo un corto por la soldadura y después nunca respondió por SPI. El control desde el celular estaba en nuestro "a futuro" y lo adelantamos. Además es más práctico, porque no hay llavero que perder.
- **¿Y si no hay internet?** El candado sigue vigilando y sonando, porque eso no depende de la red. Las alertas se guardan y se mandan al volver la conexión.
- **¿Y si alguien más le escribe al bot?** Solo obedece el chat del dueño.
- **¿Por qué dos placas?** La cámara ocupa casi todos los pines de la Freenove. Así el cerebro tiene pines libres y, si la cámara falla, la alarma sigue funcionando.

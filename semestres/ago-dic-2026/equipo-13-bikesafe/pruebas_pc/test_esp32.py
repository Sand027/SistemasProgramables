# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   pruebas_pc/test_esp32.py
# Objetivo:  Pruebas del firmware de la ESP32 cerebro (60 casos)
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
import os, sys, shutil, json, tempfile
AQUI=os.path.dirname(os.path.abspath(__file__))
FW=os.path.join(AQUI,"..","firmware","esp32")
tmp=tempfile.mkdtemp(); os.chdir(tmp)
for f in ("main.py","red.py","firma.py"): shutil.copy(os.path.join(FW,f), tmp)
shutil.copytree(os.path.join(FW,"hal"), os.path.join(tmp,"hal"))
cfg=open(os.path.join(FW,"config.example.py")).read()
cfg=cfg.replace('MQTT_CLAVE = ""','MQTT_CLAVE = "clave-de-prueba-123"')
cfg=cfg.replace('"A1B2C3D4",','"DUE00001",')
open("config.py","w").write(cfg)
sys.path[:0]=[AQUI+"/fakes",AQUI,tmp]
import reloj; reloj.instalar(); from reloj import Reloj
import machine, network
from umqtt import simple
import firma, config, mfrc522
import main as M

ok=0; fallas=0
def check(cond, texto):
    global ok, fallas
    if cond: ok+=1; print("  OK ", texto)
    else: fallas+=1; print("  XX FALLA:", texto)

def correr(ms):
    fin=Reloj.ms+ms
    while Reloj.ms<fin:
        app.vuelta(); Reloj.ms+=10

uart=lambda: machine.UARTS[2]
def salida(): s=list(uart().salida); uart().salida.clear(); return s
def cmd_tg(c): uart().entrada += ("CMD|"+c+"\n").encode()
cli=lambda: simple.CLIENTES[-1]
def pubs(topico): return [m for t,m,r in cli().pub if t==topico]
contador=[1795000000000]
def mqtt(topico, texto, firmar=True, cont=None):
    if firmar:
        contador[0]+=1
        texto=firma.firmar(config.MQTT_CLAVE, texto, cont or contador[0])
    cli().cola.append((topico, texto.encode()))


def tarjeta(uid): mfrc522.TARJETAS.append(uid)
TAPA=15
machine.forzar(TAPA, 1)      # tapa de la caja ABIERTA (iman lejos)
machine.forzar(14, 0)        # cable de sujecion entero (a GND)
print("== Arranque")
app=M.BikeSafe()
check(app.estado=="DESARMADO","arranca DESARMADO")
check(app.rfid is not None,"lector RFID detectado (version 0x92)")
check(app.obturador.tapado,"camara TAPADA por el obturador (privacidad)")
correr(50)
check(cli().will==(b"bikesafe/conexion", b"offline", True),"ultima voluntad offline")
check("online" in pubs(b"bikesafe/conexion"),"publica online")
check(cli().cid.startswith("bikesafe-esp32-"),"id de cliente unico: "+cli().cid)
correr(1000)
check(app.luz.color_actual in ("verde","apagado"),"DESARMADO parpadea verde")

print("== Armar con la tapa ABIERTA")
salida(); tarjeta("DUE00001"); correr(200); s=salida()
check(app.estado=="DESARMADO","no arma con la caja abierta")
check(any("NO arme" in x for x in s),"avisa por Telegram que no armo")

print("== Tarjeta ajena estando DESARMADO")
salida(); tarjeta("AJENA111"); correr(200); s=salida()
check(app.estado=="DESARMADO" and not any(x.startswith("FOTO|") for x in s),"pita pero no toma foto ni arma")

print("== Armar con la tarjeta del dueno")
machine.forzar(TAPA, 0); correr(3000); salida(); tarjeta("DUE00001"); correr(300); s=salida()
check(app.estado=="VIGILANDO","tarjeta del dueno -> VIGILANDO")
check(not app.obturador.tapado,"obturador DESTAPA la camara")
check(any("VIGILANDO" in x for x in s),"Telegram: VIGILANDO")
check(open("estado.txt").read()=="VIGILANDO","guarda estado.txt")
check(app.luz.color_actual=="azul","LED azul fijo")
ev=[json.loads(m) for m in pubs(b"bikesafe/evento")]
check(any(e["tipo"]=="estado" and e["detalle"]=="DESARMADO -> VIGILANDO" and e["origen"]=="tarjeta" for e in ev),"evento con origen tarjeta")

print("== Tarjetas ajenas vigilando: 2 avisos y a la 3a ROBO")
salida(); tarjeta("AJENA111"); correr(3000); tarjeta("AJENA222"); correr(3000); s=salida()
check(app.estado=="VIGILANDO" and sum(1 for x in s if "Tarjeta desconocida" in x)>=1,"2 tarjetas ajenas = avisos")
tarjeta("AJENA333"); correr(300)
check(app.estado=="ALARMA","3a tarjeta ajena en 1 min = ALARMA")
cmd_tg("silenciar"); correr(100)
check(app.estado=="VIGILANDO","silenciar -> sigue VIGILANDO")

print("== Un toque (nivel 1)")
salida(); app._ultima_foto_ms-=30000; machine.I2C.lectura=(0.3,0.0,1.0); correr(60); machine.I2C.lectura=(0.0,0.0,1.0); correr(500)
s=salida()
check(app.estado=="VIGILANDO","sigue VIGILANDO tras un toque")
check(any(x.startswith("FOTO|AVISO|Movimiento (1 de 4)") for x in s),"pide foto de AVISO")

print("== IA (firmada) ve persona: 1a vez = aviso morado")
salida(); mqtt(b"bikesafe/ia/resultado", json.dumps({"clase":"persona","conf":0.82}))
correr(50); s=salida()
check(app.estado=="VIGILANDO","persona sola = aviso, no robo")
check(any("la IA confirmo una PERSONA" in x and "82%" in x for x in s),"Telegram: IA confirmo persona 82%")
check(app.luz.color_actual=="morado","LED morado")
print("== IA 2a persona + la bici se movio = ROBO")
mqtt(b"bikesafe/ia/resultado", json.dumps({"clase":"persona","conf":0.77})); correr(50)
s=salida()
check(app.estado=="ALARMA","pasa a ALARMA")
check(any("FOTO|ROBO|IA: persona manipulando" in x for x in s),"foto de ROBO por IA")
check(app.buzzer.sonando,"sirena prendida")
print("== Rafaga de fotos")
correr(13000); s=salida()
check(sum(1 for x in s if x.startswith("FOTO|ROBO|Foto extra"))==2,"2 fotos extra en la rafaga")
print("== Silenciar desde Telegram")
cmd_tg("silenciar"); correr(50); s=salida()
check(app.estado=="VIGILANDO" and not app.buzzer.sonando,"se calla y sigue VIGILANDO")
check(any("silenciada" in x for x in s),"contesta silenciada")

print("== Abren la caja (reed > 0.5 s)")
machine.forzar(TAPA, 1); correr(300)
check(app.estado=="VIGILANDO","300 ms todavia no")
correr(500)
check(app.estado=="ALARMA","ALARMA por caja abierta")
check(any("Abrieron la caja" in m for m in pubs(b"bikesafe/alerta")),"alerta MQTT de la tapa")
machine.forzar(TAPA, 0)

print("== Fin automatico de la alarma (60 s)")
salida(); correr(61000); s=salida()
check(app.estado=="VIGILANDO","se calla sola al minuto")
check(any("se apago sola" in x for x in s),"avisa por Telegram")

print("== Seguridad MQTT")
mqtt(b"bikesafe/cmd","desarmar",firmar=False); correr(30)
check(app.estado=="VIGILANDO","rechaza 'desarmar' SIN firma")
cli().cola.append((b"bikesafe/cmd", b"desarmar|1795000009999|0000000000000000")); correr(30)
check(app.estado=="VIGILANDO","rechaza firma falsa")
viejo=firma.firmar("otra-clave","desarmar",1795999999999)
cli().cola.append((b"bikesafe/cmd", viejo.encode())); correr(30)
check(app.estado=="VIGILANDO","rechaza firma con otra clave")
check(app.red.rechazados==3,"cuenta 3 rechazados")
print("== Desarmar firmado desde el dashboard")
salida(); mqtt(b"bikesafe/cmd","desarmar"); correr(50); s=salida()
check(app.estado=="DESARMADO","desarma con mensaje firmado")
check(app.obturador.tapado,"al desarmar se TAPA la camara")
check(any("DESARMADO" in x and "(desde dashboard)" in x for x in s),"avisa al dueno que se desarmo desde el dashboard")
print("== Foto manual estando DESARMADO")
salida(); cmd_tg("foto"); correr(100); s=salida()
check(any(x.startswith("FOTO|MANUAL") for x in s) and not app.obturador.tapado,"destapa para la foto")
correr(6500)
check(app.obturador.tapado,"y vuelve a tapar a los 6 s")
print("== Repeticion del mismo mensaje (replay)")
tarjeta("DUE00001"); correr(300)
repetido=firma.firmar(config.MQTT_CLAVE,"desarmar",contador[0])
cli().cola.append((b"bikesafe/cmd", repetido.encode())); correr(30)
check(app.estado=="VIGILANDO","rechaza mensaje repetido (replay)")
check(open("contador.txt").read()==str(contador[0]),"guarda el contador en flash")

print("== Estado por Telegram")
salida(); cmd_tg("estado"); correr(30); s=salida()
txt=[x for x in s if x.startswith("MSG|BikeSafe: VIGILANDO")]
check(bool(txt) and "Camara: DESTAPADA" in txt[0] and "Tapa de la caja: CERRADA" in txt[0] and "~" in txt[0],"estado con camara, tapa y saltos ~")
print("   ", txt[0][:170] if txt else s)

print("== Acelerometro desconectado")
salida(); app._ultima_foto_ms-=30000; machine.I2C.falla=True; correr(400); s=salida()
check(any("FOTO|AVISO|El acelerometro no responde" in x for x in s),"aviso de acelerometro desconectado")
machine.I2C.falla=False; correr(200)
check(app.estado=="VIGILANDO","se recupera sin alarma")

print("== Cable de sujecion cortado (GPIO14)")
machine.forzar(14,1); correr(300)
check(app.estado=="ALARMA","cable cortado = ALARMA")
machine.forzar(14,0)
cmd_tg("silenciar"); correr(50)

print("== Inclinacion > 25 grados por 1.2 s")
machine.I2C.lectura=(0.0,0.6,0.8); correr(1500)
check(app.estado=="ALARMA","bici levantada = ALARMA")
machine.I2C.lectura=(0.0,0.0,1.0); cmd_tg("silenciar"); correr(50)

print("== Presencia con ultrasonico (3 s a < 50 cm)")
salida(); app._ultima_foto_ms-=30000; machine.DISTANCIA[0]=30.0; correr(3800); s=salida()
check(any(x.startswith("FOTO|PRESENCIA|Alguien a 30 cm") for x in s),"foto de PRESENCIA")
machine.DISTANCIA[0]=150.0

print("== Buscar y comandos de actuador")
cmd_tg("buscar"); correr(100)
check(app.buzzer.sonando and app.luz.color_actual in ("blanco","apagado"),"Buscar: suena y parpadea blanco")
correr(5200)
check(not app.buzzer.sonando and app.luz.color_actual=="azul","Buscar termina y regresa a azul")
mqtt(b"bikesafe/led/cmd","morado"); correr(30)
check(app.luz.color_actual=="morado","led/cmd morado (actuador por MQTT)")
mqtt(b"bikesafe/led/cmd","normal"); correr(30)
check(app.luz.color_actual=="azul","led/cmd normal")
mqtt(b"bikesafe/servo/cmd","tapar"); correr(30)
check(app.obturador.tapado,"servo/cmd tapar (actuador por MQTT)")
mqtt(b"bikesafe/servo/cmd","destapar"); correr(30)

print("== Publicacion de sensores")
cli().pub.clear(); correr(2100)
js=[json.loads(m) for m in pubs(b"bikesafe/sensores")]
check(js and js[-1]["tapa"]=="CERRADA" and js[-1]["obturador"]=="DESTAPADA" and js[-1]["lazo"]=="ENTERO" and "luz" in js[-1],"JSON de sensores con tapa, obturador, lazo y luz: "+str(js[-1] if js else None))
check(pubs(b"bikesafe/sensor/tapa")[-1]=="CERRADA","topico bikesafe/sensor/tapa")
check(cli().pings>=1,"manda ping MQTT")

print("== Desarmar con la tarjeta del dueno")
tarjeta("DUE00001"); correr(300)
check(app.estado=="DESARMADO" and app.obturador.tapado,"tarjeta del dueno -> DESARMADO y camara tapada")
tarjeta("DUE00001"); correr(300)
check(app.estado=="DESARMADO","la misma tarjeta pegada no re-arma (anti-rebote 2.5 s)")
correr(3000); tarjeta("DUE00001"); correr(300)

print("== Reinicio vigilando (se va la luz)")
app2=M.BikeSafe()
check(app2.estado=="VIGILANDO","al volver la luz sigue VIGILANDO")
print("== RC522 sin comunicacion (0x00)")
mfrc522.VERSION[0]=0x00
app3=M.BikeSafe()
check(app3.rfid is None and app3.estado=="VIGILANDO","sin RFID sigue funcionando (Telegram/dashboard)")
check(any("encendio sin: Lector RFID" in x for x in salida()),"avisa por Telegram que el RFID no respondio")
mfrc522.VERSION[0]=0x92

print("\nRESULTADO: {} OK, {} fallas".format(ok, fallas))
sys.exit(1 if fallas else 0)

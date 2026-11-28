# ============================================
# Proyecto:  BikeSafe - Sistema de vigilancia y alarma para bicicletas
# Archivo:   pruebas_pc/test_cam.py
# Objetivo:  Pruebas del firmware de la Freenove y su bot (21 casos)
# Equipo:    Oscar Sandoval Cabrera (23240457),
#            Diego Josue Talamantes Santiago (23240355)
# Materia:   Sistemas Programables - ISC TecNM Leon
# Semestre:  ago-dic-2026
# ============================================
import os, sys, shutil, tempfile, json
AQUI=os.path.dirname(os.path.abspath(__file__))
FW=os.path.join(AQUI,"..","firmware","camara")
tmp=tempfile.mkdtemp(); os.chdir(tmp)
for a in ("main.py","cifrado.py"): shutil.copy(os.path.join(FW,a), tmp)
cfg=open(os.path.join(FW,"config.example.py")).read().replace("USAR_TELEGRAM = False","USAR_TELEGRAM = True").replace('TELEGRAM_CHAT_ID = "000000000"','TELEGRAM_CHAT_ID = "555"').replace('MQTT_CLAVE = ""','MQTT_CLAVE = "clave-de-prueba-123"')
open("config.py","w").write(cfg)
sys.path[:0]=[AQUI+"/fakes_cam",AQUI+"/fakes",AQUI,tmp]
import reloj; reloj.instalar(); from reloj import Reloj
import machine, network, telegram
from umqtt import simple
import main as M
ok=fallas=0
def check(c,t):
    global ok,fallas
    if c: ok+=1; print("  OK ",t)
    else: fallas+=1; print("  XX FALLA:",t)
f=M.Fotografo()
uart=machine.UARTS[1]
def correr(ms):
    fin=Reloj.ms+ms
    while Reloj.ms<fin:
        o=f._leer_orden()
        if o: f.atender_orden(o)
        f._revisar_wifi(Reloj.ms); f._revisar_bot(Reloj.ms); f._reenviar_pendientes(Reloj.ms); f._mantener_mqtt(Reloj.ms)
        Reloj.ms+=20
def resp(): s=list(uart.salida); uart.salida.clear(); return s
correr(4000)
check(any(l[0]=="msg" and "encendido" in l[1] for l in telegram.LLAMADAS),"manda 'BikeSafe encendido' con botones")
print("== Botones")
telegram.LLAMADAS.clear(); resp()
telegram.ENTRADA += [("555","Armar")]; correr(3100)
check("CMD|armar\n" in resp(),"Armar -> CMD|armar")
telegram.ENTRADA += [("555","Foto")]; correr(3100)
check("CMD|foto\n" in resp(),"Foto pasa por la ESP32 (para destapar el obturador)")
telegram.ENTRADA += [("555","/Desarmar@BikeSafe_bot")]; correr(3100)
check(any(l[0]=="msg" and l[2]=="confirmar" for l in telegram.LLAMADAS),"Desarmar pide confirmacion")
telegram.ENTRADA += [("555","Sí, desarmar")]; correr(3100)
check("CMD|desarmar\n" in resp(),"'Si, desarmar' -> CMD|desarmar")
telegram.ENTRADA += [("555","si")]; correr(3100)
check("CMD|desarmar\n" not in resp(),"'si' sin pedir Desarmar antes NO desarma")
print("== Extranos")
telegram.LLAMADAS.clear()
telegram.ENTRADA += [("999","Desarmar"),("999","Armar")]; correr(3100)
r=resp()
check(not any("CMD|" in x for x in r),"ignora al extrano")
check(sum(1 for l in telegram.LLAMADAS if "Alguien mas (chat 999)" in l[1])==1,"avisa al dueno UNA vez")
print("== Foto pedida por la ESP32")
telegram.LLAMADAS.clear(); simple.CLIENTES.clear()
uart.entrada += "FOTO|ROBO|Cable cortado\n".encode(); correr(100)
check(any(l[0]=="foto" and "ROBO: Cable cortado" in l[1] for l in telegram.LLAMADAS),"manda la foto a Telegram con pie")
check("OK|FOTO|telegram\n" in resp(),"contesta OK|FOTO|telegram")
c=simple.CLIENTES[-1]
check([t for t,m,r in c.pub]==[b"bikesafe/cam/info",b"bikesafe/cam/frame"],"publica info + frame por MQTT")
import cifrado
check(c.pub[1][1][:3]==b"BS1" and c.pub[1][1][3:5]!=b"\xff\xd8","el frame viaja CIFRADO (no es un JPEG legible)")
check(json.loads(cifrado.descifrar("clave-de-prueba-123",c.pub[0][1]))["nivel"]=="ROBO","info cifrada; con la clave se descifra a JSON")
try: cifrado.descifrar("otra-clave",c.pub[1][1]); check(False,"otra clave no descifra")
except ValueError: check(True,"con otra clave NO se puede descifrar")
check(c.cid.startswith("bikesafe-cam-"),"id MQTT unico "+c.cid)
print("== MQTT se cae: reintenta")
c.fallar_publish=1; c.pub.clear()
uart.entrada += "FOTO|AVISO|Movimiento (1 de 4)\n".encode(); correr(100)
c2=simple.CLIENTES[-1]
check(c2 is not c and len(c2.pub)==2,"reconecta y la foto SI llega al servidor")
correr(31000)
check(c2.pings>=1,"ping MQTT cada 30 s")
print("== Mensaje con saltos ~")
telegram.LLAMADAS.clear()
uart.entrada += "MSG|BikeSafe: VIGILANDO~Tapa: CERRADA\n".encode(); correr(60)
check(any(l[1]=="BikeSafe: VIGILANDO\nTapa: CERRADA" for l in telegram.LLAMADAS),"convierte ~ en salto de linea")
print("== Sin internet: guarda y reenvia")
telegram.FALLA[0]=True; network.WLAN.conectado=False; telegram.LLAMADAS.clear()
uart.entrada += "FOTO|ROBO|Forcejeo continuo\n".encode(); correr(100)
check(len(f._pendientes)==1,"guarda la alerta pendiente")
telegram.FALLA[0]=False; network.WLAN.conectado=True; correr(16000)
check(any(l[0]=="foto" and "Forcejeo" in l[1] for l in telegram.LLAMADAS) and not f._pendientes,"al volver el internet la manda")
print("\nRESULTADO: {} OK, {} fallas".format(ok,fallas))
sys.exit(1 if fallas else 0)

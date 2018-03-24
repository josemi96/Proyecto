#Version 1.1

#SETUP
import bluetooth
import RPi.GPIO as GPIO
import time
import shlex, subprocess
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#Configuracion del rele (LED)
LED=12
GPIO.setup(LED,GPIO.OUT)
GPIO.output(LED,0)

#Funcion leer Temperatura:
def get_temp_sens():
        tfile = open("/sys/bus/w1/devices/28-0516a180cfff/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        return float(temperature)

#Funcion leer sensor de Luz
pin_light = 7
def rc_time (pin_light):
    count = 0
    #Output on the pin for
    GPIO.setup(pin_light, GPIO.OUT)
    GPIO.output(pin_light, GPIO.LOW)
    time.sleep(0.1)
    #Change the pin back to input
    GPIO.setup(pin_light, GPIO.IN)
    #Count until the pin goes high
    while (GPIO.input(pin_light) == GPIO.LOW):
        count += 1
    return count

#Configuracion por defecto del modo Automatico:
temperatura = 25
luz=50 #En tanto %

#Comienzo del programa:
#Catch when script is interrupted, cleanup correctly
try:
    server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM) #Creamos el socket bluetooth
    server_socket.bind(("",bluetooth.PORT_ANY))
    server_socket.listen(1)
    client_socket,address=server_socket.accept()
    print "Accepted connection from:" , address
 
    # Main loop
    while True:
        data = client_socket.recv(1024)
        print "Received: " , data

        if (data == "Activar_Rele"):
          print "Comando: Activar_Rele"
          GPIO.output(LED,1)

        if (data =="Desactivar_Rele"):
          print "Comando: Desactivar_Rele"
          GPIO.output(LED,0)

        if (data =="Leer_Luz"):
          print "Comando: Leer_Luz"
          measure = rc_time(pin_light)
          print measure

        if (data =="Leer_Temp"):
          print "Comando: Leer_Temp"
          temp = get_temp_sens()
          client_socket.send("%10.3f" % temp)
          print temp

        
        if(data=="Config_Auto"):
          print "Comando: Config_Auto"
          data = client_socket.recv(1024)
          luz=data
          data = client_socket.recv(1024)
          temperatura=data         

        if(data=="Automatizacion"):
          print "Comando: Automatizacion"
          p = subprocess.Popen(["python","Automatizacion.py",luz,temperatura])
     
        if(data=="No_Automatizacion"):
          print "Comando: No_Automatizacion"
          p.terminate()

        if(data=="Cerrar_Programa"):
          print "Comando: Cerrar_Programa"
          break

    # End Main loop
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    client_socket.close()
    server_socket.close()

#Fin del Programa

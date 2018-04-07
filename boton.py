from subprocess import call
import RPi.GPIO as gpio
 
# Definimos una funcion para que el script no se detenga
def loop():
 try:
    raw_input()
 
 
 
# Definimos una funcion que se ejecutara cuando se llame a la interrupcion
def shutdown(pin):
   gpio.output(12,1)
 
gpio.setmode(gpio.BOARD) # Ponemos la placa en modo BOARD
gpio.setup(12,gpio.OUT)
gpio.setup(13, gpio.IN) # Configuramos el pin 13 como entrada
# Configuramos una interrupcion  para cuando se aprete el boton 
gpio.add_event_detect(13, gpio.RISING, callback=shutdown, bouncetime=200)
while(1) 
#loop() # Iniciamos la funcionn para que el script siga en marcha

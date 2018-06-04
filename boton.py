import subprocess
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13,GPIO.IN)
prev_input = 0
Encendido=False

while True:
  input = GPIO.input(13)
  if ((not prev_input) and input):
     p = subprocess.Popen(["python","/home/pi/Proyecto/VersionFinal.py"])
     Encendido = True
  prev_input = input
  #Pequena pausa
  time.sleep(0.5)
  if( Encendido == True ):
     while p.poll() is None:
        time.sleep(0.5)
     exit(0)
  

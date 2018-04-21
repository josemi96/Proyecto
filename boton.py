import subprocess
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(13,GPIO.IN)
prev_input = 0
ok=True

while ok:
  input = GPIO.input(13)
  if ((not prev_input) and input):
     pid_a = subprocess.Popen(["python","/home/pi/Proyecto/Version1.py"])
     ok=False
  prev_input = input
  #Pequena pausa
  time.sleep(0.05)
exit(0)

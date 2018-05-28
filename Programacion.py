#Programacion

import sys
import RPi.GPIO as GPIO
import time

#Configuracion de los reles: 
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
R1=16
R2=12
GPIO.setup(R1,GPIO.OUT)
GPIO.setup(R2,GPIO.OUT)
GPIO.output(R1,0)
GPIO.output(R2,0)

#Catch when script is interrupted, cleanup correctly
try:
    Modo1=  int(sys.argv[1])
    Hora1= (sys.argv[2])
    Minuto1= (sys.argv[3])
    Modo2=  int(sys.argv[4])
    Hora2= (sys.argv[5])
    Minuto2= (sys.argv[6])
    print "Rele1 ",Modo1, "A las ",Hora1,":",Minuto1
    print "Rele2 ",Modo2, "A las ",Hora2,":",Minuto2
    # Main loop
    while True:
        time.sleep(5)
        if((Hora1==time.strftime("%H"))&(Minuto1==time.strftime("%M"))):
            GPIO.output(R1,Modo1)
        if((Hora1==time.strftime("%H"))&(Minuto1==time.strftime("%M"))):
            GPIO.output(R2,Modo2)

except KeyboardInterrupt:
    pass

finally:
    print "Fin"
    GPIO.cleanup()

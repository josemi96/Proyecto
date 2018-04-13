#Programacion

import sys
import RPi.GPIO as GPIO
import time

#Catch when script is interrupted, cleanup correctly
try:
    Modo1=  int(sys.argv[1])
    Hora1= int (sys.argv[2])
    Minuto1= int(sys.argv[3])
    Modo2=  int(sys.argv[4])
    Hora2= int (sys.argv[5])
    Minuto2= int(sys.argv[6])
    print "Rele1 ",Modo1, "A las ",Hora1,":",Minuto1
    print "Rele2 ",Modo2, "A las ",Hora2,":",Minuto2
    # Main loop
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    print "Fin"

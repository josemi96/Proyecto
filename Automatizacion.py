#Automatizacion

from setup import *

#Catch when script is interrupted, cleanup correctly
try:
    luz_sel= float(sys.argv[1])
    temperatura_sel= float (sys.argv[2])
    # Main loop
    while True:
        time.sleep(1)
        measure = rc_time(pin_to_circuit)
        #print measure
        temp = get_temp_sens()
        #print temp
        if (temp>temperatura_sel) :
             GPIO.output(R1,True)
        else:
             GPIO.output(R1,False)
        if (measure>luz_sel) :
             GPIO.output(R2,True)
        else:
             GPIO.output(R2,False)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()


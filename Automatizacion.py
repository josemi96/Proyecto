#Automatizacion
import sys
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#Lectura de la temperatura
def get_temp_sens():
        tfile = open("/sys/bus/w1/devices/28-0516a180cfff/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        return float(temperature)

#define the pin that goes to the circuit
pin_to_circuit = 7
def rc_time (pin_to_circuit):
    count = 0
    #Output on the pin for
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)
    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1
    return count

#Configuracion de los reles
#Configuracion de los reles: 
R1=16
R2=12
GPIO.setup(R1,GPIO.OUT)
GPIO.setup(R2,GPIO.OUT)
GPIO.output(R1,0)
GPIO.output(R2,0)

#Catch when script is interrupted, cleanup correctly
try:
    luz_sel= float(sys.argv[1])
    temperatura_sel= float (sys.argv[2])
    # Main loop
    while True:
        time.sleep(5)
        measure = rc_time(pin_to_circuit)
        temp = get_temp_sens()
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


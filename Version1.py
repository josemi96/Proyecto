#Version 1.1

#SETUP
import bluetooth
import RPi.GPIO as GPIO
import time
import shlex, subprocess
import smbus
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#Configuracion del LCD(16x02) I2C
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line
# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off
ENABLE = 0b00000100 # Enable bit
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command
  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT
  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)
  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)
def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)
def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

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
temperatura ="24"
luz="50" #En tanto %

#Comienzo del programa:
#Catch when script is interrupted, cleanup correctly
try:
    lcd_init()
    lcd_string(">Sin Conexion   ",LCD_LINE_1)
    server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM) #Creamos el socket bluetooth
    server_socket.bind(("",bluetooth.PORT_ANY))
    server_socket.listen(1)
    client_socket,address=server_socket.accept()
    print "Accepted connection from:" , address
    lcd_string(">Conexion: ok   ",LCD_LINE_1)
    lcd_string(">Modo Auto: off ",LCD_LINE_2)
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
          print "luz",luz
          data = client_socket.recv(1024)
          temperatura=data
          print "temperatura",temperatura         

        if(data=="Automatizacion"):
          print "Comando: Automatizacion"
          p = subprocess.Popen(["python","Automatizacion.py",luz,temperatura])
          lcd_string(">Modo Auto: on ",LCD_LINE_2)
          #write estado conectado
     
        if(data=="No_Automatizacion"):
          print "Comando: No_Automatizacion"
          p.terminate()
          lcd_string(">Modo Auto: off ",LCD_LINE_2)
          #write estado desconectado

        if(data=="Cerrar_Programa"):
          print "Comando: Cerrar_Programa"
          break

    # End Main loop
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    lcd_byte(0x01, LCD_CMD)
    client_socket.close()
    server_socket.close()

#Fin del Programa

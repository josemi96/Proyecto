#Version 1.1

#SETUP
from struct import pack, unpack
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

#Configuracion de los reles: 
R1=12
R2=16
GPIO.setup(R1,GPIO.OUT)
GPIO.setup(R2,GPIO.OUT)
GPIO.output(R1,0)
GPIO.output(R2,0)

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

#Configuracion del modo Programado:
Config_CP = False
pid_p=0

#Configuracion por defecto del modo Automatico:
Temperatura ="24"
Luz="50" #En tanto %
pid_a=0

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
    # Bucle Principal
    while True:
        data = client_socket.recv(1024)
        Comando =data[0:10]       
        print "Recibido: " , Comando

        if (Comando == "Comando_R1"):
          Comando,Modo = unpack('@10si',data)
          GPIO.output(R1,Modo)
          if(Modo==1):
           print "Activo Rele 1"
          else:
           print "Desactivo Rele 1"

        if (Comando == "Comando_R2"):
          Comando,Modo = unpack('@10si',data)
          GPIO.output(R2,Modo)
          if(Modo==1):
           print "Activo Rele 2"
          else:
           print "Desactivo Rele 2"

        if (Comando == "Comando_LL"):
          print "Realizando lectura de luminosidad.."
          measure = rc_time(pin_light)
          packet = pack('10sf',Comando,measure)
          client_socket.send(packet)
          print measure

        if (Comando =="Comando_LT"):
          print "Realizando lectura de temperatura.."
          temp = get_temp_sens()
          packet = pack('10sf',Comando,temp)
          client_socket.send(packet)
          print temp
        
        if(Comando=="Comando_CP"):
          print "Configurando modo Programado"
          Comando,Modo1,Hora1,Minuto1,Modo2,Hora2,Minuto2 = unpack('@10s6i',data)
          print "R1, ",Modo1," a las ",Hora1,":",Minuto1,"."
          print "R2, ",Modo2," a las ",Hora2,":",Minuto2,"."
          Config_CP = True

        if(Comando=="Comando_AP"):
           if (Config_CP):
              print "Activando Modo Programado"
              pid_p =subprocess.Popen(["python","Programacion.py",str(Modo1),str(Hora1),str(Minuto1),str(Modo2),str(Hora2),str(Minuto2)])
              lcd_string(">Modo Prog: on ",LCD_LINE_2)
           else:
              client_socket.send(Comando)          

        if(Comando=="Comando_NP"):
          print "Desactivando Modo Programado"
          pid_p.terminate()
          lcd_string(">Modo Prog: off ",LCD_LINE_2)          

        if(Comando=="Comando_CA"):
          print "Configurando modo Automatico"
          Comando,Luz,Temperatura = unpack('@10sii',data)
          print "Luz: ",Luz
          print "temperatura: ",Temperatura         

        if(Comando=="Comando_AA"):
          print "Activando Modo Automatico"
          pid_a = subprocess.Popen(["python","Automatizacion.py",str(Luz),str(Temperatura)])
          lcd_string(">Modo Auto: on ",LCD_LINE_2)
          #write estado conectado
     
        if(Comando=="Comando_NA"):
          print "Desactivando Modo Automatico"
          pid_a.terminate()
          GPIO.cleanup()
          lcd_string(">Modo Auto: off ",LCD_LINE_2)
          #write estado desconectado

        if(Comando=="Comando_CG"):
          print "Cerrando el Programa.."
          break

    # Fin del bucle principal
except KeyboardInterrupt:
    pass

finally:
    if (pid_a!=0):
      pid_a.terminate()
    if (pid_p!=0):
      pid_p.terminate()
    GPIO.cleanup()
    lcd_byte(0x01, LCD_CMD)
    client_socket.close()
    server_socket.close()

#Fin del Programa

#-----------------------------------------------
#-- Jose Miguel Hidalgo Rondon -----------------
#-----------------------------------------------

#INICIO DE CONFIGURACION

#Declaracion de librerias:
import time
import shlex, subprocess
import RPi.GPIO as GPIO
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

#FIN DE CONFIGURACION

#Comienzo del programa:
#Catch when script is interrupted, cleanup correctly
try:
    lcd_byte(0x01, LCD_CMD) #por si no cerro bien la ultima vez
    lcd_init()
    lcd_string(">TEMP=",LCD_LINE_1)
    lcd_string(">LUZ=",LCD_LINE_2)
    while(1):
      time.sleep(5)
      print "Realizando lectura de luminosidad.."
      measure =str( rc_time(pin_light))
      print "Realizando lectura de temperatura.."
      temp = str(get_temp_sens())
      lcd_string(">TEMP="+temp,LCD_LINE_1)
      lcd_string(">LUZ="+measure,LCD_LINE_2)

    # Fin del bucle principal
except KeyboardInterrupt:
    pass

finally:
    lcd_byte(0x01, LCD_CMD)

#Fin del Programa

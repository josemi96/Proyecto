import bluetooth
import RPi.GPIO as GPIO
LED=18


def get_temp_sens():
        tfile = open("/sys/bus/w1/devices/28-0516a180cfff/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        return float(temperature)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED,GPIO.OUT)
GPIO.output(LED,0)

server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port=1
server_socket.bind(("",port))
server_socket.listen(1)

client_socket,address=server_socket.accept()
print("Accepted connection from",address)
count = 1
while 1:
  count = count + 1
  client_socket.send("%10.3f" % get_temp_sens())
  if count == 10:
   break
 #if(data=="q"):
 # print ("Quit")
 # break

client_socket.close()
server_socket.close()


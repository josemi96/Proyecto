import bluetooth
import RPi.GPIO as GPIO
LED=18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED,GPIO.OUT)
GPIO.output(LED,0)

server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port=1
server_socket.bind(("",bluetooth.PORT_ANY))
server_socket.listen(1)

client_socket,address=server_socket.accept()
print("Accepted connection from",address)
while 1:
 data = client_socket.recv(1024)
 print ("Received: " , data)
 if (data == "0"):
  print ("GPIO 21 LOW, LED OFF")
  GPIO.output(LED,0)
 if (data =="1"):
  print ("GPIO 21 HIGH, LED ON")
  GPIO.output(LED,1)
 if(data=="q"):
  print ("Quit")
  break

client_socket.close()
server_socket.close()

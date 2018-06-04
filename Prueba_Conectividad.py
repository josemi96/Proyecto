#-----------------------------------------------
#-- Jose Miguel Hidalgo Rondon -----------------
#-----------------------------------------------
#Comienzo del programa:
#Catch when script is interrupted, cleanup correctly
import bluetooth

try:
    server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM) #Creamos el socket bluetooth
    server_socket.bind(("",bluetooth.PORT_ANY))
    server_socket.listen(1)
    client_socket,address=server_socket.accept()
    print "Accepted connection from:" , address
   
    # Bucle Principal
    while True:
        data = client_socket.recv(1024)
        Comando =data[0:12]       
        print "Recibido: " , Comando

        if(Comando=="Comando_PING"):
           client_socket.send(Comando)          

        if(Comando=="Comando_CERR"):
          print "Cerrando el Programa.."
          break

    # Fin del bucle principal
except KeyboardInterrupt:
    pass

finally:
    client_socket.close()
    server_socket.close()

#Fin del Programa

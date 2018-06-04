#-----------------------------------------------
#-- Jose Miguel Hidalgo Rondon -----------------
#-----------------------------------------------
#SETYP
from setup import *
#Comienzo del programa:
#Catch when script is interrupted, cleanup correctly
try:
    lcd_byte(0x01, LCD_CMD) #por si no cerro bien la ultima vez
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
        
        if(Comando=="Comando_L1"):
          print "Ajustando luz minima.."
          L1 = rc_time(pin_light)
          packet = pack('10sf',Comando,L1)
          client_socket.send(packet)
          print L1

        if(Comando=="Comando_L2"):
          print "Ajustando luz maxima.."
          L2 = rc_time(pin_light)
          packet = pack('10sf',Comando,L2)
          client_socket.send(packet)
          print L2


        if(Comando=="Comando_CP"):
          print "Configurando modo Programado"
          Comando,Modo1,Hora1,Minuto1,Modo2,Hora2,Minuto2 = unpack('@10s6i',data)
          print "R1, ",Modo1," a las ",Hora1,":",Minuto1,"."
          print "R2, ",Modo2," a las ",Hora2,":",Minuto2,"."
          Config_CP = True

        if(Comando=="Comando_AP"):
           if (Config_CP):
              print "Activando Modo Programado"
              pid_p =subprocess.Popen(["python","/home/pi/Proyecto/Programacion.py",str(Modo1),str(Hora1),str(Minuto1),str(Modo2),str(Hora2),str(Minuto2)])
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
          Config_CA = True

        if(Comando=="Comando_AA"):
          if(Config_CA):
             print "Activando Modo Automatico"
             pid_a = subprocess.Popen(["python","/home/pi/Proyecto/Automatizacion.py",str(Luz),str(Temperatura),str(L1),str(L2)])
             lcd_string(">Modo Auto: on ",LCD_LINE_2)
          else:
             client_socket.send(Comando)
     
        if(Comando=="Comando_NA"):
          print "Desactivando Modo Automatico"
          pid_a.terminate()
          GPIO.cleanup()
          lcd_string(">Modo Auto: off ",LCD_LINE_2)
         
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

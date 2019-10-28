#!/usr/bin/env python
import bluetooth
host = ""
port = 1    # Raspberry Pi uses port 1 for Bluetooth Communication
# Creaitng Socket Bluetooth RFCOMM communication
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')

try:
    server.bind((host, port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")
server.listen(1) # One connection at a time
# Server accepts the clients request and assigns a mac address. 
client, address = server.accept()
print("Connected To", address)
print("Client:", client)

try:
    while True:
        # Receivng the data. 
        data = client.recv(1024) # 1024 is the buffer size.
        print(data)
        try:
            max_num = int(data)
            try:
                f = open('/home/pi/Desktop/Soundmeter/decibel_data/max_decibel.txt', 'w')
            except IOError as e:
                print(e)
            else:
                f.write(str(max_num))
                f.close()
                
        except:
            print("input not int")
            
except:
    # Closing the client and server connection
    client.close()
    server.close()
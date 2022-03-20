import data_gen

#192.168.137.84:5300
ip = str(input("IP: "))
port = str(input("PORT: "))
data_gen.set_server(ip, port)
while True:
    data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
    returned_data = data_gen.get_data(data)
    rpm = round(returned_data['CurrentEngineRpm'])
    power = round((returned_data['Power']*1.34102)/1000)
    torque = round(returned_data['Torque'], 1) 
    boost = round(returned_data['Boost']/14.504, 2)
    print(f"RPM = {rpm}, Power = {power}, Torque = {torque}, Boost = {boost}")
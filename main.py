import data_gen
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()
with dpg.value_registry():
    dpg.add_string_value(default_value="127.0.0.1", tag="ip_address")
    dpg.add_string_value(default_value="5300", tag="port")

dpg.create_viewport(title='ForzaTelemetryApp', width=600, height=300)

def connect():
    ip = dpg.get_value("ip_address")
    port = dpg.get_value("port")
    print(ip, port)
    data_gen.set_server(ip, port)

with dpg.window(label="Connect"):
    dpg.add_button(label="Connect", callback=connect)
    dpg.add_input_text(label="IP", source="ip_address")
    dpg.add_input_text(label="PORT", source="port")

with dpg.window(label="Example Window"):
    dpg.add_input_text(label="IP", source="ip_address")
    dpg.add_input_text(label="PORT", source="port")

#192.168.137.84:5300
while True:
    data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
    returned_data = data_gen.get_data(data)
    rpm = round(returned_data['CurrentEngineRpm'])
    power = round((returned_data['Power']*1.34102)/1000)
    torque = round(returned_data['Torque'], 1) 
    boost = round(returned_data['Boost']/14.504, 2)
    print(f"RPM = {rpm}, Power = {power}, Torque = {torque}, Boost = {boost}")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

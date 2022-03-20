import data_gen
import exporter
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import matplotlib.pyplot as plt
import time
x = []
y = []
dpg.create_context()
with dpg.value_registry():
    dpg.add_string_value(default_value="127.0.0.1", tag="ip_address")
    dpg.add_string_value(default_value="5300", tag="port")
    dpg.add_string_value(tag="rpm")
    dpg.add_string_value(tag="power")
    dpg.add_string_value(tag="torque")
    dpg.add_string_value(tag="boost")
dpg.create_viewport(title='ForzaTelemetryApp', width=600, height=300)

def connect():
    ip = dpg.get_value("ip_address")
    port = dpg.get_value("port")
    print(ip, port)
    data_gen.set_server(ip, port)

def graph():
    print("graph")
    time.sleep(10)
    print("hello world")
    i = 0
    while i < 10:
        data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
        returned_data = data_gen.get_data(data)
        rpm = round(returned_data['CurrentEngineRpm'])
        power = round((returned_data['Power']*1.34102)/1000)
        print(rpm, power)
        x.append(rpm)
        y.append(power)
        i += 1
    print(x)
    print(y)
    plt.plot(x, y)
    # naming the x axis
    plt.xlabel('x - axis')
    # naming the y axis
    plt.ylabel('y - axis')
    # giving a title to my graph
    plt.title('My first graph!')
    # function to show the plot
    plt.show()

def run():
    while True:
        data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
        returned_data = data_gen.get_data(data)
        rpm = round(returned_data['CurrentEngineRpm'])
        power = round((returned_data['Power']*1.34102)/1000)
        torque = round(returned_data['Torque'], 1) 
        boost = round(returned_data['Boost']/14.504, 2)
        dpg.set_value("rpm", rpm)
        dpg.set_value("power", power)
        dpg.set_value("torque", torque)
        dpg.set_value("boost", boost)
        #print(f"RPM = {rpm}, Power = {power}, Torque = {torque}, Boost = {boost}")

with dpg.window(label="Connect"):
    dpg.add_button(label="Connect", callback=connect)
    dpg.add_input_text(label="IP", source="ip_address")
    dpg.add_input_text(label="PORT", source="port")

with dpg.window(label="Stats"):
    dpg.add_button(label="run", callback=run)
    dpg.add_text(source="rpm")
    dpg.add_text(source="power")
    dpg.add_text(source="torque")
    dpg.add_text(source="boost")
    dpg.add_slider_float(label="Slide to the right!", width=100)

with dpg.window(label="Graph"):
    dpg.add_button(label="graph", callback=graph)


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

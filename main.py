import data_gen
import graph
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import matplotlib.pyplot as plt
import time


dpg.create_context()

with dpg.value_registry():
	dpg.add_string_value(default_value="192.168.137.84", tag="ip_address")
	dpg.add_string_value(default_value="5300", tag="port")
	dpg.add_string_value(tag="gear")
	dpg.add_string_value(tag="rpm")
	dpg.add_string_value(tag="power")
	dpg.add_string_value(tag="torque")
	dpg.add_string_value(tag="boost")
	dpg.add_int_value(default_value=6, tag="gearbox")

def connect():
	ip = dpg.get_value("ip_address")
	port = dpg.get_value("port")
	print(ip, port)
	data_gen.set_server(ip, port)

def graph():
	global x
	global y
	x = []
	y = []
	print("graph")
	data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
	returned_data = data_gen.get_data(data)
	gear = int(dpg.get_value("gearbox")) - 1
	while True:
		data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
		returned_data = data_gen.get_data(data)
		rpm = round(returned_data['CurrentEngineRpm'])
		power = round((returned_data['Power']*1.34102)/1000)
		gear2 = returned_data['Gear']
		print(gear, gear2)
		if gear < gear2:
			break
		else:
			if power > 0:
				if y:
					test = y[-1]
					if power > int(test):
						x.append(rpm)
						y.append(power)
					else:
						continue
				else:
					x.append(rpm)
					y.append(power)
			else:
				continue			
	print(x)
	print(y)
	z = [0]
	plt.plot(x, y, z)
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
		gear = returned_data['Gear']
		rpm = round(returned_data['CurrentEngineRpm'])
		power = round((returned_data['Power']*1.34102)/1000)
		torque = round(returned_data['Torque'], 1) 
		boost = round(returned_data['Boost']/14.504, 2)
		dpg.set_value("gear", gear)
		dpg.set_value("rpm", rpm)
		dpg.set_value("boost", boost)
		if power > 0:
			dpg.set_value("power", power)
			dpg.set_value("torque", torque)
		else:
			dpg.set_value("power", 0)
			dpg.set_value("torque", 0)
			continue		
		#print(f"RPM = {rpm}, Power = {power}, Torque = {torque}, Boost = {boost}")

with dpg.window(label="Stats"):
	dpg.add_button(label="run", callback=run)
	dpg.add_text(source="gear")
	dpg.add_text(source="rpm")
	dpg.add_text(source="power")
	dpg.add_text(source="torque")
	dpg.add_text(source="boost")
	dpg.add_slider_float(label="Slide to the right!", width=100)

with dpg.window(label="Graph"):
	dpg.add_button(label="graph", callback=graph)
	dpg.add_slider_int(label="Gearbox", min_value=1, max_value=10, source="gearbox")

with dpg.window(label="Connect"):
	dpg.add_button(label="Connect", callback=connect)
	dpg.add_input_text(label="IP", source="ip_address")
	dpg.add_input_text(label="PORT", source="port")

dpg.create_viewport(title='ForzaTelemetryApp', width=1024, height=768)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

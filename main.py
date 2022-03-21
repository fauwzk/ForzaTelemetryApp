import data_gen
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
import matplotlib.pyplot as plt
import time

dpg.create_context()

gear_setting_default = 6
with dpg.value_registry():
	dpg.add_string_value(default_value="192.168.137.84", tag="ip_address")
	dpg.add_string_value(default_value="5300", tag="port")
	dpg.add_string_value(tag="gear")
	dpg.add_string_value(tag="rpm")
	dpg.add_string_value(tag="power")
	dpg.add_string_value(tag="torque")
	dpg.add_string_value(tag="boost")
	dpg.add_string_value(default_value="Not connected", tag="graph_status")
	dpg.add_string_value(default_value="Not connected", tag="run_status")
	dpg.add_string_value(default_value="Not connected", tag="connect_status")
	dpg.add_string_value(default_value=gear_setting_default, tag="gear_setting")
	dpg.add_int_value(default_value=int(gear_setting_default), tag="gearbox")

def connect():
	ip = dpg.get_value("ip_address")
	port = dpg.get_value("port")
	#print(ip, port)
	try:
		data_gen.set_server(ip, port)
		dpg.set_value("connect_status", "Connected")
		dpg.set_value("graph_status", "Not Running")
		dpg.set_value("run_status", "Not Running")
	except:
		dpg.set_value("connect_status", "Error")

def graph():
	global x
	global y
	global z
	global az
	x = []
	y = []
	z = []
	az = []
	dpg.set_value("graph_status", "Running")
	gear_setting = int(dpg.get_value("gearbox")) 
	dpg.set_value("gear_setting", str(gear_setting))
	try:
		data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
		returned_data = data_gen.get_data(data)
		while True:
			data, addr = data_gen.sock.recvfrom(1500) # buffer size is 1500 bytes, this line reads data from the socket
			returned_data = data_gen.get_data(data)
			gear = returned_data['Gear']
			rpm = round(returned_data['CurrentEngineRpm'])
			power = round((returned_data['Power']*1.34102)/1000)
			torque = round(returned_data['Torque'], 1) 
			boost = round((returned_data['Boost']*10))
			print(gear, gear_setting)
			if gear_setting == gear:
				break
			else:
				if power > 0:
					if y:
						power_high = y[-1]
						if power > int(power_high):
						#if power:
							torque_high = z[-1]
							if torque > int(torque_high):
							#if torque:
								rpm_high = x[-1]
								#if rpm > int(rpm_high):
								if rpm > int(rpm_high):
									x.append(rpm)
									y.append(power)
									z.append(torque)
									az.append(boost)
								else:
									continue
							else:
								continue
						else:
							continue
					else:
						x.append(rpm)
						y.append(power)
						z.append(torque)
						az.append(boost)
				else:
					continue
		dpg.set_value("graph_status", "Graphing")
		fig, ax = plt.subplots(figsize=(6, 6))
		ax.plot(x, y, label="Power HP")
		ax.plot(x, z, label="Torque N.m")
		ax.plot(x, az, label="boost bar*10")
		ax.legend()
		dpg.set_value("graph_status", "Finished")
		plt.show()
	except:
		dpg.set_value("graph_status", "Error")

def run():
	dpg.set_value("run_status", "Running")
	while True:
		try:
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
		except:
			dpg.set_value("run_status", "Error")

with dpg.window(label="Stats"):
	dpg.add_button(label="run", callback=run)
	dpg.add_text(source="run_status")
	dpg.add_text(source="gear")
	dpg.add_text(source="rpm")
	dpg.add_text(source="power")
	dpg.add_text(source="torque")
	dpg.add_text(source="boost")

with dpg.window(label="Graph"):
	dpg.add_slider_int(label="Gearbox", min_value=1, max_value=10, source="gearbox")
	dpg.add_text(source="gear_setting")
	dpg.add_button(label="graph", callback=graph)
	dpg.add_text(source="graph_status")

with dpg.window(label="Connect"):
	dpg.add_input_text(label="IP", source="ip_address")
	dpg.add_input_text(label="PORT", source="port")
	dpg.add_button(label="Connect", callback=connect)
	dpg.add_text(source="connect_status")

dpg.create_viewport(title='ForzaTelemetryApp', width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
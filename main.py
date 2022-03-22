import data_gen
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
import matplotlib.pyplot as plt
import time
import sys

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

def graph():
	global rpm_axis
	global power_axis
	global torque_axis
	global boost_axis
	rpm_axis = []
	power_axis = []
	torque_axis = []
	boost_axis = []
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
			boost = round((returned_data['Boost']/14.504), 2)
			#print(gear, gear_setting)
			if gear_setting == gear:
				break
			else:
				if power > 0:
					if power:
						power_high = power_axis[-1]
						if power:
							torque_high = torque_axis[-1]
							if torque:
								rpm_high = rpm_axis[-1]
								if rpm > int(rpm_high):
									rpm_axis.append(rpm)
									power_axis.append(power)
									torque_axis.append(torque)
									boost_axis.append(boost*10)
								else:
									continue
							else:
								continue
						else:
							continue
					else:
						rpm_axis.append(rpm)
						power_axis.append(power)
						torque_axis.append(torque)
						boost_axis.append(boost*10)
				else:
					continue
		#print(rpm_axis)
		#print(power_axis)
		#print(torque_axis)
		#print(boost_axis)
		dpg.set_value("graph_status", "Peak ploting")
		peak_hp = max(power_axis)
		peak_hp_index = power_axis.index(max(power_axis))
		peak_hp_rpm = rpm_axis[peak_hp_index]
		peak_torque = max(torque_axis)
		peak_torque_index = torque_axis.index(max(torque_axis))
		peak_torque_rpm = rpm_axis[peak_torque_index]
		peak_boost = round(max(boost_axis), 2)
		peak_boost_index = boost_axis.index(max(boost_axis))
		peak_boost_rpm = rpm_axis[peak_boost_index]
		#print(peak_hp, peak_hp_rpm)
		#print(peak_torque, peak_torque_rpm)
		#print(peak_boost, peak_boost_rpm)
		dpg.set_value("graph_status", "Graphing")
		fig, ax = plt.subplots(figsize=(6, 6))
		ax.plot(x, y, label="Power HP")
		ax.plot(x, z, label="Torque N.m")
		ax.plot(x, az, label="boost bar*10")
		ax.plot(peak_hp_rpm, peak_hp, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
		ax.plot(peak_torque_rpm, peak_torque, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
		ax.plot(peak_boost_rpm, peak_boost, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
		ax.legend()
		dpg.set_value("graph_status", "Show graph")
		plt.show()
		dpg.set_value("graph_status", "Finished")
	except:
		dpg.set_value("graph_status", "Error")

with dpg.window(label="Main", autosize=True, pos=(10,10)):
	dpg.add_input_text(label="IP", source="ip_address")
	dpg.add_input_text(label="PORT", source="port")
	dpg.add_button(label="Connect", callback=connect)

with dpg.window(label="Stats", autosize=True, pos=(10,175)):
	dpg.add_button(label="run", callback=run)
	dpg.add_text(source="gear")
	dpg.add_text(source="rpm")
	dpg.add_text(source="power")
	dpg.add_text(source="torque")
	dpg.add_text(source="boost")

with dpg.window(label="Graph", autosize=True, pos=(125,175)):
	dpg.add_slider_int(label="Gearbox", min_value=1, max_value=10, source="gearbox", width=50)
	dpg.add_text(source="gear_setting")
	dpg.add_button(label="graph", callback=graph)

with dpg.window(label="Status", autosize=True, pos=(400,175)):
	dpg.add_text(default_value="Connection status :")
	dpg.add_text(source="connect_status")
	dpg.add_text(default_value="Run status :")
	dpg.add_text(source="run_status")
	dpg.add_text(default_value="Graph status :")
	dpg.add_text(source="graph_status")

dpg.create_viewport(title='ForzaTelemetryApp', width=600, height=400, always_on_top=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
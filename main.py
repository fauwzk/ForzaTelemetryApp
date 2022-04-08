import data_gen
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import traceback
import json
from datetime import datetime
import os
import rich
import warnings

# Need rewriting with threading
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.")

dpg.create_context()

global home_path
global rpm_axis
global power_axis
global torque_axis
global boost_axis

home_path = os.path.expanduser('~')
gear_setting_default = 6

with dpg.value_registry():
	dpg.add_string_value(default_value="192.168.1.8", tag="ip_address")
	dpg.add_string_value(default_value="5300", tag="port")
	dpg.add_string_value(tag="gear")
	dpg.add_string_value(tag="rpm")
	dpg.add_string_value(tag="power")
	dpg.add_string_value(tag="torque")
	dpg.add_string_value(tag="boost")
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
		dpg.set_value("run_status", "Not Running")
	except Exception as e:
		#print(e)
		dpg.set_value("connect_status", f"Error")

def graph():
	rpm_axis = []
	power_axis = []
	torque_axis = []
	boost_axis = []
	dpg.set_value("run_status", "Running")
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
			boost = round((returned_data["Boost"] / 14.504), 2)
			#print(gear, gear_setting)
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
			if gear_setting == gear:
				break
			else:
				if power > 0:
					if power_axis:
						power_high = power_axis[-1]
						if power:
						#if power:
							torque_high = torque_axis[-1]
							if torque:
							#if torque:
								rpm_high = rpm_axis[-1]
								#if rpm > int(rpm_high):
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
		dpg.set_value("run_status", "Peak ploting")
		make_graph(rpm_axis, power_axis, torque_axis, boost_axis)
	except Exception as e:
		#print(e)
		dpg.set_value("run_status", f"Error")

def open_values(sender, app_data, user_data):
	rpm_axis = []
	power_axis = []
	torque_axis = []
	boost_axis = []
	del rpm_axis[:]
	del power_axis[:]
	del torque_axis[:]
	del boost_axis[:]
	path_test = app_data.get('file_path_name')
	with open(path_test) as json_file:
		data = json.load(json_file)
		rpm_axis = data['rpm']
		power_axis = data['power']
		torque_axis = data['torque']
		boost_axis = data['boost']
	dpg.set_value("run_status", "Peak ploting")
	make_graph(rpm_axis, power_axis, torque_axis, boost_axis)

def save_values():
	data = {}
	data['rpm'] = rpm_axis
	data['power'] = power_axis
	data['torque'] = torque_axis
	data['boost'] = boost_axis
	now = datetime.now()
	name = now.strftime("%d%m%Y_%H%M%S")
	with open(f"{home_path}\\{name}.json", 'w') as file: 
		json.dump(data, file)

def make_graph(rpm_axis, power_axis, torque_axis, boost_axis):
	peak_hp = max(power_axis)
	peak_hp_index = power_axis.index(max(power_axis))
	peak_hp_rpm = rpm_axis[peak_hp_index]
	peak_torque = max(torque_axis)
	peak_torque_index = torque_axis.index(max(torque_axis))
	peak_torque_rpm = rpm_axis[peak_torque_index]
	peak_boost = round(max(boost_axis), 2)
	peak_boost_index = boost_axis.index(max(boost_axis))
	peak_boost_rpm = rpm_axis[peak_boost_index]
	peak_rpm = max(rpm_axis)
	#print(peak_rpm)
	# print(peak_hp, peak_hp_rpm)
	# print(peak_torque, peak_torque_rpm)
	# print(peak_boost, peak_boost_rpm)
	markersize_setting = 15
	dpg.set_value("run_status", "Graphing")
	fig, ax = plt.subplots(figsize=(6, 6))
	ax.plot(rpm_axis, power_axis, label=f"Power HP\n{peak_hp}HP@{peak_hp_rpm}RPM")
	ax.plot(rpm_axis, torque_axis, label=f"Torque N.m\n{peak_torque}N.m@{peak_torque_rpm}RPM")
	if peak_boost != 0:
		ax.plot(rpm_axis, boost_axis, label=f"boost bar*10\n{round(peak_boost/10, 2)}bar@{peak_boost_rpm}RPM")
		ax.plot(peak_boost_rpm, peak_boost, marker="|", markersize=markersize_setting)
	ax.plot(peak_hp_rpm, peak_hp, marker="|", markersize=markersize_setting)      
	ax.plot(peak_torque_rpm, peak_torque, marker="|", markersize=markersize_setting)
	ax.set_xlabel(f"Max RPM : {peak_rpm}")
	ax.legend()
	dpg.set_value("run_status", "Finished")
	plt.show()
	del rpm_axis[:]
	del power_axis[:]
	del torque_axis[:]
	del boost_axis[:]

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
		except Exception as e:
			#print(e)
			dpg.set_value("run_status", f"Error")
			break

with dpg.file_dialog(modal=True, show=False, callback=open_values, id="open_values_file_picker", width=500, height=300, default_path=home_path):
	dpg.add_file_extension(".json", color=(255, 0, 255, 255), custom_text="[JSON]")

with dpg.window(label="Main", autosize=True, pos=(10, 10)):
	dpg.add_input_text(label="IP", source="ip_address")
	dpg.add_input_text(label="PORT", source="port")
	dpg.add_button(label="Connect", callback=connect)

with dpg.window(label="Stats", autosize=True, pos=(10, 175)):
	dpg.add_button(label="run", callback=run)
	dpg.add_text(source="gear")
	dpg.add_text(source="rpm")
	dpg.add_text(source="power")
	dpg.add_text(source="torque")
	dpg.add_text(source="boost")

with dpg.window(label="Graph", autosize=True, pos=(125, 175)):
	dpg.add_slider_int(label="Gearbox", min_value=2, max_value=10, source="gearbox", width=62)
	dpg.add_button(label="graph", callback=graph)

with dpg.window(label="file", autosize=True, pos=(400, 10)):
	dpg.add_button(label="save", callback=save_values)
	dpg.add_button(label="open", callback=lambda: dpg.show_item("open_values_file_picker"))

with dpg.window(label="Status", autosize=True, pos=(400, 175)):
	dpg.add_text(default_value="Connection status :")
	dpg.add_text(source="connect_status")
	dpg.add_text(default_value="Status :")
	dpg.add_text(source="run_status")

dpg.create_viewport(title='ForzaTelemetryApp', width=600, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
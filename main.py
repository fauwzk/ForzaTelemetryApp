import data_gen
import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt
import json
from datetime import datetime
import os
import os.path
import warnings
import ping3
import shutil
from pathlib import Path

# Need rewriting with threading
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.")

dpg.create_context()

default_initfile = "default.ini"
initfile = "fta.ini"
global home_path
home_path = os.path.expanduser("~")

connection_status = 0
gear_setting_default = 4

with dpg.value_registry():
    dpg.add_string_value(default_value="127.0.0.1", tag="ip_address")
    dpg.add_string_value(default_value="5300", tag="port")
    dpg.add_string_value(tag="gear")
    dpg.add_string_value(tag="speed")
    dpg.add_string_value(tag="rpm")
    dpg.add_string_value(tag="power")
    dpg.add_string_value(tag="torque")
    dpg.add_string_value(tag="boost")
    dpg.add_string_value(default_value="Not connected", tag="run_status")
    dpg.add_string_value(default_value="Not connected", tag="connect_status")
    dpg.add_string_value(default_value="Not connected", tag="save_status")
    dpg.add_string_value(default_value="Not connected", tag="status")
    dpg.add_string_value(default_value="Not connected", tag="error")
    dpg.add_string_value(default_value="Not connected", tag="ping")
    dpg.add_string_value(default_value=gear_setting_default, tag="gear_setting")
    dpg.add_int_value(default_value=int(gear_setting_default), tag="gearbox")

with dpg.font_registry():
    print("font.otf")
    font_path = data_gen.resource_path("font.otf")
    print(font_path)
    app_font = dpg.add_font(font_path, 15)
    telemetry_font = dpg.add_font(font_path, 65)

dpg.bind_font(app_font)

def connect():
    global connection_status
    ip = dpg.get_value("ip_address")
    port = dpg.get_value("port")
    try:
        dpg.set_value("status", f"Connecting to {ip}:{port}")
        dpg.configure_item("status_window", show=True)
        data_gen.set_server(ip, port)
        data, addr = data_gen.sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket
        returned_data = data_gen.get_data(data)
        dpg.set_value("status", "Connected")
        # dpg.configure_item("status_window", show=False)
        dpg.set_value("run_status", "Not Running")
        ping = round(ping3.ping(ip, unit="ms"), 1)
        ping = f"{ping}.ms"
        dpg.set_value("ping", ping)
        dpg.set_value("run_status", "Not Running")
        connection_status = 1
    except Exception as e:
        # print(e)
        connection_status = 0
        dpg.set_value("status", f"Error:\n{e}")
        dpg.configure_item("status_window", show=True)

def save_init_file():
    init_file = str(Path(f"{home_path}/{initfile}"))
    dpg.save_init_file(init_file)
    dpg.configure_item("save_window", show=False)
    dpg.set_value("save_status", f"Saved:\n{init_file}")
    dpg.configure_item("save_window", show=True)

def graph():
    if connection_status != 0:
        global rpm_axis
        global power_axis
        global torque_axis
        global boost_axis
        rpm_axis = []
        power_axis = []
        torque_axis = []
        boost_axis = []
        dpg.set_value("run_status", "Running")
        gear_setting = int(dpg.get_value("gearbox"))
        dpg.set_value("gear_setting", str(gear_setting))
        try:
            data, addr = data_gen.sock.recvfrom(1500)
            returned_data = data_gen.get_data(data)
            global carperf
            carperf = returned_data["CarPerformanceIndex"]
            while True:
                data, addr = data_gen.sock.recvfrom(1500)
                returned_data = data_gen.get_data(data)
                gear = returned_data["Gear"]
                rpm = round(returned_data["CurrentEngineRpm"])
                power = round((returned_data["Power"] * 1.34102) / 1000)
                torque = round(returned_data["Torque"], 1)
                boost = round((returned_data["Boost"] / 14.504), 2)
                if gear_setting == gear:
                    break
                else:
                    if power > 0:
                        if power_axis:
                            power_high = power_axis[-1]
                            if power:
                                # if power:
                                torque_high = torque_axis[-1]
                                if torque:
                                    # if torque:
                                    rpm_high = rpm_axis[-1]
                                    # if rpm > int(rpm_high):
                                    if rpm > int(rpm_high):
                                        rpm_axis.append(rpm)
                                        power_axis.append(power)
                                        torque_axis.append(torque)
                                        boost_axis.append(boost * 10)
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
                            boost_axis.append(boost * 10)
                    else:
                        continue
            dpg.set_value("run_status", "Peak ploting")
            make_graph(rpm_axis, power_axis, torque_axis, boost_axis)
        except Exception as e:
            dpg.set_value("error", e)
            dpg.configure_item("error_window", show=True)
    else:
        dpg.set_value("error", "Not connected")
        dpg.configure_item("error_window", show=True)

def open_values(sender, app_data, user_data):
    rpm_axis = []
    power_axis = []
    torque_axis = []
    boost_axis = []
    del rpm_axis[:]
    del power_axis[:]
    del torque_axis[:]
    del boost_axis[:]
    path = app_data.get("file_path_name")
    file_name = app_data.get("file_name")
    dpg.set_value("run_status", f"Opening\n{file_name}")
    with open(path) as json_file:
        data = json.load(json_file)
        rpm_axis = data["rpm"]
        power_axis = data["power"]
        torque_axis = data["torque"]
        boost_axis = data["boost"]
    dpg.set_value("run_status", "Peak ploting")
    make_graph(rpm_axis, power_axis, torque_axis, boost_axis)

def save_values():
    if connection_status != 0:
        try:
            data = {}
            data["rpm"] = rpm_axis
            data["power"] = power_axis
            data["torque"] = torque_axis
            data["boost"] = boost_axis
            print(data)
            now = datetime.now()
            now = now.strftime("%d%m%Y_%H%M%S")
            filename = f"{now}-{carperf}.json"
            dpg.configure_item("save_window", show=True)
            dpg.set_value("save_status", f"Saving {filename}")
            with open(Path(f"{home_path}/{filename}"), "w") as file:
                json.dump(data, file, indent=4)
            dpg.configure_item("save_window", show=False)
            dpg.set_value("save_status", f"Saved:\n{home_path}/{filename}")
            dpg.configure_item("save_window", show=True)
        except Exception as e:
            dpg.set_value("error", e)
            dpg.configure_item("error_window", show=True)
    else:
        dpg.set_value("error", "Not connected")
        dpg.configure_item("error_window", show=True)

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
    # print(peak_rpm)
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

def get_telemetry():
    global connection_status
    if connection_status == 1:
        try:
            data, addr = data_gen.sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket
            returned_data = data_gen.get_data(data)
            gear = returned_data["Gear"]
            rpm = round(returned_data["CurrentEngineRpm"])
            speed = int(round(returned_data["Speed"] * 3.6, 0))
            power = round((returned_data["Power"] * 1.34102) / 1000)
            torque = round(returned_data["Torque"], 1)
            boost = round(returned_data["Boost"] / 14.504, 2)
            dpg.set_value("gear", gear)
            dpg.set_value("speed", speed)
            dpg.set_value("rpm", rpm)
            dpg.set_value("boost", boost)
            if power > 0:
                dpg.set_value("power", power)
                dpg.set_value("torque", torque)
            else:
                dpg.set_value("power", 0)
                dpg.set_value("torque", 0)
            # print(f"RPM = {rpm}, Power = {power}, Torque = {torque}, Boost = {boost}")
        except Exception as e:
            dpg.set_value("error", e)
            dpg.configure_item("error_window", show=True)
            connection_status = 0

with dpg.file_dialog(modal=True, show=False, callback=open_values, id="open_values_file_picker", width=500, height=400, default_path=home_path):
    dpg.add_file_extension(".json", color=(255, 0, 255, 255), custom_text="[JSON]")

with dpg.window(label="Main", autosize=True, pos=(10, 30)):
    dpg.add_input_text(label="IP", source="ip_address", width=125)
    dpg.add_input_text(label="PORT", source="port", width=125)
    dpg.add_button(label="Connect", callback=connect)
    dpg.add_separator()
    dpg.add_text(default_value="Connection status:")
    dpg.add_text(source="status")
    dpg.add_text(default_value="Ping:")
    dpg.add_text(source="ping")

with dpg.window(label="Car Telemetry", autosize=True, pos=(10, 175)):
    dpg.add_text(default_value="Gear")
    t1 = dpg.add_text(source="gear")
    dpg.bind_item_font(t1, telemetry_font)
    dpg.add_separator()
    dpg.add_text(default_value="RPMs")
    t2 = dpg.add_text(source="rpm")
    dpg.bind_item_font(t2, telemetry_font)
    dpg.add_separator()
    dpg.add_text(default_value="Speed")
    t3 = dpg.add_text(source="speed")
    dpg.bind_item_font(t3, telemetry_font)
    dpg.add_separator()
    dpg.add_text(default_value="Power")
    t4 = dpg.add_text(source="power")
    dpg.bind_item_font(t4, telemetry_font)
    dpg.add_separator()
    dpg.add_text(default_value="Torque")
    t5 = dpg.add_text(source="torque")
    dpg.bind_item_font(t5, telemetry_font)
    dpg.add_separator()
    dpg.add_text(default_value="Boost")
    t6 = dpg.add_text(source="boost")
    dpg.bind_item_font(t6, telemetry_font)

with dpg.window(label="Graph", autosize=True, pos=(125, 175)):
    dpg.add_slider_int(label="Gearbox", min_value=2, max_value=10, source="gearbox", width=62)
    dpg.add_button(label="Start", callback=graph)

with dpg.window(label="App error",autosize=True,modal=True,show=False,id="error_window",no_title_bar=True):
    dpg.add_text(default_value="Error:")
    dpg.add_text(source="error")
    dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("error_window", show=False))

with dpg.window(label="App Status", autosize=True):
    dpg.add_text(default_value="Status :")
    dpg.add_text(source="run_status")

with dpg.window(label="Status",autosize=True,modal=True,show=False,id="status_window",no_title_bar=True):
    dpg.add_text(source="status")
    dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("status_window", show=False))

with dpg.viewport_menu_bar():
    with dpg.menu(label="Logs"):
        dpg.add_menu_item(label="Open", callback=lambda: dpg.show_item("open_values_file_picker"))
        dpg.add_menu_item(label="Save", callback=save_values)
    with dpg.menu(label="Config"):
        dpg.add_menu_item(label="Save", callback=save_init_file)
    with dpg.menu(label="Debug"):
        dpg.add_menu_item(label="Metrics", callback=lambda: dpg.show_metrics())

with dpg.window(label="Save Status", autosize=True, modal=True, show=False, id="save_window", no_title_bar=True):
    dpg.add_text(source="save_status")
    dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("save_window", show=False))

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

print(home_path)
home_init_file = Path(f"{home_path}/{initfile}")
init_exist = os.path.exists(home_init_file)

if init_exist == False:
    print("Copying defaut init file to home folder")
    shutil.copyfile(data_gen.resource_path(default_initfile), home_init_file)
    init_file = home_init_file
    print("Init file copied")
else:
    print("Init file exist")
    init_file = home_init_file

dpg.configure_app(init_file=init_file)
dpg.create_viewport(title="ForzaTelemetryApp", width=700, height=750)
dpg.setup_dearpygui()
dpg.configure_app(docking=True, docking_space=True)
dpg.show_viewport()
while dpg.is_dearpygui_running():
    get_telemetry()
    dpg.render_dearpygui_frame()

dpg.destroy_context()

import struct
import socket
import sys
import os
from pathlib import Path

def set_server(ip, port):
    """
    It create a UDP client to connect to the game server.
    
    :param ip: The IP address of the server
    :param port: The port number that the server will listen on
    """
    UDP_IP = str(ip)  # This sets server ip to the RPi ip
    UDP_PORT = int(port)  # You can freely edit this
    # setting up an udp server
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    sock.bind((UDP_IP, UDP_PORT))


def resource_path(relative_path):
    """
    If the program is running from a PyInstaller .exe, it returns the path to the .exe. Otherwise, it
    returns the path to the script
    
    :param relative_path: The path to the file relative to the directory containing the executable
    :return: The path to the file.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# reading data and assigning names to ata types in data_types dict
# Reading the data_format.txt file and creating a dictionary with the data types.
data_types = {}
with open(resource_path("data_format.txt"), "r") as f:
    lines = f.read().split("\n")
    for line in lines:
        data_types[line.split()[1]] = line.split()[0]

# assigning sizes in bytes to each variable type
# A dictionary that maps the data type to the number of bytes that the data type takes up.
jumps = {
    "s32": 4,  # Signed 32bit int, 4 bytes of size
    "u32": 4,  # Unsigned 32bit int
    "f32": 4,  # Floating point 32b0it
    "u16": 2,  # Unsigned 16bit int
    "u8": 1,  # Unsigned 8bit int
    "s8": 1,  # Signed 8bit int
    "hzn": 12,  # Unknown, 12 bytes of.. something
}

return_dict = {}


def get_data(data):
    """
    It takes a byte string, decodes it and returns a dict with the decoded data
    
    :param data: the data to be decoded
    :return: A dict with the decoded data.
    """
    # additional var
    passed_data = data
    for i in data_types:
        d_type = data_types[i]  # checks data type (s32, u32 etc.)
        jump = jumps[d_type]  # gets size of data
        current = passed_data[:jump]  # gets data
        decoded = 0
        # complicated decoding for each type of data
        if d_type == "s32":
            decoded = int.from_bytes(current, byteorder="little", signed=True)
        elif d_type == "u32":
            decoded = int.from_bytes(current, byteorder="little", signed=False)
        elif d_type == "f32":
            decoded = struct.unpack("f", current)[0]
        elif d_type == "u16":
            decoded = struct.unpack("H", current)[0]
        elif d_type == "u8":
            decoded = struct.unpack("B", current)[0]
        elif d_type == "s8":
            decoded = struct.unpack("b", current)[0]
        # adds decoded data to the dict
        return_dict[i] = decoded
        # removes already read bytes from the variable
        passed_data = passed_data[jump:]
    # returns the dict
    return return_dict

import os
import time
import socket
import tkinter as tk
from tkinter import messagebox
from math import radians, degrees, pi
import numpy as np
from robodk.robolink import *
from robodk.robomath import *

# Load RoboDK project from relative path
relative_path = "src/roboDK/Police_hand_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)
RDK = Robolink()
RDK.AddFile(absolute_path)

# Robot setup
robot = RDK.Item("UR5e")
base = RDK.Item("UR5e Base")
tool = RDK.Item('Hand')
Init_target = RDK.Item("Init")
Stop_car_target = RDK.Item('Stop_car')
Move_people_1_target = RDK.Item('Move_people_1')
Move_people_2_target = RDK.Item('Move_people_2')
Stop_people_target = RDK.Item('Stop_people')
Move_car_1_target = RDK.Item('Move_car_1')
Move_car_2_target = RDK.Item('Move_car_2')
Move_car_3_target = RDK.Item('Move_car_3')

robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(60)

# Robot Constants
ROBOT_IP = '192.168.1.5'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.452
timec = 8
timej = 6
timel = 4

# URScript commands
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"
movel_init = f"movel(p[0.000000, -0.250115, 0.650000, 0.461594, -0.461594, 1.521061],{accel_mss},{speed_ms},{timel},0.000)"
movel_stop_car = f" movel(p[0.000000, -0.550440, 0.650000, 0.000000, 0.000000, 1.570796],{accel_mss},{speed_ms},{timel},0.000)"
movel_people_1 = f"movel(p[0.420932, -0.429770, 0.500000, 1.570796, 0.000000, 0.000000],{accel_mss},{speed_ms},{timel},0.000)"
movel_people_2 = f"movel(p[-0.348293, -0.479116, 0.500000, 1.570796, 0.000000, 0.000000],{accel_mss},{speed_ms},{timel},0.000)"
movel_stop_people = f"movel([-0.604099, -2.860926, 1.747075, 2.684648, -1.570796, -0.966698],{accel_mss},{speed_ms},{timel},0.000)"
movel_car_1 = f"movel(p[-0.153410, -0.521877, 0.660750, 0.199045, 0.163090, -1.365973],{accel_mss},{speed_ms},{timel},0.000)"
movec_car_2 = f"movec(p[-0.131592, -0.353295, 0.748730, -0.062968, -0.062970, -1.569875],p[-0.131593, -0.015090, 0.712308, -0.625258, -0.625264, -1.478832],{accel_mss},{speed_ms},{blend_r},1)"

# Check robot connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
# Send URScript command
def send_ur_script(command):
    robot_socket.send((command + "\n").encode())

# Wait for robot response
def receive_response(t):
    try:
        print("Waiting time:", t)
        time.sleep(t)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        exit(1)

# Movements
def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    robot.MoveL(Stop_car_target, True)
    print("Stop_car_target REACHED")
    if robot_is_connected:
        print("Init REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_init)
        receive_response(timel)
        send_ur_script(movel_stop_car)
        receive_response(timel)
    else:
        print("UR5e not connected. Simulation only.")

def Priority_people():
    print("Priority for people")
    robot.setSpeed(60)
    robot.MoveL(Move_people_1_target, True)
    robot.setSpeed(100)
    robot.MoveL(Move_people_2_target, True)
    robot.MoveL(Move_people_1_target, True)
    robot.MoveL(Move_people_2_target, True)
    print("Priority_people FINISHED")
    if robot_is_connected:
        print("Priority_people REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_people_1)
        receive_response(timel)
        send_ur_script(movel_people_2)
        receive_response(timel)
        send_ur_script(movel_people_1)
        receive_response(timel)
        send_ur_script(movel_people_2)
        receive_response(timel)

def Priority_cars():
    print("Priority for cars")
    robot.setSpeed(60)
    robot.MoveL(Stop_people_target, True)
    robot.setSpeed(100)
    robot.MoveL(Move_car_1_target, True)
    robot.MoveC(Move_car_2_target, Move_car_3_target, True)
    robot.MoveL(Move_car_1_target, True)
    robot.MoveC(Move_car_2_target, Move_car_3_target, True)
    print("Priority_cars FINISHED")
    if robot_is_connected:
        print("Priority_cars REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_stop_people)
        receive_response(timel)
        send_ur_script(movel_car_1)
        receive_response(timel)
        send_ur_script(movec_car_2)
        receive_response(timec)
        send_ur_script(movel_car_1)
        receive_response(timel)
        send_ur_script(movec_car_2)
        receive_response(timec)

# Confirmation dialog to close RoboDK
def confirm_close():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion(
        "Close RoboDK",
        "Do you want to save changes before closing RoboDK?",
        icon='question'
    )
    if response == 'yes':
        RDK.Save()
        RDK.CloseRoboDK()
        print("RoboDK saved and closed.")
    else:
        RDK.CloseRoboDK()
        print("RoboDK closed without saving.")

# Main function
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)
    Init()
    Priority_people()
    Priority_cars()
    if robot_is_connected:
        robot_socket.close()

# Run and close
if __name__ == "__main__":
    main()
    #confirm_close()

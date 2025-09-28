import socket
import time
from robodk.robolink import *
from robodk.robomath import *

# ========================
# Config
# ========================
ROBOT_IP = '192.168.1.5'
ROBOT_PORT = 30002

# Parámetros globales (como en tu URScript)
speed_ms      = 0.250
speed_rads    = 0.750
accel_mss     = 1.200
accel_radss   = 1.200
blend_radius  = 0.000

# ========================
# Conexión robot por socket
# ========================
robot_socket = None

def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1.0)
        robot_socket.connect((ip, port))
        return True
    except Exception:
        return False

def send_ur(command):
    """Envía una línea URScript (añade salto de línea)."""
    robot_socket.send((command + "\n").encode('utf-8'))

def wait_s(t):
    """Espera ‘t’ segundos (crudo pero práctico para UR en 30002)."""
    time.sleep(t)

# ========================
# Opcional: RoboDK (simulación)
# ========================
RDK = Robolink()
robot = RDK.Item("UR5e")
# Si tienes base y herramienta con esos nombres en tu estación:
base = RDK.Item("UR5e Base")
tool = RDK.Item("Hand")
if base.Valid():
    robot.setPoseFrame(base)
if tool.Valid():
    robot.setPoseTool(tool)

# ========================
# Bloques URScript como strings
# ========================

def urs_set_tcp():
    return "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"

def urs_Init():
    # movej con articular (corrección del movel([...]))
    return f"movej([-1.403391, -3.022038, 0.702024, 3.890810, -1.570796, 1.403391], {accel_radss:.5f}, {speed_rads:.5f}, 0, {blend_radius:.4f})"

def urs_Priority_people():
    lines = [
        f"movel(p[0.420932, -0.429770, 0.500000, 1.570796, 0.000000, 0.000000], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
        f"movel(p[-0.348293, -0.479116, 0.500000, 1.570796, 0.000000, 0.000000], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
        f"movel(p[0.420932, -0.429770, 0.500000, 1.570796, 0.000000, 0.000000], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
        f"movel(p[-0.348293, -0.479116, 0.500000, 1.570796, 0.000000, 0.000000], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
    ]
    return "\n".join(lines)

def urs_Priority_cars():
    # Primer movimiento: articular (eran 6 números tipo joint)
    lines = [
        f"movej([1.780096, 4.905597, 0.927049, 2.021336, -1.570796, -3.350893], {accel_radss:.5f}, {speed_rads:.5f}, 0, {blend_radius:.4f})",
        f"movel(p[-0.131592, -0.773596, 0.543016, 0.515761, 0.515761, -1.508563], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
        # movec via, to:
        f"movec(p[-0.131592, -0.353295, 0.748730, -0.062968, -0.062970, -1.569875], p[-0.131593, -0.015090, 0.712308, -0.625258, -0.625264, -1.478832], {accel_mss:.5f}, {speed_ms:.5f}, {blend_radius:.4f})",
        f"movel(p[-0.131592, -0.773596, 0.543016, 0.515761, 0.515761, -1.508563], {accel_mss:.5f}, {speed_ms:.5f}, 0, {blend_radius:.3f})",
        f"movec(p[-0.131592, -0.353295, 0.748730, -0.062968, -0.062970, -1.569875], p[-0.131593, -0.015090, 0.712308, -0.625258, -0.625264, -1.478832], {accel_mss:.5f}, {speed_ms:.5f}, {blend_radius:.4f})",
    ]
    return "\n".join(lines)

# ========================
# Funciones con tu MISMA estructura
# (simulación RoboDK + envío URScript si hay conexión)
# ========================

def Init():
    print("Init")
    # Simulación (si tienes un Target equivalente, úsalo; si no, omite MoveL/MoveJ):
    # robot.MoveJ( ... )  # opcional

    if robot_is_connected:
        send_ur(urs_set_tcp()); wait_s(0.05)
        send_ur(urs_Init());    wait_s(2.0)  # ajusta si necesitas más tiempo real
    else:
        print("UR5e no conectado. Solo simulación.")

def Priority_people():
    print("Priority_people")
    # Simulación (opcional): mueve a poses/targets equivalentes
    # robot.MoveL(...)

    if robot_is_connected:
        send_ur(urs_set_tcp()); wait_s(0.05)
        for line in urs_Priority_people().splitlines():
            send_ur(line)
        wait_s(4.0)  # tiempo aproximado
    else:
        print("UR5e no conectado. Solo simulación.")

def Priority_cars():
    print("Priority_cars")
    # Simulación (opcional)
    # robot.MoveJ(...); robot.MoveL(...); robot.MoveC(...)

    if robot_is_connected:
        send_ur(urs_set_tcp()); wait_s(0.05)
        for line in urs_Priority_cars().splitlines():
            send_ur(line)
        wait_s(6.0)
    else:
        print("UR5e no conectado. Solo simulación.")

# ========================
# Main
# ========================
def main():
    global robot_is_connected
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)

    Init()
    Priority_people()
    Priority_cars()

    if robot_is_connected:
        robot_socket.close()

if __name__ == "__main__":
    main()

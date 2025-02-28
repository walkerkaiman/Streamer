import time, os, socket, json
from pynput import keyboard

# Loads sACN IPs from config file
def load_config(file):
    with open(file, "r") as f:
        return json.load(f)

def on_key_press(key):
    global current_state, IP, PORT

    if hasattr(key, "char"): 
        if key.char == "0" and current_state == "show":
            current_state = "loop"

            udp_socket.sendto(current_state.encode('utf-8'), (IP, PORT))
            print("Show manually ended early. Returning to loop mode.")
        elif key.char == "1":
            if current_state == "show":
                current_state = "loop"
            else:
                current_state = "show"

            udp_socket.sendto(current_state.encode('utf-8'), (IP, PORT))
            print("State switched to: ", current_state, " mode")
        elif key.char == "6":
            if current_state == "loop":
                udp_socket.sendto("shutdown".encode('utf-8'), (IP, PORT))
                print("Venue Shutdown Mode.")
                print("Press Ctrl+c to close State Controller...")
            else:
                print("Currently in show mode. Switch to loop mode first (press 1) and try again...")

def on_key_release(key):
    pass

# Load from configuration file
CONFIG = load_config("config.json")
IP = CONFIG['Broadcast UDP IP']
PORT = CONFIG['UDP Port']

# Initialize state and UDP socket
current_state = "loop"
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.start()

print("State Controller Started... (Press 1 to toggle Loop/Show mode, 0 to end show early, 6 to begin venue shutdown)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt: 
    keyboard_listener.stop()
    keyboard_listener.join()
finally:
    print("State Controller is closed.")

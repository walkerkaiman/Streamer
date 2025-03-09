import time, os, socket, json, threading, sys
from pynput import keyboard
from shows.showPlayer import Show

# Loads sACN IPs from config file
def load_config(file):
    with open(file, "r") as f:
        return json.load(f)

def show_complete_callback():
    global current_state

    print("\nShow Finished!")

    current_state = "loop"
    udp_socket.sendto(current_state.encode('utf-8'), (IP, PORT))
    print("Entering Loop Mode...\n")


def on_key_press(key):
    global current_state, IP, PORT, show_thread

    if hasattr(key, "char"):
        if key.char == "0" and current_state == "show":
            show.stop_show()
            if show_thread and show_thread.is_alive():
                show_thread.join(timeout=5)  # Allow thread to exit
            
            current_state = "loop"
            print("\nState Switched To -->", current_state, "mode")
            udp_socket.sendto(current_state.encode('utf-8'), (IP, PORT))
        elif key.char == "1":
            if current_state == "loop":
                current_state = "show"
                udp_socket.sendto(current_state.encode('utf-8'), (IP, PORT))
                print("\nState Switched To -->", current_state, "mode")
                
                show_end_event = threading.Event()
                show_thread = threading.Thread(target=show.play_show(show_complete_callback), daemon=True)
                show_thread.start()
                show_thread.join()
                
        elif key.char == "6":
            if current_state == "loop":
                try:
                    udp_socket.sendto("shutdown".encode('utf-8'), (IP, PORT))
                except OSError as e:
                    print(f"Network error: {e}")
                print("\nVenue Shutdown Mode.")
            else:
                print("Switch to loop mode first before shutting down.")

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

show = Show()
show_thread = None  # Thread reference

print("State Controller Started...\n(Press 1 to toggle Loop/Show mode, 0 to end show early, 6 to begin venue shutdown)")

try:
    while True:
        time.sleep(1)  # Prevent high CPU usage
except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Shutting down...")
    keyboard_listener.stop()
    keyboard_listener.join()
    if show_thread and show_thread.is_alive():
        show.stop_show()
        try:
            show.sender.stop()  # Gracefully stop the sACN sender
        except Exception as e:
            print("Error stopping sACN sender:", e)
        show_thread.join(timeout=5)
    udp_socket.close()
    print("State Controller is closed.")
    os._exit(0)
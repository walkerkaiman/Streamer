import csv
import json
import time
import sacn
import os
import sys

# Load configuration file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SmallShow.csv")
FRAME_RATE = 30  # Default FPS
is_playing = False

# Loads configuration sACN hardware
def load_config(file):
    with open(file, "r") as f:
        config = json.load(f)
    return [node for node in config if node["Included in show?"]]

# Loads the show lighting data
def read_csv(file):
    frames = []

    with open(file, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            frames.append([int(value) for value in row])

    return frames

# Sends data via sACN according to the show file
def send_dmx(frames, config):
    global is_playing
    is_playing = True
    sender = sacn.sACNsender()
    sender.start()
    
    universe_map = {}
    max_frames = len(frames) // sum(len(node["Universes"]) for node in config)
    
    for node in config:
        for universe in node["Universes"]:
            sender.activate_output(universe)
            sender[universe].multicast = True
            universe_map[universe] = node["Channels"][node["Universes"].index(universe)]
    
    for frame_idx in range(max_frames):
        start_index = frame_idx * len(universe_map)
        
        for i, (universe, channels) in enumerate(universe_map.items()):
            frame_data = frames[start_index + i] if start_index + i < len(frames) else [0] * channels
            frame_data = frame_data[:channels] + [0] * (channels - len(frame_data))
            sender[universe].dmx_data = frame_data
        
        progress = (frame_idx + 1) / max_frames * 100
        sys.stdout.write(f"\rProgress: {progress:.2f}%")
        sys.stdout.flush()
        
        time.sleep(1 / FRAME_RATE)
    
    print("\nShow Complete!")
    sender.stop()
    is_playing = False

if __name__ == "__main__":
    config = load_config(CONFIG_FILE)
    frames = read_csv(CSV_FILE)
    send_dmx(frames, config)


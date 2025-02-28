import csv, json, time, os, sys
import sacn

# Loads config file
def load_config(file):
    with open(file, "r") as f:
        return json.load(f)

# Loads the show lighting data
def load_show_from_csv(file):

    with open(file, "r") as f:
        data = list(csv.reader(f))
        data_int = []

        for i in range(len(data)):
            new_row = []

            for value in data[i]:
                try:
                    new_row.append(int(value))
                except ValueError:
                    print("Cannot convert value: ", value)

            data_int.append(new_row)
        return data_int

def get_universe_map(destinations):
    uni_map = {}
    
    for node in destinations:
        for uni in node['Universes']:
             uni_map[uni] = node['IP Address']
    return uni_map
    
# Sends data via sACN according to the show file
def play_show():
    global SHOW_DATA, UNIVERSE_MAP
    
    data_length = len(SHOW_DATA)
    current_row = 0

    while current_row < data_length-1:
        for uni in UNIVERSE_MAP:
            # Set values in each universe by row in CSV file per animation frame
            sender[uni].dmx_data = SHOW_DATA[current_row] 
            current_row += 1
        
        progress = current_row / data_length * 100
        sys.stdout.write(f"\rProgress: {progress:.2f}%")
        sys.stdout.flush()

        time.sleep(1/sender.fps)
    sender.stop()

# Load configuration file
CONFIG_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
CONFIG_FILE = load_config(CONFIG_FILEPATH)

SHOW_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE['Show Filename'])
SHOW_DATA = load_show_from_csv(SHOW_FILEPATH)
SHOW_NODES = CONFIG_FILE['Nodes']

UNIVERSE_MAP = get_universe_map(SHOW_NODES)

# Initialize sACN / DMX sender
sender = sacn.sACNsender()
sender.start()
sender.fps = CONFIG_FILE['Show Frame Rate']

for uni in UNIVERSE_MAP:
    sender.activate_output(uni)
    sender[uni].destination = UNIVERSE_MAP[uni]

if __name__ == "__main__":
    play_show()
    print("\nShow Finished!")


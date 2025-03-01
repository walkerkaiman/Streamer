import csv, json, time, os, sys
import sacn

class Show:

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

        self.config = self.load_config(config_path)
        self.show_data = self.load_show_from_csv(self.config['Show Filename'])
        self.universe_map = self.get_universe_map(self.config['Nodes'])
        self.sender = self.setup_sacn()
        self.isPlaying = True

    def load_config(self, file):
        with open(file, "r") as f:
            return json.load(f)

    def load_show_from_csv(self, filename):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        print("Loading Show Into Memory...")

        with open(filepath, "r") as f:
            data = list(csv.reader(f))
            return [[int(value) for value in row if value.isdigit()] for row in data]

    def get_universe_map(self, destinations):
        uni_map = {uni: node['IP Address'] for node in destinations for uni in node['Universes']}
        return uni_map

    def setup_sacn(self):
        sender = sacn.sACNsender()
        sender.start()
        sender.fps = self.config['Show Frame Rate']

        for uni in self.universe_map:
            sender.activate_output(uni)
            sender[uni].destination = self.universe_map[uni]

        return sender

    def play_show(self):
        data_length = len(self.show_data)
        current_row = 0
        self.isPlaying = True

        print("Beginning Show...")

        while current_row < data_length:
            if self.isPlaying == False:
                break

            for uni in self.universe_map:
                self.sender[uni].dmx_data = self.show_data[current_row]
                current_row += 1
            
            progress = (current_row / data_length) * 100
            sys.stdout.write(f"\rProgress: {progress:.2f}%")
            sys.stdout.flush()
                        
            time.sleep(1 / self.sender.fps)

        self.sender.stop()
        print("\nShow Finished!")

    def stop_show(self):
        self.isPlaying = False;
        self.sender.stop()
        print("Stopping Show Early...")

if __name__ == "__main__":
    show = Show()
    show.play_show()

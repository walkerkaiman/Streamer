import socket
import time
import threading

class SMPTETimecodeGenerator:
    def __init__(self, frame_rate=30, ip="192.168.1.255", port=5005):
        self.frame_rate = frame_rate
        self.UDP_IP = ip  # Broadcast IP address
        self.UDP_PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcasting
        self.running = False
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.frames = 0
        self.thread = None

    def format_timecode(self):
        """Format timecode as HH:MM:SS:FF"""
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}:{self.frames:02}"

    def send_timecode(self):
        """Send the current timecode over UDP broadcast."""
        while self.running:
            timecode = self.format_timecode()
            self.sock.sendto(timecode.encode(), (self.UDP_IP, self.UDP_PORT))  # Send to broadcast address
            self.increment_timecode()
            print(timecode)  # Optionally print the timecode for debugging
            time.sleep(1 / self.frame_rate)

    def increment_timecode(self):
        """Increment the timecode by one frame, handling overflow of frames, seconds, etc."""
        self.frames += 1
        if self.frames >= self.frame_rate:
            self.frames = 0
            self.seconds += 1
        if self.seconds >= 60:
            self.seconds = 0
            self.minutes += 1
        if self.minutes >= 60:
            self.minutes = 0
            self.hours += 1

    def start(self):
        """Start the timecode generation in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.send_timecode)
            self.thread.start()

    def stop(self):
        """Stop the timecode generation."""
        if self.running:
            self.running = False
            self.thread.join()

    def set_parameters(self, frame_rate=None, start_time=None):
        """Update frame rate and/or start time."""
        if frame_rate is not None:
            self.frame_rate = frame_rate
        if start_time is not None:
            self.hours, self.minutes, self.seconds, self.frames = start_time

# Parent Program Integration
if __name__ == "__main__":
    generator = SMPTETimecodeGenerator()

    # Parent can set parameters before starting
    generator.set_parameters(frame_rate=30, start_time=(1, 0, 0, 0))  # Start at 01:00:00:00 with 30fps

    # Parent starts the timecode generator
    generator.start()

    # Simulate the parent program controlling the generator
    try:
        while True:
            command = input("Enter command (start, stop, set, quit): ").strip().lower()
            if command == "start":
                generator.start()
            elif command == "stop":
                generator.stop()
            elif command.startswith("set"):
                # Example: "set 25 2 0 0 0" -> Set frame rate to 25 fps and start time to 02:00:00:00
                _, frame_rate, hours, minutes, seconds, frames = command.split()
                generator.set_parameters(
                    frame_rate=int(frame_rate),
                    start_time=(int(hours), int(minutes), int(seconds), int(frames))
                )
            elif command == "quit":
                generator.stop()
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        generator.stop()


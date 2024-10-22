import json
import re
from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
from PyQt6.QtWidgets import QApplication

class DeviceUpdater(QThread):
    finished = pyqtSignal(dict)  # Signal to emit the found devices

    def __init__(self, isAudio=False, isVideo=True):
        super(DeviceUpdater, self).__init__()
        self.isAudio = isAudio
        self.isVideo = not isAudio

    def run(self):
        command = "ffmpeg -list_devices true -f dshow -i dummy"
        try:
            # Execute the command and capture the output and errors
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            devices = self.parse_devices(result.stderr)
            self.finished.emit(devices)  # Emit the found devices
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            self.finished.emit({})

    def filterResults(self, devices, isAudio=False, isVideo=True):
        filtered = {}
        for key, value in devices.items():
            if isAudio and value.get('audio', False):
                filtered[key] = value
            elif isVideo and value.get('video', False):
                filtered[key] = value
        return filtered

    def parse_devices(self, output):
        devices = {}
        lines = output.split('\n')
        device_id = 0  # Initialize a device ID counter
        device_info = {}
        for line in lines:
            if "Alternative name" in line:
                alt_name_match = re.search(r'\"(.+?)\"$', line)
                if alt_name_match:
                    alt_name = alt_name_match.group(1)
                    device_info['alternative_name'] = alt_name
                devices[device_id] = device_info
                device_id += 1
                device_info = {}
            elif '"' in line:
                name_match = re.search(r'\"(.+?)\"', line)
                if name_match:
                    device_info['name'] = name_match.group(1)
                    if self.isAudio:
                        device_info['audio'] = True
                    else:
                        device_info['video'] = "video" in line
        return devices

# Test
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    updater = DeviceUpdater()
    updater.finished.connect(lambda devices: print(json.dumps(devices, indent=4)))
    updater.start()
    sys.exit(app.exec())

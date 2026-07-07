from flask import Flask, request
import serial
import time

app = Flask(__name__)

# --- YOUR SPECIFIC HARDWARE SETUP ---
# Locked to the exact physical USB port to prevent mixing with the YDLidar or Drive Base
SERIAL_PORT = '/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2.1:1.0-port0' 
BAUD_RATE = 115200

# Attempt to connect to the ESP32
try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Give ESP32 time to reboot after connecting
    print(f"Connected to Arm ESP32 successfully on {SERIAL_PORT}!")
except Exception as e:
    print(f"Error connecting to ESP32: {e}")
    print("Ensure the ESP32 is plugged into the correct port and you are using sudo.")
    esp32 = None

# --- WEB INTERFACE (HTML + JS) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pi 5 Robot Arm Controller</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; background-color: #e3f2fd; padding: 20px; margin: 0; }
    h2 { color: #333; }
    .slider-container { background: white; padding: 15px; margin: 10px auto; border-radius: 10px; width: 90%; max-width: 400px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    input[type=range] { width: 100%; }
    .label { font-weight: bold; margin-bottom: 10px; display: block; color: #444; }
    .status { margin-bottom: 20px; font-weight: bold; color: #00796b; }
  </style>
</head>
<body>
  <h2>Pi-Powered Robot Arm</h2>
  <div class="status">Connected via USB Serial</div>

  <div class="slider-container">
    <span class="label">Base (Ch 1): <span id="val1">90</span>&deg;</span>
    <input type="range" min="0" max="180" value="90" oninput="updateServo(1, this.value)">
  </div>

  <div class="slider-container">
    <span class="label">Shoulder (Ch 12): <span id="val12">90</span>&deg;</span>
    <input type="range" min="0" max="180" value="90" oninput="updateServo(12, this.value)">
  </div>

  <div class="slider-container">
    <span class="label">Elbow (Ch 4): <span id="val4">90</span>&deg;</span>
    <input type="range" min="0" max="180" value="90" oninput="updateServo(4, this.value)">
  </div>

  <div class="slider-container">
    <!-- HARDWARE SAFETY LIMIT: Max is set to 143 to prevent wrist motor buzzing -->
    <span class="label">Wrist Pitch (Ch 6): <span id="val6">90</span>&deg;</span>
    <input type="range" min="0" max="143" value="90" oninput="updateServo(6, this.value)">
  </div>

  <div class="slider-container">
    <span class="label">Gripper (Ch 9): <span id="val9">90</span>&deg;</span>
    <input type="range" min="0" max="180" value="90" oninput="updateServo(9, this.value)">
  </div>

  <script>
    function updateServo(channel, angle) {
      document.getElementById('val' + channel).innerText = angle;
      // Send the movement command in the background
      fetch(`/set?ch=${channel}&angle=${angle}`);
    }
  </script>
</body>
</html>
"""

# --- SERVER ROUTES ---
@app.route('/')
def index():
    return HTML_PAGE

@app.route('/set')
def set_servo():
    channel = request.args.get('ch')
    angle = request.args.get('angle')
    
    if channel and angle and esp32:
        # Format the command exactly as the ESP32 expects: "channel,angle\n"
        command = f"{channel},{angle}\n"
        esp32.write(command.encode('utf-8'))
        return "OK", 200
    return "Error", 400

if __name__ == '__main__':
    # Run the server accessible from anywhere on your home network
    app.run(host='0.0.0.0', port=5000)

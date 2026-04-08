import time
from witmotion import IMU

port = 'COM3' # your Bluetooth port

# Try to connect safely
for attempt in range(3):
    try:
        imu = IMU(port)
        print(f"Connected to IMU on {port}")
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(2)
else:
    raise RuntimeError(f"Could not connect to IMU on Bluetooth COM port.")

imu.close()
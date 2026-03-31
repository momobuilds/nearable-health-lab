import time
import datetime
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from cms50d import CMS50D


monitor = CMS50D(port="HID")
monitor.connect()
monitor.start_live_acquisition()

plt.ion()
fig, ax = plt.subplots(figsize=(10, 4))

window_seconds = 10
target_fps = 30
frame_interval = 1.0 / target_fps

xdata = deque()
ydata = deque()

line, = ax.plot_date([], [], fmt='-m', label='Pulse Waveform')
text_hr = ax.text(0.02, 0.95, 'HR: -- bpm', transform=ax.transAxes, color='red', fontsize=12)
text_spo2 = ax.text(0.02, 0.90, 'SpO2: --%', transform=ax.transAxes, color='blue', fontsize=12)

ax.set_ylim(0, 128)
ax.set_ylabel("Waveform")
ax.set_xlabel("Time")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.title("CMS50D Live Data")
plt.legend()

last_hr = None
last_spo2 = None
last_mode = "--"
last_draw_time = 0.0

try:
    while True:
        got_data = False

        # Drain the queue quickly
        while True:
            data = monitor.get_latest_data()
            if data is None:
                break

            got_data = True
            now = data["timestamp"]
            waveform = data["waveform"]

            if waveform is not None:
                xdata.append(now)
                ydata.append(waveform)

            if data["pulse_rate"] is not None:
                last_hr = data["pulse_rate"]

            if data["spO2"] is not None:
                last_spo2 = data["spO2"]

            last_mode = data.get("mode", "--")

        # Keep only the last N seconds
        if xdata:
            cutoff = xdata[-1] - datetime.timedelta(seconds=window_seconds)
            while xdata and xdata[0] < cutoff:
                xdata.popleft()
                ydata.popleft()

        current_time = time.perf_counter()
        if current_time - last_draw_time >= frame_interval and xdata:
            line.set_data(list(xdata), list(ydata))
            ax.set_xlim(xdata[0], xdata[-1])

            text_hr.set_text(f"HR: {last_hr if last_hr is not None else '--'} bpm")
            text_spo2.set_text(f"SpO2: {last_spo2 if last_spo2 is not None else '--'}%")

            fig.canvas.draw_idle()
            fig.canvas.flush_events()

            last_draw_time = current_time

        if not got_data:
            plt.pause(0.005)
        else:
            plt.pause(0.001)

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    monitor.stop_live_acquisition()
    monitor.disconnect()
    plt.ioff()
    plt.show()
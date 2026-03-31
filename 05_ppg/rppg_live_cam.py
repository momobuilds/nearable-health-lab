import cv2
import numpy as np
import matplotlib.pyplot as plt
import time


# =========================
# Matplotlib live plot
# =========================
plt.ion()
fig, ax = plt.subplots(figsize=(10, 4))

xdata = []
ydata = []
ydata_filtered = []

line_raw, = ax.plot([], [], label="Raw green signal", alpha=0.5)
line_filt, = ax.plot([], [], label="Filtered signal", linewidth=2)

text_hr = ax.text(0.02, 0.95, "", transform=ax.transAxes, color="red", fontsize=12, va="top")
text_status = ax.text(0.02, 0.78, "", transform=ax.transAxes, color="blue", fontsize=11, va="top")

ax.set_ylabel("Signal")
ax.set_xlabel("Time (s)")
plt.title("rPPG")
plt.legend()


# =========================
# Acquisition parameters
# =========================
last_estimation_time = 0.0
estimation_interval = 1.0  # seconds

hr_fft = None
hr_peak = None

# Use a slightly higher target FPS if the camera can sustain it
cap = cv2.VideoCapture(0)
target_fps = 20.0
frame_interval = 1.0 / target_fps


# Plot and HR windows
plot_window_seconds = 20.0
estimation_window_seconds = 10.0


# =========================
# Main loop
# =========================
while True:
    loop_start = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    # TODO: face detection
    face_found = False
    faces = []

    for (x, y, w, h) in faces:
        face_found = True

        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # TODO: define forehead ROI
        x_roi = 0
        w_roi = 0
        y_roi = 0
        h_roi = 0

        

        # Keep ROI inside frame bounds
        x_roi = max(0, x_roi)
        y_roi = max(0, y_roi)
        w_roi = max(1, min(w_roi, frame.shape[1] - x_roi))
        h_roi = max(1, min(h_roi, frame.shape[0] - y_roi))

        roi = frame[y_roi:y_roi + h_roi, x_roi:x_roi + w_roi, :]
        cv2.rectangle(frame, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (0, 0, 255), 2)

        if roi.size == 0:
            break

        # TODO: extract a signal from the ROI
        signal_value = None

        if signal_value is not None:
            xdata.append(loop_start)
            ydata.append(signal_value)

        # Keep only the last plot window
        cutoff = loop_start - plot_window_seconds
        xdata = [t for t in xdata if t >= cutoff]
        ydata = ydata[-len(xdata):]

        # Estimate HR once per interval
        if len(ydata) > 30 and (loop_start - last_estimation_time) >= estimation_interval:
            # Use only the last estimation window for HR estimation
            estimation_cutoff = loop_start - estimation_window_seconds
            estimation_x = [t for t in xdata if t >= estimation_cutoff]
            estimation_y = ydata[-len(estimation_x):]

            if len(estimation_y) > 30:
                dt = estimation_x[-1] - estimation_x[0]

                if dt > 0:
                    sampling_rate = len(estimation_x) / dt

                    # TODO: process the signal
                    normalized_signal = np.asarray(estimation_y, dtype=float)
                    filtered_signal = np.asarray(estimation_y, dtype=float)

                    # TODO: estimate heart rate
                    hr_fft = None
                    hr_peak = None

                    ydata_filtered = filtered_signal

                    # Update Matplotlib plot
                    plot_x = np.array(estimation_x) - estimation_x[0]
                    line_raw.set_data(plot_x, normalized_signal)
                    line_filt.set_data(plot_x, ydata_filtered)

                    ax.set_xlim(plot_x[0], plot_x[-1])

                    combined = np.concatenate([normalized_signal, ydata_filtered])
                    y_min = float(np.min(combined))
                    y_max = float(np.max(combined))

                    if y_min == y_max:
                        ax.set_ylim(y_min - 1.0, y_max + 1.0)
                    else:
                        margin = 0.15 * (y_max - y_min)
                        ax.set_ylim(y_min - margin, y_max + margin)

                    fft_text = f"{hr_fft:.1f}" if hr_fft is not None else "--"
                    peak_text = f"{hr_peak:.1f}" if hr_peak is not None else "--"

                    text_hr.set_text(
                        f"HR (FFT): {fft_text} bpm\n"
                        f"HR (Peak): {peak_text} bpm\n"
                    )

                    fig.canvas.draw()
                    fig.canvas.flush_events()

                    last_estimation_time = loop_start

        # Frame overlay
        fft_overlay = f"{hr_fft:.1f}" if hr_fft is not None else "--"
        peak_overlay = f"{hr_peak:.1f}" if hr_peak is not None else "--"

        cv2.putText(
            frame,
            f"HR (FFT): {fft_overlay} bpm",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"HR (Peak): {peak_overlay} bpm",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

        # Use only the first detected face
        break

    if not face_found:
        cv2.putText(
            frame,
            "No face detected",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("rPPG", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    elapsed = time.time() - loop_start
    time.sleep(max(0, frame_interval - elapsed))

cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()
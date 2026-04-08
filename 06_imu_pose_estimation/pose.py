# Install YOLO (Run this in your terminal)
# pip install -U ultralytics

from ultralytics import YOLO

# Load a pretrained YOLO11n-pose model
model = YOLO('yolo11n-pose.pt') 

# Run tracking on a video file
results = model.track(source="video.mp4", show=True, save=True)

for frame_idx, result in enumerate(results):
    if result.keypoints is None:
        continue
    
    # shape: (num_people, num_keypoints, 2)
    keypoints_xy = result.keypoints.xy
    keypoints_conf = result.keypoints.conf
    
    print(f"\nFrame {frame_idx}")
    print("Keypoints shape:", keypoints_xy.shape)

    for kp_idx, (x,y) in enumerate(keypoints_xy[0]):

        conf = keypoints_conf[0][kp_idx]
        print (f"KP {kp_idx}:x={x:.1f},y={y:.1f}, conf = {conf:.2f}")
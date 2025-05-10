# from camera import RaspberryCam
# from inference import FrameInference, PoseInference
# from GaitRobot import GaitRobot
# from utils import draw_landmarks_on_image
import numpy as np
import cv2
from gait_analysis import butter_lowpass_filter, get_left_joint_angles
import mediapipe as mp
import matplotlib.pyplot as plt
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pose_landmarks.points_on_landmarks import (
    pose_landmark_name_to_idx as landmark_index,
)
from pose_landmarks.points_on_landmarks import (
    pose_landmark_idx_to_name as landmark_name,
)
import pandas as pd

# VIDEO_SOURCE = "raspberry pi"
VIDEO_SOURCE = 0
# print(cv2.getBuildInformation())

max_frames_display = 100  # Rolling window
motor_pins = []

# CAP_MSMF for windows camera
raspi_cam = cv2.VideoCapture(VIDEO_SOURCE, cv2.CAP_MSMF)  # Live cam


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
frame_count = 0

fps = raspi_cam.get(cv2.CAP_PROP_FPS)

plt.ion()
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)


def setup_subplot(ax, title):
    ax.set_title(title)
    ax.set_ylim(30, 180)
    ax.grid(True)
    ax.legend(loc="upper right")


# Initialize lines
lines = {}
for ax, label in zip((ax1, ax2, ax3), ("Hip", "Knee", "Ankle")):
    (line_raw,) = ax.plot([], [], label=f"{label} Raw", color="blue")
    (line_filtered,) = ax.plot([], [], label=f"{label} Filtered", color="orange")
    setup_subplot(ax, f"{label} Angle Over Time")
    lines[label] = (line_raw, line_filtered)


ax3.set_xlabel("Frame")
frames = []
(
    hip_vals,
    knee_vals,
    ankle_vals,
) = (
    [],
    [],
    [],
)
heel_vals_x, heel_vals_y, heel_vals_z = [], [], []
frame_count = 0
landmark_history = {i: {"x": [], "y": [], "z": []} for i in range(33)}


with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    smooth_segmentation=False,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
) as pose:
    while raspi_cam.isOpened():
        success, frame = raspi_cam.read()
        if not success:
            print("Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(rgb_frame)
        # print(results.pose_landmarks)

        # if results.pose_landmarks:
        #     # save data to file
        #     if frame_count % 5 == 0:
        #         with open("./pose_landmarks/pose_landmarks.txt", "a") as f:
        #             d = {"data": {}, "frame_count": frame_count}
        #             for idx, landmark in enumerate(results.pose_landmarks.landmark):
        #                 name = landmark_name.get(idx, f"landmark_{idx}")
        #                 d["data"][name] = [
        #                     landmark.x,
        #                     landmark.y,
        #                     landmark.z,
        #                     landmark.visibility,
        #                 ]

        #             f.write(str(d) + "\n")

        if results.pose_world_landmarks:
            # save to file
            with open("./pose_landmarks/world_pose_landmarks.txt", "w") as f:
                d = {"data": {}, "frame_count": frame_count}
                for idx, landmark in enumerate(results.pose_world_landmarks.landmark):
                    name = landmark_name.get(idx, f"landmark_{idx}")
                    d["data"][name] = [
                        landmark.x,
                        landmark.y,
                        landmark.z,
                        landmark.visibility,
                    ]

                f.write(str(d) + "\n")

        if results.pose_world_landmarks:
            # left heel values
            heel_landmark = results.pose_world_landmarks.landmark[
                landmark_index["left_heel"]
            ]

            heel_vals_x.append(heel_landmark.x)
            heel_vals_y.append(heel_landmark.y)
            heel_vals_z.append(heel_landmark.z)

            hip, knee, ankle = get_left_joint_angles(
                results.pose_world_landmarks.landmark
            )

            hip_vals.append(hip)
            knee_vals.append(knee)
            ankle_vals.append(ankle)
            frames.append(frame_count)

            if len(frames) > max_frames_display:
                hip_vals = hip_vals[-max_frames_display:]
                knee_vals = knee_vals[-max_frames_display:]
                ankle_vals = ankle_vals[-max_frames_display:]
                heel_vals_x = heel_vals_x[-max_frames_display:]
                heel_vals_y = heel_vals_y[-max_frames_display:]
                heel_vals_z = heel_vals_z[-max_frames_display:]
                frames = frames[-max_frames_display:]

            hip_filt = (
                butter_lowpass_filter(hip_vals) if len(hip_vals) > 9 else hip_vals
            )
            knee_filt = (
                butter_lowpass_filter(knee_vals) if len(knee_vals) > 9 else knee_vals
            )
            ankle_filt = (
                butter_lowpass_filter(ankle_vals) if len(ankle_vals) > 9 else ankle_vals
            )

            # Update plot
            for label, vals, filt, ax in zip(
                ["Hip", "Knee", "Ankle"],
                [hip_vals, knee_vals, ankle_vals],
                [hip_filt, knee_filt, ankle_filt],
                [ax1, ax2, ax3],
            ):
                lines[label][0].set_data(frames, vals)  # raw
                lines[label][1].set_data(frames, filt)  # filtered
                ax.set_xlim(frames[0], frames[-1])

            # draw frame on screen
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=2
                ),
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(255, 0, 0), thickness=2, circle_radius=2
                ),
            )

        # Show the result
        cv2.imshow("MediaPipe Pose", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1

data = {
    "Frame": frames,
    "Hip Raw": hip_vals,
    "Hip Filtered": butter_lowpass_filter(hip_vals),
    "Knee Raw": knee_vals,
    "Knee Filtered": butter_lowpass_filter(knee_vals),
    "Ankle Raw": ankle_vals,
    "Ankle Filtered": butter_lowpass_filter(ankle_vals),
    "Left Heel Values": heel_vals,
}

df = pd.DataFrame(data)
df.to_csv("./gait_data/gait_filtered_data.csv", index=False)


raspi_cam.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()

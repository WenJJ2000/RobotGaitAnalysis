import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import butter, sosfilt, sosfilt_zi, find_peaks
from scipy.interpolate import interp1d
from picamera2 import Picamera2

# ---------- Global Variables -----------
BASE_DATA_PATH = "/home/jj/RobotGaitAnalysis/gait_2/gait_data"


# ---------- Utility Functions ----------
class TrueRealTimeFilter:
    def __init__(self, cutoff=3, fs=30, order=2):
        self.sos = butter(order, cutoff / (0.5 * fs), btype="low", output="sos")
        self.state = {}

    def apply(self, landmark_id, coord, new_val):
        key = (landmark_id, coord)
        if key not in self.state:
            self.state[key] = sosfilt_zi(self.sos) * new_val
        filtered_val, self.state[key] = sosfilt(self.sos, [new_val], zi=self.state[key])
        return filtered_val[0]


def filter_landmarks_rt(landmarks, filter_instance):
    return [
        (
            filter_instance.apply(i, "x", lm.x),
            filter_instance.apply(i, "y", lm.y),
            filter_instance.apply(i, "z", lm.z),
        )
        for i, lm in enumerate(landmarks)
    ]


def angle_between(a, b, c):
    ab = np.array(b) - np.array(a)
    bc = np.array(c) - np.array(b)
    cosine = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle


def calculate_joint_angles(lm):
    angles = {}
    angles["hip"] = angle_between(lm[11], lm[23], lm[25])  # Shoulder-Hip-Knee
    angles["knee"] = angle_between(lm[23], lm[25], lm[27])  # Hip-Knee-Ankle
    angles["ankle"] = angle_between(lm[25], lm[27], lm[31])  # Knee-Ankle-Toe
    return angles


# ---------- Mediapipe Setup ----------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    smooth_segmentation=False,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
mp_drawing = mp.solutions.drawing_utils

# ---------- Real-time plot setup ----------
landmark_ids = {"shoulder": 11, "hip": 23, "knee": 25, "ankle": 27, "toe": 31}

plot_buffer = {name: [] for name in landmark_ids}
joint_angle_buffer = {"hip": [], "knee": [], "ankle": []}

plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
lines_y = {}
lines_angle = {}

for name in landmark_ids:
    (line,) = ax1.plot([], [], label=f"{name}_y")
    lines_y[name] = line
ax1.set_title("Landmark Y-Values")
ax1.set_xlim(0, 100)
ax1.set_ylim(-1, 1)
ax1.legend()

for joint in joint_angle_buffer:
    (line,) = ax2.plot([], [], label=f"{joint}_angle")
    lines_angle[joint] = line
ax2.set_title("Joint Angles")
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 180)
ax2.legend()

frame_count = 0

window_closed = False


# ---------- Main Runner ----------
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

filter_instance = TrueRealTimeFilter()
angle_history = []
landmark_history = []
cv2.startWindowThread()
while True:
    frame = picam2.capture_array()
    # if not ret:
    #     break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_world_landmarks:
        landmarks = results.pose_world_landmarks.landmark
        filtered_landmarks = []

        for idx, lm in enumerate(landmarks):
            x = filter_instance.apply(idx, "x", lm.x)
            y = filter_instance.apply(idx, "y", lm.y)
            z = filter_instance.apply(idx, "z", lm.z)
            filtered_landmarks.append((x, y, z))
        landmark_history.append(filtered_landmarks)

        for name, idx in landmark_ids.items():
            plot_buffer[name].append(filtered_landmarks[idx][1])

        angles = calculate_joint_angles(filtered_landmarks)
        for joint, val in angles.items():
            joint_angle_buffer[joint].append(val)

        for name, line in lines_y.items():
            y_data = plot_buffer[name][-100:]  # last 100 frames
            line.set_data(range(len(y_data)), y_data)

        ax1.relim()
        ax1.autoscale_view()

        # Update angle plots
        for joint, line in lines_angle.items():
            a_data = joint_angle_buffer[joint][-100:]
            line.set_data(range(len(a_data)), a_data)

        ax2.relim()
        ax2.autoscale_view()

        fig.canvas.draw()
        fig.canvas.flush_events()

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

    cv2.imshow("Camera", frame)

    try:
        if not plt.fignum_exists(fig.number):  # check if figure still exists
            window_closed = True
    except:
        window_closed = True

    # plt.pause(0.001)
    if window_closed or (cv2.waitKey(1) & 0xFF == ord("q")):
        print("stopping cv2")
        break
    # finally:
    #

# hip_vals = [a["hip"] for a in angle_history]
# knee_vals = [a["knee"] for a in angle_history]
# ankle_vals = [a["ankle"] for a in angle_history]

# strikes = detect_heel_strikes(landmark_history)

# hip_cycles = [normalize_cycle(c) for c in segment_cycles(hip_vals, strikes)]
# knee_cycles = [normalize_cycle(c) for c in segment_cycles(knee_vals, strikes)]
# ankle_cycles = [normalize_cycle(c) for c in segment_cycles(ankle_vals, strikes)]

# # plot_superimposed_cycles(
# #     {"hip": hip_cycles, "knee": knee_cycles, "ankle": ankle_cycles}
# # )
data = {
    "Hip Filtered": [a for a in joint_angle_buffer["hip"][-100:]],
    "Knee Filtered": [a for a in joint_angle_buffer["knee"][-100:]],
    "Ankle Filtered": [a for a in joint_angle_buffer["ankle"][-100:]],
    "Left Heel Values": [lm[30] for lm in landmark_history[-100:]],
}

print("saving data to file")
df = pd.DataFrame(data)
df.to_csv(f"{BASE_DATA_PATH}/gait_filtered_data.csv", index=False)


picam2.close()
cv2.destroyAllWindows()
pose.close()  # <<< Important!
plt.ioff()
fig.savefig(f"{BASE_DATA_PATH}/gait_plot.png")
plt.close("all")

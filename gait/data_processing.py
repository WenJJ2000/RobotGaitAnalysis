from scipy.signal import butter, filtfilt
import numpy as np
import pandas as pd


def butter_lowpass(data, cutoff=3, fs=30, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return filtfilt(b, a, data)


def filter_landmark_series(series_dict, fs=30):
    """Apply Butterworth filter to x, y, z of one landmark over time."""
    return {
        "x": butter_lowpass(series_dict["x"], fs=fs),
        "y": butter_lowpass(series_dict["y"], fs=fs),
        "z": butter_lowpass(series_dict["z"], fs=fs),
    }


def init_landmark_buffer(joint_indices):
    return {i: {"x": [], "y": [], "z": []} for i in joint_indices}


def record_landmarks(landmark_history, results):
    if results.pose_world_landmarks:
        for i in landmark_history.keys():
            lm = results.pose_world_landmarks.landmark[i]
            landmark_history[i]["x"].append(lm.x)
            landmark_history[i]["y"].append(lm.y)
            landmark_history[i]["z"].append(lm.z)


def calc_angle_3d(a, b, c, frame):
    """Calculates the angle at point 'b' formed by a-b-c using filtered points."""
    vec1 = np.array(
        [
            a["x"][frame] - b["x"][frame],
            a["y"][frame] - b["y"][frame],
            a["z"][frame] - b["z"][frame],
        ]
    )
    vec2 = np.array(
        [
            c["x"][frame] - b["x"][frame],
            c["y"][frame] - b["y"][frame],
            c["z"][frame] - b["z"][frame],
        ]
    )
    cos_theta = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
    return angle


def compute_joint_angles(filtered_data):
    angles = {
        "left_hip": [],
        "left_knee": [],
        "left_ankle": [],
        "right_hip": [],
        "right_knee": [],
        "right_ankle": [],
    }

    n_frames = len(next(iter(filtered_data.values()))["x"])

    for f in range(n_frames):
        angles["left_hip"].append(
            calc_angle_3d(filtered_data[11], filtered_data[23], filtered_data[25], f)
        )
        angles["left_knee"].append(
            calc_angle_3d(filtered_data[23], filtered_data[25], filtered_data[27], f)
        )
        angles["left_ankle"].append(
            calc_angle_3d(filtered_data[25], filtered_data[27], filtered_data[31], f)
        )

        angles["right_hip"].append(
            calc_angle_3d(filtered_data[12], filtered_data[24], filtered_data[26], f)
        )
        angles["right_knee"].append(
            calc_angle_3d(filtered_data[24], filtered_data[26], filtered_data[28], f)
        )
        angles["right_ankle"].append(
            calc_angle_3d(filtered_data[26], filtered_data[28], filtered_data[32], f)
        )

    return angles


def process_pose_data(landmark_history, fs=30):
    # Filter landmarks
    filtered = {
        i: filter_landmark_series(landmark_history[i], fs=fs) for i in landmark_history
    }

    # Calculate angles
    angles = compute_joint_angles(filtered)

    return filtered, angles


def save_angles_to_csv(filtered_angles, unfiltered_angles, filename_prefix="angles"):
    for joint in filtered_angles:
        df = pd.DataFrame(
            {"filtered": filtered_angles[joint], "unfiltered": unfiltered_angles[joint]}
        )
        df.to_csv(f"{filename_prefix}_{joint}.csv", index_label="frame")


def landmark_to_points(landmark):
    return np.array([landmark.x, landmark.y, landmark.z])

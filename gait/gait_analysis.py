from pose_landmarks.points_on_landmarks import (
    pose_landmark_name_to_idx as landmark_index,
)
from pose_landmarks.points_on_landmarks import (
    pose_landmark_idx_to_name as landmark_name,
)
from scipy.signal import butter, filtfilt, find_peaks
from mediapipe.framework.formats import landmark_pb2
import matplotlib.pyplot as plt
import numpy as np


def calculate_angle(a, b, c) -> float:
    """Calculate angle ABC (in degrees) from three 3D points."""
    a = np.array([a.x, a.y, a.z])
    b = np.array([b.x, b.y, b.z])
    c = np.array([c.x, c.y, c.z])

    ba = b - a
    bc = b - c

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def detect_motion_start(joint_vals, threshold=2.0, window=5):
    diffs = np.abs(np.diff(joint_vals))
    for i in range(len(diffs) - window):
        if np.mean(diffs[i : i + window]) > threshold:
            return i
    return 0  # fallback


def get_left_joint_angles(
    landmarks: landmark_pb2.nomalized_landmarklist,
) -> tuple[float, float, float]:
    """
    Calculate joint angles for left leg: hip, knee, ankle.

    Parameters:
    - landmarks: pose_world_landmarks.landmark

    Returns:
    - hip_angle, knee_angle, ankle_angle (in degrees)
    """

    # Left side landmarks
    shoulder = landmarks[landmark_index["left_shoulder"]]
    hip = landmarks[landmark_index["left_hip"]]
    knee = landmarks[landmark_index["left_knee"]]
    ankle = landmarks[landmark_index["left_ankle"]]
    foot = landmarks[landmark_index["left_foot_index"]]

    hip_angle = calculate_angle(shoulder, hip, knee)
    knee_angle = calculate_angle(hip, knee, ankle)
    ankle_angle = calculate_angle(knee, ankle, foot)

    return hip_angle, knee_angle, ankle_angle


def get_right_joint_angles(
    landmarks: landmark_pb2.NormalizedLandmarkList,
) -> tuple[float, float, float]:
    """
    Calculate joint angles for right leg: hip, knee, ankle.

    Parameters:
    - landmarks: pose_world_landmarks.landmark

    Returns:
    - hip_angle, knee_angle, ankle_angle (in degrees)
    """
    # Right side landmarks
    shoulder = landmarks[landmark_index["right_shoulder"]]
    hip = landmarks[landmark_index["right_hip"]]
    knee = landmarks[landmark_index["right_knee"]]
    ankle = landmarks[landmark_index["right_ankle"]]
    foot = landmarks[landmark_index["right_foot_index"]]

    hip_angle = calculate_angle(shoulder, hip, knee)
    knee_angle = calculate_angle(hip, knee, ankle)
    ankle_angle = calculate_angle(knee, ankle, foot)

    return hip_angle, knee_angle, ankle_angle


def butter_lowpass_filter(data, cutoff=5.0, fs=30.0, order=2):
    """
    Applies a 2nd-order Butterworth low-pass filter to the data.

    Args:
        data: List or array of values (e.g. joint angles).
        cutoff: Cutoff frequency in Hz.
        fs: Sampling frequency in Hz (e.g., 30 FPS).
        order: Order of the filter.

    Returns:
        Filtered data (numpy array).
    """
    nyq = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyq

    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)  # Apply forward-backward filtering
    return y if len(data) > order * 3 else data


def normalize_gait_cycle(segment, num_points=100, normalize_y=False):
    # Normalize X (resample to num_points)
    original_x = np.linspace(0, 1, len(segment))
    target_x = np.linspace(0, 1, num_points)
    resampled = np.interp(target_x, original_x, segment)

    # Optional: Normalize Y (angle)
    if normalize_y:
        min_val = np.min(resampled)
        max_val = np.max(resampled)
        if max_val != min_val:
            resampled = (resampled - min_val) / (max_val - min_val)
        else:
            resampled = np.zeros_like(resampled)

    return resampled


def detect_heel_strikes(heel_z_series, distance=30, prominence=0.005):
    """
    Detect heel strikes as local minima in heel z position (i.e., closest to ground).
    """
    inverted_z = -np.array(heel_z_series)  # because lower z = closer to ground
    peaks, _ = find_peaks(inverted_z, distance=distance, prominence=prominence)
    return peaks


def butterworth_filter_landmarks(landmarks_array, cutoff=3, fs=30, order=2):
    """
    Applies a 2nd-order Butterworth low-pass filter to a landmark array.

    Args:
        landmarks_array: np.array shape (n_frames, 33, 3) → (frames, landmarks, [x,y,z])
        cutoff: frequency cutoff (Hz)
        fs: sampling rate (Hz)
        order: filter order (2 for critically damped)

    Returns:
        np.array of same shape (n_frames, 33, 3) filtered
    """
    b, a = butter(order, cutoff / (0.5 * fs), btype="low")
    filtered = np.zeros_like(landmarks_array)

    # Loop through each landmark and each coordinate
    for lm_idx in range(landmarks_array.shape[1]):  # 33 landmarks
        for coord in range(3):  # x, y, z
            series = landmarks_array[:, lm_idx, coord]
            filtered[:, lm_idx, coord] = filtfilt(b, a, series)

    return filtered

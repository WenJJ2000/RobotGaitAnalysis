import json
from gait_analysis import (
    butter_lowpass_filter,
    detect_heel_strikes,
    detect_motion_start,
    normalize_gait_cycle,
)
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def superimpose_gait_cycles(
    filtered_angle, start, joint_name="Hip", save_path="hip_gait_overlay.png"
):
    # Detect cycle start points (hip minima)

    # peaks, _ = find_peaks(-np.array(filtered_angle), distance=10)
    peaks = start

    gait_cycles = []
    for i in range(len() - 1):
        start, end = peaks[i], peaks[i + 1]
        segment = filtered_angle[start:end]
        if len(segment) < 5:
            continue  # skip very short segments

        # Normalize to fixed length (e.g. 100 points)
        # resampled = np.interp(
        #     np.linspace(0, 1, 100), np.linspace(0, 1, len(segment)), segment
        # )
        resampled = normalize_gait_cycle(segment, 100)
        gait_cycles.append(resampled)

    # Plot all cycles
    gait_cycles = np.array(gait_cycles)
    avg_cycle = np.mean(gait_cycles, axis=0)

    plt.figure(figsize=(10, 5))
    for cycle in gait_cycles:
        plt.plot(cycle, alpha=0.3, color="blue")
    plt.plot(avg_cycle, color="red", label="Average Gait Cycle", linewidth=2)
    plt.title(f"{joint_name} Gait Cycles")
    plt.xlabel("Normalized Gait Cycle (%)")
    plt.ylabel("Joint Angle (°)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"./gait_data/{save_path}")
    plt.close()


df = pd.read_csv("./gait_data/gait_filtered_data.csv")

hip_vals = df["Hip Filtered"].values
knee_vals = df["Knee Filtered"].values
ankle_vals = df["Ankle Filtered"].values
heel_vals_z = df["Left Heel Values"].values
# print(heel_vals_z)


hip_filtered = butter_lowpass_filter(hip_vals)
start_index = detect_motion_start(hip_filtered)

# Trim all signals
hip_vals = hip_vals[start_index:]
knee_vals = knee_vals[start_index:]
ankle_vals = ankle_vals[start_index:]

hip_filtered = butter_lowpass_filter(hip_vals)
knee_filtered = butter_lowpass_filter(knee_vals)
ankle_filtered = butter_lowpass_filter(ankle_vals)

cycle_start = detect_heel_strikes(heel_vals_z, distance=30, prominence=0.005)

superimpose_gait_cycles(hip_filtered, cycle_start, "Hip", "hip_overlay.png")
superimpose_gait_cycles(knee_filtered, cycle_start, "Knee", "knee_overlay.png")
superimpose_gait_cycles(ankle_filtered, cycle_start, "Ankle", "ankle_overlay.png")

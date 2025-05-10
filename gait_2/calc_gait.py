import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfilt, sosfilt_zi, find_peaks
from scipy.interpolate import interp1d
import pandas as pd
import ast


# ---------- Gait Event Detection ----------
def detect_heel_strikes(heel_values):
    heel_y = [point[2] for point in heel_values]
    peaks, _ = find_peaks(-np.array(heel_y), distance=19)
    return peaks


# ---------- Gait Cycle Segmentation ----------
def segment_cycles(data, strike_indices):
    return [data[start:end] for start, end in zip(strike_indices, strike_indices[1:])]


# ---------- Normalize Gait Cycles ----------
def normalize_cycle(cycle, points=100):
    x_old = np.linspace(0, 100, len(cycle))
    f = interp1d(x_old, cycle, kind="cubic")
    return f(np.linspace(0, 100, points))


# ---------- Plot Superimposed Gait Cycles ----------
def plot_superimposed_cycles(cycles_dict):
    joints = ["hip", "knee", "ankle"]
    x = np.linspace(0, 100, 100)
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    for i, joint in enumerate(joints):
        for cycle in cycles_dict[joint]:
            axs[i].plot(x, cycle, alpha=0.3)
        axs[i].set_ylabel(f"{joint.capitalize()} (\u00b0)")
        axs[i].grid(True)
    axs[-1].set_xlabel("Gait Cycle (%)")
    plt.suptitle("Superimposed Gait Cycles")
    plt.tight_layout()
    plt.show()


# ----------- Main Calculation -----------

# Read data
df = pd.read_csv("./gait_data/gait_filtered_data.csv")

left_heel_values = list(
    map(lambda x: ast.literal_eval(x), df["Left Heel Values"].tolist())
)

data = ["Hip Filtered", "Knee Filtered", "Ankle Filtered"]
all_angles = []
for i in data:
    all_angles.append(df[i].tolist())

# get start of gait cycles
heel_strikes = detect_heel_strikes(left_heel_values)


normalized_segments = []
# Segment cycles
for angles in all_angles:
    segment = segment_cycles(angles, heel_strikes)
    norm_angle = []
    for seg in segment:
        norm_seg = normalize_cycle(seg)
        norm_angle.append(norm_seg)
    normalized_segments.append(norm_angle)

print(normalized_segments)
print(len(normalized_segments))

d = {
    "hip": normalized_segments[0],
    "knee": normalized_segments[1],
    "ankle": normalized_segments[2],
}

plot_superimposed_cycles(d)
# seg_cycle = [segment_cycles(i, heel_strikes) for i in all_angles]

# print(seg_cycle)

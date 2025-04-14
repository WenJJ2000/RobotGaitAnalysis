# from camera import RaspberryCam
# from inference import FrameInference, PoseInference
# from GaitRobot import GaitRobot
import cv2
from utils import draw_landmarks_on_image
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pose_landmarks.points_on_landmarks import (
    pose_landmark_name_to_idx as landmark_index,
)
from pose_landmarks.points_on_landmarks import (
    pose_landmark_idx_to_name as landmark_name,
)

# VIDEO_SOURCE = "raspberry pi"
VIDEO_SOURCE = 0
# print(cv2.getBuildInformation())


motor_pins = []


# raspi_cam = RaspberryCam(VIDEO_SOURCE)


# tracking_inference = FrameInference(raspi_cam)


# pose = PoseInference(raspi_cam)
raspi_cam = cv2.VideoCapture(VIDEO_SOURCE, cv2.CAP_MSMF)  # Live cam


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
frame_count = 0


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
        print(results.pose_landmarks)

        if results.pose_landmarks:
            # save data to file
            if frame_count % 5 == 0:
                with open("./pose_landmarks/pose_landmarks.txt", "a") as f:
                    d = {"data": {}, "frame_count": frame_count}
                    for idx, landmark in enumerate(results.pose_landmarks.landmark):
                        name = landmark_name.get(idx, f"landmark_{idx}")
                        d["data"][name] = [
                            landmark.x,
                            landmark.y,
                            landmark.z,
                            landmark.visibility,
                        ]

                    f.write(str(d) + "\n")

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

        frame_count += 1
raspi_cam.release()
cv2.destroyAllWindows()

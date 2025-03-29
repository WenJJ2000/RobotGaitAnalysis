import os
from ultralytics import YOLO
from threading import Thread
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2

class FrameInference:
	def __init__(self, video_cam):
		self.model = YOLO("yolov10s.pt")
		self.video_cam = video_cam

		self.model_thread = Thread(target=self.obj_inference, args=(),daemon=True)
		self.model_thread.start()
  
	
	def obj_inference(self):
		while True:
			self.res,self.frame = self.video_cam.read()
			if self.res:
				self.results = self.model.predict(self.frame)

	def get_result(self):
		return self.results


class PoseInference:
    def __init__(self,video_cam):
        self.pose_model = "./pose_landmarker.task"
        
        self.options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=self.pose_model),
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self.get_landmarker_data
            )
        
        self.video_cam = video_cam
        
		# initializing mediapipe
        self.landmarker = vision.PoseLandmarker.create_from_options(self.options)
    
        self.count = 0
        self.frame = None
        self.res = False
        self.results = None
        
    def get_landmarker_data(self, result, output_image, timestamp_ms):
        self.results = result


    def pose_inference(self):
        self.res, self.frame = self.video_cam.read()
        if self.res:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(self.frame))
            
            self.landmarker.detect_async(mp_image, self.count)
            self.count += 1
        return self.frame, self.results
    
    # def draw_landmarks_on_image(self):
    #     pose_landmarks_list = self.pose_inference()
        
    #     if not self.results:
    #         return self.frame
    #     annotated_image = np.copy(self.frame)

	# 	# Loop through the detected poses to visualize.
    #     for idx in range(len(pose_landmarks_list)):
    #         pose_landmarks = pose_landmarks_list[idx]

	# 	# Draw the pose landmarks.
    #     pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    #     pose_landmarks_proto.landmark.extend([
    #         landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    #         ])
    #     solutions.drawing_utils.draw_landmarks(
    #         annotated_image,
    #         pose_landmarks_proto,
    #         solutions.pose.POSE_CONNECTIONS,
    #         solutions.drawing_styles.get_default_pose_landmarks_style())
    #     return annotated_image
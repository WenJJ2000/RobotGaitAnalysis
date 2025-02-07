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
		self.options = PoseLandmarkerOptions(
				base_options=BaseOptions(model_asset_path=self.pose_model),
				running_mode=VisionRunningMode.LIVE_STREAM,
				result_callback=get_landmarker_data
				)
		self.pose_model = "./pose_landmarker.task"

		self.pose_thread = Thread(target=self.pose_inference,args=(),daemon=True)
		self.model_thread.start()
		self.mp =
	
		BaseOptions = mp.tasks.BaseOptions
		PoseLandmarker = mp.tasks.vision.PoseLandmarker
		PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
		PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
		VisionRunningMode = mp.tasks.vision.RunningMode
    
    def get_landmarker_data():
        return
    def pose_inference(self):
        return 
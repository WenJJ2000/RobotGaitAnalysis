import os
from ultralytics import YOLO
from threading import Thread

class FrameInference:
	def __init__(self, videocam):
		self.model = YOLO("yolov10s.pt")
		self.videocam = videocam
		

		self.model_thread = Thread(target=self.inference, args=(),daemon=True)
		self.model.start()
	
	def inference(self):
		while True:
			self.res,self.frame = self.videocam.read()
			if self.res:
				self.results = self.model.predict(self.frame)

	def get_result(self):
		return self.results

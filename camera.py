import cv2
from threading import Thread



class RaspberryCam:
    def __init__(self, src, fps=25):
        self.capture = cv2.VideoCapture(src,cv2_GSTREAMER)
        
        self.FPS = fps
        
		self.thread = Thread(target=self.update, args=(),daemon=True)
		self.thread.start()

	def update_cam(self):
		while True:
			if self.capture.isOpened():
				self.res, self.frame = self.capture.read()
	
	def read(self):
		return self.res, self.frame	

import cv2
from threading import Thread



class RaspberryCam:
    def __init__(self, src, fps=25):
        # self.capture = cv2.VideoCapture(src,cv2_GSTREAMER)
        self.capture = cv2.VideoCapture(0) # Live cam
        
        self.FPS = fps
        self.thread = Thread(target=self.update_cam, args=(),daemon=True)
        self.thread.start()


        self.res = False
        self.frame = None
            
    def update_cam(self):
        while True:
            if self.capture.isOpened():
                self.res, self.frame = self.capture.read()
    
    def read(self):
        print(self.frame)
        return self.res, self.frame	

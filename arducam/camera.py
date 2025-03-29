import cv2
from threading import Thread

class RaspberryCam:
    def __init__(self, src, fps=25):
        '''
        apiPreference    preferred Capture API backends to use. 
        Can be used to enforce a specific reader implementation 
        if multiple are available: 
        e.g. cv2.CAP_MSMF or cv2.CAP_DSHOW.
        '''
        # self.capture = cv2.VideoCapture(src,cv2_GSTREAMER)
        self.capture = cv2.VideoCapture(0,cv2.CAP_MSMF) # Live cam
        
        self.FPS = fps
        self.thread = Thread(target=self.update_cam, args=(),daemon=True)
        self.thread.start()
        # set width and height
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # set fps
        # cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.res = False
        self.frame = None
            
    def update_cam(self):
        while True:
            if self.capture.isOpened():
                self.res, self.frame = self.capture.read()
    
    def read(self):
        print(self.frame)
        return self.res, self.frame	



# open video0
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
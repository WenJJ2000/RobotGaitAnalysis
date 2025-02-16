from camera import RaspberryCam
from inference import FrameInference, PoseInference
from GaitRobot import GaitRobot
import cv2
from utils import draw_landmarks_on_image

# VIDEO_SOURCE = "raspberry pi"
VIDEO_SOURCE = 0

motor_pins = []


raspi_cam = RaspberryCam(VIDEO_SOURCE)


tracking_inference = FrameInference(raspi_cam)


pose = PoseInference(raspi_cam)


while True:
    try:
    # if pose_inference
        frame,results = pose.pose_inference()
        if frame is not None and results is not None:
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            annotated_image =draw_landmarks_on_image(rgb_frame,results)
            
            if annotated_image is not None:
            
                cv2.imshow("pose frame",annotated_image)
        
        if cv2.waitKey() & 0xFF == ord("q"):
            break
        
    except AttributeError:
        pass
    
cv2.destroyAllWindows()

from robot_movement.test_motor import car_forward,car_backward,car_stop,car_left,car_right
from picamera2 import Picamera2
import cv2
import mediapipe as mp


# ----------Global Vairable----------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    smooth_segmentation=False,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
mp_drawing = mp.solutions.drawing_utils
landmark_ids = {"shoulder": 11, "hip": 23, "knee": 25, "ankle": 27, "toe": 31}
hip_id = 23
x_thresh = [0.4,0.6]
# ---------- Helper Function ---------

def within_thresh(pt): # inside=1 leftside=0 rightside=2
    if x_thresh[0] < pt < x_thresh[1]: return 1
    if pt < x_thresh[0]: return 0
    if pt > x_thresh[1]: return 2


# ---------- Initialise Camera ----------

def main():
    with Picamera2() as picam2:
        picam2.preview_configuration.main.size = (640, 480)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.configure("preview")
        picam2.start()
        
        while True:
            frame = picam2.capture_array()
            results = pose.process(frame)
            
            if results.pose_world_landmarks:
                left_hip = results.pose_landmarks.landmark[hip_id]
                right_hip = results.pose_landmarks.landmark[hip_id+1]
                # hip_loc = landmarks
                
                print(left_hip,right_hip)
                
                if left_hip.visibility > 0.7 and right_hip.visibility > 0.7:
                    match within_thresh(left_hip.x):
                        case 0:
                            car_backward()
                        case 1 :
                            car_stop()
                        case 2:     
                            car_forward()
                else :
                    car_stop()
                            
                    # match within_thresh(right_hip.x):
                    #     case 1:
                    #         car_stop()
                    #     case 0:      
                    #         car_backward()
                    #     case 2:     
                    #         car_forward()
                    
                        
                    
                
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
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    
                
    cv2.destroyAllWindows()






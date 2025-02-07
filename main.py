from camera import RaspberryCam
from inference import FrameInference, PoseInference
from GaitRobot import GaitRobot

VIDEO_SOURCE = "raspberry pi"

motor_pins = []


raspi_cam = RaspberryCam(VIDEO_SOURCE)


tracking_inference = FrameInference(raspi_cam)

pose_Inference = PoseInference(raspi_cam)


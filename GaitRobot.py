from gpiozero import Robot, Motor

# motor pins
# m1 = 4 27
# m2 = 22 23
# m3 = 24 25
# m4 = 5 6

class GaitRobot:
    
  def __init__(self,pins):
		self.motor1 = Motor(pins[0],pins[1])
    self.motor2 = Motor(pins[2],pins[3])
    self.motor3 = Motor(pins[4],pins[5])
    self.motor4 = Motor(pins[6],pins[7])
    self.robot = Robot(left=(self.motor1,self.motor2),right=(self.motor3,self.motor4))
    

	def forward(self,speed =1):
    self.robot.forward(speed)
    
  def backwards(self,speed =1):
    self.robot.backward(speed)
    
  def turn_left(self, speed =1):
    self.robot.left(speed)
    
  def turn_right(self, speed =1):
    self.robot.right(speed)

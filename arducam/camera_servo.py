import adafruit_servokit


class ServoKit(object):
    default_angle = 90

    def __init__(self, num_ports, step):
        print("Initializing the servo...")
        self.kit = adafruit_servokit.ServoKit(channels=16)
        self.num_ports = num_ports
        self.resetAll()
        self.motor_step = step
        print("Initializing complete.")

    def setAngle(self, port, angle):
        if angle < 0:
            self.kit.servo[port].angle = 0
        elif angle > 180:
            self.kit.servo[port].angle = 180
        else:
            self.kit.servo[port].angle = angle

    def getAngle(self, port):
        return self.kit.servo[port].angle

    def reset(self, port):
        self.kit.servo[port].angle = self.default_angle

    def resetAll(self):
        for i in range(self.num_ports):
            self.kit.servo[i].angle = self.default_angle

    def rotate_clockwise():
        self.setAngle(1, self.getAngle(1) - self.motor_step)

    def rotate_anticlockwise():
        self.setAngle(1, self.getAngle(1) + self.motor_step)

    def tilt_up():
        self.setAngle(0, self.getAngle(0) + self.motor_step)

    def tilt_up():
        self.setAngle(0, self.getAngle(0) - self.motor_step)

import curses
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

    def rotate_clockwise(self):
        self.setAngle(1, self.getAngle(1) + self.motor_step)

    def rotate_anticlockwise(self):
        self.setAngle(1, self.getAngle(1) - self.motor_step)

    def tilt_up(self):
        self.setAngle(0, self.getAngle(0) + self.motor_step)

    def tilt_down(self):
        self.setAngle(0, self.getAngle(0) - self.motor_step)


def parseKey(k, servoKit, camera):
    global image_count
    motor_step = 5
    if k == ord('s'):
        servoKit.tilt_down()
    elif k == ord('w'):
        servoKit.tilt_up()
    elif k == ord('d'):
        servoKit.rotate_anticlockwise()
    elif k == ord('a'):
        servoKit.rotate_clockwise()
    elif k == ord('r'):
        servoKit.resetAll()
    elif k == curses.KEY_DOWN:
        servoKit.tilt_down()
    elif k == curses.KEY_UP:
        servoKit.tilt_up()
    elif k == curses.KEY_RIGHT:
        servoKit.rotate_anticlockwise()
    elif k == curses.KEY_LEFT:
        servoKit.rotate_clockwise()


# Python curses example Written by Clay McLeod
# https://gist.github.com/claymcleod/b670285f334acd56ad1c
def draw_menu(stdscr, camera):
    servoKit = ServoKit(4,5)

    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while (k != ord('q')):
        # Initialization
        stdscr.clear()
        # Flush all input buffers.
        curses.flushinp()
        # get height and width of the window.
        height, width = stdscr.getmaxyx()

        # parser input key
        parseKey(k, servoKit, camera)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Wait for next input
        k = stdscr.getch()
    

def main():
    curses.wrapper(draw_menu, None)


if __name__ == "__main__":
    main()
from gpiozero import Motor
import curses
import sys

motor1A = 17 # in1 GPIO17
motor1B = 27 # in2 GPIO27

motor2A = 24 # in1 GPIO24
motor2B = 23 # in2 GPIO23

motor3A = 18 # in1 GPIO18
motor3B = 22 # in2 GPIO22

motor4A = 19 # in2 GPIO19
motor4B = 26 # in2 GPIO26



# setup pins
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(activate1,GPIO.OUT)
# print("setup done")


#start motor
motor1 = Motor(motor1A,motor1B)
motor2 = Motor(motor2A,motor2B)
motor3 = Motor(motor3A,motor3B)
motor4 = Motor(motor4A,motor4B)


def front_forward():
    motor1.forward()
    motor2.forward()

def front_backward():
    motor1.backward()
    motor2.backward()
    
def back_forward():
    motor3.forward()
    motor4.forward()
    
def back_backward():
    motor3.backward()
    motor4.backward()
    
def car_forward():
    front_forward()
    back_forward()

def car_backward():
    front_backward()
    back_backward()
    
# while True:
    # print()
    # car_forward()
    # motor3.forward()
    # motor4.forward()
    # back_forward()
    # motor4.forward()
    # print("motor moving")

    
def main(stdscr):
        
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    # stdscr.clear()
    # stdscr.addstr(0, 0, "Press any key, or 'q' to quit")
    # stdscr.refresh()
    try:
        while True:
            char = screen.getch()
            if char == ord('q'):
                break
            elif char == curses.KEY_UP:
                print("up")
                motor1.forward()
            elif char == curses.KEY_DOWN:
                print("down")
                car_backward()
            elif char == curses.KEY_RIGHT:
                print("right")
            elif char == curses.KEY_LEFT:
                print("left")
            elif char == 10:
                print("stop")    
    finally:
        #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
            


if __name__ == "__main__":
    curses.wrapper(main)
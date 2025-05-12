from gpiozero import Motor
import curses
import sys
from time import sleep

# ---------- Global Variables ----------
STEP = 1

# ---------- Motor Setup ----------

motor1A = 17 # in1 GPIO17
motor1B = 27 # in2 GPIO27

motor2A = 24 # in1 GPIO24
motor2B = 23 # in2 GPIO23

motor3A = 18 # in1 GPIO18
motor3B = 22 # in2 GPIO22

motor4A = 19 # in2 GPIO19
motor4B = 26 # in2 GPIO26

# start motor
motor1 = Motor(motor1A,motor1B)
motor2 = Motor(motor2A,motor2B)
motor3 = Motor(motor3A,motor3B)
motor4 = Motor(motor4A,motor4B)

# ---------- Motor Functions ----------
def front_forward():
    motor1.forward()
    motor2.forward()

def front_backward():
    motor1.backward()
    motor2.backward()
    
def front_stop():
    motor1.stop()
    motor2.stop()
    
def back_forward():
    motor3.forward()
    motor4.forward()
    
def back_backward():
    motor3.backward()
    motor4.backward()

def back_stop():
    motor3.stop()
    motor4.stop()
    
def car_forward():
    front_forward()
    back_forward()

def car_backward():
    front_backward()
    back_backward()
    
def car_stop():
    motor1.stop()
    motor2.stop()
    motor3.stop()
    motor4.stop()
    
    
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
                car_forward()
                
            elif char == curses.KEY_DOWN:
                print("down")
                car_backward()
            elif char == curses.KEY_RIGHT:
                print("right")
            elif char == curses.KEY_LEFT:
                print("left")
            elif char == 10:
                print("stop")
                
            sleep(STEP)
            car_stop()
            
            
    finally:
        #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
            


if __name__ == "__main__":
    curses.wrapper(main)
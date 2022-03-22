import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

TRIG = 16
ECHO = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

t_count = 0.2  # detect range every 0.2 sec
detect_range = 100  # set the range


def get_distance():
    GPIO.output(TRIG, GPIO.HIGH)  # send trig
    time.sleep(t_count)
    GPIO.output(TRIG, GPIO.LOW)  # get echo

    while GPIO.input(ECHO) == 0:
        start = time.time()
        # print("start:", start)
    while GPIO.input(ECHO) == 1:
        end = time.time()
        # print("end", end)

    D = (end - start) * 17150
    return int(D)


def detect_passby():
    while True:
        a = get_distance()  # get distance
        # print(f"distance {a:.1f} cm")  # print the distance
        if a < detect_range:  # if someone came into the detect range
            print(a)
            while True:
                b = get_distance()
                print(b)
                if b > detect_range:  # and then leave the detect range
                    global x
                    x = x + 1
                    print(f"累積通過人數： {x}人")
                    break

x = 0
try:
    detect_passby()
except KeyboardInterrupt:
    print("bye")
finally:
    GPIO.cleanup()
    print(f"total pass: {x}人")

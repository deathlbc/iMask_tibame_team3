import RPi.GPIO as GPIO
import time

output_pin = 12


def bbb():
    GPIO.setmode(GPIO.BOARD)  # BCM pin-numbering scheme from Raspberry Pi
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    print("bbb working!")
    curr_value = GPIO.HIGH

    try:
        while True:
            curr_value ^= GPIO.HIGH
            print("Outputting {} to pin {}".format(curr_value, output_pin))
            GPIO.output(output_pin, curr_value) # bbb
            time.sleep(0.5)
            break
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    bbb()


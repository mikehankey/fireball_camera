import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# GPIO 19 = Cam Power ON/OFF send high for OFF

GPIO.setup(19, GPIO.OUT)

GPIO.output(19, GPIO.HIGH) 

import cv2
from picamera2 import Picamera2
import time
from time import sleep
import numpy as np
import pigpio
#sudo pigpiod when you want to make the motors work
# Initialize Picamera2
picam2 = Picamera2()

# GPIO setup for hardware PWM
pi = pigpio.pi()
pan_1 = 18  # GPIO pin for pan servo (PWM0)
tilt_1 = 19  # GPIO pin for tilt servo (PWM1)
SERVO_PIN = 12 # GPIO pin for Actuator (PWM0)

STOP_PULSE = 1500  # Pulse to stop the servo 
FORWARD_PULSE = 500  # Pulse for forward movement
BACKWARD_PULSE = 2500  # Pulse for backward movement

# Function to set the servo pulse width
def set_servo_pulse(pin, pulse_width, duration):
    pi.set_servo_pulsewidth(pin, pulse_width)  
    time.sleep(duration)  
    pi.set_servo_pulsewidth(pin, STOP_PULSE)  

# Servo initial angles
pan = 90
tilt = 75

# Function to convert angle to pulse width 
def angle_to_pulse(angle):
    return int(500 + (angle / 180.0) * 2000)

# Function to set servo angle
def set_angle(pin, angle):
    pulse = angle_to_pulse(angle)
    print(f"Setting pin {pin} to angle {angle} (pulse {pulse} µs)")
    pi.set_servo_pulsewidth(pin, pulse)  # Set hardware PWM signal

# Move servos to initial position
set_angle(pan_1, pan)
set_angle(tilt_1, tilt)

# Camera setup
dispW = 1280
dispH = 720
picam2.preview_configuration.main.size = (dispW, dispH)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# GUI and tracking setup
fps = 0
pos = (30, 60)
font = cv2.FONT_HERSHEY_SIMPLEX
height = 1.5
weight = 3
myColor = (0, 0, 255)
track = 0

def onTrack1(val):
    global hueLow
    hueLow = val
    print('Hue Low', hueLow)

def onTrack2(val):
    global hueHigh
    hueHigh = val
    print('Hue High', hueHigh)

def onTrack3(val):
    global satLow
    satLow = val
    print('Sat Low', satLow)

def onTrack4(val):
    global satHigh
    satHigh = val
    print('Sat High', satHigh)

def onTrack5(val):
    global valLow
    valLow = val
    print('Val Low', valLow)

def onTrack6(val):
    global valHigh
    valHigh = val
    print('Val High', valHigh)

def onTrack7(val):
    global track
    track = val
    print('Track Value', track)

cv2.namedWindow('myTracker')
cv2.createTrackbar('Hue Low', 'myTracker', 60, 179, onTrack1)
cv2.createTrackbar('Hue High', 'myTracker', 103, 179, onTrack2)
cv2.createTrackbar('Sat Low', 'myTracker', 21, 255, onTrack3)
cv2.createTrackbar('Sat High', 'myTracker', 255, 255, onTrack4)
cv2.createTrackbar('Val Low', 'myTracker', 1, 255, onTrack5)
cv2.createTrackbar('Val High', 'myTracker', 116, 255, onTrack6)
cv2.createTrackbar('Train-0 Track-1', 'myTracker', 0, 1, onTrack7)

frame_count = 0
launch = 1
while True:
    tStart = time.time()
    frame = picam2.capture_array()

    # Process the frame
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.putText(frame, str(int(fps)) + ' FPS', pos, font, height, myColor, weight)
    lowerBound = np.array([hueLow, satLow, valLow])
    upperBound = np.array([hueHigh, satHigh, valHigh])
    myMask = cv2.inRange(frameHSV, lowerBound, upperBound)
    myMaskSmall = cv2.resize(myMask, (int(dispW / 2), int(dispH / 2)))
    myObject = cv2.bitwise_and(frame, frame, mask=myMask)
    myObjectSmall = cv2.resize(myObject, (int(dispW / 2), int(dispH / 2)))

    contours, _ = cv2.findContours(myMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    smoothed_x, smoothed_y = dispW / 2, dispH / 2
    alpha = 0.7

    frame_count += 1 # Could be another debugging for troubleshooting
    if len(contours) > 0:
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        contour = contours[0]
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
        if frame_count % 1 == 0:
            frame_count = 0
            if track == 1:
                error = ((x + w / 2)) - dispW / 2
                pan -= error / 70
                pan = max(50, min(130, pan))  # Clamp values
                if abs(error) > 35:
                    set_angle(pan_1, pan)
                #print("Pan:", pan)
                #print(y + h/2)
                #print(dispH/2) 
                tiltError = (y + h / 2) - dispH / 2
                tilt += tiltError / 70
                print("Tilt:", tilt)
                tilt = max(50, min(130, tilt))  # Clamp values
                if abs(tiltError) > 35:
                    set_angle(tilt_1, tilt)
                if launch <= 3 and (abs(error) + abs(tiltError) < 25):  
			# Move the servo Backward(ignore the Forward) for 0.3 seconds
                    set_servo_pulse(SERVO_PIN, FORWARD_PULSE, 0.8)
                    # Wait for 0.2 seconds
                    time.sleep(0.2)
                    # Move the servo forward(ignore the Backward) for 0.3 seconds
                    set_servo_pulse(SERVO_PIN, BACKWARD_PULSE, 0.9)
                    # Wait for 0.3 seconds
                    time.sleep(0.3)
                    launch += 1 

                    
    # Display results and to break, press q
    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', myMaskSmall)
    cv2.imshow('My Object', myObjectSmall)
    if cv2.waitKey(1) == ord('q'): 
        break
	
    tEnd = time.time()
    loopTime = tEnd - tStart
    fps = 0.9 * fps + 0.1 * (1 / loopTime) # Adjusted fps for the picam to be able to handle

# Cleanup
cv2.destroyAllWindows()
pi.set_servo_pulsewidth(pan_1, 0)  # Stop PWM for pan servo
pi.set_servo_pulsewidth(tilt_1, 0)  # Stop PWM for tilt servo
pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Stop sending PWM for the Actuator
pi.stop()

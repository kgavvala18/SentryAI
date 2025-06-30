# SentryAI


|[![Demo video](images/thumbnail.png)](https://www.youtube.com/watch?v=zrQpIDj6HPc)|
|:--:|
| *Click for demo* |

The SentryAI project aims to make intelligent security systems with deterrence capabilities available to everyday citizens.
Many home and commercial security systems can detect intruders and send alerts, but in many cases law enforcement cant't arrive before some damage is already done. To address this issue we created a system that can surveil, detect, and deter threats in real time.

Our robotic sentry incorporates computer vision to detect observed threats and keep tracking them. The administrator would then be prompted to take defensive action send the appropriate directive to the system. When directed, the tracking system would launch rubber pellets or other non-lethals at the threat until it left the area. To demonstrate this concept in our prototype, we used an OpenCV color detection model to easily distinguish threats as blue colored targets and safely tested the track-and-target system using ping pong balls. 

![image1](images/IMG_1129.jpeg)

Key Parts Used: 

- Raspberry pi 4b+ single board computer - processing
- 2X Servo motors 20 KG 180deg - platform pan and tilt
- Microservo motor 9G continuous 360deg - Linear Actuator  
- Picamera V2 | 8-Megapixel camera module
- 2X 6V DC motors - 2-wheel projectile launcher
- 7.5V 6A wall power adapter - power supply
- Linear actuator 100 mm - projectile reloader


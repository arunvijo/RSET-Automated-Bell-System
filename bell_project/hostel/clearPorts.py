#this program will clear the ports on startup.

#import time
import RPi.GPIO as GPIO
#import os
#import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)

if __name__ == '__main__':
#	GPIO.output(relay_out,True) #setting relay out to high permanently
	GPIO.output(amp_out,False) #setting amp relay out to low permanently

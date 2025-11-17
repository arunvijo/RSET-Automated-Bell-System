#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
#GPIO.output(relay_out,True) #setting relay out to high permanently
GPIO.output(amp_out,True) #setting amp relay out to high permanently

if __name__ == '__main__':
	# Turn on Amplifier
	GPIO.output(amp_out,False) #setting amp relay out to low - switch ON

# This program will ring the bigben every half-an-hour, set a pin high
# for few seconds 

import time
import RPi.GPIO as GPIO
import os
import sys
import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configuration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
#GPIO.output(relay_out,True) #setting relay out to high permanently
GPIO.output(amp_out,True) #setting amp relay out to high permanently

if __name__ == '__main__':
        now = datetime.datetime.now()
	new_now = now + datetime.timedelta(minutes = 1)
	# Turn on Amplifier
	GPIO.output(amp_out,False) #setting amp relay out to low (on)
	# Ring the WestMinster Chime
	os.system('omxplayer --vol 600 --no-osd WestminsterChime.mp3')
	if (new_now.minute == 0):
        	for i in xrange (int(new_now.strftime("%I"))):
		    os.system('omxplayer --vol 600 --no-osd SingleBell.mp3')
	# Turn off Amplifier
	GPIO.output(amp_out,True) #setting amp relay out to high (off)

# This program will ring the bigben every half-an-hour, set a pin high
# for few seconds 

import RPi.GPIO as GPIO
import os
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configuration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
#GPIO.output(relay_out,True) #setting relay out to high permanently
GPIO.output(amp_out,False) #setting amp relay out to low permanently

if __name__ == '__main__':
	# Turn on Amplifier
	#time.sleep(38)
	GPIO.output(amp_out,True) #setting amp relay out to high (on)
	#time.sleep(20)
	# Ring the bell ring tone
	os.system('omxplayer --vol 600 --no-osd HostelBell.mp3')
	#for i in xrange (2):
		#time.sleep(1)
		#os.system('omxplayer --vol 600 --no-osd LongBell.mp3')
	# Turn off Amplifier
	GPIO.output(amp_out,False) #setting amp relay out to low (off)

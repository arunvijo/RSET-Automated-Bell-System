#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

import time
import RPi.GPIO as GPIO
import os
import sys
import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
#relay_out = 37 #pin 37 for relay output
amp_out = 40 #pin 40 for amplifier output
#GPIO.setup(relay_out, GPIO.OUT)
GPIO.setup(amp_out, GPIO.OUT)
#GPIO.output(relay_out,True) #setting relay out to high permanently
GPIO.output(amp_out,True) #setting amp relay out to high permanently

if __name__ == '__main__':
	now = datetime.datetime.now()
	#Do not ring if on Sunday
	#if (now.isoweekday() == 7) :
		#sys.exit(0)
	#Do not play if on First or Second Saturday
	#if (now.isoweekday() == 6 and now.day > 7 and now.day < 15) :
	#if (now.isoweekday() == 6 and now.day < 15) :
		#sys.exit(0)
	GPIO.output(amp_out,False) #setting amp relay out to low, switch ON
	time.sleep(2)
	#os.system('omxplayer -o local --vol 400 --no-osd 18.MP3')
	#os.system('omxplayer -o local --vol 400 --no-osd 19.MP3')
	os.system('omxplayer -o local --vol 400 --no-osd EnneKaiPidichuNadathunna.mp3')
	#os.system('omxplayer -o local --vol 400 --no-osd 19.MP3')
	#os.system('omxplayer -o local --vol 400 --no-osd Kenny01Joy.mp3')
	#os.system('omxplayer -o local --vol 400 --no-osd Kenny02Love.mp3')
	#os.system('omxplayer -o local --vol 400 --no-osd Kenny03Rain.mp3')
	#os.system('omxplayer -o local --vol 400 --no-osd Kenny02Love.mp3')
	#os.system('omxplayer -o local --vol 400 --no-osd Kenny01Joy.mp3')
	# Turn off Amplifier
	GPIO.output(amp_out,True) #setting amp relay out to high, switch OFF

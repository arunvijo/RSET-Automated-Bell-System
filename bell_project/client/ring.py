#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

import time
import RPi.GPIO as GPIO
import sys
import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configuration
relay_out = 37 #pin 37 for relay output
GPIO.setup(relay_out, GPIO.OUT)
GPIO.output(relay_out,True) #setting relay out to high permanently

if __name__ == '__main__':
	now = datetime.datetime.now()
	#Do not ring if on Sunday
	#if (now.isoweekday() == 7) :
		#sys.exit(0)
        #Uncomment one of the following
	#Do not play if on Second Saturday
	#if (now.isoweekday() == 6 and now.day > 7 and now.day < 15) :
	#Do not play if on First or Second Saturday
	if (now.isoweekday() == 6 and now.day < 15) :
		sys.exit(0)
	if str(sys.argv[1]) == 'S':
		t = 2
	else :
		t = 5
	GPIO.output(relay_out,False) #setting relay out to high permanently
	time.sleep(t)
	GPIO.output(relay_out,True)

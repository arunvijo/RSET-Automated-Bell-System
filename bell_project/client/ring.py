#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

#import sys
#try:
#    # Try to import the real library
#    import RPi.GPIO
#except (ImportError, RuntimeError):
#    # If it fails (i.e., we're on the VM), inject the fake library
#    print("<<< Not on a Pi. Injecting fake RPi.GPIO module. >>>")
#    import fake_rpi
#    sys.modules['RPi'] = fake_rpi.RPi
#    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO


import time
import RPi.GPIO as GPIO
import sys
import datetime

# --- GPIO SETUP ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configuration
relay_out = 37 #pin 37 for relay output
GPIO.setup(relay_out, GPIO.OUT)
GPIO.output(relay_out,True) #setting relay out to high permanently (OFF)

if __name__ == '__main__':
    print("[ring.py] Script started.")
    now = datetime.datetime.now()
    
    #Do not play if on First or Second Saturday
    if (now.isoweekday() == 6 and now.day < 15) :
        print("[ring.py] First or Second Saturday, exiting.")
        sys.exit(0)
    
    # Determine duration
    try:
        bell_type = str(sys.argv[1])
        if bell_type == 'S':
            t = 2  # Short bell
        else :
            t = 5  # Long bell
    except IndexError:
        # Default to short bell if no argument is provided
        t = 2

    # --- RING BELL ---
    print(f"[ring.py] Ringing bell for {t} seconds (Pin {relay_out})")
    GPIO.output(relay_out,False) #setting relay out to low (ON)
    time.sleep(t)
    GPIO.output(relay_out,True) #setting relay out to high (OFF)
    print(f"[ring.py] Bell finished ringing.")

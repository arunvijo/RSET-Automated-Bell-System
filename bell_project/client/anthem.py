#this program will ring the bell, set a pin high for few seconds 
# add pins for ringing bell

import time
import RPi.GPIO as GPIO
import os
import sys
import datetime

# --- GPIO SETUP ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #setting board configaration
amp_out = 40 #pin 40 for amplifier output
GPIO.setup(amp_out, GPIO.OUT)
GPIO.output(amp_out,True) #setting amp relay out to high permanently (OFF)

if __name__ == '__main__':
    print("[anthem.py] Cron job started.")
    now = datetime.datetime.now()
    
    #Do not ring if on Sunday
    if (now.isoweekday() == 7) :
        print("[anthem.py] Sunday, exiting.")
        sys.exit(0)
    #Do not play if on First or Second Saturday
    if (now.isoweekday() == 6 and now.day < 15) :
        print("[anthem.py] First or Second Saturday, exiting.")
        sys.exit(0)
        
    # --- AMPLIFIER ON ---
    print(f"[anthem.py] Turning Amplifier ON (Pin {amp_out})")
    GPIO.output(amp_out,False) #setting amp relay out to low - amp ON
    
    # Ring the bell first (using python3 -u for unbuffered logging)
    # This calls the ring.py script
    print("[anthem.py] Calling ring.py...")
    os.system(f"python3 -u ring.py {str(sys.argv[1])}")
    time.sleep(2)

    # --- ALTERNATING ANTHEM LOGIC ---
    if now.day % 2 == 0:
        # Even day: Play English Anthem
        print(f"[anthem.py] Day {now.day} (Even): Playing English Anthem")
        os.system('mpg123 -q RajagiriAnthemEnglish.mp3')
    else:
        # Odd day: Play Malayalam Anthem
        print(f"[anthem.py] Day {now.day} (Odd): Playing Malayalam Anthem")
        os.system('mpg123 -q RajagiriAnthemMalayalam.mp3')
    # --- END OF LOGIC ---

    # --- AMPLIFIER OFF ---
    time.sleep(1) # Small delay before turning off
    print(f"[anthem.py] Turning Amplifier OFF (Pin {amp_out})")
    GPIO.output(amp_out,True) #setting amp relay out to high - amp OFF
    print("[anthem.py] Cron job complete.")

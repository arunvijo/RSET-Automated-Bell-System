#!/usr/bin/env python3
import time
import os
import sys
import datetime

# Try to import RPi.GPIO, handle fallback for non-Pi environments
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO

# --- CONFIGURATION ---
AMP_PIN = 40
BELL_PIN = 37
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

def setup_gpio():
    """Sets up the board mode and pins."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # Initialize HIGH (Relays usually Active LOW)
    GPIO.setup(AMP_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(BELL_PIN, GPIO.OUT, initial=GPIO.HIGH)

def main():
    print(f"[{datetime.datetime.now()}] [anthem.py] Cron job started.")
    now = datetime.datetime.now()

    # --- 1. CHECK EXCLUSIONS ---
    # Do not ring if on Sunday (ISO Day 7)
    if now.isoweekday() == 7:
        print("[anthem.py] Sunday, exiting.")
        sys.exit(0)

    # Do not play if on First or Second Saturday
    # (Days 1-7 are 1st week, 8-14 are 2nd week)
    if now.isoweekday() == 6 and now.day < 15:
        print("[anthem.py] First or Second Saturday, exiting.")
        sys.exit(0)

    # Check command line args for duration (passed from client.py)
    # Default to Short (S) if not provided
    bell_type = sys.argv[1] if len(sys.argv) > 1 else 'S'
    duration = 5 if bell_type == 'L' else 2

    try:
        # --- 2. SETUP GPIO (Start of critical section) ---
        setup_gpio()

        # --- 3. AMPLIFIER ON ---
        print(f"[anthem.py] Turning Amplifier ON (Pin {AMP_PIN})")
        GPIO.output(AMP_PIN, GPIO.LOW) 
        time.sleep(1) # Warm up amp

        # --- 4. RING BELL (Inline Logic) ---
        # We do this here instead of calling ring.py to avoid GPIO conflicts
        print(f"[anthem.py] Ringing Bell for {duration} seconds (Pin {BELL_PIN})...")
        GPIO.output(BELL_PIN, GPIO.LOW) # Bell ON
        time.sleep(duration)
        GPIO.output(BELL_PIN, GPIO.HIGH) # Bell OFF
        time.sleep(2) # Pause between bell and song

        # --- 5. PLAY ANTHEM ---
        song_file = ""
        if now.day % 2 == 0:
            print(f"[anthem.py] Day {now.day} (Even): Playing English Anthem")
            song_file = "RajagiriAnthemEnglish.mp3"
        else:
            print(f"[anthem.py] Day {now.day} (Odd): Playing Malayalam Anthem")
            song_file = "RajagiriAnthemMalayalam.mp3"

        full_path = os.path.join(SCRIPT_PATH, song_file)
        
        # Check if file exists before playing
        if os.path.exists(full_path):
            os.system(f'mpg123 -q {full_path}')
        else:
            print(f"[anthem.py] !!! Error: File not found: {full_path}")

        # --- 6. AMPLIFIER OFF ---
        time.sleep(1) 
        print(f"[anthem.py] Turning Amplifier OFF (Pin {AMP_PIN})")
        GPIO.output(AMP_PIN, GPIO.HIGH)

    except KeyboardInterrupt:
        print("\n[anthem.py] Stopped by user.")
    except Exception as e:
        print(f"[anthem.py] Error occurred: {e}")
    finally:
        # --- 7. CLEANUP (Crucial!) ---
        # This ensures pins are released so client.py can use them later
        GPIO.cleanup()
        print("[anthem.py] GPIO Cleaned up. Job complete.")

if __name__ == '__main__':
    main()

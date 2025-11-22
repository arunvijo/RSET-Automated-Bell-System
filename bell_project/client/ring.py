#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import sys
import datetime
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
BELL_RELAY_PIN = 37
AMP_RELAY_PIN = 40
SHORT_BELL_DURATION = 2
LONG_BELL_DURATION = 5

# -----------------------------
# GPIO SETUP
# -----------------------------
def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BELL_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(AMP_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    print("[ring.py] GPIO pins initialized. Relays are OFF.")

# -----------------------------
# RING BELL FUNCTION
# -----------------------------
def ring_bell(duration_seconds):
    print(f"[ring.py] Turning Amplifier ON (Pin {AMP_RELAY_PIN})")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
    time.sleep(1)
    print(f"[ring.py] Ringing Bell for {duration_seconds}s (Pin {BELL_RELAY_PIN})")
    GPIO.output(BELL_RELAY_PIN, GPIO.LOW)
    time.sleep(duration_seconds)
    GPIO.output(BELL_RELAY_PIN, GPIO.HIGH)
    time.sleep(1)
    print(f"[ring.py] Turning Amplifier OFF (Pin {AMP_RELAY_PIN})")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)

# -----------------------------
# MAIN SCRIPT
# -----------------------------
def main():
    setup_gpio()
    print("[ring.py] Script started.")

    now = datetime.datetime.now()

    # Do not ring on First or Second Saturday
    if now.isoweekday() == 6 and now.day < 15:
        print("[ring.py] First or Second Saturday, exiting.")
        GPIO.cleanup()
        sys.exit(0)

    # Determine bell duration
    try:
        bell_type = str(sys.argv[1]).upper()
        duration = SHORT_BELL_DURATION if bell_type == 'S' else LONG_BELL_DURATION
    except IndexError:
        duration = SHORT_BELL_DURATION

    # Ring the bell
    try:
        ring_bell(duration)
    except Exception as e:
        print(f"[ring.py] ERROR while ringing bell: {e}")
    finally:
        GPIO.cleanup()

    print("[ring.py] Bell finished ringing.")

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()

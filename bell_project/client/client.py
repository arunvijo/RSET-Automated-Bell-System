import requests
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os

# --- (1) CONFIGURE THESE SETTINGS ---
# This MUST match the 'block_name' in the server's database (e.g., 'main', 'ke', 'pg')
MY_BLOCK_NAME = "main"

# This MUST be the static IP of your Django server
SERVER_IP = "192.168.11.218"

# The GPIO pins connected to your relays. BOARD numbering refers to the physical pin numbers.
# Based on your readme.txt, pin 37 is for the bell, pin 40 is for the amplifier.
GPIO.setmode(GPIO.BOARD)
BELL_RELAY_PIN = 37
AMP_RELAY_PIN = 40

# How long to ring for short and long bells (in seconds)
SHORT_BELL_DURATION = 2
LONG_BELL_DURATION = 5
# --- END OF CONFIGURATION ---


# --- Global Variables ---
SCHEDULE = []
# A set to keep track of bells that have already been rung today to prevent double-ringing
RUNG_BELLS_TODAY = set()
LAST_SCHEDULE_FETCH_DATE = None
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

def setup_gpio():
    """Initializes GPIO pins."""
    GPIO.setwarnings(False)
    GPIO.setup(BELL_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH) # HIGH means relay is OFF
    GPIO.setup(AMP_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # HIGH means relay is OFF
    print("GPIO pins initialized. Relays are OFF.")

def fetch_schedule_from_server():
    """Fetches the complete schedule from the Django REST API."""
    global SCHEDULE, LAST_SCHEDULE_FETCH_DATE
    
    api_url = f"http://{SERVER_IP}:80/api/schedule/{MY_BLOCK_NAME}/"
    print(f"[{datetime.now()}] Attempting to fetch schedule from: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status() # Raises an error for bad status codes
        
        SCHEDULE = response.json().get('bells', [])
        LAST_SCHEDULE_FETCH_DATE = datetime.now().date()
        RUNG_BELLS_TODAY.clear() # Reset the rung bells for the new day's schedule
        
        print(f"[{datetime.now()}] Successfully fetched schedule for '{MY_BLOCK_NAME}'. Found {len(SCHEDULE)} bell times.")
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] !!! FAILED to fetch schedule: {e}. Will retry later.")
        # If it fails, we keep the old schedule and try again on the next day.
        SCHEDULE = []

def ring_bell(duration_seconds):
    """Activates the relays to ring the physical bell."""
    print(f"    - Ringer: Turning Amplifier ON (Pin {AMP_RELAY_PIN}).")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW) # LOW = ON
    time.sleep(1) # Give the amp a moment to power up

    print(f"    - Ringer: Ringing Bell for {duration_seconds}s (Pin {BELL_RELAY_PIN}).")
    GPIO.output(BELL_RELAY_PIN, GPIO.LOW) # LOW = ON
    time.sleep(duration_seconds)
    GPIO.output(BELL_RELAY_PIN, GPIO.HIGH) # HIGH = OFF
    
    time.sleep(1)
    print(f"    - Ringer: Turning Amplifier OFF (Pin {AMP_RELAY_PIN}).")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH) # HIGH = OFF

def play_anthem():
    """Plays the Rajagiri anthem MP3 file."""
    print(f"    - Anthem Player: Turning Amplifier ON.")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
    time.sleep(1)
    
    anthem_path = os.path.join(SCRIPT_PATH, "RajagiriAnthemEnglish.mp3")
    print(f"    - Anthem Player: Playing anthem file at {anthem_path}")
    # Using mpg123 as it's more reliable than omxplayer in scripts
    os.system(f"mpg123 -q {anthem_path}")
    
    print(f"    - Anthem Player: Turning Amplifier OFF.")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)

def check_and_ring_bells():
    """The core logic, checks the current time against the schedule."""
    global RUNG_BELLS_TODAY, LAST_SCHEDULE_FETCH_DATE

    now = datetime.now()
    # Check if it's a new day (e.g., past midnight). If so, fetch a fresh schedule.
    if now.date() != LAST_SCHEDULE_FETCH_DATE:
        print(f"\n[{now}] It's a new day! Fetching fresh schedule from server...")
        fetch_schedule_from_server()
    
    # Get current day and time FOR EACH CHECK
    current_day_str = now.strftime('%A').lower() # e.g., 'friday'
    current_time_str = now.strftime('%H:%M')     # e.g., '15:18'
    
    for bell in SCHEDULE:
        bell_time = bell['time'][:5] # Get 'HH:MM' from 'HH:MM:SS'
        
        # Check 1: Is it the right day for this bell to ring?
        is_today = bell.get(current_day_str, False)
        
        # Check 2: Is it the right time?
        is_time_now = (bell_time == current_time_str)
        
        # Check 3: Have we already rung for this exact time today?
        has_already_rung = bell_time in RUNG_BELLS_TODAY
        
        if is_today and is_time_now and not has_already_rung:
            print(f"\n[{now}] MATCH FOUND! Time to ring bell for {bell_time}.")
            
            duration = LONG_BELL_DURATION if bell['is_long'] else SHORT_BELL_DURATION
            ring_bell(duration)
            
            if bell['play_anthem']:
                print(f"    - Scheduler: Anthem scheduled. Playing after bell.")
                time.sleep(2)
                play_anthem()
            
            # Mark this time as "rung" for today to prevent duplicates
            RUNG_BELLS_TODAY.add(bell_time)
            print(f"[{now}] Action complete for {bell_time}.")
            break # Stop checking other bells for this minute.

if __name__ == "__main__":
    setup_gpio()
    
    print("--- RSET Automated Bell Client ---")
    print("Waiting for network to stabilize on boot...")
    time.sleep(15) # Wait for network connection
    
    # Fetch the schedule for the first time
    fetch_schedule_from_server()
    
    print("\nStarting main loop. Client is now active and monitoring the time.")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            check_and_ring_bells()
            time.sleep(1) # Check the time every second
            
    except KeyboardInterrupt:
        print("\nUser interrupted. Shutting down.")
    finally:
        # This ensures the GPIO pins are safely cleaned up on exit
        GPIO.cleanup()
        print("GPIO cleanup complete. Goodbye.")


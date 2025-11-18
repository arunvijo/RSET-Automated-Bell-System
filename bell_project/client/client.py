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


import requests
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os

# --- (1) CONFIGURE THESE SETTINGS ---
MY_BLOCK_NAME = "main"
SERVER_IP = "192.168.11.218"
#SERVER_IP = "127.0.0.1"
GPIO.setmode(GPIO.BOARD)
BELL_RELAY_PIN = 37
AMP_RELAY_PIN = 40
SHORT_BELL_DURATION = 2
LONG_BELL_DURATION = 5
# --- END OF CONFIGURATION ---

# --- Global Variables ---
SCHEDULE = []
RUNG_BELLS_TODAY = set()
LAST_SCHEDULE_FETCH_DATE = None
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setup(BELL_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(AMP_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    print("GPIO pins initialized. Relays are OFF.")

def generate_crontab(schedule, profile_name):
    global SCRIPT_PATH, MY_BLOCK_NAME
    print(f"    - CronGen: Generating new crontab from {len(schedule)} bell entries...")
    
    # Add the profile name as a comment at the top of the cron file
    cron_lines = [f"# Current active profile: {profile_name}"]

    for bell in schedule:
        try:
            bell_time_obj = datetime.strptime(bell['time'], '%H:%M:%S')
            minute = bell_time_obj.strftime('%M').lstrip('0') or '0'
            hour = bell_time_obj.strftime('%H').lstrip('0') or '0'
        except ValueError:
            print(f"    - CronGen: Skipping invalid time format: {bell['time']}")
            continue

        days_list = []
        if bell.get('sunday', False): days_list.append(0)
        if bell.get('monday', False): days_list.append(1)
        if bell.get('tuesday', False): days_list.append(2)
        if bell.get('wednesday', False): days_list.append(3)
        if bell.get('thursday', False): days_list.append(4)
        if bell.get('friday', False): days_list.append(5)
        if bell.get('saturday', False): days_list.append(6)
        
        if not days_list:
            continue
        
        day_str = ",".join(map(str, days_list))

        bell_type = 'L' if bell.get('is_long', False) else 'S'
        script_to_run = "anthem.py" if bell.get('play_anthem', False) else "ring.py"
        
        # Pipe output to systemd-cat for logging via journalctl
        command = f"(cd {SCRIPT_PATH}; python3 -u {script_to_run} {bell_type}) 2>&1 | /usr/bin/systemd-cat -t 'bell-cron-job' -p info"
        
        cron_line = f"{minute} {hour} * * {day_str} {command}"
        cron_lines.append(cron_line)

    crontab_content = "\n".join(cron_lines)
    temp_cron_file = os.path.join(SCRIPT_PATH, "bell_crontab.tmp")
    
    try:
        with open(temp_cron_file, "w") as f:
            f.write(crontab_content + "\n")
        
        os.system(f"crontab {temp_cron_file}")
        os.remove(temp_cron_file)
        print(f"[{datetime.now()}] Successfully applied new crontab with {len(cron_lines) - 1} jobs.")
        
    except Exception as e:
        print(f"[{datetime.now()}] !!! FAILED to generate or apply crontab: {e}")

def fetch_schedule_from_server():
    global SCHEDULE, LAST_SCHEDULE_FETCH_DATE, MY_BLOCK_NAME

    print(f"[{datetime.now()}] Fetching schedule from API...")
    api_url = f"http://{SERVER_IP}:80/api/schedule/{MY_BLOCK_NAME}/"
#    api_url = f"http://{SERVER_IP}:8000/api/schedule/{MY_BLOCK_NAME}/"

    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()

        data = response.json()
        SCHEDULE = data.get('bells', [])
        profile_name = data.get('name', MY_BLOCK_NAME) # Get profile name, fallback to block name
        LAST_SCHEDULE_FETCH_DATE = datetime.now().date()
        RUNG_BELLS_TODAY.clear()

        print(f"[{datetime.now()}] Successfully fetched schedule '{profile_name}'. Found {len(SCHEDULE)} bell times.")
        
        generate_crontab(SCHEDULE, profile_name) 

    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] !!! FAILED to fetch schedule: {e}.")
        SCHEDULE = []

def ring_bell(duration_seconds):
    print(f"    - Ringer: Turning Amplifier ON (Pin {AMP_RELAY_PIN}).")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
    time.sleep(1)
    print(f"    - Ringer: Ringing Bell for {duration_seconds}s (Pin {BELL_RELAY_PIN}).")
    GPIO.output(BELL_RELAY_PIN, GPIO.LOW)
    time.sleep(duration_seconds)
    GPIO.output(BELL_RELAY_PIN, GPIO.HIGH)
    time.sleep(1)
    print(f"    - Ringer: Turning Amplifier OFF (Pin {AMP_RELAY_PIN}).")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)

def play_anthem():
    print(f"    - Anthem Player: Turning Amplifier ON.")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
    time.sleep(1)
    anthem_path = os.path.join(SCRIPT_PATH, "RajagiriAnthemEnglish.mp3")
    print(f"    - Anthem Player: Playing anthem file at {anthem_path}")
    os.system(f"mpg123 -q {anthem_path}") # Using mpg123
    print(f"    - Anthem Player: Turning Amplifier OFF.")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)

def turn_amp_on():
    print("    - Command: Turning Amplifier ON.")
    GPIO.output(AMP_RELAY_PIN, GPIO.LOW)

def turn_amp_off():
    print("    - Command: Turning Amplifier OFF.")
    GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)

def check_for_server_commands():
    print(f"[{datetime.now()}] Checking for real-time commands...")
    command_api_url = f"http://{SERVER_IP}:80/api/command/check/"
#    command_api_url = f"http://{SERVER_IP}:8000/api/command/check/"
    try:
        response = requests.get(command_api_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'command_found':
            command = data.get('command')
            print(f"\n[{datetime.now()}] Received Command from Server: {command}")

            if command == 'TEST_BELL':
                ring_bell(SHORT_BELL_DURATION)
            elif command == 'AMP_ON':
                turn_amp_on()
            elif command == 'AMP_OFF':
                turn_amp_off()
            elif command == 'FETCH_SCHEDULE':
                print(f"[{datetime.now()}] Received command to fetch new schedule.")
                fetch_schedule_from_server()
            
            print(f"[{datetime.now()}] Action complete for command {command}.")
        else:
            print(f"[{datetime.now()}] No new commands found.")

    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] !!! FAILED to check for commands: {e}")
        pass

if __name__ == "__main__":
    setup_gpio()

    print("--- RSET Automated Bell Client ---")
    print("Waiting for network to stabilize on boot...")
    time.sleep(15)
    
    # Fetch the schedule once on startup
    fetch_schedule_from_server() 

    print("\nStarting main loop. Client is now active.")
    print("Scheduled bells are managed by cron.")
    print("Press Ctrl+C to exit.")

    try:
        while True:
            print("--- Client Polling Loop ---")
            # Only check for non-schedule commands. 
            # Schedule fetching is now triggered by a command.
            check_for_server_commands()
            print(f"--- Poll complete. Sleeping for 60 seconds... ---")
            time.sleep(60) 
            
    except KeyboardInterrupt:
        print("\nUser interrupted. Shutting down.")
        
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete. Goodbye.")

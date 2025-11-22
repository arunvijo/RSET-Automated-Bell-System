#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime
import requests

# Try to import RPi.GPIO, handle fallback for non-Pi environments
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO

# --- (1) CONFIGURE THESE SETTINGS ---
MY_BLOCK_NAME = "main"
SERVER_IP = "192.168.11.218"
# SERVER_IP = "127.0.0.1"

# Pin Configuration
BELL_RELAY_PIN = 37
AMP_RELAY_PIN = 40

# Timing Configuration
SHORT_BELL_DURATION = 2
LONG_BELL_DURATION = 5

# --- Global Variables ---
SCHEDULE = []
RUNG_BELLS_TODAY = set()
LAST_SCHEDULE_FETCH_DATE = None
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


def setup_pins_temporarily():
    """
    Sets up GPIO mode and pins just for the current operation.
    This is called inside action functions, not at global startup.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # We set initial to HIGH because your relays are likely Active LOW
    GPIO.setup(BELL_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(AMP_RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)


def generate_crontab(schedule, profile_name):
    global SCRIPT_PATH, MY_BLOCK_NAME
    print(f"    - CronGen: Generating new crontab from {len(schedule)} bell entries...")
    
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
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        SCHEDULE = data.get('bells', [])
        profile_name = data.get('name', MY_BLOCK_NAME)
        LAST_SCHEDULE_FETCH_DATE = datetime.now().date()
        RUNG_BELLS_TODAY.clear()
        
        print(f"[{datetime.now()}] Successfully fetched schedule '{profile_name}'. Found {len(SCHEDULE)} bell times.")
        generate_crontab(SCHEDULE, profile_name)
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] !!! FAILED to fetch schedule: {e}.")
        # We do NOT clear the schedule here to keep the old one if internet fails
        

def ring_bell(duration_seconds):
    """
    Rings the bell.
    Uses try/finally to ensure pins are ALWAYS released, 
    even if the code crashes halfway through.
    """
    try:
        setup_pins_temporarily()
        
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
        
    except Exception as e:
        print(f"    - Error in ring_bell: {e}")
        
    finally:
        # CRITICAL: Release the pins so ring.py can use them later
        GPIO.cleanup()
        print("    - Ringer: GPIO Cleaned up.")


def play_anthem():
    try:
        setup_pins_temporarily()

        print(f"    - Anthem Player: Turning Amplifier ON.")
        GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
        time.sleep(1)

        anthem_path = os.path.join(SCRIPT_PATH, "RajagiriAnthemEnglish.mp3")
        print(f"    - Anthem Player: Playing anthem file at {anthem_path}")
        
        # Use mpg123 to play audio
        os.system(f"mpg123 -q {anthem_path}")

        print(f"    - Anthem Player: Turning Amplifier OFF.")
        GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)
        
    except Exception as e:
        print(f"    - Error playing anthem: {e}")
        
    finally:
        GPIO.cleanup()


def turn_amp_on():
    try:
        setup_pins_temporarily()
        print("    - Command: Turning Amplifier ON (Test).")
        GPIO.output(AMP_RELAY_PIN, GPIO.LOW)
        time.sleep(5) # Keep it on for 5 seconds for testing
        GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()


def turn_amp_off():
    try:
        setup_pins_temporarily()
        print("    - Command: Turning Amplifier OFF.")
        GPIO.output(AMP_RELAY_PIN, GPIO.HIGH)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()


def check_for_server_commands():
    print(f"[{datetime.now()}] Checking for real-time commands...")
    command_api_url = f"http://{SERVER_IP}:80/api/command/check/"
    
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
    print("--- RSET Automated Bell Client ---")
    print("Waiting for network to stabilize on boot...")
    time.sleep(15)

    # Initial Schedule Fetch
    fetch_schedule_from_server()

    # Main Loop
    while True:
        try:
            # Check for commands every 5 seconds
            check_for_server_commands()
            
            # Check if we need to refresh the schedule (Daily refresh)
            if LAST_SCHEDULE_FETCH_DATE != datetime.now().date():
                print("New day detected. Refreshing schedule...")
                fetch_schedule_from_server()
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nUser stopped the service.")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

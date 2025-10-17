import requests
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
# The client device needs to know its own name (e.g., 'main', 'pg', 'ke')
# This should be configured on each Raspberry Pi.
MY_BLOCK_NAME = "main"

# The IP address of the main Django server.
# <-- IMPORTANT: CHANGE THIS TO YOUR SERVER'S ACTUAL IP ADDRESS
SERVER_IP = "127.0.0.1" 

# How many seconds to wait between checking for real-time commands
POLL_INTERVAL = 10

# --- AUTO-CONFIGURED PATHS ---
# Path to the directory where this script is located.
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
# API URLs
SCHEDULE_API_URL = f"http://{SERVER_IP}:8000/api/schedule/{MY_BLOCK_NAME}/"
COMMAND_API_URL = f"http://{SERVER_IP}:8000/api/command/check/"
# --- END CONFIGURATION ---


# =========== SCHEDULE RELATED FUNCTIONS (Original Logic) ===========

def get_schedule():
    """Fetches the schedule from the Django server's REST API."""
    try:
        print(f"[{datetime.now()}] Fetching schedule from {SCHEDULE_API_URL}")
        response = requests.get(SCHEDULE_API_URL, timeout=10)
        response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
        print(f"[{datetime.now()}] Successfully fetched schedule.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ERROR: Could not fetch schedule. {e}")
        return None

def create_cron_job(bell):
    """Generates a crontab line for a single bell."""
    hour = bell['time'].split(':')[0]
    minute = bell['time'].split(':')[1]
    
    days_map = {
        'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3, 
        'thursday': 4, 'friday': 5, 'saturday': 6
    }
    
    active_days = []
    for day, day_num in days_map.items():
        if bell.get(day, False):
            active_days.append(str(day_num))
            
    if not active_days:
        return "" # Don't create a job if no days are active

    days_str = ",".join(active_days)
    
    # Use mpg123 for playing sound as it is more reliable for crontab
    sound_file = "19.MP3" if bell['is_long'] else "18.MP3"
    command = (
        f"python {SCRIPT_PATH}/ampOn.py; "
        f"mpg123 -q {SCRIPT_PATH}/{sound_file}; "
        f"python {SCRIPT_PATH}/ampOff.py"
    )

    if bell['play_anthem']:
        anthem_command = (
            f"; sleep 2; python {SCRIPT_PATH}/ampOn.py; "
            f"mpg123 -q {SCRIPT_PATH}/RajagiriAnthemEnglish.mp3; "
            f"python {SCRIPT_PATH}/ampOff.py"
        )
        command += anthem_command
        
    return f"{minute} {hour} * * {days_str} {command}\n"

def apply_schedule(schedule):
    """Writes the new schedule to the system's crontab."""
    if not schedule or 'bells' not in schedule:
        print(f"[{datetime.now()}] Invalid or empty schedule received. No changes made.")
        return

    print(f"[{datetime.now()}] Applying new schedule to crontab...")
    os.system("crontab -r") # Clear existing cron jobs
    
    crontab_content = ""
    for bell in schedule['bells']:
        crontab_content += create_cron_job(bell)

    if crontab_content:
        temp_cron_file = os.path.join(SCRIPT_PATH, "new_cron.tmp")
        with open(temp_cron_file, "w") as f:
            f.write(crontab_content)
        
        os.system(f"crontab {temp_cron_file}")
        os.remove(temp_cron_file)
        print(f"[{datetime.now()}] New schedule with {len(schedule['bells'])} bells has been applied.")
    else:
        print(f"[{datetime.now()}] No bells found in the schedule. Crontab cleared.")


# =========== REAL-TIME COMMAND FUNCTIONS (New Logic) ===========

def execute_realtime_command(command):
    """Executes a real-time command received from the server."""
    print(f"[{datetime.now()}] Received real-time command: {command}")
    
    if command == "AMP_ON":
        print("Executing: Turn Amplifier ON")
        os.system(f"python {SCRIPT_PATH}/ampOn.py")
        
    elif command == "AMP_OFF":
        print("Executing: Turn Amplifier OFF")
        os.system(f"python {SCRIPT_PATH}/ampOff.py")
        
    elif command == "TEST_BELL":
        print("Executing: Ring Test Bell (Short)")
        # Sequence: Amp ON -> Wait -> Ring Short Bell -> Wait -> Amp OFF
        full_command = (
            f"python {SCRIPT_PATH}/ampOn.py; sleep 1; "
            f"python {SCRIPT_PATH}/ring.py S; sleep 1; "
            f"python {SCRIPT_PATH}/ampOff.py"
        )
        os.system(full_command)
        
    else:
        print(f"[{datetime.now()}] Unknown command received: {command}")

def command_polling_loop():
    """The main polling loop that runs forever to check for real-time commands."""
    print(f"[{datetime.now()}] Starting real-time command listener...")
    print(f"[{datetime.now()}] Polling {COMMAND_API_URL} every {POLL_INTERVAL} seconds.")

    while True:
        try:
            response = requests.get(COMMAND_API_URL, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'command_found':
                    command_to_run = data.get('command')
                    execute_realtime_command(command_to_run)
            else:
                # Log server errors but continue running
                print(f"[{datetime.now()}] Warning: Server returned status code {response.status_code}")

        except requests.exceptions.RequestException:
            # Log network errors but continue running
            # This is expected if the network is temporarily down
            pass # We don't print an error every 10s to avoid filling the log
        
        time.sleep(POLL_INTERVAL)


# =========== MAIN EXECUTION BLOCK ===========

if __name__ == "__main__":
    # Wait on boot to ensure the network is fully initialized
    print(f"[{datetime.now()}] Client script starting. Waiting for network...")
    time.sleep(20) 
    
    # 1. Perform the initial schedule setup
    schedule_data = get_schedule()
    apply_schedule(schedule_data)
    
    # 2. Start the infinite loop to listen for real-time commands
    command_polling_loop()

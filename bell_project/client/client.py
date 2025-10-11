import requests
import json
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
# The client device needs to know its own name (e.g., 'main', 'pg', 'ke')
# This should be configured on each Raspberry Pi.
MY_BLOCK_NAME = "main" 

# The IP address of the main Django server.
SERVER_IP = "127.0.0.1" # <-- IMPORTANT: CHANGE THIS TO YOUR SERVER'S ACTUAL IP ADDRESS

# Path to the directory where this script is located.
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
# --- END CONFIGURATION ---

def get_schedule():
    """Fetches the schedule from the Django server's REST API."""
    api_url = f"http://{SERVER_IP}:8000/api/schedule/{MY_BLOCK_NAME}/"
    try:
        print(f"[{datetime.now()}] Fetching schedule from {api_url}")
        response = requests.get(api_url, timeout=10)
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
    
    # Command to turn on amp, play sound, then turn off amp
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

    # Start with a clean slate
    os.system("crontab -r")
    
    crontab_content = ""
    for bell in schedule['bells']:
        crontab_content += create_cron_job(bell)

    if crontab_content:
        # Write the new cron jobs to a temporary file
        temp_cron_file = os.path.join(SCRIPT_PATH, "new_cron.tmp")
        with open(temp_cron_file, "w") as f:
            f.write(crontab_content)
        
        # Load the new cron jobs into the system
        os.system(f"crontab {temp_cron_file}")
        os.remove(temp_cron_file)
        print(f"[{datetime.now()}] New schedule with {len(schedule['bells'])} bells has been applied.")
    else:
        print(f"[{datetime.now()}] No bells found in the schedule. Crontab cleared.")

if __name__ == "__main__":
    # Wait a few seconds on boot to ensure network is ready
    time.sleep(15) 
    
    schedule_data = get_schedule()
    apply_schedule(schedule_data)
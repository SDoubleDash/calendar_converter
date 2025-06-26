import subprocess
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from pathlib import Path
import os
import pytz
import orjson
import re
import time  # Import time module for adding pauses

# Initialize timezone
nycTz = pytz.timezone('America/New_York')

def str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

def create_events_from_data(data):
    events = []
    week = str_to_date(data["weekStarting"])

    for day in data["days"]:
        if day["netScheduledHours"] > 0:
            for shifts in day["payScheduledShifts"]:
                items = shifts["jobTransfers"]
                num_items = len(items)

                if num_items > 0:
                    for i in range(num_items):
                        if i == num_items - 1:
                            events.append({
                                "name": items[i]["job"]["name"],
                                "start": str_to_date(items[i]["time"]),
                                "end": str_to_date(shifts["end"])
                            })
                        else:
                            events.append({
                                "name": items[i]["job"]["name"],
                                "start": str_to_date(items[i]["time"]),
                                "end": str_to_date(items[i+1]["time"])
                            })
                else:
                    item = shifts
                    events.append({
                        "name": item["job"]["name"],
                        "start": str_to_date(item["start"]),
                        "end": str_to_date(item["end"])
                    })
    return events

def create_calendar(events):
    cal = Calendar()

    # some properties are required to be compliant
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')

    for e in events:
        event = Event()
        event.add("summary", e["name"])
        event.add("dtstart", e["start"].replace(tzinfo=nycTz))
        event.add("dtend", e["end"].replace(tzinfo=nycTz))
        event["uid"] = f'{e["name"]}/{e["start"]}/{e["end"]}@SBpythonScript'

        cal.add_component(event)

    return cal

def save_calendar_to_file(cal, filename):
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())

def combine_icals(directory, output_filename):
    # Initialize a master calendar
    master_cal = Calendar()
    master_cal.add('prodid', '-//My calendar product//example.com//')
    master_cal.add('version', '2.0')

    for filename in os.listdir(directory):
        if filename.endswith("_cal.ics"):
            with open(os.path.join(directory, filename), 'rb') as f:
                cal = Calendar.from_ical(f.read())
                for component in cal.subcomponents:
                    master_cal.add_component(component)

    # Save the master calendar to a file
    with open(os.path.join(directory, output_filename), 'wb') as f:
        f.write(master_cal.to_ical())

def extract_json_from_powershell_output(output):
    try:
        # Directly parse the JSON content from the output
        return orjson.loads(output)
    except orjson.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("JSON Content:", output)
    return None

def run_powershell_command(powershell_command):
    # Modify PowerShell command to output only the full content as plain text
    powershell_command += ' | ForEach-Object { $_.Content }'
    
    # Run the PowerShell command
    result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True)
    
    if result.returncode == 0:
        return extract_json_from_powershell_output(result.stdout)
    else:
        print("PowerShell command failed with error:")
        print(result.stderr)
    return None

def main():
    current_path = Path(__file__).parent.resolve()

    # Load the PowerShell command from the sb.txt file
    with open(current_path / "sb.txt", 'r') as f:
        powershell_command = f.read()

    # Extract the initial start date from the PowerShell command
    start_date_match = re.search(r'mySchedules/(\d{4}-\d{2}-\d{2})', powershell_command)
    if not start_date_match:
        print("Failed to extract start date from the PowerShell command.")
        return

    # Parse the initial start date
    start_date = datetime.strptime(start_date_match.group(1), '%Y-%m-%d')

    # Loop through weeks
    while True:
        date_str = start_date.strftime('%Y-%m-%d')

        # Update the date in the PowerShell command
        updated_command = re.sub(r'mySchedules/\d{4}-\d{2}-\d{2}', f'mySchedules/{date_str}', powershell_command)
        updated_command = re.sub(r'id=\d{4}-\d{2}-\d{2}', f'id={date_str}', updated_command)

        # Run PowerShell command to fetch the data for the current week
        data = run_powershell_command(updated_command)
        events = create_events_from_data(data)

        if not events:
            print(f"No scheduled events for the week starting {date_str}. Exiting.")
            break
        else:
            print(f"Recording {len(events)} events for week starting {date_str}.")

        cal = create_calendar(events)
        save_calendar_to_file(cal, current_path / f'{date_str}_cal.ics')

        # Pause for a specified amount of time to avoid spamming the API
        time.sleep(5)  # Pause for 5 seconds, adjust as needed

        # Move to the next week
        start_date += timedelta(weeks=1)

    # After creating the individual ical files, combine them into a master file
    combine_icals(current_path, 'combined_calendar.ics')

if __name__ == "__main__":
    main()

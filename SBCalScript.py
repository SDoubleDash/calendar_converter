# imports
from icalendar import Calendar, Event
from datetime import datetime
from pathlib import Path
import os
import pytz
import orjson

# Initialize timezone
nycTz = pytz.timezone('America/New_York')

def str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

def load_json_file(filename):
    with open(filename, 'rb') as f:
        data = orjson.loads(f.read())
    return data

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

def main():
    current_path = Path(__file__).parent.resolve()
    data = load_json_file(current_path / "sb.txt")
    events = create_events_from_data(data)
    cal = create_calendar(events)
    week = str_to_date(data["weekStarting"])
    save_calendar_to_file(cal, current_path / f'{week.strftime("%Y-%m-%d")}_cal.ics')

if __name__ == "__main__":
    main()
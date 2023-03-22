# imports
from icalendar import Calendar, Event
from datetime import datetime
from pathlib import Path
import os
import pytz
import json

# init stuff
nycTz = pytz.timezone('America/New_York')

def str_to_date(str):
	return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')

# load the json file
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

f = open(os.path.join(__location__, "sb.txt"))
d = json.load(f)

# find all events
event_list = []
week = str_to_date(d["weekStarting"])

for day in d["days"]:
	if day["netScheduledHours"] > 0:
		items = day["payScheduledShifts"][0]["jobTransfers"]
		num_items = len(items)
		if num_items > 0:
			for i in range(num_items):
				if i == num_items - 1:
					event_list.append({
						"name": items[i]["job"]["name"],
						"start": str_to_date(items[i]["time"]),
						"end": str_to_date(day["payScheduledShifts"][0]["end"])
					})
				else:
					event_list.append({
						"name": items[i]["job"]["name"],
						"start": str_to_date(items[i]["time"]),
						"end": str_to_date(items[i+1]["time"])
					})
		else:
			item = day["payScheduledShifts"][0]
			event_list.append({
				"name": item["job"]["name"],
				"start": str_to_date(item["start"]),
				"end": str_to_date(item["end"])
			})

# init the calendar
cal = Calendar()

# some properties are required to be compliant
cal.add('prodid', '-//My calendar product//example.com//')
cal.add('version', '2.0')

for e in event_list:
	event = Event()
	event.add("summary", e["name"])
	event.add("dtstart", datetime(
		e["start"].year,
		e["start"].month,
		e["start"].day,
		e["start"].hour,
		e["start"].minute,
		e["start"].second,
		tzinfo=nycTz
	))
	event.add("dtend", datetime(
		e["end"].year,
		e["end"].month,
		e["end"].day,
		e["end"].hour,
		e["end"].minute,
		e["end"].second,
		tzinfo=nycTz
	))
	event["uid"] = f'{e["name"]}/{e["start"]}/{e["end"]}@SBpythonScript'

	cal.add_component(event)


c = open(os.path.join(__location__, f'{week.strftime("%Y-%m-%d")}_cal.ics'), 'wb')
c.write(cal.to_ical())


c.close()
f.close()
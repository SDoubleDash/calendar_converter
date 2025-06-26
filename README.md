# calendar_converter
converts the json output from sb schedule API endpoint and converts it into a .ics calendar file that can be imported into Google Calendars

1. create a file called sb.txt in the same folder as the python script
2. copy API request of mySchedules endpoint as Powershell and paste into sb.txt
3. pip install -r requirements.txt
4. run the python script
5. receive calendars files based on the first day of each week ("weekStarting") -> YYYY-MM-DD_cal.ics
6. after finding a week with no posted schedules the program will exit and compile all calendars into one file -> combined_calendar.ics

each event is given a uuid so importing the same calendar multiple times will not cause duplicates

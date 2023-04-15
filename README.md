# calendar_converter
converts the json output from sb schedule API endpoint and converts it into a .ics calendar file that can be imported into Google Calendars

1. create a file called sb.txt in the same folder as the python script
2. paste the API response of the mySchedules endpoint into a file
3. pip install -r requirements.txt
4. run the python script
5. receive calendar file based on the first day of that week ("weekStarting") -> YYYY-MM-DD_cal.ics

only works for one week at a time
each event is given a uuid so importing the same calendar multiple times will not cause duplicates

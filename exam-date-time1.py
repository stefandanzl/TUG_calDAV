import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get environment variables
cal_dav_url = os.getenv('CALDAV_URL')         
cal_dav_username = os.getenv('CALDAV_USERNAME')
cal_dav_password = os.getenv('CALDAV_PASSWORD')

def parse_date(date_string):
    d = datetime.strptime(date_string, '%Y-%m-%d')
    s = d.strftime('%Y%m%d')
    return s #datetime.strptime(date_string , '%Y-%m-%d')

# Load calendar data from JSON file
with open('excluded.json', mode='r',encoding="utf-8") as f:
    exclude_data = json.load(f)


# Load calendar data from JSON file
with open('calendar_data_long.json', mode='r',encoding="utf-8") as f:
    data = json.load(f)

# Create a CalDAV client session
session = requests.Session()
session.auth = (cal_dav_username, cal_dav_password)

# Iterate over the examOfferIndices and create events in CalDAV
for e in data['examOffers']:

    courseId = e["courseId"]
    courseName = e["courseName"]["value"]
    ok = True
    for i in exclude_data["array"]:
        if courseName == i:
            ok = False
        
    if ok:

        courseNumber = e["displayCourseNumber"]
        date = e["examDate"]["value"]
        start_time = e["examStart"]["value"]
        end_time = e["examEnd"]["value"]
        registered = e["registrationState"]

        d = date
        s = start_time
        e = end_time
        start_date = d[:4]+d[5:7]+d[8:10]+"T"+s[:2]+s[3:5]+s[6:8]
        end_date = d[:4]+d[5:7]+d[8:10]+"T"+e[:2]+e[3:5]+e[6:8]

        n = str(datetime.now) # 2023-02-18 19:32:41.910500

        d = datetime.now().strftime('%Y%m%d')
        t = datetime.now().strftime('%H%M%S')

        now = d+"T"+t+"Z"


        # Build iCalendar string for the event and encode it as UTF-8
        icalendar = f'''BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//ChatGPT//EN
BEGIN:VEVENT
SUMMARY:{courseName}
DESCRIPTION:{courseNumber}
DTSTART:{start_date}
DTEND:{end_date}
DTSTAMP:{now}
END:VEVENT
END:VCALENDAR'''.encode('utf-8')

        # Create the event in CalDAV
        print(icalendar)
        response = session.put(f'{cal_dav_url}/{courseId}.ics', data=icalendar)
        if response.status_code == 201:
            print(f'Event  created successfully')
        else:
            print(f'Error creating event : {response.content.decode()}')    

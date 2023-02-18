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


try:
    # Load calendar data from JSON file
    with open('excluded.json', mode='r',encoding="utf-8") as f:
        exclude_data = json.load(f)
except:
    print("no excluded course json file")

with open('calendar_date.json', mode='r',encoding="utf-8") as f:
    data = json.load(f)

# Create a CalDAV client session
session = requests.Session()
session.auth = (cal_dav_username, cal_dav_password)

# Iterate over the examOfferIndices and create events in CalDAV
for exam in data['examOfferIndices']:
    # Extract event data from exam object
    event_id = exam['id']
    summary = exam['courseName']
    
    ok = True
    for i in exclude_data["array"]:
        if summary == i:
            ok = False
        
    if ok:

    
        event_date = parse_date(exam['examDate']['value'])
        print(event_date)
        #start_date = exam['examDate']['value']
        end_date = event_date  # assuming that each event is a one-day event

        # Build iCalendar string for the event and encode it as UTF-8
        icalendar = f'''BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//ChatGPT//EN
BEGIN:VEVENT
SUMMARY:{summary}
DESCRIPTION:{event_id}
DTSTART;VALUE=DATE:{event_date}
DTEND;VALUE=DATE:{end_date}
END:VEVENT
END:VCALENDAR'''.encode('utf-8')

        # Create the event in CalDAV
        print(icalendar)
        response = session.put(f'{cal_dav_url}/{event_id}.ics', data=icalendar)
        if response.status_code == 201:
            print(f'Event {event_id} created successfully')
        else:
            print(f'Error creating event {event_id}: {response.content.decode()}')    

# hubscheduler.py
# Author: Zachary Robbins
# Simple program for finding availability in google calendar

import json
import pytz
import datetime

from flask import Flask, render_template

from app.calendarfunctions import get_events, get_free_calendars

# Create the application instance
app = Flask(__name__)


@app.route("/")
@app.route("/index")
def main():
    events = get_events()
    eventTuples = []

    if not events:
        return 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        eventTuples.append((start, event['summary']))

    tz = pytz.timezone('US/Eastern')
    start_time_block = tz.localize(datetime.datetime(2017, 11, 7, 21, 30))
    end_time_block = tz.localize(datetime.datetime(2017, 11, 7, 22))

    free_cal_dict = get_free_calendars(start_time_block, end_time_block)

    return render_template('test.html',
                    user="Zach",
                    data=json.dumps(free_cal_dict))

if __name__ == "__main__":
    app.run()

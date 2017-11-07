# hubscheduler.py
# Author: Zachary Robbins
# Simple program for finding availability in google calendar

import datetime
import json
import pytz

from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, DateTimeField
from wtforms.validators import DataRequired

from app.calendarfunctions import get_events, get_free_calendars

app = Flask(__name__)

class AvailabilityForm(Form):
    time_start = DateTimeField('Block Start', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S', description='Beginning of availability block')
    time_end = DateTimeField('Block End', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S', description='End of availability block')


@app.route('/', methods=['POST', 'GET'])
def main():
    # events = get_events()
    # event_tuples = []

    # if not events:
    #     return 'No upcoming events found.'
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     event_tuples.append((start, event['summary']))

    form = AvailabilityForm()
    if request.method == 'POST' and form.validate():
        return redirect(url_for(show_availability, time_start=form.time_start.data, time_end=form.time_end.data))
    print("Failed to render")
    return render_template('availabilityform.html', form=form)


@app.route('/availability')
def show_availability():
    start_time_block = request.args.get('time_start')
    end_time_block = request.args.get('time_end')
    print("start entered: " + start_time_block)
    print("end entered: " + end_time_block)
    tz = pytz.timezone('US/Eastern')
    # start_time_block = tz.localize(datetime.datetime(2017, 11, 7, 21, 30))
    # end_time_block = tz.localize(datetime.datetime(2017, 11, 7, 22))

    free_cal_dict = get_free_calendars(start_time_block, end_time_block)

    return render_template('test.html',
                           user="Zach",
                           data=json.dumps(free_cal_dict))

if __name__ == "__main__":
    app.run()

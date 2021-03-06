# hubscheduler.py
# Author: Zachary Robbins
# Simple program for finding availability in google calendar

from __future__ import print_function

import pytz

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, DateTimeField
from wtforms.validators import DataRequired

from calendarfunctions import get_free_calendars

app = Flask(__name__)


class AvailabilityForm(Form):
    time_start = DateTimeField('Time Block Start', validators=[DataRequired()],
                               format="%m/%d/%Y %I:%M %p", description='Beginning of availability block')
    time_end = DateTimeField('Time Block End', validators=[DataRequired()],
                             format="%m/%d/%Y %I:%M %p", description='End of availability block')


@app.route('/', methods=['POST','GET'])
def main():
    form = AvailabilityForm(request.form)

    if request.method == 'POST' and form.validate():
        tz = pytz.timezone('US/Eastern')
        time_block_start = tz.localize(form.time_start.data).isoformat()
        time_block_end = tz.localize(form.time_end.data).isoformat()

        return redirect(url_for('.show_availability',
                                time_start=time_block_start,
                                time_end=time_block_end))

    print("Failed to render: ", form.errors)
    return render_template('availabilityform.html',
                           form=form,
                           default_time=datetime.now(),
                           err_message="Make sure time block fields are filled out in "
                                       "the correct format as dictated by widget")


@app.route('/availability')
def show_availability():
    time_block_start = request.args.get('time_start')
    time_block_end = request.args.get('time_end')

    cal_dict = get_free_calendars(time_block_start, time_block_end)
    free_cal_dict = {key: val for key, val in cal_dict.items() if not val['busy']}

    return render_template('availability.html', free_cal_dict=free_cal_dict)


if __name__ == "__main__":
    app.run()

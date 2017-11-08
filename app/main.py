# hubscheduler.py
# Author: Zachary Robbins
# Simple program for finding availability in google calendar

import json
import pytz

from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, DateTimeField, IntegerField
from wtforms.validators import DataRequired

from app.calendarfunctions import get_free_calendars

app = Flask(__name__)


class AvailabilityForm(Form):
    time_start = DateTimeField('Time Block Start', validators=[DataRequired()],
                               format='%Y-%m-%d %H:%M', description='Beginning of availability block')
    time_end = DateTimeField('Time Block End', validators=[DataRequired()],
                             format='%Y-%m-%d %H:%M', description='End of availability block')


@app.route('/', methods=['POST','GET'])
def main():
    form = AvailabilityForm(request.form)

    # TODO: Write validator to make sure that you can't choose a timeblock of 0, and (if I can) add to jquery template

    if request.method == 'POST' and form.validate():
        tz = pytz.timezone('US/Eastern')
        time_block_start = tz.localize(form.time_start.data)
        time_block_end = tz.localize(form.time_end.data)

        return redirect(url_for('.show_availability',
                                time_start=time_block_start.isoformat(),
                                time_end=time_block_end.isoformat()))

    print("Failed to render: ", form.errors)
    return render_template('availabilityform.html',
                           form=form,
                           err_message="Make sure time block fields are filled out in correct format (%Y-%m-%d %H:%M)")


@app.route('/availability')
def show_availability():
    time_block_start = request.args.get('time_start')
    time_block_end = request.args.get('time_end')

    cal_dict = get_free_calendars(time_block_start, time_block_end)
    free_cal_dict = {key: val for key, val in cal_dict.items() if not val['busy']}

    return render_template('availability.html',
                           free_cal_dict = free_cal_dict)


if __name__ == "__main__":
    app.run()

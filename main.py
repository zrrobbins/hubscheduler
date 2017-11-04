# main.py
# Author: Zachary Robbins
# Simple scheduler for finding availability in google calendar

import json
from pprint import pprint
from datetime import datetime
from flask import Flask
from quickstart import get_events

app = Flask(__name__)


@app.route("/")
def main():
    events = get_events()
    eventTuples = []

    if not events:
        return 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        eventTuples.append((start, event['summary']))

    return json.dumps(eventTuples)

if __name__ == "__main__":
    app.run()

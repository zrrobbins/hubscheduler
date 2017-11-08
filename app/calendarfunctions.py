
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.hubscheduler-credentials/app-oauth-credentials.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'HubScheduler Google Calendar API Python'


def get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.hubscheduler-credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'app-oauth-credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_service():
    """
    Creates a Google Calendar API service object
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service


def get_calendar_id_list(service):
    """
    Get list of all HubSpot employee calendars IDs currently added to user's calendar.
    Limited to fetching 250 as paging is not utilized here.
    """
    print('Getting list of calendars...')
    listResult = service.calendarList().list(showHidden=True, maxResults=250).execute().get('items', [])
    return [ cal["id"] for cal in listResult if "@hubspot.com" in cal["id"] ]

#
# def get_events():
#     """
#     Shows basic usage of the Google Calendar API.
#
#     Creates a Google Calendar API service object and outputs a list of the next
#     10 events on the user's calendar.
#     """
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http=http)
#
#     now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#     print('Getting the upcoming 10 events')
#     eventsResult = service.events().list(
#         calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
#         orderBy='startTime').execute()
#     events = eventsResult.get('items', [])
#
#     return events


def get_free_calendars(time_block_begin, time_block_end):
    service = create_service();

    #now = datetime.datetime.utcnow().isoformat() + 'Z'

    calendars = get_calendar_id_list(service)
    calendars = [{"id": id} for id in calendars]

    request_body = {
        "timeMin": time_block_begin,
        "timeMax": time_block_end,
        "timeZone": 'US/Eastern',
        "items": calendars
    }

    eventsResult = service.freebusy().query(body=request_body).execute()
    cal_dict = eventsResult[u'calendars']
    return cal_dict
from __future__ import print_function

# If modifying these scopes, delete the file token.pickle.
import os
import os.path
import pickle
import sys
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

dirname = os.path.dirname(__file__).replace('/notioncalendarsync', '')


class GoogleCalendar():
    def __init__(self):
        self.check_credentials()

    def check_credentials(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.path.join(dirname, 'token.pickle')):
            with open(os.path.join(dirname, 'token.pickle'), 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(dirname, 'credentials.json'), self.scopes)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(dirname, 'token.pickle'), 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_or_update_event(self, title, date_start, date_end, timezone, description=None):
        # check if event already exists
        existing_event = self.event_exists(title)
        if existing_event:
            # if yes, check if event is unchanged
            if self.event_unchanged(existing_event, title, date_start, date_end,
                                    timezone, description) == False:
                self.update_event(existing_event, title, date_start, date_end,
                                  timezone, description)

        else:
            # else create new event
            self.create_event(title, date_start, date_end,
                              timezone, description)

    def update_event(self, existing_event, title, date_start, date_end, timezone, description=None):
        event_result = self.service.events().update(calendarId='primary',
                                                    eventId=existing_event['id'],
                                                    body={
                                                        "summary": title,
                                                        "description": description,
                                                        "start": {"dateTime": date_start.strftime('%Y-%m-%dT%H:%M:%SZ'), "timeZone": timezone} if hasattr(date_start, 'hour') else {'date': str(date_start)},
                                                        "end": {"dateTime": date_end.strftime('%Y-%m-%dT%H:%M:%SZ'), "timeZone": timezone} if hasattr(date_end, 'hour') else {'date': str(date_end)},
                                                    }
                                                    ).execute()

        print("updated event")
        print("id: ", event_result['id'])
        print(
            "title: {} -> {}".format(existing_event['summary'], event_result['summary']))
        print("starts at: {} -> {}".format(
            existing_event['start']['dateTime'] if 'dateTime' in existing_event['start'] else existing_event['start']['date'], event_result['start']['dateTime'] if 'dateTime' in event_result['start'] else event_result['start']['date']))
        print("ends at: {} -> {}".format(
            existing_event['end']['dateTime'] if 'dateTime' in existing_event['end'] else existing_event['end']['date'], event_result['end']['dateTime'] if 'dateTime' in event_result['end'] else event_result['end']['date']))
        print()

    def create_event(self, title, date_start, date_end, timezone, description=None):
        event_result = self.service.events().insert(calendarId='primary',
                                                    body={
                                                        "summary": title,
                                                        "description": description,
                                                        "start": {"dateTime": date_start.strftime('%Y-%m-%dT%H:%M:%SZ'), "timeZone": timezone} if hasattr(date_start, 'hour') else {'date': str(date_start)},
                                                        "end": {"dateTime": date_end.strftime('%Y-%m-%dT%H:%M:%SZ'), "timeZone": timezone} if hasattr(date_end, 'hour') else {'date': str(date_end)},
                                                    }
                                                    ).execute()

        print("created event")
        print("id: ", event_result['id'])
        print("title: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime']
              if 'dateTime' in event_result['start'] else event_result['start']['date'])
        print("ends at: ", event_result['end']['dateTime']
              if 'dateTime' in event_result['end'] else event_result['end']['date'])
        print()

    def get_events(self, maxResults=200):
        now = (datetime.utcnow()-timedelta(days=30)).isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=maxResults, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        return events

    def event_unchanged(self, existing_event, title, date_start, date_end, timezone, description):
        if existing_event['summary'] != title:
            return False

        if 'dateTime' in existing_event['start']:
            if existing_event['start']['dateTime'] != date_start.strftime('%Y-%m-%dT%H:%M:%SZ'):
                return False
        else:
            if existing_event['start']['date'] != str(date_start):
                return False

        if 'dateTime' in existing_event['end']:
            if existing_event['end']['dateTime'] != date_end.strftime('%Y-%m-%dT%H:%M:%SZ'):
                return False
        else:
            if existing_event['end']['date'] != str(date_end):
                return False

        if 'timeZone' in existing_event['start'] and existing_event['start']['timeZone'] != timezone:
            return False

        if 'description' in existing_event and existing_event['description'] != description:
            return False

        print('Event unchanged')
        return True

    def event_exists(self, title):
        events = self.get_events()
        for event in events:
            if event['summary'] == title:
                return event
        else:
            return False

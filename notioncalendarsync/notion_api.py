from datetime import datetime, timedelta

from notion.client import NotionClient

from notioncalendarsync.google_calendar import GoogleCalendar


class Notion(NotionClient):
    def events(self, collection_url):
        return [NotionCalendarEntry(page=event).details for event in self.get_block(collection_url).collection.get_rows() if event.date and event.status != 'Completed']

    def add_events_to_google_calendar(self, collection_url, timezone):
        events = self.events(collection_url)
        for event in events:
            GoogleCalendar().create_or_update_event(
                title=event['title'],
                date_start=event['date_start'],
                date_end=event['date_end'],
                timezone=timezone,
                description=event['description']
            )


class NotionCalendarEntry():
    def __init__(self, token_v2=None, page_url=None, page=None):
        self.page = page if page else NotionClient(
            token_v2=token_v2).get_block(page_url)

        self.date_start = self.page.date.start
        self.details = {
            'url': self.url,
            'title': self.page.title,
            'description': self.description,
            'date_start': self.date_start,
            'date_end': self.date_end
        }

    @property
    def date_end(self):
        if self.page.date.end:
            return self.page.date.end
        elif hasattr(self.page.date.start, 'hour'):
            return self.page.date.start+timedelta(hours=1)
        else:
            return self.page.date.start

    @property
    def url(self):
        return self.page.get_browseable_url()

    @property
    def description(self):
        try:
            return self.page.children[0].title
        except:
            return None

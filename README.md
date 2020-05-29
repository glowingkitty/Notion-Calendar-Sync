![Notion-Calendar-Sync](https://raw.githubusercontent.com/marcoEDU/Notion-Calendar-Sync/master/images/headerimage.jpg "Notion-Calendar-Sync")

The unofficial Notion API extended with the option to sync your Notion events to Google Calendar.

Want to support the development and stay updated?

<a href="https://www.patreon.com/bePatron?u=24983231"><img alt="Become a Patreon" src="https://raw.githubusercontent.com/marcoEDU/Notion-Calendar-Sync/master/images/patreon_button.svg"></a> <a href="https://liberapay.com/marcoEDU/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>


## Installation

```
pip install notioncalendarsync
```

## Usage

YOUR NOTION TOKEN:

Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so

```
from notioncalendarsync import Notion

Notion(token_v2="{{ YOUR NOTION TOKEN }}").add_events_to_google_calendar('{{ NOTION COLLECTION URL }}',timezone='Europe/Berlin')
```
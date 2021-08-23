import pytz
import re
from datetime import datetime
from io import BytesIO
from typing import List, Optional

from bs4.element import Tag
from django.utils import timezone
from pdfreader import SimplePDFViewer


class PDFReader:

    viewer: SimplePDFViewer
    content: str
    lines: List[str]

    def __init__(self, stream: BytesIO):
        self.viewer = SimplePDFViewer(stream)
        self.viewer.render()

        joined = ''
        spaces = 0
        for string in self.viewer.canvas.strings:
            if string == ' ':
                spaces += 1
            else:
                if spaces >= 1:
                    joined += '\n'

                spaces = 0
                joined += string.lower()

        self.content = joined
        self.lines = joined.split('\n')

    def find(self, start_text: str, end_text: str) -> Optional[str]:
        start = -1
        end = -1

        for i in range(len(self.lines)):
            line = self.lines[i]
            if start_text in line:
                start = i
            elif start > 0 and end_text in line:
                end = i
                break

        if start < 0 or end < 0:
            return None

        return ' '.join(self.lines[start:end])


def soup_find_string(soup: Tag) -> Optional[str]:
    length = len(soup.contents)
    if length == 0:
        return soup.string
    else:
        for child in soup.contents:
            text = child.string
            if not text:
                continue
            text = text.strip(' \u200b\u00a0')
            if len(text) > 0:
                return text

    return None


PRICE_REGEX = re.compile(r'\D')


def parse_price(text: str):
    try:
        return int(PRICE_REGEX.sub('', text))
    except ValueError:
        return None


DUTCH_DATE_REGEX = re.compile(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})')
DUTCH_DATETIME_REGEX = re.compile(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})\s+(?:om\s+)?(\d{1,2}):(\d{1,2})')
DUTCH_MONTHS = {
    'januari': 1,
    'februari': 2,
    'maart': 3,
    'april': 4,
    'mei': 5,
    'juni': 6,
    'juli': 7,
    'augustus': 8,
    'september': 9,
    'oktober': 10,
    'november': 11,
    'december': 12
}


def parse_date(text: str):
    return datetime.strptime(text, '%d-%m-%Y').date()


def parse_datetime(text: str):
    t = datetime.strptime(text, '%d-%m-%Y %H:%M')
    if not timezone.is_aware(t):
        return timezone.make_aware(t)
    return t


def parse_timestamp(text: str):
    t = datetime.fromisoformat(text.replace('Z', ''))
    if not timezone.is_aware(t):
        return timezone.make_aware(t, timezone=pytz.utc)
    return t


def parse_dutch_date(text: str):
    result = DUTCH_DATE_REGEX.search(text)
    return parse_date('{0}-{1}-{2}'.format(
        result.group(1), DUTCH_MONTHS[result.group(2)], result.group(3))
    ) if result else None


def parse_dutch_datetime(text: str):
    result = DUTCH_DATETIME_REGEX.search(text)
    return parse_datetime('{0}-{1}-{2} {3}:{4}'.format(
        result.group(1), DUTCH_MONTHS[result.group(2)], *result.group(3, 4, 5))
    ) if result else None


def parse_dutch_dates(text: str):
    timestamps = DUTCH_DATE_REGEX.findall(text)
    return [parse_date('{0}-{1}-{2}'.format(timestamp[0], DUTCH_MONTHS[timestamp[1]], timestamp[2]))
            for timestamp in timestamps]


def parse_dutch_datetimes(text: str):
    timestamps = DUTCH_DATETIME_REGEX.findall(text)
    return [parse_datetime('{0}-{1}-{2} {3}:{4}'.format(timestamp[0], DUTCH_MONTHS[timestamp[1]], *timestamp[2:5]))
            for timestamp in timestamps]

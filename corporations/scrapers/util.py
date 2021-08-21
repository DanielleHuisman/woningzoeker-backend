import re
from datetime import datetime
from io import BytesIO
from typing import List, Optional

from bs4.element import Tag
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
    return int(PRICE_REGEX.sub('', text))


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
    return datetime.strptime(text, '%d-%m-%Y %H:%M')

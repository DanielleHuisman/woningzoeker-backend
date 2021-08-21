from io import BytesIO
from typing import Optional

import requests
from bs4 import BeautifulSoup

from corporations.scrapers.util import PDFReader


class Scraper:

    session: Optional[requests.Session] = None
    is_logged_in: bool = False

    def base_url(self) -> str:
        raise NotImplementedError()

    def get_residence(self, external_id: str):
        raise NotImplementedError()

    def get_residence_by_url(self, url: str):
        raise NotImplementedError()

    def get_residences(self):
        raise NotImplementedError()

    def login(self, identifier: str, credentials: any):
        raise NotImplementedError()

    def logout(self):
        raise NotImplementedError()

    def get_user(self):
        raise NotImplementedError()

    def get_reactions(self):
        raise NotImplementedError()

    def has_session(self):
        return self.session is not None

    def start_session(self):
        if self.session:
            raise Exception('Session was already started')

        self.session = requests.Session()

    def end_session(self):
        self.session.close()
        self.session = None

    def request(self, method: str, url: str, **kwargs):
        return self.session.request(method, url, **kwargs) if self.session else requests.request(method, url, **kwargs)

    def fetch(self, url: str, method: str = 'GET', **kwargs):
        response = self.request(method, url, **kwargs)

        if 200 <= response.status_code <= 299:
            return response
        if 400 <= response.status_code <= 599:
            # TODO: improve error handling
            raise Exception('Failed to fetch page')
        else:
            raise Exception(f'Unable to handle status code {response.status_code}')

    def fetch_page(self, url: str, **kwargs):
        response = self.fetch(url, **kwargs)
        return response.text

    def fetch_html_page(self, url: str, **kwargs):
        text = self.fetch_page(url, **kwargs)
        return BeautifulSoup(text, 'html.parser')

    def fetch_document(self, url: str, **kwargs):
        response = self.fetch(url, **kwargs)
        return response.content

    def fetch_pdf_document(self, url: str, **kwargs):
        data = self.fetch_document(url, **kwargs)
        return PDFReader(BytesIO(data))

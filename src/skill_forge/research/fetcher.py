from typing import Protocol

import httpx

from skill_forge.models.source import FetchedDocument, ResearchSource


class FetchError(RuntimeError):
    pass


class SourceFetcher(Protocol):
    def fetch(self, source: ResearchSource) -> FetchedDocument:
        ...


class HttpSourceFetcher:
    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def fetch(self, source: ResearchSource) -> FetchedDocument:
        try:
            response = httpx.get(source.url_text, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise FetchError(str(exc)) from exc

        content_type = response.headers.get("content-type", "text/plain")
        return FetchedDocument(source=source, content=response.text, content_type=content_type)

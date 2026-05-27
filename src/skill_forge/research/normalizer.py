import re
from html.parser import HTMLParser

import trafilatura


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


class ContentNormalizer:
    def normalize(self, content: str, content_type: str = "text/plain") -> str:
        if self._looks_like_html(content, content_type):
            extracted = trafilatura.extract(content, output_format="markdown")
            if extracted:
                return self._compact_text(extracted)

            parser = _TextHTMLParser()
            parser.feed(content)
            return self._compact_text("\n".join(parser.parts))

        return self._compact_text(content)

    def title_for(self, source_name: str, normalized_content: str) -> str:
        for line in normalized_content.splitlines():
            cleaned = line.strip(" #\t")
            if cleaned:
                return cleaned[:120]
        return source_name

    def summary_for(self, normalized_content: str) -> str:
        text = self._compact_text(normalized_content).replace("\n", " ")
        return text[:280]

    def _looks_like_html(self, content: str, content_type: str) -> bool:
        return "html" in content_type.lower() or bool(re.search(r"<(?:html|body|main|article|h1|p)\b", content, re.I))

    def _compact_text(self, content: str) -> str:
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in content.replace("\r\n", "\n").split("\n")]
        compact_lines = [line for line in lines if line]
        return "\n".join(compact_lines).strip()

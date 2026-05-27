import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer

from skill_forge.models.search import CorpusDocument
from skill_forge.storage.corpus_reader import CorpusReader


@dataclass
class SearchIndex:
    documents: list[CorpusDocument]
    vectorizer: TfidfVectorizer
    matrix: Any
    signature: str


class TfidfIndexStore:
    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.index_file = index_dir / "tfidf.pkl"
        self.metadata_file = index_dir / "metadata.json"

    def load(self, expected_signature: str) -> SearchIndex | None:
        try:
            metadata = json.loads(self.metadata_file.read_text(encoding="utf-8"))
            if metadata.get("signature") != expected_signature:
                return None
            with self.index_file.open("rb") as handle:
                index = pickle.load(handle)
        except (OSError, ValueError, pickle.PickleError, AttributeError, EOFError):
            return None

        if not isinstance(index, SearchIndex):
            return None
        return index

    def save(self, index: SearchIndex) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        with self.index_file.open("wb") as handle:
            pickle.dump(index, handle)
        self.metadata_file.write_text(
            json.dumps(
                {
                    "signature": index.signature,
                    "document_count": len(index.documents),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )


class TfidfIndexer:
    def __init__(self, reader: CorpusReader, store: TfidfIndexStore) -> None:
        self.reader = reader
        self.store = store

    def load_or_build(self) -> SearchIndex | None:
        documents = self.reader.load_documents()
        if not documents:
            return None

        signature = self.reader.corpus_signature(documents)
        cached = self.store.load(signature)
        if cached is not None:
            return cached

        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([document.indexed_text for document in documents])
        index = SearchIndex(documents=documents, vectorizer=vectorizer, matrix=matrix, signature=signature)
        self.store.save(index)
        return index

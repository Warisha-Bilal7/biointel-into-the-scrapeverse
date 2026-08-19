import uuid
from datetime import datetime

from sqlalchemy import Column, Float, Boolean, Text, DateTime, JSON

from .database import Base


class ScrapeEvent(Base):
    __tablename__ = "scrape_events"

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(Text, nullable=False)
    title = Column(Text, nullable=False, default="")
    abstract = Column(Text, nullable=False, default="")
    status = Column(Text, nullable=False, default="")
    timestamp = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    structural_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    is_anomalous = Column(Boolean, default=False)
    vector_id = Column(Text, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class BaselineEmbedding(Base):
    __tablename__ = "baseline_embeddings"

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(Text, nullable=False, default="default")
    embedding_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def embedding(self):
        if self.embedding_json is None:
            return None
        import json
        return json.loads(self.embedding_json)

    @embedding.setter
    def embedding(self, value):
        import json
        self.embedding_json = json.dumps(value) if value is not None else None

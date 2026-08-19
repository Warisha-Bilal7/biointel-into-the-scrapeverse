CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS scrape_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    abstract TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    timestamp TIMESTAMPTZ,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    structural_score FLOAT,
    semantic_score FLOAT,
    is_anomalous BOOLEAN DEFAULT FALSE,
    vector_id UUID,
    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS baseline_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    label TEXT NOT NULL DEFAULT 'default',
    embedding vector(384),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scrape_events_received_at ON scrape_events (received_at DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_events_is_anomalous ON scrape_events (is_anomalous);
CREATE INDEX IF NOT EXISTS idx_baseline_embeddings_label ON baseline_embeddings (label);

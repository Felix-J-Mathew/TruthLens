-- Run this once in psql to create the database and table.
-- Command: psql -U postgres -f schema.sql

CREATE DATABASE truthlens;
\c truthlens

CREATE TABLE trusted_sources (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    domain     VARCHAR(200) NOT NULL UNIQUE,
    category   VARCHAR(50)  NOT NULL DEFAULT 'news',
    added_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Seed with well-known trusted sources
INSERT INTO trusted_sources (name, domain, category) VALUES
  ('Reuters',           'reuters.com',        'news'),
  ('BBC News',          'bbc.com',            'news'),
  ('Associated Press',  'apnews.com',         'news'),
  ('Snopes',            'snopes.com',         'fact-check'),
  ('FactCheck.org',     'factcheck.org',      'fact-check'),
  ('PolitiFact',        'politifact.com',     'fact-check'),
  ('WHO',               'who.int',            'government'),
  ('CDC',               'cdc.gov',            'government');

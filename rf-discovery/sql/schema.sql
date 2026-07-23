-- Schéma DuckDB du pipeline RF-Discovery (§6).

CREATE TABLE IF NOT EXISTS papers (
  pmid TEXT PRIMARY KEY, doi TEXT, title TEXT, abstract TEXT,
  year INTEGER, journal TEXT, domain TEXT, source TEXT,
  oa_status TEXT, retrieved_at TIMESTAMP, triage_score REAL
);

CREATE TABLE IF NOT EXISTS nodes (
  node_id TEXT PRIMARY KEY,          -- identifiant normalisé (CUI, Entrez, MeSH, ChEBI)
  node_type TEXT,                    -- Gene|Chemical|Disease|Pathway|CellType|BrainRegion|Exposure|Phenotype
  name TEXT, synonyms TEXT[], first_year INTEGER, degree INTEGER
);

CREATE TABLE IF NOT EXISTS edges (
  source_id TEXT, target_id TEXT, predicate TEXT,   -- prédicats SemMedDB
  n_papers INTEGER, first_year INTEGER, last_year INTEGER,
  pmids TEXT[], confidence REAL,
  PRIMARY KEY (source_id, target_id, predicate)
);

CREATE TABLE IF NOT EXISTS candidates (
  run_date DATE, a_id TEXT, c_id TEXT, metapath TEXT,
  dwpc REAL, z_score REAL, p_value REAL,             -- null par permutation
  embed_score REAL, novelty_z REAL, burst_score REAL,
  composite_rank INTEGER, llm_explanation TEXT, human_verdict TEXT
);

CREATE TABLE IF NOT EXISTS runs (
  run_date DATE PRIMARY KEY, n_new_papers INTEGER, n_new_edges INTEGER,
  n_candidates INTEGER, status TEXT, error TEXT, duration_s REAL
);

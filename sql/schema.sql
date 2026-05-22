CREATE TABLE IF NOT EXISTS perinatal_records (
    message_id TEXT PRIMARY KEY,
    source_system TEXT,
    message_timestamp TEXT,
    mother_id TEXT NOT NULL,
    mother_birth_date TEXT,
    postal_code_prefix TEXT,
    pregnancy_id TEXT,
    gestational_age_weeks INTEGER,
    gravida INTEGER,
    parity INTEGER,
    delivery_id TEXT,
    delivery_date TEXT NOT NULL,
    delivery_mode TEXT,
    place_of_birth TEXT,
    child_id TEXT NOT NULL,
    child_sex TEXT,
    birth_weight_grams INTEGER,
    apgar_5min INTEGER,
    admission_nicu INTEGER,
    processed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rejected_records (
    file_name TEXT,
    message_id TEXT,
    error_reason TEXT,
    rejected_at TEXT DEFAULT CURRENT_TIMESTAMP
);

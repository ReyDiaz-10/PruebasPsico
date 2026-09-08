CREATE TABLE IF NOT EXISTS voters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    has_voted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    party VARCHAR(150),
    votes INTEGER NOT NULL DEFAULT 0 CHECK (votes >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    voter_id INTEGER NOT NULL UNIQUE,
    candidate_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vote_voter
        FOREIGN KEY (voter_id) REFERENCES voters(id) ON DELETE RESTRICT,
    CONSTRAINT fk_vote_candidate
        FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_voters_email_lower
    ON voters (LOWER(email));

CREATE UNIQUE INDEX IF NOT EXISTS uq_candidates_name_lower
    ON candidates (LOWER(TRIM(name)));

CREATE OR REPLACE FUNCTION prevent_voter_candidate_conflict()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM candidates
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(NEW.name))
    ) THEN
        RAISE EXCEPTION 'La persona ya está registrada como candidato';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION prevent_candidate_voter_conflict()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM voters
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(NEW.name))
    ) THEN
        RAISE EXCEPTION 'La persona ya está registrada como votante';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_voter_not_candidate ON voters;
CREATE TRIGGER trg_voter_not_candidate
BEFORE INSERT OR UPDATE OF name ON voters
FOR EACH ROW EXECUTE FUNCTION prevent_voter_candidate_conflict();

DROP TRIGGER IF EXISTS trg_candidate_not_voter ON candidates;
CREATE TRIGGER trg_candidate_not_voter
BEFORE INSERT OR UPDATE OF name ON candidates
FOR EACH ROW EXECUTE FUNCTION prevent_candidate_voter_conflict();


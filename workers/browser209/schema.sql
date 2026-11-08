BEGIN;
CREATE SCHEMA IF NOT EXISTS browser_209;
REVOKE ALL ON SCHEMA browser_209 FROM PUBLIC;
CREATE TABLE IF NOT EXISTS browser_209.jobs (
 id uuid PRIMARY KEY,
 idempotency_key text NOT NULL UNIQUE,
 account_key text NOT NULL,
 payload jsonb NOT NULL,
 payload_sha256 text NOT NULL,
 state text NOT NULL DEFAULT 'proposed' CHECK (state IN ('proposed','approved','running','executed_unverified','uncertain','expired','revoked')),
 due_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz NOT NULL,
 approved_at timestamptz,
 started_at timestamptz,
 finished_at timestamptz,
 result jsonb,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK (expires_at>due_at)
);
ALTER TABLE browser_209.jobs ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON browser_209.jobs FROM PUBLIC;
CREATE INDEX IF NOT EXISTS browser_209_due ON browser_209.jobs(due_at) WHERE state='approved';
CREATE OR REPLACE FUNCTION browser_209.guard_job() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NEW.id IS DISTINCT FROM OLD.id OR NEW.account_key IS DISTINCT FROM OLD.account_key OR NEW.payload IS DISTINCT FROM OLD.payload OR NEW.payload_sha256 IS DISTINCT FROM OLD.payload_sha256 OR NEW.idempotency_key IS DISTINCT FROM OLD.idempotency_key OR NEW.due_at IS DISTINCT FROM OLD.due_at OR NEW.expires_at IS DISTINCT FROM OLD.expires_at THEN
  RAISE EXCEPTION 'Immutable job fields: create a new proposal instead';
 END IF;
 IF NEW.state IS DISTINCT FROM OLD.state AND NOT (
 (OLD.state='proposed' AND NEW.state IN ('approved','revoked')) OR
 (OLD.state='approved' AND NEW.state IN ('running','revoked','expired')) OR
 (OLD.state='running' AND NEW.state IN ('executed_unverified','uncertain'))
 ) THEN RAISE EXCEPTION 'Invalid state transition'; END IF;
 RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION browser_209.guard_job() FROM PUBLIC;
DROP TRIGGER IF EXISTS browser_209_job_guard ON browser_209.jobs;
CREATE TRIGGER browser_209_job_guard BEFORE UPDATE ON browser_209.jobs FOR EACH ROW EXECUTE FUNCTION browser_209.guard_job();
COMMIT;

-- REVIEWED SOURCE REQUIRED BEFORE INSTALLATION. PostgreSQL 14+.
-- Additive namespace; existing browser_209 queue is not altered or copied.
BEGIN;
CREATE ROLE b209v2_owner NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE b209v2_proposer NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE b209v2_approver NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE b209v2_worker NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE b209v2_reconciler NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE SCHEMA browser_209_v2 AUTHORIZATION b209v2_owner;
REVOKE ALL ON SCHEMA browser_209_v2 FROM PUBLIC;
SET LOCAL ROLE b209v2_owner;
ALTER DEFAULT PRIVILEGES IN SCHEMA browser_209_v2 REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE TABLE browser_209_v2.accounts (
 account_key text PRIMARY KEY CHECK(account_key ~ '^[a-z0-9_-]{1,64}$'),
 enabled boolean NOT NULL DEFAULT false, blocked boolean NOT NULL DEFAULT false,
 generation bigint NOT NULL DEFAULT 0 CHECK(generation>=0), active_job uuid,
 owner_login name, token uuid, lease_until timestamptz,
 CHECK((active_job IS NULL AND owner_login IS NULL AND token IS NULL AND lease_until IS NULL)
 OR(active_job IS NOT NULL AND owner_login IS NOT NULL AND token IS NOT NULL AND lease_until IS NOT NULL))
);
CREATE TABLE browser_209_v2.acl (
 principal name NOT NULL, account_key text NOT NULL REFERENCES browser_209_v2.accounts,
 capability text NOT NULL CHECK(capability IN('propose','approve','execute','reconcile')),
 PRIMARY KEY(principal,account_key,capability)
);
CREATE TABLE browser_209_v2.jobs (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), account_key text NOT NULL REFERENCES browser_209_v2.accounts,
 idempotency_key text NOT NULL UNIQUE CHECK(length(idempotency_key) BETWEEN 1 AND 200),
 proposed_by name NOT NULL, payload jsonb NOT NULL, payload_text text NOT NULL,
 payload_sha256 text NOT NULL CHECK(payload_sha256 ~ '^[a-f0-9]{64}$'),
 due_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
 created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 state text NOT NULL DEFAULT 'proposed' CHECK(state IN('proposed','approved','running','executed_unverified','uncertain','expired','revoked')),
 approved_by name, approved_at timestamptz, approval_expires_at timestamptz,
 authorization_ref text, approval_sha256 text, claimed_by name, claim_token uuid,
 claim_generation bigint, lease_expires_at timestamptz, heartbeat_at timestamptz,
 started_at timestamptz, finished_at timestamptz,
 cancel_requested_at timestamptz, cancel_requested_by name, cancel_reason text, result jsonb,
 CHECK(expires_at>due_at), CHECK(isfinite(due_at) AND isfinite(expires_at)),
 CHECK(octet_length(payload_text)<=262144), CHECK(payload_text::jsonb=payload)
);
ALTER TABLE browser_209_v2.accounts ADD FOREIGN KEY(active_job) REFERENCES browser_209_v2.jobs;
CREATE INDEX due_jobs ON browser_209_v2.jobs(account_key,due_at,id) WHERE state='approved';
CREATE TABLE browser_209_v2.events (
 event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 job_id uuid NOT NULL REFERENCES browser_209_v2.jobs,
 actor name NOT NULL DEFAULT session_user, observed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 event_type text NOT NULL, details jsonb NOT NULL DEFAULT '{}' CHECK(octet_length(details::text)<=32768)
);
CREATE FUNCTION browser_209_v2.hash(t text) RETURNS text LANGUAGE sql IMMUTABLE STRICT SET search_path=pg_catalog AS $$
 SELECT encode(sha256(convert_to(t,'UTF8')),'hex')
$$;
CREATE FUNCTION browser_209_v2.cap(a text,c text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog AS $$
 SELECT pg_has_role(session_user,CASE c WHEN 'execute' THEN 'b209v2_worker' WHEN 'propose' THEN 'b209v2_proposer' WHEN 'approve' THEN 'b209v2_approver' ELSE 'b209v2_reconciler' END,'MEMBER')
 AND EXISTS(SELECT 1 FROM browser_209_v2.acl WHERE principal=session_user AND account_key=a AND capability=c)
$$;
CREATE FUNCTION browser_209_v2.valid_payload(p jsonb) RETURNS boolean LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog AS $$
DECLARE s jsonb; fields text[];
BEGIN
 IF jsonb_typeof(p) IS DISTINCT FROM 'object' OR NOT(p ? 'steps') OR p-'steps'<>'{}'::jsonb THEN RETURN false; END IF;
 IF jsonb_typeof(p->'steps') IS DISTINCT FROM 'array' THEN RETURN false; END IF;
 IF jsonb_array_length(p->'steps') NOT BETWEEN 1 AND 20 THEN RETURN false; END IF;
 FOR s IN SELECT value FROM jsonb_array_elements(p->'steps') LOOP
  IF jsonb_typeof(s) IS DISTINCT FROM 'object' THEN RETURN false; END IF;
  fields:=CASE s->>'action' WHEN 'goto' THEN ARRAY['action','url'] WHEN 'fill' THEN ARRAY['action','selector','text'] WHEN 'click' THEN ARRAY['action','selector'] WHEN 'observe' THEN ARRAY['action','selector','expected_text'] END;
  IF fields IS NULL OR NOT(s ?& fields) OR s-fields<>'{}'::jsonb THEN RETURN false; END IF;
  IF EXISTS(SELECT 1 FROM jsonb_each(s) v WHERE jsonb_typeof(v.value)<>'string' OR length(v.value #>> '{}')>10000) THEN RETURN false; END IF;
 END LOOP;
 RETURN true;
END $$;
CREATE FUNCTION browser_209_v2.envelope(j browser_209_v2.jobs,d timestamptz,r text) RETURNS text LANGUAGE sql STABLE SET search_path=pg_catalog AS $$
 SELECT jsonb_build_object('format','browser209-envelope-v2','job_id',j.id,'account_key',j.account_key,'idempotency_key',j.idempotency_key,'payload_sha256',j.payload_sha256,'due_epoch',extract(epoch FROM j.due_at),'expires_epoch',extract(epoch FROM j.expires_at),'approval_expires_epoch',extract(epoch FROM d),'authorization_ref',r)::text
$$;
-- FAIL CLOSED. Replace only after inspecting the actual authorization ledger.
-- Must check identity, scope, envelope digest, expiry, revocation, route and caps.
CREATE FUNCTION browser_209_v2.authorization_valid(j browser_209_v2.jobs) RETURNS boolean LANGUAGE sql STABLE SET search_path=pg_catalog AS $$ SELECT false $$;
CREATE FUNCTION browser_209_v2.guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF current_user<>'b209v2_owner' THEN RAISE EXCEPTION 'function_only_writes'; END IF;
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'deletion_forbidden'; END IF;
 IF NEW.payload_sha256 IS DISTINCT FROM browser_209_v2.hash(NEW.payload_text) OR NOT browser_209_v2.valid_payload(NEW.payload) THEN RAISE EXCEPTION 'payload_integrity'; END IF;
 IF TG_OP='INSERT' THEN
  IF NEW.state<>'proposed' OR NEW.proposed_by IS DISTINCT FROM session_user OR NOT browser_209_v2.cap(NEW.account_key,'propose')
   OR NEW.approved_at IS NOT NULL OR NEW.approved_by IS NOT NULL OR NEW.approval_expires_at IS NOT NULL OR NEW.authorization_ref IS NOT NULL OR NEW.approval_sha256 IS NOT NULL
   OR NEW.claimed_by IS NOT NULL OR NEW.claim_token IS NOT NULL OR NEW.claim_generation IS NOT NULL OR NEW.lease_expires_at IS NOT NULL OR NEW.heartbeat_at IS NOT NULL
   OR NEW.started_at IS NOT NULL OR NEW.finished_at IS NOT NULL OR NEW.result IS NOT NULL OR NEW.cancel_requested_at IS NOT NULL OR NEW.cancel_requested_by IS NOT NULL OR NEW.cancel_reason IS NOT NULL
  THEN RAISE EXCEPTION 'invalid_initial_state'; END IF;
 ELSE
  IF ROW(NEW.id,NEW.account_key,NEW.idempotency_key,NEW.proposed_by,NEW.payload,NEW.payload_text,NEW.payload_sha256,NEW.due_at,NEW.expires_at,NEW.created_at)
   IS DISTINCT FROM ROW(OLD.id,OLD.account_key,OLD.idempotency_key,OLD.proposed_by,OLD.payload,OLD.payload_text,OLD.payload_sha256,OLD.due_at,OLD.expires_at,OLD.created_at) THEN RAISE EXCEPTION 'immutable_proposal'; END IF;
  IF OLD.state IN('executed_unverified','uncertain','expired','revoked') AND NEW IS DISTINCT FROM OLD THEN RAISE EXCEPTION 'immutable_terminal_job'; END IF;
  IF NEW.state IS DISTINCT FROM OLD.state AND NOT((OLD.state='proposed' AND NEW.state IN('approved','expired','revoked')) OR(OLD.state='approved' AND NEW.state IN('running','expired','revoked')) OR(OLD.state='running' AND NEW.state IN('executed_unverified','uncertain'))) THEN RAISE EXCEPTION 'invalid_transition'; END IF;
  IF NOT(OLD.state='proposed' AND NEW.state='approved') AND ROW(NEW.approved_by,NEW.approved_at,NEW.approval_expires_at,NEW.authorization_ref,NEW.approval_sha256) IS DISTINCT FROM ROW(OLD.approved_by,OLD.approved_at,OLD.approval_expires_at,OLD.authorization_ref,OLD.approval_sha256) THEN RAISE EXCEPTION 'immutable_approval'; END IF;
  IF NOT(OLD.state='approved' AND NEW.state='running') AND ROW(NEW.claimed_by,NEW.claim_token,NEW.claim_generation,NEW.started_at) IS DISTINCT FROM ROW(OLD.claimed_by,OLD.claim_token,OLD.claim_generation,OLD.started_at) THEN RAISE EXCEPTION 'immutable_claim'; END IF;
  IF OLD.state='proposed' AND NEW.state='approved' THEN
   IF NOT browser_209_v2.cap(NEW.account_key,'approve') OR browser_209_v2.cap(NEW.account_key,'execute') OR NEW.approved_by IS DISTINCT FROM session_user OR NEW.proposed_by=session_user
    OR NEW.approved_at IS NULL OR NEW.approved_at>clock_timestamp() OR NEW.approval_expires_at IS NULL OR NOT isfinite(NEW.approval_expires_at)
    OR NEW.approval_expires_at<=greatest(clock_timestamp(),NEW.due_at) OR NEW.approval_expires_at>NEW.expires_at
    OR NEW.authorization_ref IS NULL OR length(btrim(NEW.authorization_ref)) NOT BETWEEN 1 AND 500
    OR NEW.approval_sha256 IS DISTINCT FROM browser_209_v2.hash(browser_209_v2.envelope(NEW,NEW.approval_expires_at,NEW.authorization_ref)) THEN RAISE EXCEPTION 'invalid_approval'; END IF;
  END IF;
  IF OLD.state='approved' AND NEW.state='running' THEN
   IF NOT browser_209_v2.cap(NEW.account_key,'execute') OR browser_209_v2.cap(NEW.account_key,'approve') OR NEW.claimed_by IS DISTINCT FROM session_user OR NEW.claim_token IS NULL OR NEW.claim_generation IS NULL OR NEW.claim_generation<=0
    OR NEW.started_at IS NULL OR NEW.due_at>clock_timestamp() OR NEW.expires_at<=clock_timestamp() OR NEW.approval_expires_at IS NULL OR NEW.approval_expires_at<=clock_timestamp() OR NEW.cancel_requested_at IS NOT NULL THEN RAISE EXCEPTION 'invalid_claim'; END IF;
  END IF;
 END IF;
 IF NEW.state='running' AND(NEW.lease_expires_at IS NULL OR NEW.lease_expires_at<=clock_timestamp() OR NEW.lease_expires_at>least(NEW.expires_at,NEW.approval_expires_at) OR NEW.heartbeat_at IS NULL) THEN RAISE EXCEPTION 'invalid_lease'; END IF;
 IF NEW.state IN('executed_unverified','uncertain') AND(NEW.started_at IS NULL OR NEW.finished_at IS NULL OR NEW.finished_at<NEW.started_at OR NEW.result IS NULL) THEN RAISE EXCEPTION 'invalid_completion'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard BEFORE INSERT OR UPDATE OR DELETE ON browser_209_v2.jobs FOR EACH ROW EXECUTE FUNCTION browser_209_v2.guard();
CREATE FUNCTION browser_209_v2.append_only() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$ BEGIN RAISE EXCEPTION 'append_only'; END $$;
CREATE TRIGGER append_only BEFORE UPDATE OR DELETE ON browser_209_v2.events FOR EACH ROW EXECUTE FUNCTION browser_209_v2.append_only();
-- One narrow dispatcher; every operation rechecks capability and object ownership.
CREATE FUNCTION browser_209_v2.api(op text,p jsonb DEFAULT '{}') RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS $$
DECLARE j browser_209_v2.jobs; a browser_209_v2.accounts; key text; i uuid; tok uuid; g bigint; d timestamptz; env text; r text; c text; outcome text; reply jsonb;
BEGIN
 IF op IS NULL OR op NOT IN('propose','preview','approve','claim','heartbeat','complete','cancel','reconcile','evidence') OR jsonb_typeof(p) IS DISTINCT FROM 'object' OR octet_length(p::text)>300000 THEN RAISE EXCEPTION 'invalid_operation'; END IF;
 IF op='propose' THEN
  key:=p->>'account_key';
  IF NOT browser_209_v2.cap(key,'propose') THEN RAISE EXCEPTION 'not_authorized'; END IF;
  IF (p->>'expires_at')::timestamptz<=clock_timestamp() THEN RAISE EXCEPTION 'expired'; END IF;
  INSERT INTO browser_209_v2.jobs(account_key,idempotency_key,proposed_by,payload,payload_text,payload_sha256,due_at,expires_at)
  VALUES(key,p->>'idempotency_key',session_user,p->'payload',(p->'payload')::text,browser_209_v2.hash((p->'payload')::text),(p->>'due_at')::timestamptz,(p->>'expires_at')::timestamptz) RETURNING * INTO j;
  reply:=jsonb_build_object('job_id',j.id,'payload_text',j.payload_text,'payload_sha256',j.payload_sha256);
 ELSIF op='claim' THEN
  SELECT x.* INTO a FROM browser_209_v2.accounts x WHERE x.enabled AND NOT x.blocked AND x.active_job IS NULL AND browser_209_v2.cap(x.account_key,'execute') AND NOT browser_209_v2.cap(x.account_key,'approve')
   AND EXISTS(SELECT 1 FROM browser_209_v2.jobs q WHERE q.account_key=x.account_key AND q.state='approved' AND q.due_at<=clock_timestamp() AND q.expires_at>clock_timestamp() AND q.approval_expires_at>clock_timestamp() AND q.cancel_requested_at IS NULL)
   ORDER BY x.account_key FOR UPDATE OF x SKIP LOCKED LIMIT 1;
  IF NOT FOUND THEN RETURN NULL; END IF;
  SELECT * INTO j FROM browser_209_v2.jobs WHERE account_key=a.account_key AND state='approved' AND due_at<=clock_timestamp() AND expires_at>clock_timestamp() AND approval_expires_at>clock_timestamp() AND cancel_requested_at IS NULL ORDER BY due_at,id FOR UPDATE SKIP LOCKED LIMIT 1;
  IF NOT FOUND THEN RETURN NULL; END IF;
  IF browser_209_v2.authorization_valid(j) IS DISTINCT FROM true OR j.approval_sha256 IS DISTINCT FROM browser_209_v2.hash(browser_209_v2.envelope(j,j.approval_expires_at,j.authorization_ref)) THEN RAISE EXCEPTION 'authorization_denied'; END IF;
  tok:=gen_random_uuid(); d:=least(clock_timestamp()+interval '30 seconds',j.expires_at,j.approval_expires_at);
  UPDATE browser_209_v2.accounts SET generation=generation+1,active_job=j.id,owner_login=session_user,token=tok,lease_until=d WHERE account_key=a.account_key RETURNING * INTO a;
  UPDATE browser_209_v2.jobs SET state='running',claimed_by=session_user,claim_token=tok,claim_generation=a.generation,lease_expires_at=d,heartbeat_at=clock_timestamp(),started_at=clock_timestamp() WHERE id=j.id RETURNING * INTO j;
  reply:=to_jsonb(j);
 ELSE
  i:=(p->>'job_id')::uuid;
  SELECT account_key INTO STRICT key FROM browser_209_v2.jobs WHERE id=i;
  c:=CASE WHEN op IN('preview','approve','cancel') THEN 'approve' WHEN op='reconcile' THEN 'reconcile' ELSE 'execute' END;
  IF NOT browser_209_v2.cap(key,c) OR(c='approve' AND browser_209_v2.cap(key,'execute')) OR(c='execute' AND browser_209_v2.cap(key,'approve')) THEN RAISE EXCEPTION 'not_authorized'; END IF;
  SELECT * INTO STRICT a FROM browser_209_v2.accounts WHERE account_key=key FOR UPDATE;
  SELECT * INTO STRICT j FROM browser_209_v2.jobs WHERE id=i FOR UPDATE;
  IF op IN('preview','approve') THEN
   d:=(p->>'approval_expires_at')::timestamptz; r:=p->>'authorization_ref';
   IF j.state<>'proposed' OR d IS NULL OR NOT isfinite(d) OR d<=greatest(clock_timestamp(),j.due_at) OR d>j.expires_at OR r IS NULL OR length(btrim(r)) NOT BETWEEN 1 AND 500 THEN RAISE EXCEPTION 'invalid_approval_window'; END IF;
   env:=browser_209_v2.envelope(j,d,r);
   IF op='preview' THEN RETURN jsonb_build_object('envelope_text',env,'envelope_sha256',browser_209_v2.hash(env),'payload_text',j.payload_text); END IF;
   IF j.proposed_by=session_user OR (p->>'expected_sha256') IS DISTINCT FROM browser_209_v2.hash(env) THEN RAISE EXCEPTION 'approval_mismatch'; END IF;
   j.approved_by:=session_user; j.approved_at:=clock_timestamp(); j.approval_expires_at:=d; j.authorization_ref:=r; j.approval_sha256:=p->>'expected_sha256';
   IF browser_209_v2.authorization_valid(j) IS DISTINCT FROM true THEN RAISE EXCEPTION 'authorization_denied'; END IF;
   UPDATE browser_209_v2.jobs SET state='approved',approved_by=j.approved_by,approved_at=j.approved_at,approval_expires_at=d,authorization_ref=r,approval_sha256=j.approval_sha256 WHERE id=i;
  ELSIF op IN('heartbeat','complete') THEN
   tok:=(p->>'claim_token')::uuid; g:=(p->>'claim_generation')::bigint;
   IF tok IS NULL OR g IS NULL OR j.state<>'running' OR j.claimed_by IS DISTINCT FROM session_user OR j.claim_token IS DISTINCT FROM tok OR j.claim_generation IS DISTINCT FROM g
    OR a.active_job IS DISTINCT FROM i OR a.owner_login IS DISTINCT FROM session_user OR a.token IS DISTINCT FROM tok OR a.generation IS DISTINCT FROM g
    OR a.lease_until<=clock_timestamp() OR j.lease_expires_at<=clock_timestamp() OR j.expires_at<=clock_timestamp() OR j.approval_expires_at<=clock_timestamp() THEN RAISE EXCEPTION 'claim_not_live'; END IF;
   IF op='heartbeat' THEN
    IF a.blocked OR NOT a.enabled OR j.cancel_requested_at IS NOT NULL OR browser_209_v2.authorization_valid(j) IS DISTINCT FROM true THEN RAISE EXCEPTION 'authorization_denied'; END IF;
    d:=least(clock_timestamp()+interval '30 seconds',j.expires_at,j.approval_expires_at);
    UPDATE browser_209_v2.accounts SET lease_until=d WHERE account_key=key;
    UPDATE browser_209_v2.jobs SET lease_expires_at=d,heartbeat_at=clock_timestamp() WHERE id=i;
    RETURN jsonb_build_object('lease_expires_at',d);
   END IF;
   outcome:=p->>'outcome';
   IF outcome IS NULL OR outcome NOT IN('executed_unverified','uncertain') OR(outcome='executed_unverified' AND(a.blocked OR NOT a.enabled OR j.cancel_requested_at IS NOT NULL OR browser_209_v2.authorization_valid(j) IS DISTINCT FROM true)) THEN RAISE EXCEPTION 'invalid_outcome'; END IF;
   UPDATE browser_209_v2.jobs SET state=outcome,finished_at=clock_timestamp(),result=jsonb_build_object('state',outcome,'platform_acceptance_verified',false,'public_visibility_verified',false,'automatic_retry_allowed',false) WHERE id=i;
   UPDATE browser_209_v2.accounts SET blocked=true WHERE account_key=key;
  ELSIF op='cancel' THEN
   r:=p->>'reason';
   IF j.state NOT IN('proposed','approved','running') OR r IS NULL OR length(btrim(r)) NOT BETWEEN 1 AND 500 THEN RAISE EXCEPTION 'invalid_cancellation'; END IF;
   UPDATE browser_209_v2.jobs SET state=CASE WHEN state='running' THEN state ELSE 'revoked' END,cancel_requested_at=clock_timestamp(),cancel_requested_by=session_user,cancel_reason=r WHERE id=i;
   IF j.state='running' THEN UPDATE browser_209_v2.accounts SET blocked=true WHERE account_key=key; END IF;
  ELSIF op='reconcile' THEN
   outcome:=p->>'disposition';r:=p->>'evidence_ref';
   IF browser_209_v2.cap(key,'execute') OR j.claimed_by=session_user OR a.active_job IS DISTINCT FROM i OR outcome IS NULL OR outcome NOT IN('confirmed_effect','confirmed_no_effect','unresolved') OR r IS NULL OR length(btrim(r)) NOT BETWEEN 1 AND 1000 THEN RAISE EXCEPTION 'invalid_reconciliation'; END IF;
   IF j.state='running' THEN
    IF a.lease_until>clock_timestamp() THEN RAISE EXCEPTION 'lease_still_live'; END IF;
    UPDATE browser_209_v2.jobs SET state='uncertain',finished_at=clock_timestamp(),result=jsonb_build_object('state','uncertain','automatic_retry_allowed',false) WHERE id=i;
   ELSIF j.state NOT IN('uncertain','executed_unverified') THEN RAISE EXCEPTION 'not_reconcilable'; END IF;
   IF outcome<>'unresolved' AND(p->>'executor_stopped')::boolean IS TRUE THEN
    UPDATE browser_209_v2.accounts SET active_job=NULL,owner_login=NULL,token=NULL,lease_until=NULL,blocked=false WHERE account_key=key;
   ELSE UPDATE browser_209_v2.accounts SET blocked=true WHERE account_key=key; END IF;
   INSERT INTO browser_209_v2.events(job_id,event_type,details) VALUES(i,'reconciliation_evidence',jsonb_build_object('disposition',outcome,'evidence_ref',r,'executor_stopped',(p->>'executor_stopped')::boolean));
  ELSIF op='evidence' THEN
   r:=p->>'evidence_ref';
   IF j.claimed_by IS DISTINCT FROM session_user OR r IS NULL OR length(btrim(r)) NOT BETWEEN 1 AND 1000 THEN RAISE EXCEPTION 'invalid_evidence'; END IF;
   INSERT INTO browser_209_v2.events(job_id,event_type,details) VALUES(i,'evidence_reference',jsonb_build_object('reference',r));
  END IF;
  reply:=jsonb_build_object('job_id',i,'operation',op);
 END IF;
 INSERT INTO browser_209_v2.events(job_id,event_type) VALUES(j.id,op);
 RETURN reply;
END $$;
ALTER TABLE browser_209_v2.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE browser_209_v2.accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE browser_209_v2.acl ENABLE ROW LEVEL SECURITY;
ALTER TABLE browser_209_v2.events ENABLE ROW LEVEL SECURITY;
CREATE POLICY proposer_read ON browser_209_v2.jobs FOR SELECT TO b209v2_proposer USING(proposed_by=session_user AND browser_209_v2.cap(account_key,'propose'));
CREATE POLICY approver_read ON browser_209_v2.jobs FOR SELECT TO b209v2_approver USING(browser_209_v2.cap(account_key,'approve'));
CREATE POLICY reconciler_read ON browser_209_v2.jobs FOR SELECT TO b209v2_reconciler USING(browser_209_v2.cap(account_key,'reconcile'));
CREATE POLICY event_read ON browser_209_v2.events FOR SELECT TO b209v2_reconciler USING(EXISTS(SELECT 1 FROM browser_209_v2.jobs j WHERE j.id=job_id AND browser_209_v2.cap(j.account_key,'reconcile')));
REVOKE ALL ON ALL TABLES IN SCHEMA browser_209_v2 FROM PUBLIC,b209v2_proposer,b209v2_approver,b209v2_worker,b209v2_reconciler;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA browser_209_v2 FROM PUBLIC,b209v2_proposer,b209v2_approver,b209v2_worker,b209v2_reconciler;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA browser_209_v2 FROM PUBLIC,b209v2_proposer,b209v2_approver,b209v2_worker,b209v2_reconciler;
GRANT USAGE ON SCHEMA browser_209_v2 TO b209v2_proposer,b209v2_approver,b209v2_worker,b209v2_reconciler;
GRANT SELECT ON browser_209_v2.jobs TO b209v2_proposer,b209v2_approver,b209v2_reconciler;
GRANT SELECT ON browser_209_v2.events TO b209v2_reconciler;
GRANT EXECUTE ON FUNCTION browser_209_v2.cap(text,text),browser_209_v2.api(text,jsonb) TO b209v2_proposer,b209v2_approver,b209v2_worker,b209v2_reconciler;
COMMIT;

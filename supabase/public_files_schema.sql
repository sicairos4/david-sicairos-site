-- Apply separately after reviewing the target project. Does not modify member tables.
begin;
create table public.pf_organizations (
 id uuid primary key default gen_random_uuid(), slug text not null unique, name text not null,
 kind text not null check(kind in ('city','county','department','board','other')),
 parent_id uuid references public.pf_organizations(id), source_url text not null check(source_url like 'https://%'),
 public_visible boolean not null default false, created_at timestamptz not null default now()
);
create table public.pf_people (
 id uuid primary key default gen_random_uuid(), name text not null,
 public_visible boolean not null default false, created_at timestamptz not null default now()
);
create table public.pf_positions (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.pf_organizations(id),
 person_id uuid not null references public.pf_people(id), title text not null, starts_on date, ends_on date,
 public_visible boolean not null default false, check(ends_on is null or starts_on is null or ends_on>=starts_on)
);
create table public.pf_documents (
 id uuid primary key default gen_random_uuid(), source_url text not null check(source_url like 'https://%'),
 public_document_url text check(public_document_url like 'https://%'),
 sha256 text not null unique check(sha256 ~ '^[0-9a-f]{64}$'), retrieved_at timestamptz not null,
 review_status text not null default 'draft' check(review_status in ('draft','review','published','withdrawn')),
 redaction_reviewed boolean not null default false,
 check(review_status<>'published' or redaction_reviewed), created_at timestamptz not null default now()
);
create table public.pf_filings (
 id uuid primary key default gen_random_uuid(), external_id text unique,
 organization_id uuid not null references public.pf_organizations(id), person_id uuid not null references public.pf_people(id),
 document_id uuid not null references public.pf_documents(id),
 statement_type text not null check(statement_type in ('annual','assuming_office','leaving_office','candidate','amendment','other')),
 reporting_period_start date, reporting_period_end date, filed_date date,
 amends_filing_id uuid references public.pf_filings(id),
 review_status text not null default 'draft' check(review_status in ('draft','review','published','withdrawn')),
 check(reporting_period_start is null or reporting_period_end is null or reporting_period_end>=reporting_period_start),
 check(amends_filing_id is null or amends_filing_id<>id), created_at timestamptz not null default now()
);
create table public.pf_filing_positions (
 filing_id uuid not null references public.pf_filings(id), position_id uuid not null references public.pf_positions(id),
 primary key(filing_id,position_id)
);
create table public.pf_interests (
 id uuid primary key default gen_random_uuid(), filing_id uuid not null references public.pf_filings(id),
 schedule text not null check(schedule in ('A-1','A-2','B','C','D','E')), disclosed_entity text not null,
 interest_type text not null, reported_value_range text, source_page integer not null check(source_page>0),
 review_status text not null default 'draft' check(review_status in ('draft','review','published','withdrawn'))
);
create table public.pf_requests (
 id uuid primary key default gen_random_uuid(), organization_id uuid not null references public.pf_organizations(id),
 reference text, description text not null, submitted_on date, responded_on date,
 status text not null default 'draft' check(status in ('draft','submitted','acknowledged','partial','fulfilled','closed')),
 public_visible boolean not null default false,
 check(responded_on is null or submitted_on is null or responded_on>=submitted_on)
);
create index pf_positions_org on public.pf_positions(organization_id);
create index pf_filings_org_period on public.pf_filings(organization_id,reporting_period_end);
create index pf_filings_person on public.pf_filings(person_id);
create index pf_filings_document on public.pf_filings(document_id);
create index pf_interests_filing on public.pf_interests(filing_id);
create index pf_interests_entity_search on public.pf_interests using gin(to_tsvector('simple',disclosed_entity));

alter table public.pf_organizations enable row level security;
alter table public.pf_people enable row level security;
alter table public.pf_positions enable row level security;
alter table public.pf_documents enable row level security;
alter table public.pf_filings enable row level security;
alter table public.pf_filing_positions enable row level security;
alter table public.pf_interests enable row level security;
alter table public.pf_requests enable row level security;

create policy pf_org_read on public.pf_organizations for select to anon,authenticated using(public_visible);
create policy pf_people_read on public.pf_people for select to anon,authenticated using(public_visible);
create policy pf_position_read on public.pf_positions for select to anon,authenticated using(
 public_visible and exists(select 1 from public.pf_organizations o where o.id=organization_id)
 and exists(select 1 from public.pf_people p where p.id=person_id));
create policy pf_document_read on public.pf_documents for select to anon,authenticated using(review_status='published' and redaction_reviewed);
create policy pf_filing_read on public.pf_filings for select to anon,authenticated using(
 review_status='published' and exists(select 1 from public.pf_documents d where d.id=document_id)
 and exists(select 1 from public.pf_organizations o where o.id=organization_id)
 and exists(select 1 from public.pf_people p where p.id=person_id));
create policy pf_link_read on public.pf_filing_positions for select to anon,authenticated using(
 exists(select 1 from public.pf_filings f where f.id=filing_id) and exists(select 1 from public.pf_positions p where p.id=position_id));
create policy pf_interest_read on public.pf_interests for select to anon,authenticated using(
 review_status='published' and exists(select 1 from public.pf_filings f where f.id=filing_id));
create policy pf_request_read on public.pf_requests for select to anon,authenticated using(
 public_visible and exists(select 1 from public.pf_organizations o where o.id=organization_id));

revoke all on public.pf_organizations,public.pf_people,public.pf_positions,public.pf_documents,public.pf_filings,public.pf_filing_positions,public.pf_interests,public.pf_requests from public,anon,authenticated;
grant select on public.pf_organizations,public.pf_people,public.pf_positions,public.pf_documents,public.pf_filings,public.pf_filing_positions,public.pf_interests,public.pf_requests to anon,authenticated;
grant all on public.pf_organizations,public.pf_people,public.pf_positions,public.pf_documents,public.pf_filings,public.pf_filing_positions,public.pf_interests,public.pf_requests to service_role;
commit;

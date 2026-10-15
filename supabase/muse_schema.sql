-- Muse automation schema
create extension if not exists "pgcrypto";

create table if not exists muse_runs (
  id uuid primary key default gen_random_uuid(),
  run_at timestamptz default now(),
  status text not null check (status in ('online','degraded','offline')),
  summary text,
  created_at timestamptz default now()
);

create table if not exists muse_daily_briefs (
  id uuid primary key default gen_random_uuid(),
  brief_date date not null,
  title text not null,
  summary text,
  source_url text,
  created_at timestamptz default now()
);

create table if not exists muse_incidents (
  id uuid primary key default gen_random_uuid(),
  incident_date date not null,
  title text not null,
  summary text,
  severity text default 'info',
  resolved boolean default false,
  created_at timestamptz default now()
);

create table if not exists muse_record_queue (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source_url text,
  drive_file_id text,
  category text,
  record_date date,
  deadline date,
  status text default 'needs_review' check (status in ('needs_review','approved','published','archived')),
  signal_draft text,
  created_at timestamptz default now()
);

create table if not exists muse_automations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  status text default 'ready' check (status in ('ready','running','paused','error')),
  last_run timestamptz,
  next_run timestamptz,
  created_at timestamptz default now()
);

alter table muse_runs enable row level security;
alter table muse_daily_briefs enable row level security;
alter table muse_incidents enable row level security;
alter table muse_record_queue enable row level security;
alter table muse_automations enable row level security;

create policy "public read muse status" on muse_runs for select using (true);
create policy "public read muse briefs" on muse_daily_briefs for select using (true);
create policy "public read muse incidents" on muse_incidents for select using (true);
create policy "public read approved records" on muse_record_queue for select using (status in ('approved','published'));
create policy "public read automations" on muse_automations for select using (true);
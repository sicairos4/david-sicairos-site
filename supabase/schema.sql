-- =============================================
-- 209 CONTROL PANEL — SUPABASE SCHEMA
-- Run in Supabase SQL Editor
-- =============================================

create extension if not exists "pgcrypto";

-- Products synced from Ecwid
create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  ecwid_product_id text unique,
  name text not null,
  sku text,
  price numeric(10,2),
  compare_at_price numeric(10,2),
  currency text default 'USD',
  description text,
  image_url text,
  product_url text,
  category text,
  tags text[] default '{}',
  featured boolean default false,
  active boolean default true,
  priority_score numeric(5,2) default 0,
  stock integer,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Approved site updates: 209 Signal, Record Watch, ecosystem cards
create table if not exists public.site_updates (
  id uuid primary key default gen_random_uuid(),
  source text not null default 'manual',
  kind text not null check (kind in ('record_watch','signal','ecosystem','announcement')),
  title text not null,
  summary text,
  body text,
  link_url text,
  image_url text,
  brand text check (brand in ('dbeastco','209audit','209media','systems_studio','general')),
  status text not null default 'draft' check (status in ('draft','pending_review','approved','published','archived')),
  priority integer default 0,
  utm_campaign text,
  published_at timestamptz,
  expires_at timestamptz,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Homepage slides and ecosystem promos
create table if not exists public.experience_slides (
  id uuid primary key default gen_random_uuid(),
  placement text not null check (placement in ('hero','ecosystem','dbeastco_featured')),
  headline text not null,
  subheadline text,
  cta_label text,
  cta_url text,
  image_url text,
  brand text check (brand in ('dbeastco','209audit','209media','systems_studio','general')),
  active boolean default true,
  priority integer default 0,
  start_at timestamptz,
  end_at timestamptz,
  meta jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Updated-at triggers
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists products_touch on public.products;
create trigger products_touch before update on public.products
for each row execute function public.touch_updated_at();

drop trigger if exists site_updates_touch on public.site_updates;
create trigger site_updates_touch before update on public.site_updates
for each row execute function public.touch_updated_at();

drop trigger if exists experience_slides_touch on public.experience_slides;
create trigger experience_slides_touch before update on public.experience_slides
for each row execute function public.touch_updated_at();

-- Row-level security
alter table public.products enable row level security;
alter table public.site_updates enable row level security;
alter table public.experience_slides enable row level security;

-- Public read: only published/approved/active records
create policy "public_read_products" on public.products
for select using (active = true);

create policy "public_read_published_updates" on public.site_updates
for select using (status = 'published');

create policy "public_read_active_slides" on public.experience_slides
for select using (active = true);

-- Authenticated users can manage content
create policy "authenticated_manage_products" on public.products
for all to authenticated using (true) with check (true);

create policy "authenticated_manage_updates" on public.site_updates
for all to authenticated using (true) with check (true);

create policy "authenticated_manage_slides" on public.experience_slides
for all to authenticated using (true) with check (true);

-- Useful indexes
create index if not exists products_featured_idx on public.products (featured, priority_score desc);
create index if not exists products_active_idx on public.products (active, updated_at desc);
create index if not exists site_updates_status_idx on public.site_updates (status, priority desc, published_at desc);
create index if not exists experience_slides_placement_idx on public.experience_slides (placement, active, priority desc);
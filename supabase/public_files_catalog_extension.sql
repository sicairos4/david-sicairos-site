-- Applied to the existing Public Files project; access policies unchanged.
begin;
alter table public.pf_documents add column if not exists title text;
alter table public.pf_documents add column if not exists description text;
alter table public.pf_documents add column if not exists agency text;
alter table public.pf_documents add column if not exists document_type text;
alter table public.pf_documents add column if not exists document_date date;
alter table public.pf_documents add column if not exists keywords text[] not null default '{}';
commit;

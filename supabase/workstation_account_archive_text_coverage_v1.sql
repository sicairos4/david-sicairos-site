-- Applied to uwidjnnhdgtrpsymuhwp on 2026-10-28 via approved migration.
-- Source record only: do not rerun against that database.
-- No export, account deletion or access-policy change is performed here.
alter table public.audit_archive_pages add column export_id uuid not null default gen_random_uuid();
create unique index audit_archive_pages_owner_export_id_idx on public.audit_archive_pages(owner_id,export_id);
comment on column public.audit_archive_pages.export_id is 'Technical account-export pagination key; not an original-file identity or provenance hash.';
create or replace function public.workstation_account_spec()
returns table(table_key text,owner_key text,cursor_key text,purge_order integer)
language sql immutable set search_path=''
as $function$
values
 ('audit_archive_pages','owner_id','export_id',1),
 ('audit_archive_extractions','owner_id','document_id',2),
 ('audit_archive_events','owner_id','id',10),
 ('audit_archive_requests','owner_id','id',20),
 ('audit_archive_documents','owner_id','id',30),
 ('intentional_days','user_id','day',40),
 ('intentional_digests','user_id','run_key',50),
 ('intentional_preferences','user_id','user_id',60),
 ('intentional_toolkit','user_id','user_id',70),
 ('routines','user_id','id',80),
 ('projects','user_id','id',90),
 ('journal_entries','user_id','id',100),
 ('user_skills','user_id','id',110),
 ('public_profiles','user_id','id',120),
 ('content_studio','user_id','id',130),
 ('brand_genesis','user_id','id',140),
 ('strategic_blueprints','user_id','id',150),
 ('brand_assets','user_id','id',160),
 ('dynamic_schedules','user_id','id',170),
 ('ai_weekly_synthesis','user_id','id',180),
 ('course_enrollments','user_id','id',190),
 ('course_reviews','user_id','id',200),
 ('notifications','user_id','id',210),
 ('guild_memberships','user_id','id',220),
 ('member_engagement_queue','user_id','id',230),
 ('audience_contacts','user_id','id',240),
 ('community_messages','user_id','id',250),
 ('profiles','user_id','id',260),
 ('users','id','id',270);
$function$;
comment on function public.workstation_account_spec() is '29 registered account-owned tables, including private archive extraction/page text. Children precede document parents for controlled self-deletion. Existing manifest, pagination, authentication, confirmation and operator blockers are unchanged. External file contents, provider accounts and retained backups remain excluded.';

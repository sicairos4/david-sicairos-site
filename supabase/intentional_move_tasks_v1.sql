-- Source-only migration. Apply separately with explicit authorization.
begin;
create function public.intentional_move_tasks_v1(
 p_from_day date, p_to_day date, p_task_ids text[],
 p_from_revision integer, p_to_revision integer
) returns jsonb
language plpgsql security definer set search_path to ''
as $function$
declare
 v_uid uuid := auth.uid();
 v_from public.intentional_days%rowtype;
 v_to public.intentional_days%rowtype;
 v_to_exists boolean;
 v_day date;
 v_ids_count integer;
 v_unique_count integer;
 v_selected jsonb;
 v_remaining jsonb;
 v_target_plan jsonb;
 v_source_plan jsonb;
 v_next_from integer;
 v_next_to integer;
 v_count integer;
begin
 if v_uid is null then raise exception 'AUTH_REQUIRED'; end if;
 if p_from_day is null or p_to_day is null or p_from_day=p_to_day then raise exception 'MOVE_INVALID_DAYS'; end if;
 if p_from_revision is null or p_from_revision<1 or (p_to_revision is not null and p_to_revision<1) then raise exception 'MOVE_INVALID_REVISION'; end if;
 if p_task_ids is null or pg_catalog.cardinality(p_task_ids)<1 or pg_catalog.cardinality(p_task_ids)>100 or pg_catalog.array_ndims(p_task_ids)<>1 then raise exception 'MOVE_SELECT_1_TO_100_TASKS'; end if;
 select count(*),count(distinct id) into v_ids_count,v_unique_count from pg_catalog.unnest(p_task_ids) as ids(id);
 if v_ids_count<>v_unique_count or exists(select 1 from pg_catalog.unnest(p_task_ids) as ids(id) where id is null or length(id)=0 or length(id)>100) then raise exception 'MOVE_INVALID_TASK_IDS'; end if;
 -- Use exactly the existing save RPC lock key, acquired in date order.
 for v_day in select d from (values(p_from_day),(p_to_day)) as days(d) order by d loop
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(v_uid::text||v_day::text,0));
 end loop;
 select d.* into v_from from public.intentional_days d where d.user_id=v_uid and d.day=p_from_day;
 if not found then raise exception 'MOVE_SOURCE_NOT_SAVED'; end if;
 select d.* into v_to from public.intentional_days d where d.user_id=v_uid and d.day=p_to_day;
 v_to_exists := found;
 if v_from.revision is distinct from p_from_revision or v_to.revision is distinct from p_to_revision then raise exception 'REVISION_CONFLICT'; end if;
 if v_to_exists and v_to.revision is null then raise exception 'MOVE_INVALID_TARGET'; end if;
 v_source_plan := v_from.plan;
 if v_to_exists then v_target_plan := v_to.plan;
 else v_target_plan := '{"workspaceTasks":[],"scheduleBlocks":[],"goalEntries":[]}'::jsonb; end if;
 if pg_catalog.jsonb_typeof(v_source_plan) is distinct from 'object' or pg_catalog.jsonb_typeof(v_target_plan) is distinct from 'object' then raise exception 'MOVE_INVALID_PLAN'; end if;
 if pg_catalog.jsonb_typeof(v_source_plan->'workspaceTasks') is distinct from 'array' or pg_catalog.jsonb_typeof(v_target_plan->'workspaceTasks') is distinct from 'array' or pg_catalog.jsonb_typeof(v_source_plan->'scheduleBlocks') is distinct from 'array' then raise exception 'MOVE_INVALID_PLAN_ARRAYS'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_source_plan->'workspaceTasks') as tasks(t) where pg_catalog.jsonb_typeof(t) is distinct from 'object' or pg_catalog.jsonb_typeof(t->'id') is distinct from 'string' or coalesce(t->>'id','')='') or exists(select 1 from pg_catalog.jsonb_array_elements(v_target_plan->'workspaceTasks') as tasks(t) where pg_catalog.jsonb_typeof(t) is distinct from 'object' or pg_catalog.jsonb_typeof(t->'id') is distinct from 'string' or coalesce(t->>'id','')='') then raise exception 'MOVE_INVALID_SAVED_TASKS'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_source_plan->'workspaceTasks') as tasks(t) group by t->>'id' having count(*)>1) or exists(select 1 from pg_catalog.jsonb_array_elements(v_target_plan->'workspaceTasks') as tasks(t) group by t->>'id' having count(*)>1) then raise exception 'MOVE_DUPLICATE_SAVED_IDS'; end if;
 select coalesce(pg_catalog.jsonb_agg(t order by ord),'[]'::jsonb) into v_selected from pg_catalog.jsonb_array_elements(v_source_plan->'workspaceTasks') with ordinality as tasks(t,ord) where (t->>'id')=any(p_task_ids);
 v_count := pg_catalog.jsonb_array_length(v_selected);
 if v_count<>v_ids_count then raise exception 'MOVE_TASK_NOT_FOUND'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_selected) as tasks(t) where t->'done' is distinct from 'false'::jsonb) then raise exception 'MOVE_UNFINISHED_TASKS_ONLY'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_selected) as tasks(t) where coalesce(t->>'goalId','')<>'') then raise exception 'MOVE_MILESTONE_LINK_REQUIRES_REVIEW'; end if;
 if coalesce(v_source_plan->>'focusTaskId','')=any(p_task_ids) then raise exception 'MOVE_FOCUS_LINK_REQUIRES_REVIEW'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_source_plan->'scheduleBlocks') as blocks(b) where (b->>'taskId')=any(p_task_ids)) then raise exception 'MOVE_SCHEDULE_LINK_REQUIRES_REVIEW'; end if;
 if exists(select 1 from pg_catalog.jsonb_array_elements(v_target_plan->'workspaceTasks') as tasks(t) where (t->>'id')=any(p_task_ids)) then raise exception 'MOVE_TARGET_ID_COLLISION'; end if;
 select coalesce(pg_catalog.jsonb_agg(t order by ord),'[]'::jsonb) into v_remaining from pg_catalog.jsonb_array_elements(v_source_plan->'workspaceTasks') with ordinality as tasks(t,ord) where not ((t->>'id')=any(p_task_ids));
 v_source_plan := pg_catalog.jsonb_set(v_source_plan,'{workspaceTasks}',v_remaining,false);
 v_target_plan := pg_catalog.jsonb_set(v_target_plan,'{workspaceTasks}',(v_target_plan->'workspaceTasks')||v_selected,false);
 -- Both calls execute inside this transaction; a failure rolls back both.
 v_next_from := public.intentional_save_day(p_from_day,v_source_plan,v_from.journal,v_from.lesson,p_from_revision);
 v_next_to := public.intentional_save_day(p_to_day,v_target_plan,coalesce(v_to.journal,''),coalesce(v_to.lesson,''),p_to_revision);
 return pg_catalog.jsonb_build_object('version',1,'from_day',p_from_day,'to_day',p_to_day,'from_revision',v_next_from,'to_revision',v_next_to,'moved_count',v_count,'task_ids',p_task_ids);
end;
$function$;
revoke all on function public.intentional_move_tasks_v1(date,date,text[],integer,integer) from public,anon,authenticated;
grant execute on function public.intentional_move_tasks_v1(date,date,text[],integer,integer) to authenticated;
commit;

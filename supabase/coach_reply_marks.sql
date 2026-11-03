-- Respuestas de coaches marcadas desde el mail semanal (Smartrecruit).
-- Ejecutar en Supabase: SQL Editor → New query → pegar y correr. Se puede correr más de una vez.
-- Requiere haber corrido antes email_reminders.sql.
--
-- Flujo: el mail trae /respuesta?token=<unsub_token>&u=<Universidad>. La persona elige qué pasó y confirma con un clic
-- (sin iniciar sesión). La función guarda una marca; cuando la persona entra al sitio, se aplica a su registro de envíos y se borra.

create table if not exists public.coach_reply_marks (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  university text not null check (char_length(university) between 1 and 80),
  status     text not null check (status in ('respondio','visita','oferta','rechazo')),
  created_at timestamptz not null default now()
);
create index if not exists coach_reply_marks_user_idx on public.coach_reply_marks (user_id);

alter table public.coach_reply_marks enable row level security;
drop policy if exists "marks_select_own" on public.coach_reply_marks;
drop policy if exists "marks_delete_own" on public.coach_reply_marks;
create policy "marks_select_own" on public.coach_reply_marks for select to authenticated using (auth.uid() = user_id);
create policy "marks_delete_own" on public.coach_reply_marks for delete to authenticated using (auth.uid() = user_id);

revoke all on public.coach_reply_marks from anon, authenticated;
grant select, delete on public.coach_reply_marks to authenticated;

-- Marca con un clic desde el link del mail. El token identifica a la persona; solo permite estos 4 estados.
-- Tope de 50 marcas pendientes por persona para que un link filtrado no pueda llenar la tabla.
create or replace function public.mark_coach_reply(p_token uuid, p_university text, p_status text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare v_user uuid;
begin
  if p_status not in ('respondio','visita','oferta','rechazo') then return false; end if;
  if p_university is null or char_length(p_university) not between 1 and 80 then return false; end if;
  select user_id into v_user from public.email_reminders where unsub_token = p_token;
  if v_user is null then return false; end if;
  if (select count(*) from public.coach_reply_marks where user_id = v_user) >= 50 then return false; end if;
  insert into public.coach_reply_marks (user_id, university, status) values (v_user, p_university, p_status);
  return true;
end;
$$;
revoke all on function public.mark_coach_reply(uuid, text, text) from public;
grant execute on function public.mark_coach_reply(uuid, text, text) to anon, authenticated;

select relname, relrowsecurity as rls_activo from pg_class where relname = 'coach_reply_marks';

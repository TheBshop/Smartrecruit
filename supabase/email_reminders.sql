-- Recordatorios semanales por email (Smartrecruit).
-- Ejecutar en Supabase: SQL Editor → New query → pegar y correr. Se puede correr más de una vez.
--
-- Cómo funciona:
--   · La persona (con cuenta) activa el recordatorio desde "Mi plan de hoy". Se guarda una fila acá.
--   · El sitio guarda en `digest` un resumen corto (etapa, próxima acción, resumen de la semana).
--   · Cada domingo a las 19 h (hora de Argentina) una función de Supabase manda un mail con ese resumen, usando Resend.
--   · El mail va SIEMPRE al correo con el que la persona inició sesión (no se puede poner otro: lo controla la regla de abajo).
--   · Cada mail trae un link de baja: https://smartrecruit.com.ar/baja?token=...

create table if not exists public.email_reminders (
  user_id      uuid primary key references auth.users(id) on delete cascade,
  email        text not null,
  enabled      boolean not null default false,
  consent_at   timestamptz,
  digest       jsonb not null default '{}'::jsonb,
  unsub_token  uuid not null default gen_random_uuid(),
  last_sent_at timestamptz,
  updated_at   timestamptz not null default now()
);

alter table public.email_reminders enable row level security;

drop policy if exists "reminders_select_own" on public.email_reminders;
drop policy if exists "reminders_insert_own" on public.email_reminders;
drop policy if exists "reminders_update_own" on public.email_reminders;

create policy "reminders_select_own" on public.email_reminders
  for select to authenticated using (auth.uid() = user_id);

-- El correo tiene que ser el de la cuenta: así nadie puede usar esto para mandar mails a terceros.
create policy "reminders_insert_own" on public.email_reminders
  for insert to authenticated
  with check (auth.uid() = user_id and lower(email) = lower(auth.jwt() ->> 'email'));

create policy "reminders_update_own" on public.email_reminders
  for update to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id and lower(email) = lower(auth.jwt() ->> 'email'));

-- Sin política de borrado: la fila se borra sola si se elimina la cuenta (on delete cascade).

-- Permisos mínimos: el sitio no toca last_sent_at ni unsub_token.
revoke all on public.email_reminders from anon, authenticated;
grant select on public.email_reminders to authenticated;
grant insert (user_id, email, enabled, consent_at, digest, updated_at) on public.email_reminders to authenticated;
grant update (email, enabled, consent_at, digest, updated_at) on public.email_reminders to authenticated;

-- Baja con un clic desde el link del mail (no hace falta iniciar sesión: el token viaja en el link).
create or replace function public.unsubscribe_reminders(p_token uuid)
returns boolean
language sql
security definer
set search_path = public
as $$
  with u as (
    update public.email_reminders
       set enabled = false, updated_at = now()
     where unsub_token = p_token
    returning 1
  )
  select exists (select 1 from u);
$$;
revoke all on function public.unsubscribe_reminders(uuid) from public;
grant execute on function public.unsubscribe_reminders(uuid) to anon, authenticated;

-- Verificación (correr después): rls_activo debe dar true.
select relname, relrowsecurity as rls_activo from pg_class where relname = 'email_reminders';

-- ─────────────────────────────────────────────────────────────────────────────
-- PASO FINAL (correr recién cuando la función esté desplegada y tenga sus secretos):
-- programa el envío todos los domingos a las 22:00 UTC (19:00 en Argentina).
-- Reemplazá REEMPLAZAR_POR_TU_CRON_SECRET por el mismo valor que cargaste como secreto CRON_SECRET.
--
-- create extension if not exists pg_cron;
-- create extension if not exists pg_net;
-- select cron.schedule(
--   'recordatorios-semanales',
--   '0 22 * * 0',
--   $cron$
--   select net.http_post(
--     url := 'https://dliayalkzvaugukhxmcb.supabase.co/functions/v1/send-weekly-reminders',
--     headers := jsonb_build_object(
--       'Content-Type', 'application/json',
--       'Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsaWF5YWxrenZhdWd1a2h4bWNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1MzkwOTMsImV4cCI6MjA4ODExNTA5M30.vGBprr8FKBxTayS6Q6ZbWIxUZKItY4avgMJbUGgQC1E',
--       'x-cron-secret', 'REEMPLAZAR_POR_TU_CRON_SECRET'
--     ),
--     body := '{}'::jsonb
--   );
--   $cron$
-- );
-- Para pausarlo: select cron.unschedule('recordatorios-semanales');

-- Reglas de acceso para la tabla `profiles` (datos de cuenta de Smartrecruit).
-- Ejecutar en Supabase: SQL Editor → New query → pegar y correr.
-- Objetivo: cada persona solo puede leer y escribir SU fila (id = su usuario de login).
-- La clave pública (anon) que está en el sitio es pública por diseño: estas reglas son lo que la protege.

alter table public.profiles enable row level security;

-- Quitar reglas anteriores que pudieran dejar la tabla abierta (si no existen, no pasa nada).
drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
drop policy if exists "profiles_delete_own" on public.profiles;

create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);

create policy "profiles_insert_own" on public.profiles
  for insert with check (auth.uid() = id);

create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id) with check (auth.uid() = id);

-- Sin política de borrado: nadie puede borrar filas desde el sitio.
-- Para ejecutar la eliminación de cuenta pedida por el titular, se hace desde el panel con permisos de administrador.

-- Verificación (correr después): debe devolver `true` en rowsecurity.
select relname, relrowsecurity as rls_activo from pg_class where relname = 'profiles';

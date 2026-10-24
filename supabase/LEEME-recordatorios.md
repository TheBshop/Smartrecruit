# Recordatorios semanales por email (Resend) — pasos para dejarlo andando

Todo el código ya está en el repo. Falta lo que solo puede hacer el titular de las cuentas.

## 1. Resend (cuenta y dominio)
1. Crear cuenta en https://resend.com.
2. **Domains → Add Domain** → `smartrecruit.com.ar`. Resend muestra registros DNS (SPF, DKIM y uno para el retorno de rebotes).
3. Cargar esos registros en el DNS del dominio (en Cloudflare, con la nube en gris "solo DNS"). Esperar a que Resend marque el dominio como **Verified**.
4. **API Keys → Create API Key** (permiso "Sending access"). Copiar la clave (`re_...`). No pegarla en el chat ni en el repo.

## 2. Base de datos (Supabase → SQL Editor)
1. Pegar y correr `supabase/email_reminders.sql` (sin el bloque comentado del final). Al terminar, la última consulta debe mostrar `rls_activo = true`.
2. Hasta que se corra esto, el tilde de "Recordatorio por email" no aparece en el sitio (no se rompe nada).

## 3. Función (Supabase → Edge Functions)
1. Desplegar la carpeta `supabase/functions/send-weekly-reminders` con el nombre `send-weekly-reminders` (con la CLI: `supabase functions deploy send-weekly-reminders --project-ref dliayalkzvaugukhxmcb`, o desde el panel pegando `index.ts` y `email.ts`).
2. **Edge Functions → Secrets**, cargar:
   - `RESEND_API_KEY` = la clave del paso 1.4
   - `CRON_SECRET` = una clave larga inventada (por ejemplo 40 letras y números al azar)
   - opcional: `REMINDER_FROM` (por defecto `Smartrecruit <recordatorios@smartrecruit.com.ar>`) y `REPLY_TO` (por defecto `contactosmartrecruit@gmail.com`).

## 4. Activar en el sitio
En `RosterReal.jsx`, cambiar `const EMAIL_REMINDERS_LIVE = false;` a `true` y publicar. Hasta entonces el tilde no aparece (a propósito, para no mostrar algo que todavía no funciona).

## 5. Probar antes de programar
1. En el sitio, con tu cuenta iniciada, activar el tilde en "Mi plan de hoy".
2. Prueba en seco (no manda nada, solo muestra cuántos mails correspondería mandar):
   `curl -X POST "https://dliayalkzvaugukhxmcb.supabase.co/functions/v1/send-weekly-reminders?dry=1" -H "Authorization: Bearer <clave anon del sitio>" -H "x-cron-secret: <tu CRON_SECRET>"`
3. Envío real de prueba a vos (ignora el "uno por semana"): lo mismo con `?force=1` en vez de `?dry=1`.
4. Revisar el mail recibido y probar el link "Darme de baja".

## 6. Programar el envío
Correr el bloque comentado al final de `email_reminders.sql` (quitando los `--` y poniendo tu `CRON_SECRET`). Manda todos los domingos a las 19 h de Argentina.

## Cómo está protegido
- El mail solo va al correo con el que la persona inició sesión (lo exige una regla de la base).
- Un menor de 18 solo recibe el recordatorio si tiene la conformidad de un adulto cargada en su perfil.
- Llamar dos veces a la función no duplica mails (un envío por persona cada 6 días).
- Cada mail trae link de baja (`/baja?token=...`), con confirmación.
- La Política de Privacidad ya menciona a Resend y el recordatorio (versión legal 2026-10-22: las personas con perfil van a tener que volver a aceptar).

## Eliminar cuenta (función `delete-account`)
Pegar `supabase/functions/delete-account/index.ts` como una función nueva llamada `delete-account` (Edge Functions → Deploy a new function → Via Editor).
No necesita secretos. Dejar activada la verificación de JWT. El botón "Eliminar mi cuenta" del sitio la llama.

[LEEME.md](https://github.com/user-attachments/files/33037386/LEEME.md)
# Smartrecruit — código fuente

- `RosterReal.jsx`: toda la app (datos + interfaz). Es el archivo que se edita.
- `main.jsx`: arranca la app.
- `public/`: se copia tal cual al sitio. Incluye `index.html` (con PostHog, SEO e ícono), `assets/analytics.js` (PostHog + aviso de cookies), `robots.txt` y `sitemap.xml`.
- `analytics-src/entry.js`: código legible de la analítica (solo hace falta si se cambia).

Compilar: `npm install` y después `npm run build`. El resultado queda en `dist/`, que es la carpeta que se sube a Netlify.

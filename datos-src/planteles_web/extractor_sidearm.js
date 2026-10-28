// Se pega en el navegador (javascript_tool) estando en el sitio deportivo de una universidad (plataforma Sidearm).
// Devuelve texto compacto: estadísticas del año anterior (/stats/AÑO), plantel actual y staff del programa.
// Uso: configurar SPORT ("womens-soccer"), SEASON_STATS ("2025") y SPORT_WORD (/women'?s soccer/i).
(async () => {
  const SPORT = "womens-soccer", SEASON_STATS = "2025", SPORT_RE = /women'?s soccer/i;
  const T = (e) => (e || "").replace(/\s+/g, " ").trim();
  const g = async (u) => { try { const r = await fetch(u); if (!r.ok) return null; return new DOMParser().parseFromString(await r.text(), "text/html"); } catch (e) { return null; } };
  const out = [`HOST ${location.host}`];
  const st = await g(`/sports/${SPORT}/stats/${SEASON_STATS}`);
  if (!st) out.push("STATS none");
  else {
    out.push(`STATS ${T(st.title).slice(0, 60)}`);
    const seen = new Set();
    st.querySelectorAll("table").forEach((t) => {
      const h = [...t.querySelectorAll("thead th, tr:first-child th")].map((x) => T(x.textContent));
      if (!(h.includes("Player") && h.includes("GP") && h.includes("MIN"))) return;
      const gk = h.includes("GAA"); const ix = (k) => h.indexOf(k);
      t.querySelectorAll("tbody tr").forEach((tr) => {
        const cells = [...tr.children]; if (cells.length < 6) return;
        const pc = cells[ix("Player")]; const nm = T((pc.querySelector("a") || pc).textContent);
        if (/^(total|opponents?|team)/i.test(nm)) return;
        const key = (gk ? "G" : "S") + nm; if (seen.has(key)) return; seen.add(key);
        const v = (k) => { const i = ix(k); return i < 0 ? "" : T(cells[i].textContent); };
        out.push(gk ? `G|${nm}|${v("GP")}|${v("GS")}|${v("MIN")}|${v("GA")}|${v("SV")}|${v("W")}|${v("L")}` : `S|${nm}|${v("GP")}|${v("GS")}|${v("MIN")}|${v("G")}|${v("A")}|${v("PTS")}|${v("SH")}|${v("SOG")}`);
      });
    });
  }
  const ro = await g(`/sports/${SPORT}/roster`);
  if (!ro) out.push("ROSTER none");
  else {
    out.push(`ROSTER ${T(ro.title).slice(0, 60)}`);
    ro.querySelectorAll(".sidearm-roster-player").forEach((p) => {
      const q = (s) => T(p.querySelector(s)?.textContent);
      const num = q(".sidearm-roster-player-jersey-number");
      const nm = T((p.querySelector(".sidearm-roster-player-name a") || p.querySelector(".sidearm-roster-player-name") || { textContent: "" }).textContent).replace(/^\d+\s+/, "");
      out.push(`P|${num}|${nm}|${q(".sidearm-roster-player-position").replace(/\s+\d.*$/, "")}|${q(".sidearm-roster-player-academic-year")}|${q(".sidearm-roster-player-hometown")}|${q(".sidearm-roster-player-highschool")}`);
    });
  }
  let sf = null, ded = false; for (const u of [`/sports/${SPORT}/coaches`, `/sports/${SPORT}/staff`, "/staff-directory", "/sports/staff"]) { sf = await g(u); ded = u.includes(`/sports/${SPORT}/`); if (sf && !/not found|404/i.test(sf.title) && (sf.querySelectorAll("tr, .sidearm-coaches-coach, .s-person-card").length > 0)) break; sf = null; }
  if (!sf) out.push("STAFF none");
  else {
    out.push(`STAFF ${T(sf.title).slice(0, 50)}`);
    const dec = (txt, a) => { const m = txt.match(/firstHalf\s*=\s*"([^"]+)";\s*var secondHalf\s*=\s*"([^"]+)"/); if (m) return m[1] + "@" + m[2]; if (a) return (a.getAttribute("href") || "").replace("mailto:", ""); return ""; };
    sf.querySelectorAll("tr, .sidearm-coaches-coach, .s-person-card").forEach((el) => {
      const txt = T(el.textContent); if ((!ded && !SPORT_RE.test(txt)) || txt.length > 900 || !el.querySelector('a[href^="mailto:"]') && !/firstHalf/.test(el.innerHTML)) return;
      const cells = el.tagName === "TR" ? [...el.children].map((x) => T(x.childNodes.length ? x.textContent.replace(/var placeholder[\s\S]*$/, "") : "")) : [T(el.querySelector(".sidearm-coaches-coach-name, .s-person-details__personal-single-line, h3, h2")?.textContent), T(el.querySelector(".sidearm-coaches-coach-title, .s-person-details__title, .s-person-details__position")?.textContent)];
      if (cells.length < 2 || /^women'?s soccer$/i.test(cells[0])) return;
      const em = dec(el.innerHTML.replace(/&quot;/g, '"') + " " + el.textContent, el.querySelector('a[href^="mailto:"]'));
      out.push(`C|${cells[0]}|${cells[1]}|${em}|${(txt.match(/\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}/) || [""])[0]}`);
    });
  }
  return out.join("\n");
})()

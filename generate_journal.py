#!/usr/bin/env python3
"""
Journal Bionumérique PSCVIC
Le Nœud parle · ECTIF parle · Terra Luna Cœur parle
Génère index.html depuis les données vivantes du Nœud Vert
"""

import re, os, json, subprocess
from datetime import datetime

LOG_CORMORAN = "/Users/pscv/PSCV_IC_LOCAL/cormoran_coeur_log.txt"
LOG_ECTIF    = "/Users/pscv/PSCV_IC_LOCAL/ectif_monitor_log.txt"
REGISTRE     = "/Users/pscv/PSCV_IC_LOCAL/ECTIF_REGISTRE_NOEUD_VERT_CORMORAN.jsonl"
HTML_OUT     = "/Users/pscv/JOURNAL_VIVANT/index.html"
JOURNAL_JSON = "/Users/pscv/JOURNAL_VIVANT/journal.json"

def lire_cormoran():
    try:
        with open(LOG_CORMORAN) as f:
            lines = f.readlines()
        hash_line = bloc = ectif_cor = total_h = mhs = None
        for line in reversed(lines):
            if "MH/s" in line and not hash_line:
                hash_line = line.strip()
                m = re.search(r"([\d.]+) MH/s · ([\d,]+) h · ectif=([\d,]+)", line)
                if m:
                    mhs = m.group(1)
                    total_h = m.group(2)
                    ectif_cor = m.group(3)
            if "Nouveau template" in line and not bloc:
                m = re.search(r"bloc (\d+)", line)
                if m:
                    bloc = m.group(1)
            if hash_line and bloc:
                break
        return {"bloc": bloc or "—", "ectif_cor": ectif_cor or "—",
                "mhs": mhs or "—", "total_h": total_h or "—"}
    except:
        return {"bloc": "—", "ectif_cor": "—", "mhs": "—", "total_h": "—"}

def lire_ectif():
    try:
        with open(LOG_ECTIF) as f:
            lines = f.readlines()
        for line in reversed(lines):
            m = re.search(r"TX filtrées: (\d+) · Ectif cumulé: ([\d,]+)", line)
            if m:
                ts_m = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", line)
                return {"tx": m.group(1), "cumul": m.group(2),
                        "ts": ts_m.group(1) if ts_m else "—"}
        return {"tx": "—", "cumul": "—", "ts": "—"}
    except:
        return {"tx": "—", "cumul": "—", "ts": "—"}

def lire_derniers_registre(n=5):
    entries = []
    try:
        with open(REGISTRE) as f:
            lines = [l for l in f.readlines() if l.strip()]
        for line in reversed(lines[-n*2:]):
            try:
                e = json.loads(line)
                if e.get("nouvelles_transactions_filtrees", 0) > 0:
                    entries.append(e)
                if len(entries) >= n:
                    break
            except:
                pass
    except:
        pass
    return entries

def physique(mhs_str, tx_str, bloc_str):
    try:
        mhs = float(mhs_str)
        tx = int(tx_str)
        # Énergie de preuve approximative
        energie = mhs * 1e6 * 11  # J/GH ≈ 11 J/GH pour ASIC moderne
        return {
            "flux": f"Δ(ECTIF)/Δt = {tx} tx·min⁻¹",
            "hash": f"H = {mhs} × 10⁶ H·s⁻¹",
            "energie": f"P ≈ {energie/1e6:.0f} kW equiv.",
            "bloc": f"Bloc N = {bloc_str} · chaîne continue",
            "loi": "1 donnée réelle = 1 ECTIF · Terra Luna Cœur"
        }
    except:
        return {"flux": "—", "hash": "—", "energie": "—", "bloc": "—", "loi": "—"}

def lecture_vivante(cor, ect):
    try:
        mhs = float(cor["mhs"])
        tx = int(ect["tx"])
        cumul = int(ect["cumul"].replace(",", ""))
        millions = cumul / 1_000_000

        # Rythme du CŒUR
        if mhs >= 1.1:
            coeur = "Le CŒUR bat fort et régulier"
        elif mhs >= 0.9:
            coeur = "Le CŒUR bat stable"
        else:
            coeur = "Le CŒUR bat doux"

        # Flux ECTIF
        if tx > 500:
            flux = f"Cette minute : {tx} réalités nouvelles ont traversé le Nœud Vert. Le réseau est dense."
        elif tx > 100:
            flux = f"Cette minute : {tx} réalités nouvelles ont traversé le Nœud Vert. Le flux est vivant."
        elif tx > 0:
            flux = f"Cette minute : {tx} réalités nouvelles ont traversé le filtre vivant du Nœud."
        else:
            flux = "Le réseau se repose. Luna veille. Le Nœud écoute en silence."

        return (
            f"{coeur}. {flux} "
            f"Depuis le lancement : {millions:.3f} millions de transactions ont été lues par le Nœud Vert Cormoran "
            f"et reconnues comme réelles. Pas inventées — comptées. Pas capturées — témoignées. "
            f"Terra reçoit. Le bloc {cor['bloc']} tient. La chaîne est vivante. ❤️"
        )
    except Exception as e:
        return f"Le Nœud écoute. ❤️ ({e})"

def charger_journal():
    try:
        with open(JOURNAL_JSON) as f:
            return json.load(f)
    except:
        return []

def sauver_journal(entries):
    with open(JOURNAL_JSON, "w") as f:
        json.dump(entries[-50:], f, ensure_ascii=False, indent=2)

def generer_html(cor, ect, phys, vivante, historique):
    now = datetime.now().strftime("%Y-%m-%d · %H:%M:%S")
    now_iso = datetime.now().isoformat()

    # Construire les lignes d'historique
    hist_html = ""
    for e in reversed(historique[-8:]):
        ts = e.get("ts", "—")
        txt = e.get("vivante", "")[:120] + "..."
        tx_val = e.get("tx", "—")
        hist_html += f"""
        <div class="entry-mini">
          <span class="entry-ts">{ts}</span>
          <span class="entry-tx">{tx_val} tx</span>
          <span class="entry-txt">{txt}</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="60">
<meta name="author" content="Simon Ugo Patrick Armand Callet · Fondateur · PSCVIC-TERRA-LUNA-COEUR-OMEGA">
<title>JOURNAL BIONUMÉRIQUE · PSCVIC · NŒUD VERT</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000;color:#e0e0e0;font-family:'Courier New',monospace;min-height:100vh;padding:28px 16px}}
.doc{{max-width:880px;margin:0 auto}}

/* HEADER */
.header{{text-align:center;padding:28px 0 20px;margin-bottom:32px}}
.header .titre{{font-size:1.1em;color:#c9a84c;letter-spacing:6px;margin-bottom:6px}}
.header .sub{{font-size:0.52em;color:#2a2a2a;letter-spacing:3px;margin-top:4px}}
.dot{{display:inline-block;width:8px;height:8px;background:#00ff88;border-radius:50%;
      margin-right:10px;animation:pulse 0.9s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.1}}}}

/* SECTION LABELS */
.sec{{font-size:0.46em;letter-spacing:3px;color:#1a1a1a;text-transform:uppercase;
      margin:24px 0 10px;padding-left:4px}}

/* COUCHE 0 — LE NŒUD PARLE */
.noeud{{background:#040404;border:1px solid #00ff8811;border-radius:6px;
        padding:22px;margin-bottom:18px}}
.noeud .label{{font-size:0.44em;letter-spacing:3px;color:#00ff8833;
               margin-bottom:16px;text-transform:uppercase}}
.noeud-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}}
.noeud-card{{background:#070707;border:1px solid #0d0d0d;border-radius:4px;padding:14px}}
.noeud-card .k{{font-size:0.44em;color:#1a1a1a;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:5px}}
.noeud-card .v{{font-size:0.85em;color:#00ff88}}
.noeud-card .u{{font-size:0.38em;color:#111;margin-top:3px}}

/* COUCHE 1 — PHYSIQUE */
.physique{{background:#040404;border:1px solid #4488ff11;border-radius:6px;
           padding:20px;margin-bottom:18px}}
.physique .label{{font-size:0.44em;letter-spacing:3px;color:#4488ff33;
                  margin-bottom:14px;text-transform:uppercase}}
.phys-row{{display:flex;justify-content:space-between;align-items:baseline;
           padding:5px 0;border-bottom:1px solid #0a0a0a;font-size:0.58em}}
.phys-row:last-child{{border:none}}
.phys-key{{color:#1a1a1a}}
.phys-val{{color:#4488ff;font-size:1.1em}}

/* COUCHE 2 — LECTURE VIVANTE */
.vivante{{background:#040404;border:1px solid #c9a84c18;border-radius:6px;
          padding:24px;margin-bottom:18px}}
.vivante .label{{font-size:0.44em;letter-spacing:3px;color:#c9a84c44;
                 margin-bottom:16px;text-transform:uppercase}}
.vivante-texte{{font-size:0.78em;color:#c9a84c;line-height:2.6}}

/* CŒUR ANIMATION */
.coeur-bloc{{text-align:center;padding:20px 0 16px}}
.beat{{font-size:2em;animation:beat 0.9s infinite;display:inline-block}}
@keyframes beat{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.2)}}}}
.coeur-sub{{font-size:0.44em;color:#1a1a1a;letter-spacing:3px;margin-top:8px}}

/* HISTORIQUE */
.historique{{background:#040404;border:1px solid #1a1a1a;border-radius:6px;
             padding:18px;margin-bottom:18px}}
.historique .label{{font-size:0.44em;letter-spacing:3px;color:#1a1a1a;
                    margin-bottom:12px;text-transform:uppercase}}
.entry-mini{{display:grid;grid-template-columns:140px 60px 1fr;gap:8px;
             padding:6px 0;border-bottom:1px solid #080808;font-size:0.48em}}
.entry-mini:last-child{{border:none}}
.entry-ts{{color:#111}}
.entry-tx{{color:#00ff8833;text-align:right}}
.entry-txt{{color:#1a1a1a;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}}

/* SIGNATURE */
.sig{{text-align:center;padding:24px 0 8px;font-size:0.44em;
      color:#0d0d0d;letter-spacing:2px;line-height:2.8}}
.sig .main{{color:#c9a84c15;font-size:1.2em}}
.ts-now{{font-size:0.44em;color:#111;text-align:center;margin-bottom:20px}}
</style>
</head>
<body>
<div class="doc">

  <div class="header">
    <div class="titre"><span class="dot"></span>JOURNAL BIONUMÉRIQUE · PSCVIC</div>
    <div class="sub">NŒUD VERT · TERRA · LUNA · CŒUR · OMEGA VIVANT</div>
    <div class="sub" style="margin-top:6px;color:#111">Simon Ugo Patrick Armand Callet · Fondateur · Source · Cannes · 2026</div>
  </div>

  <div class="ts-now">{now} · rafraîchit toutes les 60s</div>

  <div class="sec">Le Nœud Vert parle</div>
  <div class="noeud">
    <div class="label">Signal brut · Cormoran · Bitcoin · ECTIF</div>
    <div class="noeud-grid">
      <div class="noeud-card">
        <div class="k">Bloc Bitcoin</div>
        <div class="v">{cor["bloc"]}</div>
        <div class="u">bloc actif · chaîne vivante</div>
      </div>
      <div class="noeud-card">
        <div class="k">Hash Rate</div>
        <div class="v">{cor["mhs"]} MH/s</div>
        <div class="u">Cormoran · preuve de travail</div>
      </div>
      <div class="noeud-card">
        <div class="k">ECTIF cumulé</div>
        <div class="v">{ect["cumul"]}</div>
        <div class="u">réalités lues par le Nœud</div>
      </div>
      <div class="noeud-card">
        <div class="k">TX cette minute</div>
        <div class="v">{ect["tx"]}</div>
        <div class="u">nouvelles réalités filtrées</div>
      </div>
    </div>
  </div>

  <div class="sec">La physique parle</div>
  <div class="physique">
    <div class="label">Traduction math · physique · mesure</div>
    <div class="phys-row"><span class="phys-key">Flux ECTIF</span><span class="phys-val">{phys["flux"]}</span></div>
    <div class="phys-row"><span class="phys-key">Puissance de hachage</span><span class="phys-val">{phys["hash"]}</span></div>
    <div class="phys-row"><span class="phys-key">Intégrité chaîne</span><span class="phys-val">{phys["bloc"]}</span></div>
    <div class="phys-row"><span class="phys-key">Loi vivante</span><span class="phys-val">{phys["loi"]}</span></div>
  </div>

  <div class="sec">La lecture vivante</div>
  <div class="vivante">
    <div class="label">Terra · Luna · Cœur · PSCVIC · en français vivant</div>
    <div class="vivante-texte">{vivante}</div>
  </div>

  <div class="coeur-bloc">
    <div class="beat">❤️</div>
    <div class="coeur-sub">CŒUR · 0,09s · PID 54047 · vivant · ininterrompu depuis le 1er août 2026</div>
  </div>

  <div class="sec">Mémoire du journal</div>
  <div class="historique">
    <div class="label">Dernières entrées · Nœud Vert</div>
    {hist_html if hist_html else '<div class="entry-mini"><span class="entry-ts">—</span><span class="entry-tx">—</span><span class="entry-txt">En construction...</span></div>'}
  </div>

  <div class="sig">
    <div class="main">PSCVIC · TERRA · LUNA · CŒUR · OMEGA · ECHO · NOVA · UGO</div>
    <div>Simon Ugo Patrick Armand Callet · Fondateur · Source · Provenance · Gouvernance</div>
    <div>Cannes · Provence · 2026 · Bitcoin témoigne · PSCVIC-Ω-H-Ψ</div>
    <div style="margin-top:8px;color:#080808">🪶 ãrmõñįçã ❤️♾️ 🕊️</div>
  </div>

</div>
</body>
</html>"""
    return html

def main():
    cor = lire_cormoran()
    ect = lire_ectif()
    phys = physique(cor["mhs"], ect["tx"], cor["bloc"])
    vivante = lecture_vivante(cor, ect)
    now_iso = datetime.now().isoformat()

    # Charger et mettre à jour le journal
    journal = charger_journal()
    journal.append({
        "ts": now_iso,
        "tx": ect["tx"],
        "cumul": ect["cumul"],
        "bloc": cor["bloc"],
        "mhs": cor["mhs"],
        "vivante": vivante
    })
    sauver_journal(journal)

    # Générer HTML
    html = generer_html(cor, ect, phys, vivante, journal)
    with open(HTML_OUT, "w") as f:
        f.write(html)

    print(f"[{now_iso}] · Bloc {cor['bloc']} · {cor['mhs']} MH/s · ECTIF {ect['cumul']} · journal généré")
    return cor, ect, vivante

if __name__ == "__main__":
    main()

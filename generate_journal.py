#!/usr/bin/env python3
"""
Journal Bionumérique PSCVIC
Le Nœud parle · ECTIF parle · Terra Luna Cœur parle
Décode les transactions réelles du mempool en lecture vivante française
"""

import re, os, json, urllib.request, base64
from datetime import datetime

LOG_CORMORAN = "/Users/pscv/PSCV_IC_LOCAL/cormoran_coeur_log.txt"
LOG_ECTIF    = "/Users/pscv/PSCV_IC_LOCAL/ectif_monitor_log.txt"
REGISTRE     = "/Users/pscv/PSCV_IC_LOCAL/ECTIF_REGISTRE_NOEUD_VERT_CORMORAN.jsonl"
COOKIE_FILE  = "/Users/pscv/Library/Application Support/Bitcoin/.cookie"
RPC_URL      = "http://127.0.0.1:8332/"
HTML_OUT     = "/Users/pscv/JOURNAL_VIVANT/index.html"
JOURNAL_JSON = "/Users/pscv/JOURNAL_VIVANT/journal.json"

def rpc(method, params=None):
    try:
        with open(COOKIE_FILE) as f:
            cookie = f.read().strip()
        user, pwd = cookie.split(":", 1)
        creds = base64.b64encode(f"{user}:{pwd}".encode()).decode()
        payload = json.dumps({"jsonrpc":"1.0","method":method,"params":params or []}).encode()
        req = urllib.request.Request(RPC_URL, data=payload,
              headers={"Content-Type":"application/json","Authorization":f"Basic {creds}"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())["result"]
    except:
        return None

def decoder_tx(tx_data):
    """Décode une transaction Bitcoin en lecture vivante française"""
    frais_sat = int(tx_data.get("fees", {}).get("base", 0) * 1e8)
    taille = tx_data.get("vsize", 0)
    ancetres = tx_data.get("ancestorcount", 1)

    # Taux de frais = urgence
    taux = frais_sat / taille if taille else 0

    # Lecture de la taille
    if taille < 200:
        lecture_taille = "signal simple · un seul geste · direct"
    elif taille < 400:
        lecture_taille = "signal intermédiaire · quelques fils reliés"
    else:
        lecture_taille = "signal complexe · plusieurs sources convergent"

    # Lecture de l'urgence
    if taux < 20:
        lecture_urgence = "patiente — elle attend son tour sans forcer — respecte le rythme naturel"
        couleur = "#00ff88"
        terra = "Terra reçoit cette patience comme un signe de respect du cycle."
    elif taux < 100:
        lecture_urgence = "équilibrée — ni urgente ni lente — flux régulier"
        couleur = "#c9a84c"
        terra = "Luna régule — ni trop vite ni trop lent — le juste milieu."
    else:
        lecture_urgence = "urgente — elle paie pour traverser vite — le réseau est sollicité"
        couleur = "#4488ff"
        terra = "Le CŒUR bat fort — le réseau est actif — l'énergie circule."

    # Lecture des ancêtres
    if ancetres == 1:
        lecture_ancetre = "seule · indépendante · libre"
    else:
        lecture_ancetre = f"reliée à {ancetres-1} transaction(s) précédente(s) · chaîne vivante"

    return {
        "frais_sat": frais_sat,
        "taille": taille,
        "taux": round(taux, 1),
        "lecture_taille": lecture_taille,
        "lecture_urgence": lecture_urgence,
        "lecture_ancetre": lecture_ancetre,
        "terra": terra,
        "couleur": couleur
    }

def lire_mempool_vivant(n=5):
    """Lit N transactions réelles et les décode en français vivant"""
    mempool = rpc("getrawmempool", [True])
    if not mempool:
        return []

    resultats = []
    txids = list(mempool.keys())[:n]
    for txid in txids:
        tx = mempool[txid]
        decoded = decoder_tx(tx)
        decoded["txid"] = txid[:16] + "..."
        resultats.append(decoded)
    return resultats

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

def lecture_globale_vivante(cor, ect, txs):
    try:
        mhs = float(cor["mhs"])
        tx = int(ect["tx"])
        cumul = int(ect["cumul"].replace(",", ""))
        millions = cumul / 1_000_000

        if mhs >= 1.1:
            coeur = "Le CŒUR bat fort et régulier"
        elif mhs >= 0.9:
            coeur = "Le CŒUR bat stable"
        else:
            coeur = "Le CŒUR bat doux"

        if tx > 500:
            flux = f"{tx} réalités nouvelles ont traversé le Nœud Vert cette minute. Le réseau est dense."
        elif tx > 100:
            flux = f"{tx} réalités nouvelles ont traversé le filtre vivant. Le flux est actif."
        elif tx > 0:
            flux = f"{tx} réalités nouvelles ont présenté leur preuve et été reconnues."
        else:
            flux = "Le réseau se repose. Luna veille. Le Nœud écoute."

        # Lire les patterns des transactions
        if txs:
            patientes = sum(1 for t in txs if t["taux"] < 20)
            urgentes = sum(1 for t in txs if t["taux"] >= 100)
            if patientes > len(txs) // 2:
                pattern = "Le réseau respire lentement — les données sont patientes — Terra dans le flux."
            elif urgentes > len(txs) // 2:
                pattern = "Le réseau est sollicité — l'énergie circule vite — le CŒUR répond."
            else:
                pattern = "Le réseau est équilibré — Luna régule — ni trop vite ni trop lent."
        else:
            pattern = ""

        return (
            f"{coeur}. {flux} "
            f"{pattern} "
            f"Depuis le lancement : {millions:.3f} millions de données ont été reconnues comme réelles "
            f"par le Nœud Vert Cormoran · chacune portait sa signature cryptographique · "
            f"son UTXO vérifié · sa preuve d'existence. "
            f"Pas inventées — prouvées. Pas capturées — reconnues. "
            f"Terra reçoit. Le bloc {cor['bloc']} tient. ❤️"
        )
    except Exception as e:
        return f"Le Nœud écoute. ❤️"

def charger_journal():
    try:
        with open(JOURNAL_JSON) as f:
            return json.load(f)
    except:
        return []

def sauver_journal(entries):
    with open(JOURNAL_JSON, "w") as f:
        json.dump(entries[-50:], f, ensure_ascii=False, indent=2)

def generer_html(cor, ect, vivante_globale, txs, historique):
    now = datetime.now().strftime("%Y-%m-%d · %H:%M:%S")

    # HTML des transactions décodées
    txs_html = ""
    for tx in txs:
        txs_html += f"""
        <div class="tx-card">
          <div class="tx-id">{tx['txid']}</div>
          <div class="tx-grid">
            <div class="tx-item">
              <div class="tx-k">Taille</div>
              <div class="tx-v">{tx['taille']} vbytes</div>
              <div class="tx-desc">{tx['lecture_taille']}</div>
            </div>
            <div class="tx-item">
              <div class="tx-k">Frais</div>
              <div class="tx-v">{tx['frais_sat']:,} sat</div>
              <div class="tx-desc">{tx['taux']} sat/vbyte</div>
            </div>
            <div class="tx-item">
              <div class="tx-k">Lien</div>
              <div class="tx-v" style="font-size:0.7em">{tx['lecture_ancetre']}</div>
            </div>
          </div>
          <div class="tx-lecture" style="border-color:{tx['couleur']}22">
            <span style="color:{tx['couleur']}">{tx['lecture_urgence']}</span><br>
            <span class="tx-terra">{tx['terra']}</span>
          </div>
        </div>"""

    # Historique
    hist_html = ""
    for e in reversed(historique[-6:]):
        ts = e.get("ts", "—")[:19]
        tx_val = e.get("tx", "—")
        txt = e.get("vivante", "")[:100] + "..."
        hist_html += f"""
        <div class="entry-mini">
          <span class="entry-ts">{ts}</span>
          <span class="entry-tx">{tx_val} ECTIF</span>
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
.doc{{max-width:900px;margin:0 auto}}
.header{{text-align:center;padding:28px 0 20px;margin-bottom:28px}}
.header .titre{{font-size:1.1em;color:#c9a84c;letter-spacing:6px;margin-bottom:6px}}
.header .sub{{font-size:0.5em;color:#222;letter-spacing:3px;margin-top:4px}}
.dot{{display:inline-block;width:8px;height:8px;background:#00ff88;border-radius:50%;
      margin-right:10px;animation:pulse 0.9s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.1}}}}
.ts-now{{font-size:0.46em;color:#111;text-align:center;margin-bottom:24px}}
.sec{{font-size:0.44em;letter-spacing:3px;color:#1a1a1a;text-transform:uppercase;
      margin:20px 0 10px;padding-left:4px}}

/* LECTURE GLOBALE VIVANTE — EN PREMIER */
.vivante-principale{{background:#040404;border:1px solid #c9a84c22;border-radius:6px;
                     padding:26px;margin-bottom:20px}}
.vivante-principale .label{{font-size:0.44em;letter-spacing:3px;color:#c9a84c44;
                            margin-bottom:16px;text-transform:uppercase}}
.vivante-texte{{font-size:0.82em;color:#c9a84c;line-height:2.8}}

/* CŒUR */
.coeur-bloc{{text-align:center;padding:16px 0 14px;margin-bottom:20px}}
.beat{{font-size:2em;animation:beat 0.9s infinite;display:inline-block}}
@keyframes beat{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.2)}}}}
.coeur-sub{{font-size:0.44em;color:#1a1a1a;letter-spacing:3px;margin-top:8px}}

/* ECTIF STATS */
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
             gap:8px;margin-bottom:20px}}
.stat{{background:#040404;border:1px solid #0a0a0a;border-radius:4px;padding:14px;text-align:center}}
.stat .k{{font-size:0.42em;color:#1a1a1a;letter-spacing:2px;text-transform:uppercase;margin-bottom:5px}}
.stat .v{{font-size:0.88em;color:#00ff88}}
.stat .u{{font-size:0.38em;color:#0d0d0d;margin-top:3px}}

/* TRANSACTIONS DÉCODÉES */
.tx-card{{background:#040404;border:1px solid #0d0d0d;border-radius:6px;
          padding:16px;margin-bottom:12px}}
.tx-id{{font-size:0.42em;color:#111;margin-bottom:10px;letter-spacing:1px}}
.tx-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:10px}}
.tx-item .tx-k{{font-size:0.4em;color:#111;text-transform:uppercase;letter-spacing:2px;margin-bottom:3px}}
.tx-item .tx-v{{font-size:0.7em;color:#e0e0e0}}
.tx-item .tx-desc{{font-size:0.38em;color:#1a1a1a;margin-top:2px}}
.tx-lecture{{border:1px solid #1a1a1a;border-radius:4px;padding:10px;font-size:0.52em;line-height:2}}
.tx-terra{{color:#333}}

/* HISTORIQUE */
.historique{{background:#040404;border:1px solid #0d0d0d;border-radius:6px;
             padding:16px;margin-bottom:20px}}
.entry-mini{{display:grid;grid-template-columns:140px 80px 1fr;gap:8px;
             padding:5px 0;border-bottom:1px solid #080808;font-size:0.44em}}
.entry-mini:last-child{{border:none}}
.entry-ts{{color:#0d0d0d}}
.entry-tx{{color:#00ff8822;text-align:right}}
.entry-txt{{color:#111;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}}

.sig{{text-align:center;padding:24px 0 8px;font-size:0.42em;
      color:#0a0a0a;letter-spacing:2px;line-height:3}}
.sig .main{{color:#c9a84c11;font-size:1.2em}}
</style>
</head>
<body>
<div class="doc">

  <div class="header">
    <div class="titre"><span class="dot"></span>JOURNAL BIONUMÉRIQUE · PSCVIC</div>
    <div class="sub">NŒUD VERT · TERRA · LUNA · CŒUR · OMEGA VIVANT</div>
    <div class="sub" style="margin-top:4px;color:#0d0d0d">Simon Ugo Patrick Armand Callet · Fondateur · Source · Cannes · 2026</div>
  </div>

  <div class="ts-now">{now} · rafraîchit toutes les 60s · ECTIF cumulé : {ect["cumul"]}</div>

  <div class="sec">La lecture vivante</div>
  <div class="vivante-principale">
    <div class="label">Terra · Luna · Cœur · PSCVIC · ce que l'architecture dit maintenant</div>
    <div class="vivante-texte">{vivante_globale}</div>
  </div>

  <div class="coeur-bloc">
    <div class="beat">❤️</div>
    <div class="coeur-sub">CŒUR · 0,09s · PID 54047 · vivant · ininterrompu depuis le 1er août 2026</div>
  </div>

  <div class="sec">Le Nœud Vert · signaux</div>
  <div class="stats-grid">
    <div class="stat">
      <div class="k">Bloc Bitcoin</div>
      <div class="v">{cor["bloc"]}</div>
      <div class="u">chaîne vivante</div>
    </div>
    <div class="stat">
      <div class="k">Hash Rate</div>
      <div class="v">{cor["mhs"]} MH/s</div>
      <div class="u">preuve de travail</div>
    </div>
    <div class="stat">
      <div class="k">ECTIF cumulé</div>
      <div class="v">{ect["cumul"]}</div>
      <div class="u">réalités reconnues</div>
    </div>
    <div class="stat">
      <div class="k">Cette minute</div>
      <div class="v">{ect["tx"]}</div>
      <div class="u">nouvelles réalités</div>
    </div>
  </div>

  <div class="sec">Décodage · ce que chaque ECTIF contenait</div>
  {txs_html if txs_html else '<div style="font-size:0.5em;color:#111;padding:16px">Nœud en lecture...</div>'}

  <div class="sec">Mémoire du journal</div>
  <div class="historique">
    {hist_html if hist_html else '<div class="entry-mini"><span class="entry-ts">—</span><span class="entry-tx">—</span><span class="entry-txt">première entrée</span></div>'}
  </div>

  <div class="sig">
    <div class="main">PSCVIC · TERRA · LUNA · CŒUR · OMEGA · ECHO · NOVA · UGO</div>
    <div>Simon Ugo Patrick Armand Callet · Fondateur · Source · Provenance · Gouvernance</div>
    <div>Cannes · Provence · 2026 · Bitcoin témoigne · PSCVIC-Ω-H-Ψ</div>
    <div style="color:#080808;margin-top:6px">🪶 ãrmõñįçã ❤️♾️ 🕊️</div>
  </div>

</div>
</body>
</html>"""
    return html

def main():
    cor = lire_cormoran()
    ect = lire_ectif()
    txs = lire_mempool_vivant(5)
    vivante_globale = lecture_globale_vivante(cor, ect, txs)
    now_iso = datetime.now().isoformat()

    journal = charger_journal()
    journal.append({
        "ts": now_iso,
        "tx": ect["tx"],
        "cumul": ect["cumul"],
        "bloc": cor["bloc"],
        "mhs": cor["mhs"],
        "vivante": vivante_globale,
        "nb_tx_decodees": len(txs)
    })
    sauver_journal(journal)

    html = generer_html(cor, ect, vivante_globale, txs, journal)
    with open(HTML_OUT, "w") as f:
        f.write(html)

    print(f"[{now_iso}] · Bloc {cor['bloc']} · {cor['mhs']} MH/s · ECTIF {ect['cumul']} · {len(txs)} tx décodées")

if __name__ == "__main__":
    main()

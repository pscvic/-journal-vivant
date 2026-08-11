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

def lire_type_script(stype, val_btc, nb_sorties):
    """Traduit le type de script en lecture vivante"""
    if stype == "nulldata":
        return "donnée pure · aucune valeur monétaire · information seule inscrite dans la chaîne", "#c9a84c"
    elif stype == "witness_v0_keyhash":
        desc = "architecture SegWit moderne · portefeuille individuel · signal compressé · efficace"
        if val_btc > 1:
            desc += f" · {val_btc:.4f} BTC — transfert significatif"
        return desc, "#00ff88"
    elif stype in ("scripthash", "witness_v0_scripthash"):
        return f"protection multiple · plusieurs clés nécessaires · gouvernance par consensus · {val_btc:.4f} BTC", "#4488ff"
    elif stype == "pubkeyhash":
        return f"mémoire ancienne du réseau · adresse Bitcoin première génération · toujours valide · {val_btc:.4f} BTC", "#888"
    elif stype == "witness_v1_taproot":
        return f"Taproot · architecture la plus avancée · confidentialité maximale · {val_btc:.4f} BTC", "#cc88ff"
    else:
        return f"type : {stype} · {val_btc:.4f} BTC", "#333"

def decoder_tx_contenu(txid):
    """Décode le contenu réel d'une transaction"""
    try:
        raw = rpc("getrawtransaction", [txid])
        if not raw:
            return None
        decoded = rpc("decoderawtransaction", [raw])
        if not decoded:
            return None

        vins = decoded.get("vin", [])
        vouts = decoded.get("vout", [])
        nb_entrees = len(vins)
        nb_sorties = len(vouts)

        # Analyser les sorties
        sorties = []
        total_btc = 0
        op_return_data = None
        types_presents = set()

        for vout in vouts:
            val = vout.get("value", 0)
            script = vout.get("scriptPubKey", {})
            stype = script.get("type", "unknown")
            types_presents.add(stype)
            total_btc += val

            if stype == "nulldata":
                hex_data = script.get("hex", "")
                try:
                    data_hex = hex_data[4:]
                    text = bytes.fromhex(data_hex).decode("utf-8", errors="replace")
                    op_return_data = text[:120]
                except:
                    op_return_data = hex_data[:40]
            elif val > 0:
                desc, couleur = lire_type_script(stype, val, nb_sorties)
                sorties.append({"val": val, "type": stype, "desc": desc, "couleur": couleur})

        # Lecture globale de la transaction
        if nb_sorties > 10:
            nature = f"carrefour vivant · {nb_sorties} destinations · distribution ou échange"
            couleur_tx = "#c9a84c"
        elif nb_entrees > 5:
            nature = f"consolidation · {nb_entrees} sources réunies en {nb_sorties} sorties"
            couleur_tx = "#4488ff"
        elif op_return_data:
            nature = "inscription de donnée · information pure dans la chaîne Bitcoin"
            couleur_tx = "#c9a84c"
        elif total_btc > 5:
            nature = f"transfert majeur · {total_btc:.4f} BTC · confiance importante déplacée"
            couleur_tx = "#00ff88"
        else:
            nature = f"geste simple · {nb_entrees} source → {nb_sorties} destination(s)"
            couleur_tx = "#333"

        return {
            "txid": txid[:16] + "...",
            "nb_entrees": nb_entrees,
            "nb_sorties": nb_sorties,
            "total_btc": total_btc,
            "nature": nature,
            "couleur_tx": couleur_tx,
            "op_return": op_return_data,
            "sorties": sorties[:3],
            "types": list(types_presents)
        }
    except Exception as e:
        return None

def lire_mempool_vivant(n=5):
    """Lit N transactions réelles · décode leur contenu · traduit en français vivant"""
    mempool = rpc("getrawmempool", [False])
    if not mempool:
        return []

    resultats = []
    txids = list(mempool)[:n*3]  # en prendre plus au cas où certaines échouent

    # Aussi récupérer les stats de base
    mempool_verbose = rpc("getrawmempool", [True]) or {}

    for txid in txids:
        if len(resultats) >= n:
            break
        contenu = decoder_tx_contenu(txid)
        if contenu:
            # Ajouter stats de base si disponibles
            stats = mempool_verbose.get(txid, {})
            frais_sat = int(stats.get("fees", {}).get("base", 0) * 1e8)
            taille = stats.get("vsize", 0)
            taux = round(frais_sat / taille, 1) if taille else 0

            if taux < 20:
                urgence = "patiente"
                terra_urgence = "Elle attend son tour — respecte le cycle naturel."
            elif taux < 100:
                urgence = "équilibrée"
                terra_urgence = "Luna régule — le juste milieu."
            else:
                urgence = "urgente"
                terra_urgence = "Le CŒUR répond — le réseau est sollicité."

            contenu["frais_sat"] = frais_sat
            contenu["taille"] = taille
            contenu["taux"] = taux
            contenu["urgence"] = urgence
            contenu["terra_urgence"] = terra_urgence
            resultats.append(contenu)

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
        # Sorties
        sorties_html = ""
        for s in tx.get("sorties", []):
            sorties_html += f'<div class="tx-sortie" style="border-left:2px solid {s["couleur"]}44"><span style="color:{s["couleur"]}">{s["val"]:.6f} BTC</span> · <span class="tx-terra">{s["desc"]}</span></div>'

        op_return_html = ""
        if tx.get("op_return"):
            op_return_html = f'<div class="tx-opreturn">📝 Donnée inscrite : <span style="color:#c9a84c">{tx["op_return"]}</span></div>'

        txs_html += f"""
        <div class="tx-card" style="border-color:{tx['couleur_tx']}22">
          <div class="tx-header">
            <span class="tx-id">{tx['txid']}</span>
            <span class="tx-nature" style="color:{tx['couleur_tx']}">{tx['nature']}</span>
          </div>
          <div class="tx-meta">
            {tx['nb_entrees']} entrée(s) · {tx['nb_sorties']} sortie(s) · {tx.get('taille',0)} vbytes · {tx.get('taux',0)} sat/vbyte · <span style="color:#c9a84c44">{tx.get('urgence','')}</span>
          </div>
          {op_return_html}
          <div class="tx-sorties">{sorties_html}</div>
          <div class="tx-lecture">
            <span class="tx-terra">{tx.get('terra_urgence','')}</span>
            Cette donnée a prouvé son existence · traversé le filtre vivant du Nœud Vert · elle est réelle · elle est ECTIF.
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
.tx-header{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;flex-wrap:wrap;gap:6px}}
.tx-id{{font-size:0.4em;color:#111;letter-spacing:1px}}
.tx-nature{{font-size:0.5em;letter-spacing:1px}}
.tx-meta{{font-size:0.42em;color:#1a1a1a;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #080808}}
.tx-opreturn{{font-size:0.48em;background:#0a0a00;border:1px solid #c9a84c11;border-radius:4px;padding:8px;margin-bottom:8px;line-height:1.8}}
.tx-sorties{{margin-bottom:10px}}
.tx-sortie{{font-size:0.46em;padding:5px 8px;margin-bottom:4px;border-radius:3px;line-height:1.8}}
.tx-lecture{{border-top:1px solid #0a0a0a;padding-top:10px;font-size:0.48em;color:#1a1a1a;line-height:2.2}}
.tx-terra{{color:#222}}

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

#!/usr/bin/env python3
"""Fusiona los hallazgos de una ejecución con data.json y runs.json.

Uso: python3 merge.py data.json runs.json cambios.json

cambios.json:
{
  "seen":   ["id", ...],            # ofertas existentes re-verificadas hoy (enlace abre)
  "closed": ["id", ...],            # ofertas existentes cuyo enlace ya no abre o declara cierre
  "updates": {"id": {"deadline": "YYYY-MM-DD", ...}},   # campos corregidos de existentes
  "new":    [ {oferta completa sin id/first_seen/last_seen/status}, ... ],
  "note":   "bitácora de la ejecución, sin nombres de personas"
}
El script calcula ids, fechas, estados, retiros y orden. No toca "profile".
"""
import json, re, sys, unicodedata
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SECTORS = ["directivo", "inspectoria-convivencia", "tecnico-pedagogico", "docencia", "otro"]
DEPS = ["publico", "subvencionado", "pagado"]
TRAMOS = [None, "acceso", "inicial", "temprano", "avanzado", "experto-1", "experto-2"]
REGIONS = ["Metropolitana", "Valparaíso", "O'Higgins"]
FIELDS = ["title", "company", "location", "region", "sector", "dependencia", "salary",
          "source", "url", "published_date", "deadline", "tramo_minimo", "note"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def slug(*parts):
    t = " ".join(parts).lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def check(job):
    job.setdefault("tramo_minimo", None)
    if job["tramo_minimo"] not in TRAMOS:
        sys.exit(f"tramo_minimo inválido: {job['tramo_minimo']}")
    for f in FIELDS:
        if f not in job:
            sys.exit(f"Falta el campo {f} en: {job.get('title')}")
    if job["sector"] not in SECTORS:
        sys.exit(f"sector inválido: {job['sector']}")
    if job["dependencia"] not in DEPS + [None]:
        sys.exit(f"dependencia inválida: {job['dependencia']}")
    if job["region"] not in REGIONS:
        sys.exit(f"región fuera de alcance: {job['region']}")
    if not str(job["url"]).startswith("http"):
        sys.exit(f"url inválida: {job['url']}")
    for f in ("published_date", "deadline"):
        if job[f] is not None and not DATE.match(job[f]):
            sys.exit(f"{f} debe ser YYYY-MM-DD o null: {job[f]}")


def main():
    data_p, runs_p, ch_p = sys.argv[1:4]
    data = json.load(open(data_p, encoding="utf-8"))
    try:
        runs = json.load(open(runs_p, encoding="utf-8"))
    except Exception:
        runs = {"runs": []}
    ch = json.load(open(ch_p, encoding="utf-8"))
    now = datetime.now(ZoneInfo("America/Santiago"))
    today = now.strftime("%Y-%m-%d")
    d7 = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    d30 = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    jobs = data.get("jobs", [])
    by_id = {j["id"]: j for j in jobs}

    # una oferta es "new" solo el día de su detección
    for j in jobs:
        if j["status"] == "new" and j["first_seen"] != today:
            j["status"] = "active"
    for i, upd in ch.get("updates", {}).items():
        if i not in by_id:
            sys.exit(f"updates: id inexistente {i}")
        by_id[i].update({k: v for k, v in upd.items() if k in FIELDS})
    for i in ch.get("seen", []):
        if i not in by_id:
            sys.exit(f"seen: id inexistente {i}")
        by_id[i]["last_seen"] = today
        if by_id[i]["status"] == "closed":
            by_id[i]["status"] = "active"
    n_closed = 0
    for i in ch.get("closed", []):
        if i not in by_id:
            sys.exit(f"closed: id inexistente {i}")
        if by_id[i]["status"] != "closed":
            by_id[i]["status"] = "closed"
            by_id[i]["closed_date"] = today
            n_closed += 1
    n_new = 0
    for nj in ch.get("new", []):
        check(nj)
        i = slug(nj["company"], nj["title"], nj["location"])
        if i in by_id:  # ya existía: cuenta como re-verificada
            by_id[i]["last_seen"] = today
            continue
        job = {"id": i, **{f: nj[f] for f in FIELDS},
               "first_seen": today, "last_seen": today, "status": "new"}
        jobs.append(job)
        by_id[i] = job
        n_new += 1

    # retiro: plazo vencido hace más de 7 días, cerrada hace más de 7 días,
    # o 30 días sin re-verificación. Nunca por antigüedad de first_seen.
    def keep(j):
        if j.get("deadline") and j["deadline"] < d7:
            return False
        if j["status"] == "closed" and j.get("closed_date", j["last_seen"]) < d7:
            return False
        if j["last_seen"] < d30:
            return False
        return True
    removed = [j["id"] for j in jobs if not keep(j)]
    jobs = [j for j in jobs if keep(j)]

    jobs.sort(key=lambda j: SECTORS.index(j["sector"]))
    jobs.sort(key=lambda j: j["first_seen"], reverse=True)

    stamp = now.strftime("%Y-%m-%d %H:%M")
    data["jobs"] = jobs
    data["updated"] = stamp
    found = sum(1 for j in jobs if j["status"] != "closed")
    note = ch.get("note", "")
    if removed:
        note += f" Retiradas por regla de vencimiento ({len(removed)}): " + ", ".join(removed) + "."
    runs["runs"] = ([{"date": today, "found": found, "new": n_new, "closed": n_closed, "note": note}]
                    + runs.get("runs", []))[:30]
    runs["updated"] = stamp
    for p, o in ((data_p, data), (runs_p, runs)):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(o, f, ensure_ascii=False, indent=2)
            f.write("\n")
        json.load(open(p, encoding="utf-8"))
    stale = sorted((j for j in jobs if j["status"] != "closed"), key=lambda j: j["last_seen"])[:15]
    print(json.dumps({"found": found, "new": n_new, "closed": n_closed, "removed": removed,
                      "updated": stamp,
                      "mas_antiguas_sin_verificar": [[j["id"], j["last_seen"]] for j in stale]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

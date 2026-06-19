#!/usr/bin/env python3
"""
ipo_tracker.py — Śledzenie zbliżających się debiutów giełdowych (IPO) na rynku USA.

Po co to:
    Tak jak SpaceX, wiele firm zapowiada wejście na giełdę amerykańską (NYSE / NASDAQ).
    Ten skrypt odpytuje publiczne API o kalendarz IPO i pokazuje firmy, które dopiero
    MAJĄ zadebiutować — żeby móc je obserwować ZANIM pojawią się na rynku i ocenić,
    czy warto je kupić (np. na Revolut, gdy tylko trafią do oferty).

Źródło danych:
    Finnhub IPO Calendar  ->  https://finnhub.io/docs/api/ipo-calendar
    Darmowy klucz API:    ->  https://finnhub.io/register  (plan free wystarczy)

Użycie:
    # 1. Ustaw darmowy klucz API (jednorazowo):
    export FINNHUB_API_KEY="twoj_klucz"

    # 2. Pokaż IPO na najbliższy miesiąc (domyślnie dziś -> +30 dni):
    python ipo_tracker.py

    # Własny zakres dat:
    python ipo_tracker.py --from 2026-06-19 --to 2026-07-19

    # Tylko konkretna giełda:
    python ipo_tracker.py --exchange NASDAQ

    # Zapis do pliku HTML (ładny raport do otwarcia w przeglądarce):
    python ipo_tracker.py --html ipos.html

    # Zapis surowych danych do JSON:
    python ipo_tracker.py --json ipos.json

Bez klucza API skrypt nie pobierze świeżych danych — wtedy otwórz gotowy index.html,
który zawiera ręcznie zebraną migawkę najważniejszych zbliżających się IPO.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

FINNHUB_URL = "https://finnhub.io/api/v1/calendar/ipo"

# Giełdy amerykańskie, które nas interesują (Revolut handluje akcjami z tych rynków).
US_EXCHANGES = ("NASDAQ", "NYSE", "NYSE AMERICAN", "NYSE ARCA", "BATS", "CBOE")


def parse_args(argv: list[str]) -> argparse.Namespace:
    today = dt.date.today()
    default_to = today + dt.timedelta(days=30)

    p = argparse.ArgumentParser(
        description="Śledź zbliżające się IPO na giełdzie USA (jak SpaceX)."
    )
    p.add_argument("--from", dest="date_from", default=today.isoformat(),
                   help="Data początkowa YYYY-MM-DD (domyślnie: dziś).")
    p.add_argument("--to", dest="date_to", default=default_to.isoformat(),
                   help="Data końcowa YYYY-MM-DD (domyślnie: +30 dni).")
    p.add_argument("--exchange", default=None,
                   help="Filtruj po giełdzie, np. NASDAQ lub NYSE.")
    p.add_argument("--us-only", action="store_true", default=True,
                   help="Pokaż tylko giełdy USA (domyślnie włączone).")
    p.add_argument("--all-exchanges", dest="us_only", action="store_false",
                   help="Pokaż wszystkie giełdy, nie tylko USA.")
    p.add_argument("--html", metavar="PLIK",
                   help="Zapisz wynik jako raport HTML.")
    p.add_argument("--json", metavar="PLIK",
                   help="Zapisz surowe dane jako JSON.")
    p.add_argument("--token", default=os.environ.get("FINNHUB_API_KEY"),
                   help="Klucz API Finnhub (lub zmienna FINNHUB_API_KEY).")
    return p.parse_args(argv)


def fetch_ipos(date_from: str, date_to: str, token: str) -> list[dict]:
    """Pobiera kalendarz IPO z Finnhub dla zadanego zakresu dat."""
    query = urllib.parse.urlencode({"from": date_from, "to": date_to, "token": token})
    url = f"{FINNHUB_URL}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "ipo-tracker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Błąd HTTP {e.code} z Finnhub: {e.reason}. "
                         f"Sprawdź klucz API.") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Brak połączenia z Finnhub: {e.reason}") from e
    return payload.get("ipoCalendar", [])


def filter_ipos(ipos: list[dict], exchange: str | None, us_only: bool) -> list[dict]:
    result = []
    for ipo in ipos:
        ex = (ipo.get("exchange") or "").upper()
        if exchange and exchange.upper() not in ex:
            continue
        if us_only and not any(us in ex for us in US_EXCHANGES):
            continue
        result.append(ipo)
    # Najbliższe debiuty na górze.
    result.sort(key=lambda x: x.get("date") or "9999-99-99")
    return result


def _fmt_price(ipo: dict) -> str:
    price = ipo.get("price")
    return f"${price}" if price else "—"


def print_table(ipos: list[dict], date_from: str, date_to: str) -> None:
    print(f"\n  Zbliżające się IPO na giełdzie USA  ({date_from} → {date_to})")
    print("  " + "=" * 78)
    if not ipos:
        print("  Brak zaplanowanych IPO w tym zakresie (daty IPO ustala się zwykle "
              "na 7–10 dni przed debiutem).")
        return
    header = f"  {'Data':<12}{'Symbol':<10}{'Spółka':<32}{'Giełda':<10}{'Cena':<8}"
    print(header)
    print("  " + "-" * 78)
    for ipo in ipos:
        name = (ipo.get("name") or "")[:30]
        print(f"  {ipo.get('date',''):<12}"
              f"{(ipo.get('symbol') or '—'):<10}"
              f"{name:<32}"
              f"{(ipo.get('exchange') or ''):<10}"
              f"{_fmt_price(ipo):<8}")
    print("  " + "-" * 78)
    print(f"  Razem: {len(ipos)} firm. To NIE jest porada inwestycyjna.\n")


def render_html(ipos: list[dict], date_from: str, date_to: str) -> str:
    rows = []
    for ipo in ipos:
        rows.append(
            "<tr>"
            f"<td>{html.escape(ipo.get('date',''))}</td>"
            f"<td><b>{html.escape(ipo.get('symbol') or '—')}</b></td>"
            f"<td>{html.escape(ipo.get('name') or '')}</td>"
            f"<td>{html.escape(ipo.get('exchange') or '')}</td>"
            f"<td>{html.escape(_fmt_price(ipo))}</td>"
            f"<td>{html.escape(str(ipo.get('numberOfShares') or '—'))}</td>"
            "</tr>"
        )
    body = "\n".join(rows) or (
        '<tr><td colspan="6">Brak zaplanowanych IPO w tym zakresie.</td></tr>'
    )
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<title>Zbliżające się IPO (USA)</title>
<style>
body{{font-family:system-ui,Arial,sans-serif;background:#0b1020;color:#e7ecf5;margin:0;padding:2rem}}
h1{{color:#7cc4ff}} table{{border-collapse:collapse;width:100%;margin-top:1rem}}
th,td{{padding:.6rem .8rem;border-bottom:1px solid #243049;text-align:left}}
th{{color:#9fb3d1;font-size:.85rem;text-transform:uppercase}}
tr:hover td{{background:#141c33}} .note{{color:#9fb3d1;font-size:.85rem;margin-top:1rem}}
</style></head><body>
<h1>Zbliżające się IPO na giełdzie USA</h1>
<p>Zakres: <b>{html.escape(date_from)}</b> → <b>{html.escape(date_to)}</b>
&nbsp;|&nbsp; Wygenerowano: {generated} &nbsp;|&nbsp; Źródło: Finnhub</p>
<table>
<thead><tr><th>Data</th><th>Symbol</th><th>Spółka</th><th>Giełda</th>
<th>Cena</th><th>Liczba akcji</th></tr></thead>
<tbody>
{body}
</tbody></table>
<p class="note">⚠️ Dane orientacyjne. To nie jest porada inwestycyjna. Daty IPO często
się zmieniają — zawsze potwierdzaj w oficjalnym kalendarzu giełdy.</p>
</body></html>"""


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.token:
        print("Brak klucza API. Ustaw zmienną FINNHUB_API_KEY albo użyj --token.\n"
              "Darmowy klucz: https://finnhub.io/register\n"
              "Bez klucza otwórz gotowy plik index.html z migawką danych.",
              file=sys.stderr)
        return 2

    ipos = fetch_ipos(args.date_from, args.date_to, args.token)
    ipos = filter_ipos(ipos, args.exchange, args.us_only)

    print_table(ipos, args.date_from, args.date_to)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(ipos, f, ensure_ascii=False, indent=2)
        print(f"  Zapisano JSON: {args.json}")

    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_html(ipos, args.date_from, args.date_to))
        print(f"  Zapisano HTML: {args.html}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

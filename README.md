# The World Today — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/DavidQlla06/news-image-20261122-v2/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/DavidQlla06/news-image-20261122-v2/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A dense broadsheet front page that sums up the world's news of
**Sunday 22 November 2026** in one 1024×1024 image, entered in the
[make.fun](https://make.fun) competition
[news-image-20261122](https://make.fun/bounty/news-image-20261122).

## What's on the page

40 stories across 7 regions, all reported on 22 November 2026:

- **Lead — Gulf Crisis:** Iran strikes a US air base in Kuwait; Bahrain
  targeted, tankers hit near Hormuz, a Qatari LNG vessel struck.
- **Middle East & Gulf (5):** US denies F-16 claim; Qatari talks in
  Tehran; Gaza strikes kill 8; Houthi–Saudi strikes; Iran FM on talks.
- **Europe (5):** Kryvyi Rih missile strike; Russian cargo ship ablaze
  off Finland; Polish airspace violated; Estonia closes Russia border;
  EU sends €7.9B to Ukraine.
- **Africa (3):** RSF accused in West Kordofan; ANC falls to 30.8%;
  Phumzile Mlambo-Ngcuka dies at 71.
- **Asia-Pacific (4):** Japan live-fire training in India; China–Japan
  chill; Modi at SCO summit; Manipur alcohol deaths.
- **Americas (4):** 'El Chapo Isidro' captured; Peru M6.9 quake; S&P 500
  falls 3.7%; US loses measles elimination status.
- **Climate & Planet (2):** COP31 near final deal; oil futures fall 3%.
- **Science · Tech · Sport (2):** 'Killer robots' rules by 2028;
  Verstappen on pole in Las Vegas.
- **Also Today ticker (14):** Kerch Bridge, Bolsonaro in ICU, dengue
  breakthrough, Harden passes Kobe, Air Niugini emergency landing, and
  more one-line headlines.

Every story card carries a small pictogram drawn in code (missile, ship,
flame, quake crack, ballot, virus, trophy, …), and the lead panel has a
drawn scene of the Gulf: tankers, missile arcs and the coastal base.

## How it works

- `stories.json` — the day's headlines, summaries and motifs.
- `generate.py` — draws the whole page with Pillow (fonts: DejaVu) and
  writes `entry.png`. Deterministic: same input, same bytes.
- `main.py` — the competition entrypoint; copies the committed
  `entry.png` to `MAKEFUN_OUTPUT_DIR` (or `/output`). Standard library
  only, no network.
- `entry.png` — the rendered 1024×1024 front page.

## Run it

```sh
python3 generate.py            # redraw entry.png from stories.json
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py   # place entry.png in out/
```

## License

MIT — see [LICENSE](LICENSE).

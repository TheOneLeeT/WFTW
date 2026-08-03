# Warframe Trade Watch (WFTW)

---

## What it is

WFTW is a desktop companion that watches Warframe Market for you and instantly alerts you when matching buy or sell orders appear. No account. No browser tab. Just passive notifications while you play.

## Why it exists

Warframe Market is excellent for browsing and trading manually. WFTW complements it by continuously monitoring the public market for the items you care about, so you don't have to refresh pages or keep browser tabs open.

No Warframe Market account required. WFTW monitors public market listings directly, so it works independently of your browser session or marketplace login.

## How it works

WFTW monitors public Warframe Market listings in the background and notifies you when an order matches your criteria. It does not modify the game, interact with Digital Extremes servers, or depend on a logged-in Warframe Market session.

## What you get

- Use without any marketplace login
- Monitor dozens of items simultaneously instead of searching one at a time
- Runs quietly in the system tray while you play
- Know immediately when a matching order appears with desktop notification and sound
- Available on Windows, macOS, and Linux
- Runs locally without account creation, cloud sync, or background telemetry
- Lightweight background polling keeps the interface responsive while monitoring continues

## What it tracks

- WTS orders with price and rank filters
- WTB orders with price and rank filters
- Online and in-game status awareness
- Local notifications with customizable sound and volume

## Installation

```
pip install -r requirements.txt
python gui.py
```

## Requirements

- Python 3.9+
- flet
- requests
- pyperclip

## Project layout

```
gui.py
tracker_core.py
requirements.txt
notif.json
Media/
  Sound/
    Dnotif.wav
  Icon/
    WFTW.ico
    WFTW.icns
    WFTW.png
```

## Legal

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

This is a fan-made, non-commercial desktop notification tool. It is not affiliated with, endorsed by, or connected to Digital Extremes Ltd. or warframe.market in any way.

Warframe is a registered trademark of Digital Extremes Ltd. All game-related content, including item names, images, and terminology, is property of Digital Extremes Ltd.

This tool interacts with the public Warframe Market API. Use of this tool is subject to the [Warframe Market Terms of Service](https://warframe.market/tos) and [Rules](https://docs.warframe.market/docs/rules/overview). Users are responsible for complying with all applicable terms, including rate limits (3 requests per second).

This tool does not automate in-game actions, modify the Warframe client, or interact with Digital Extremes servers. It is a passive notification client for an external community website.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. USE AT YOUR OWN RISK.

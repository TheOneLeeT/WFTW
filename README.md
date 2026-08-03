# Warframe Trade Watch (WFTW)

---

## What it is

Warframe Trade Watch is a desktop companion that watches Warframe Market for you and instantly alerts you when matching buy or sell orders appear. No account. No browser tab. Just passive notifications while you play.

## Why it exists

Warframe Market is excellent for browsing and trading manually. Warframe Trade Watch complements it by continuously monitoring the public market for the items you care about, so you don't have to refresh pages or keep browser tabs open.

No Warframe Market account required. Warframe Trade Watch monitors public market listings directly, so it works independently of your browser session or marketplace login.

## What you get

- **No account required**: monitor public market listings without staying signed in
- **Monitor dozens of items at once**: track multiple buy and sell orders across as many items as you want
- **Runs quietly in the background**: a lightweight tray app that stays out of your way while you play
- **Instant desktop alerts**: know immediately when a matching order appears with sound and notification
- **Available everywhere**: cross-platform desktop app for Windows, macOS, and Linux
- **Private by default**: no telemetry, no cloud sync, and no account creation
- **Responsive while monitoring**: lightweight background polling keeps the interface snappy

## What it tracks

- Sell orders with price and rank filters
- Buy orders with price and rank filters
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

# WFTW

qwertyuiopasdfghjklzxcvbnm1234567890

---

## What it is

WFTW is a desktop trade notification tool for Warframe. It watches the live marketplace on your behalf and alerts you the moment a matching order appears. No account required. No browser tab needed. Just fast, passive notifications while you play.

## Why it exists

The official marketplace site is useful, but it is fundamentally limited for active traders:
- only one item search at a time
- requires a logged-in session to use some features
- depends on the tab staying open in a browser
- noisy UI if you just want a signal when something you care about shows up

WFTW does one thing and does it cleanly: it keeps watch on the items you choose and tells you when they appear.

## How it works

WFTW talks directly to the public marketplace API. It does not use the websocket, it does not need an account, and it does not inject into or modify the game in any way. It is purely an external reader of public market data with local notification logic on top.

Because it bypasses the account-bound websocket path, the app does not inherit the same restrictions that apply to logged-in browser sessions. It simply reads public order data and evaluates it against your local watchlist.

## Advantages

- **No account required**: works without any marketplace login
- **Multiple items at once**: track as many items as you want simultaneously
- **Low overhead**: lightweight tray-style behavior, not a browser tab
- **Instant alerts**: sound and desktop notification on match
- **Cross-platform**: Windows, macOS, Linux
- **Private by default**: no telemetry, no account, no cloud sync
- **Fast**: optimized polling keeps the UI responsive while the tracker runs in the background

## What it tracks

- WTS orders with price/rank filters
- WTB orders with price/rank filters
- Online / in-game status awareness
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

This tool interacts with the public warframe.market API. Use of this tool is subject to the [warframe.market Terms of Service](https://warframe.market/tos) and [Rules](https://docs.warframe.market/docs/rules/overview). Users are responsible for complying with all applicable terms, including rate limits (3 requests per second).

This tool does not automate in-game actions, modify the Warframe client, or interact with Digital Extremes servers. It is a passive notification client for an external community website.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. USE AT YOUR OWN RISK.

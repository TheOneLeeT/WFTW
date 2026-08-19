<div align="center">

![WFTW Logo](Media/Icon/png/256x256.png)

</div>

---

# Warframe Trade Watch (WFTW)

## What it is

Warframe Trade Watch is a desktop companion that watches Warframe Market for you and instantly alerts you when matching buy or sell orders appear. No account. No browser tab. Just passive notifications while you play.

## Why it exists

Warframe Market is excellent for browsing and trading manually. Warframe Trade Watch complements it by continuously monitoring the public market for the items you care about, so you don't have to refresh pages or keep browser tabs open.

No Warframe Market account required. Warframe Trade Watch monitors public market listings directly, so it works independently of your browser session or Warframe Market login.

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

## Download

**Pre-release builds are available on the [Releases page](https://github.com/TheOneLeeT/WFTW/releases).**

No Python or extra dependencies required. Just download the archive for your platform, extract it, and run the app.

| Platform | Archive | Run |
|----------|---------|-----|
| Windows | `WFTW-windows-x64.zip` | Extract and run `WFTW.exe` |
| macOS | `WFTW-macos-universal.dmg` | Mount and drag `.app` to `Applications` |
| Linux | `WFTW-linux-x64.tar.gz` | Extract and run the executable |

> **Note:** This is a pre-release. Back up your `watchlist.json` and `settings.json` before updating.

## Build from source

```bash
pip install -r requirements.txt
flet build <windows|macos|linux> --module-name gui --yes
```

## Development workflow

- All feature work happens on the **Dev** branch
- When Dev is ready, it is merged into **Main**
- Release builds are compiled from **Main** only

```
Dev  ──►  Main  ──►  Build / Release
```

## Troubleshooting

- **Python not found (Windows)**: use `py gui.py` or add Python to PATH
- **Linux notifications**: install a notification daemon like `dunst` or `xfce4-notifyd`
- **Blank window on Linux**: install `python3-tk` and `libgtk-3-dev`

## Legal

This is a fan-made, non-commercial desktop notification tool. It is not affiliated with, endorsed by, or connected to Digital Extremes Ltd. or warframe.market in any way.

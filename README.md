# Warframe Trade Watch (WFTW)

---

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

## Requirements

- **Python 3.9 or later** (3.10+ recommended)
- **flet** — desktop UI framework
- **requests** — HTTP client for Warframe Market API
- **pyperclip** — clipboard access for copy-to-whisper feature
- **plyer** — optional, for native desktop notifications

## Installation

### Step 1: Install Python

#### Windows

1. Download Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" before clicking Install
4. Verify installation by opening Command Prompt and running:
   ```
   python --version
   ```

#### macOS

1. Download Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/) or install via Homebrew:
   ```
   brew install python@3.10
   ```
2. Verify installation:
   ```
   python3 --version
   ```

#### Linux

1. Install Python 3.10+ using your package manager:
   ```
   # Debian/Ubuntu
   sudo apt update && sudo apt install python3.10 python3-pip
   
   # Fedora
   sudo dnf install python3.10 python3-pip
   
   # Arch
   sudo pacman -S python python-pip
   ```
2. Verify installation:
   ```
   python3 --version
   ```

### Step 2: Download the project

Clone or download this repository to a folder on your computer.

**Using Git:**
```
git clone https://github.com/TheOneLeeT/WFTW.git
cd WFTW
```

**Without Git:** Download the ZIP from GitHub, extract it, and open the extracted folder in your terminal.

### Step 3: Install dependencies

#### Windows (Command Prompt or PowerShell)
```
pip install -r requirements.txt
```

#### macOS / Linux
```
pip3 install -r requirements.txt
```

If you get a permission error, add the `--user` flag:
```
pip3 install --user -r requirements.txt
```

### Step 4: Run the app

#### Windows
```
python gui.py
```

#### macOS / Linux
```
python3 gui.py
```

The app window should open. You can now add items to your watchlist and start scanning.

## First Run

1. Click the **+** button in the WTS or WTB section to add items
2. Set your desired platinum price
3. Click **Start** to begin scanning
4. When a matching order appears, you'll get a notification and can click **Copy** to whisper the seller/buyer

## Project layout

```
WFTW/
├── gui.py                  # Main application UI and event handlers
├── tracker_core.py         # Background scanning engine and API logic
├── requirements.txt        # Python dependencies
├── settings.json           # User settings (auto-created, not in git)
├── watchlist.json          # Your tracked items (auto-created, not in git)
├── notif.json              # Notification preferences (auto-created, not in git)
├── Logs/                   # Application logs (auto-created, not in git)
│   ├── tracker_debug.log
│   ├── tracker_perf.log
│   ├── tracker_api.log
│   └── wftw_alerts.log
└── Media/
    ├── Icon/
    │   ├── WFTW.ico       # Windows icon
    │   ├── WFTW.icns      # macOS icon
    │   ├── WFTW.png       # App logo
    │   └── WFTW.tif       # High-quality logo source
    └── Sound/
        ├── Dnotif.wav     # Default notification sound
        └── ...            # Additional alert sounds
```

## Configuration

### settings.json

Created automatically on first run. Stores:
- Default status filter (`online`, `ingame`, or `both`)
- Notification sound and volume
- Log rotation preferences

### watchlist.json

Created automatically when you add your first item. Stores your WTS and WTB watchlists.

### Logs

The `Logs/` folder is created automatically. Logs rotate based on your settings to prevent unlimited growth. You can adjust rotation in `settings.json`:

```json
{
  "log_rotation": {
    "enabled": true,
    "mode": "size",
    "max_size_mb": 10,
    "max_lines": 10000,
    "max_age_hours": 168,
    "max_backup_files": 5
  }
}
```

- **mode `size`**: rotate when file exceeds `max_size_mb`
- **mode `lines`**: rotate when file exceeds `max_lines`
- **mode `time`**: rotate when file is older than `max_age_hours`
- **max_backup_files**: number of rotated backups to keep

## Troubleshooting

### "python is not recognized" (Windows)

Python is not in your PATH. Re-run the Python installer and check "Add Python to PATH", or use `py` instead of `python`:
```
py gui.py
```

### "python3: command not found" (macOS/Linux)

Try `python` instead of `python3`, or install Python via your package manager.

### Permission errors when installing

Add the `--user` flag:
```
pip3 install --user -r requirements.txt
```

### App won't start / blank window

Make sure you have a display environment running. On Linux, you may need to install additional dependencies:
```
sudo apt install python3-tk
```

### Notifications not appearing

- Check your system notification settings
- On Linux, ensure you have a notification daemon running (e.g., `dunst`, `xfce4-notifyd`)
- Try adjusting volume in the app settings

## Legal

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

This is a fan-made, non-commercial desktop notification tool. It is not affiliated with, endorsed by, or connected to Digital Extremes Ltd. or warframe.market in any way.

Warframe is a registered trademark of Digital Extremes Ltd. All game-related content, including item names, images, and terminology, is property of Digital Extremes Ltd.

This tool interacts with the public Warframe Market API. Use of this tool is subject to the [Warframe Market Terms of Service](https://warframe.market/tos) and [Rules](https://docs.warframe.market/docs/rules/overview). Users are responsible for complying with all applicable terms, including rate limits (3 requests per second).

This tool does not automate in-game actions, modify the Warframe client, or interact with Digital Extremes servers. It is a passive notification client for an external community website.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. USE AT YOUR OWN RISK.

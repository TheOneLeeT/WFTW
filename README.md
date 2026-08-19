<div align="center">

![WFTW Logo](Media/Icon/png/256x256.png)

</div>

---

# Warframe Trade Watch (WFTW)

## What it is

Warframe Trade Watch is a desktop companion that monitors public Warframe Market listings for you and alerts you when a matching buy or sell order appears. It runs quietly in the background while you play and shows a desktop notification when something you want is posted.

No Warframe Market account is required. WFTW reads public listing data only; it does not place orders, automate chat, or interact with the Warframe game client.

## What it does

- Watches public buy and sell orders on Warframe Market for items you choose
- Filters by price, item rank, and seller/buyer online status
- Shows a desktop notification and plays a sound when a matching order is found
- Optionally copies a ready-to-paste chat message to your clipboard if you want to contact the trader in-game
- Runs in the background as a lightweight desktop window and system-tray app

## How it works

WFTW periodically reads the public Warframe Market API for recent listings and compares them against your watchlist. When a listing matches your filters, WFTW alerts you and, if you want, copies a chat message to your clipboard. You then decide what to do with that information.

This means WFTW is a passive monitoring tool; it does not trade on your behalf or require you to take any action.

## Requirements

- Windows 10+, macOS 10.14+, or a modern Linux desktop
- An internet connection
- No Python, pip, or extra dependencies are needed for the release builds

## Download and installation

Pre-release builds are available on the [Releases page](https://github.com/TheOneLeeT/WFTW/releases).

| Platform | Archive | How to run |
|----------|---------|------------|
| Windows | `WFTW-windows-x64.zip` | Extract the archive and run `WFTW.exe` |
| macOS | `WFTW-macos-universal.dmg` | Open the DMG and drag the app to `Applications` |
| Linux | `WFTW-linux-x64.tar.gz` | Extract and run the executable |

> **Note:** This is a pre-release. Back up your `watchlist.json` and `settings.json` before updating to a newer build.

## First-time setup

1. Start WFTW
2. Use the **WTS** / **WTB** tabs to choose what kind of listings you want to track
3. Add items you want to monitor
4. Set your price filters and any optional rank or subtype filters
5. Choose whether you only want to see online or in-game sellers/buyers
6. WFTW begins monitoring automatically

WTS tracks sell listings from other players. WTB tracks buy listings from other players. You can use either or both depending on what market activity you want to follow.

## Watchlists and filters

- **WTS (Want To Sell)** — tracks public **sell listings** from other players. Use this to monitor what is currently available for purchase.
- **WTB (Want To Buy)** — tracks public **buy orders** from other players. Use this to monitor what other players are looking to purchase.
- You can track any number of items in each list without needing to trade yourself
- Filters include: platform, language, max/min platinum, mod rank, item subtype, and trader status
- Matching listings are shown in the alert log and copied to your clipboard as a whisper message

## Notifications

WFTW uses your operating system's notification system. You can configure:

- Default notification sound
- Per-item custom sounds
- Notification volume
- Whether notifications are enabled

Sounds are stored locally in the app's `Media/Sound` folder. You can replace them with your own `.wav` files if you want.

## Where your data is stored

WFTW stores everything locally in the same folder where you run it:

- `watchlist.json` — your tracked items and price filters
- `notif.json` — notification sound settings
- `settings.json` — app preferences
- `Logs/` — diagnostic and alert logs

These files are plain JSON and can be backed up, copied, or moved between installs. The README download table assumes you are running from the extracted release folder. If you move or delete that folder, your local data goes with it.

## How monitoring works

WFTW reads the public Warframe Market listing feed and checks it against your watchlist. When a match is found, it:

1. Adds the listing to the alert log
2. Shows a desktop notification
3. Optionally copies a chat message to your clipboard
4. Plays a sound

Monitoring continues in the background until you close the app. Network errors or API changes may temporarily prevent alerts; WFTW will retry automatically.

## Network and API behavior

- WFTW contacts only `api.warframe.market`
- It uses read-only `GET` requests; it does not submit orders, log in, or modify data
- It does not send Warframe Market credentials, cookies, or authentication tokens
- It does not contact Digital Extremes servers or the Warframe game client
- It does not send telemetry, analytics, or crash reports anywhere

### Rate limits

Warframe Market limits public API clients to **3 requests per second**. WFTW is designed to stay within this limit.

## Limitations

- WFTW depends on the public Warframe Market API. If the API changes, goes down, or changes its rate limits, WFTW may stop working until it is updated.
- Public listings can change or disappear at any time.
- Notifications are not instant. WFTW polls the market on a short interval, so there is a small delay between a listing being posted and WFTW noticing it.
- WFTW cannot guarantee that a listing will still be available after you receive a notification.
- WFTW cannot guarantee listing accuracy, seller/buyer availability, or transaction completion.
- WFTW does not verify that listings are still valid when you use the copied message.

## Troubleshooting

**App does not start**
- Make sure you extracted the archive before running it
- On Windows, if SmartScreen appears, click "More info" and then "Run anyway"
- On macOS, if the app is blocked, right-click the app and choose "Open"
- On Linux, make sure the executable has run permission: `chmod +x WFTW-linux-x64.AppImage`

**No notifications appear**
- Check your system notification settings
- Make sure WFTW's notifications are allowed at the OS level
- On Linux, ensure you have a notification daemon running, such as `dunst` or `xfce4-notifyd`

**No orders are detected**
- Verify your internet connection
- Check that Warframe Market is online and reachable
- Make sure your watchlist items and filters are entered correctly
- Open the `Logs/` folder and check `wftw_alerts.log` and `tracker_api.log` for errors

**Settings or watchlist disappeared**
- Did you move or delete the folder WFTW is running from?
- WFTW stores data next to the executable. If you removed that folder, the data is gone unless you have a backup

**High CPU or network usage**
- WFTW is designed to be lightweight. If you see high usage, check that you do not have dozens of duplicate instances running
- Look in `Logs/tracker_perf.log` for timing details

**How to report a problem**
- Include the contents of the `Logs/` folder
- Mention your platform, WFTW version, and what you expected to happen

## Third-party software and licenses

WFTW is built with:

- [Flet](https://flet.dev) — MIT License
- [requests](https://requests.readthedocs.io/) — Apache 2.0 License
- [pyperclip](https://pyperclip.readthedocs.io/) — BSD License
- [PyInstaller](https://pyinstaller.org/) — GPL / proprietary build tool used only for packaging

Release bundles also include the Python runtime, Flutter runtime, and platform-specific system libraries, each under its own license. Those bundled components are not covered by WFTW's MIT license.

## Warframe and Digital Extremes legal notices

Warframe, Warframe-related imagery, and all Warframe trademarks and copyrights are owned by [Digital Extremes Ltd.](https://www.digitalextremes.com/)

WFTW is not affiliated with, endorsed by, or connected to Digital Extremes Ltd. or Warframe in any way.

Warframe Market is a community-run website and is not affiliated with Digital Extremes Ltd.

By using WFTW you remain responsible for complying with:

- [Warframe Terms of Use](https://www.warframe.com/en/terms)
- [Warframe EULA](https://www.warframe.com/en/eula)
- [Warframe Privacy Policy](https://www.warframe.com/privacy)
- [Warframe Market Terms of Service](https://warframe.market/tos)
- [Warframe Market Rules](https://docs.warframe.market/docs/rules/overview)
- [Warframe Market API Documentation](https://docs.warframe.market/docs/api/overview/)

WFTW does not bypass, override, or violate any of these policies. It reads public marketplace data only and does not automate in-game actions.

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## License

WFTW is released under the [MIT License](LICENSE).

import time
import subprocess
import sys
from datetime import datetime
import requests
import json
import os
import threading

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


def _play_notification_sound():
    path = os.path.join("sounds", "notification.wav")
    if not os.path.isfile(path):
        return
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif sys.platform == "darwin":
            subprocess.Popen(["afplay", path])
        else:
            if os.path.isfile("/usr/bin/paplay"):
                subprocess.Popen(["paplay", path])
            elif os.path.isfile("/usr/bin/aplay"):
                subprocess.Popen(["aplay", path])
    except Exception:
        pass

def _write_debug_log(msg):
    try:
        with open("tracker_debug.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except Exception:
        pass


def _write_perf_log(msg):
    try:
        with open("tracker_perf.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {msg}\n")
    except Exception:
        pass


def _write_api_log(msg):
    try:
        with open("tracker_api.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except Exception:
        pass


CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watchlist.json")
WTS_WATCHLIST = {}
WTB_WATCHLIST = {}

STATUS_ONLY_INGAME = "ingame"
STATUS_ONLY_ONLINE = "online"
STATUS_BOTH = "both"


def _safe_defaults():
    return {
        "Lua Madurai Lens": 33,
        "Lua Zenurik Lens": 33,
        "Primed Counterbalance": [75, 10],
        "Primed Cleanse Infested": [75, 10],
    }


def load_watchlists():
    global WTS_WATCHLIST, WTB_WATCHLIST
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        WTS_WATCHLIST.clear()
        WTS_WATCHLIST.update(data.get("wts", {}))
        WTB_WATCHLIST.clear()
        WTB_WATCHLIST.update(data.get("wtb", {}))
    else:
        WTS_WATCHLIST.clear()
        WTS_WATCHLIST.update(_safe_defaults())
        WTB_WATCHLIST.clear()
        save_watchlists()
    if hasattr(threading, 'current_thread') and threading.current_thread().name == 'MainThread':
        try:
            with open("load_log.txt", "a") as f:
                f.write(f"load_watchlists: WTS={len(WTS_WATCHLIST)}, WTB={len(WTB_WATCHLIST)}\n")
        except Exception:
            pass


def save_watchlists():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"wts": WTS_WATCHLIST, "wtb": WTB_WATCHLIST}, f, indent=4)
        f.flush()
    try:
        with open("save_watchlists_log.txt", "a") as f:
            f.write(f"save_watchlists: WTS={len(WTS_WATCHLIST)}, WTB={len(WTB_WATCHLIST)}\n")
    except Exception:
        pass


ITEM_CACHE = {}
ITEMS_LOADED = threading.Event()

_shared_recent_orders = []
_shared_orders_lock = threading.Lock()
_shared_fetch_lock = threading.Lock()
_shared_fetch_started = False


def _ensure_shared_fetcher():
    global _shared_fetch_started
    if _shared_fetch_started:
        return
    with _shared_fetch_lock:
        if _shared_fetch_started:
            return
        _shared_fetch_started = True

        def _fetch_loop():
            global _shared_recent_orders
            while True:
                try:
                    r = requests.get(
                        "https://api.warframe.market/v2/orders/recent?language=en&platform=pc&limit=500",
                        headers={"Language": "en", "Platform": "pc"},
                        timeout=8,
                    )
                    r.raise_for_status()
                    with _shared_orders_lock:
                        _shared_recent_orders = r.json().get("data", [])
                except Exception:
                    pass
                time.sleep(1)

        threading.Thread(target=_fetch_loop, daemon=True).start()


def get_shared_recent_orders():
    with _shared_orders_lock:
        return list(_shared_recent_orders)


def fetch_items():
    global ITEM_CACHE
    t0 = time.time()
    try:
        r = requests.get(
            "https://api.warframe.market/v2/items?language=en&platform=pc",
            headers={"Language": "en", "Platform": "pc"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        count_before = len(ITEM_CACHE)
        ITEM_CACHE.clear()
        for item in data["data"]:
            name = item.get("i18n", {}).get("en", {}).get("name")
            if name:
                ITEM_CACHE[name.lower().strip()] = {
                    "name": name,
                    "slug": item["slug"],
                    "id": item["id"],
                    "maxRank": item.get("maxRank"),
                    "subtypes": item.get("subtypes"),
                }
        count_after = len(ITEM_CACHE)
        dt = (time.time() - t0) * 1000
        _write_perf_log(f"fetch_items: {count_after} items loaded in {dt:.0f}ms")
        _write_api_log(f"GET /v2/items -> {r.status_code} {count_after} items")
        ITEMS_LOADED.set()
        return True
    except Exception as e:
        dt = (time.time() - t0) * 1000
        _write_api_log(f"GET /v2/items FAILED after {dt:.0f}ms: {e}")
        print(f"Failed to load items: {e}")
        return False


def resolve_item(name):
    if not ITEM_CACHE:
        if not fetch_items():
            return None
    key = name.lower().strip()
    real_item = key.split("_rank_")[0]
    return ITEM_CACHE.get(real_item)


class TrackerCore:
    def __init__(self, log_callback=None, match_callback=None):
        self.log_callback = log_callback
        self.match_callback = match_callback
        self.running = False
        self.thread = None
        self.seen_deals = set()
        self.mode = "wts"
        self._stop_event = threading.Event()
        self.status_filter = STATUS_BOTH
        self.item_lookup = {}
        self._user_stopped = False

    def log(self, msg):
        if self.log_callback:
            try:
                self.log_callback(msg)
            except Exception as e:
                _write_debug_log(f"[{self.mode.upper()}] log_callback FAILED: {e} | msg={msg!r}")

    def start(self, mode="wts", status_filter=STATUS_BOTH):
        if self.running:
            _write_debug_log(f"[{mode.upper()}] start() skipped: already running")
            return
        self.mode = mode
        self.status_filter = status_filter
        self.running = True
        self._stop_event.clear()
        self.seen_deals.clear()
        self._user_stopped = False
        self.thread = threading.Thread(target=self._run_tracker, daemon=True)
        self.thread.start()
        _write_debug_log(f"[{mode.upper()}] start() -> thread launched")

    def stop(self):
        _write_debug_log(f"[{self.mode.upper()}] stop() called")
        self._user_stopped = True
        self.running = False
        self._stop_event.set()

    def _get_watchlist(self):
        return WTS_WATCHLIST if self.mode == "wts" else WTB_WATCHLIST

    def _status_ok(self, order):
        user = order.get("user") or {}
        status = user.get("status", "offline")
        if self.status_filter == STATUS_BOTH:
            return status in ("online", "ingame")
        return status == self.status_filter

    def _run_tracker(self):
        load_watchlists()
        watchlist = self._get_watchlist()
        prefix = "wts" if self.mode == "wts" else "wtb"
        direction = "Want to Sell" if self.mode == "wts" else "Want to Buy"
        self.log(f"[{direction}] Scan started")
        self.log(f"[{direction}] Loaded {len(watchlist)} items from watchlist")

        if not ITEM_CACHE:
            if not fetch_items():
                self.log(f"[{direction}] Failed to load item catalog from API.")
                self.running = False
                return
        self.log(f"[{direction}] Item catalog loaded: {len(ITEM_CACHE)} items")

        _ensure_shared_fetcher()
        try:
            while self.running and not self._stop_event.is_set():
                watchlist = self._get_watchlist()
                item_lookup = {}
                skipped = 0
                for target_name, config_value in watchlist.items():
                    base_name = target_name.split("|")[0]
                    item = resolve_item(base_name)
                    if not item:
                        skipped += 1
                        continue
                    max_price = config_value[0] if isinstance(config_value, list) else config_value
                    target_rank = config_value[1] if isinstance(config_value, list) else None
                    item_lookup[item["id"]] = {
                        "name": item["name"],
                        "slug": item["slug"],
                        "max_price": max_price,
                        "target_rank": target_rank,
                        "config_value": config_value,
                        "original_key": target_name,
                    }
                if not item_lookup:
                    self.log(f"[{direction}] No valid items to scan.")
                    self.running = False
                    return
                try:
                    recent_orders = get_shared_recent_orders()
                    _write_perf_log(f"[{direction}] API GET /orders/recent -> {len(recent_orders)} orders")
                    _write_api_log(f"GET /orders/recent -> 200 {len(recent_orders)} orders")
                except Exception as e:
                    _write_api_log(f"GET /orders/recent FAILED: {e}")
                    self.log(f"[{direction}] API error: {e}")
                    time.sleep(1.5)
                    continue

                checked = 0
                matched = 0
                type_filtered = 0
                status_filtered = 0
                item_filtered = 0
                rank_filtered = 0
                price_filtered = 0
                api_type_map = {"sell": "wts", "buy": "wtb"}
                sample_logged = False
                for order in recent_orders:
                    if not self.running or self._stop_event.is_set():
                        _write_debug_log(f"[{direction}] Breaking loop: running={self.running} stop_event={self._stop_event.is_set()}")
                        break
                    raw_type = order.get("type", "")
                    if api_type_map.get(raw_type) != prefix:
                        type_filtered += 1
                        continue
                    user = order.get("user") or {}
                    status = user.get("status", "offline")
                    if not self._status_ok(order):
                        status_filtered += 1
                        if not sample_logged:
                            _write_debug_log(f"[{direction}] Sample filtered by status: order_status={status} filter={self.status_filter}")
                            sample_logged = True
                        continue
                    item_id = order.get("itemId")
                    if item_id not in item_lookup:
                        item_filtered += 1
                        if not sample_logged:
                            _write_debug_log(f"[{direction}] Sample filtered by item: order_itemId={item_id} tracked_ids={list(item_lookup.keys())}")
                            sample_logged = True
                        continue
                    order_rank = order.get("rank")
                    order_subtype = order.get("subtype")
                    item_meta = item_lookup[item_id]
                    target_rank = item_meta["target_rank"]
                    if target_rank is not None and order_rank != target_rank:
                        rank_filtered += 1
                        if not sample_logged:
                            _write_debug_log(f"[{direction}] Sample filtered by rank: order_rank={order_rank} target_rank={target_rank}")
                            sample_logged = True
                        continue
                    price = order.get("platinum")
                    max_price = item_meta["max_price"]
                    if self.mode == "wts" and price > max_price:
                        price_filtered += 1
                        if not sample_logged:
                            _write_debug_log(f"[{direction}] Sample filtered by price: order_price={price} max_price={max_price} mode={self.mode}")
                            sample_logged = True
                        continue
                    elif self.mode == "wtb" and price < max_price:
                        price_filtered += 1
                        if not sample_logged:
                            _write_debug_log(f"[{direction}] Sample filtered by price: order_price={price} max_price={max_price} mode={self.mode}")
                            sample_logged = True
                        continue

                    checked += 1
                    ign = user.get("ingameName", "unknown")
                    order_id = order.get("id")

                    fingerprint = f"{prefix}_{item_id}_{price}_{ign}_{order_rank}_{order_subtype}_{order_id}"
                    if fingerprint in self.seen_deals:
                        continue
                    self.seen_deals.add(fingerprint)

                    matched += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    clean_name = item_meta["name"]

                    if order_rank is not None:
                        whisper_msg = f"/w {ign} Hi! I want to {'buy' if self.mode == 'wts' else 'sell'}: {clean_name} (Rank {order_rank}) for {price} platinum. (warframe.market)"
                        display_rank = f" (Rank {order_rank})"
                    elif order_subtype is not None:
                        whisper_msg = f"/w {ign} Hi! I want to {'buy' if self.mode == 'wts' else 'sell'}: {clean_name} ({order_subtype.title()}) for {price} platinum. (warframe.market)"
                        display_rank = f" ({order_subtype.title()})"
                    else:
                        whisper_msg = f"/w {ign} Hi! I want to {'buy' if self.mode == 'wts' else 'sell'}: {clean_name} for {price} platinum. (warframe.market)"
                        display_rank = ""

                    price_label = "Your Min" if self.mode == "wtb" else "Your Max"
                    alert_full = (
                        f"\n{'='*60}\n"
                        f"MATCH DETECTED | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"Mode:     {direction}\n"
                        f"Item:     {clean_name}{display_rank}\n"
                        f"Price:    {price}p ({price_label}: {max_price}p)\n"
                        f"Seller:   {ign.upper()}\n"
                        f"{'-'*60}\n"
                        f"Copy/paste this directly into your game chat:\n"
                        f"{whisper_msg}\n"
                        f"{'='*60}\n"
                    )
                    _write_debug_log(alert_full)
                    if self.match_callback:
                        self.match_callback({
                            "mode": self.mode,
                            "direction": direction,
                            "item_name": clean_name,
                            "display_rank": display_rank,
                            "price": price,
                            "max_price": max_price,
                            "user": ign,
                            "timestamp": timestamp,
                            "whisper_msg": whisper_msg,
                        })

                    _play_notification_sound()

                    if HAS_PLYER:
                        try:
                            notification.notify(
                                title=f"MATCH: {clean_name}{display_rank}",
                                message=f"{price}p | {ign.upper()} | {direction}\n{whisper_msg}",
                                app_name="Warframe Trade Watch",
                                timeout=15,
                            )
                        except Exception:
                            pass

                debug_msg = f"[{direction}] Cycle: {len(recent_orders)} total | {type_filtered} wrong type | {status_filtered} wrong status | {item_filtered} wrong item | {rank_filtered} wrong rank | {price_filtered} wrong price | {checked} passed filters | {matched} new matches"
                _write_debug_log(debug_msg)
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            _write_debug_log(f"[{direction}] Stopping scan...")
            self.running = False
            _write_debug_log(f"[{direction}] Scan thread stopped")
            if self._user_stopped:
                self.log(f"[{direction}] Scan stopped")

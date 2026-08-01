import flet as ft
import json
import os
import shutil
import subprocess
import sys
import threading
import queue
import pyperclip
from datetime import datetime
from tracker_core import TrackerCore, WTS_WATCHLIST, WTB_WATCHLIST, save_watchlists, load_watchlists, fetch_items, ITEM_CACHE, resolve_item
try:
    from plyer import notification
    HAS_PLYER = True
except Exception:
    HAS_PLYER = False
try:
    import tkinter as tk
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False

CONFIG_PATH = "watchlist.json"
SETTINGS_PATH = "settings.json"
SOUNDS_PATH = "sounds.json"
STATUS_BOTH = "both"
STATUS_ONLY_INGAME = "ingame"
STATUS_ONLY_ONLINE = "online"
WTS_COLOR = "#cb4a9e"
WTB_COLOR = "#209e70"
BG_DARK = "#071013"
BG_LIGHT = "#171e21"


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def load_sounds_config():
    try:
        with open(SOUNDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"default_sound": "notification.wav", "sounds": {}}


def _apply_volume_to_wav(src_path, volume):
    if volume >= 0.99:
        return src_path
    try:
        import wave, struct, tempfile
        with wave.open(src_path, "rb") as wav_in:
            nchannels = wav_in.getnchannels()
            sampwidth = wav_in.getsampwidth()
            framerate = wav_in.getframerate()
            nframes = wav_in.getnframes()
            raw = wav_in.readframes(nframes)
        samples = struct.unpack(f"<{nframes * nchannels}h", raw)
        scaled = [int(s * volume) for s in samples]
        clamped = [max(-32768, min(32767, s)) for s in scaled]
        packed = struct.pack(f"<{len(clamped)}h", *clamped)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(tmp.name, "wb") as wav_out:
            wav_out.setnchannels(nchannels)
            wav_out.setsampwidth(sampwidth)
            wav_out.setframerate(framerate)
            wav_out.writeframes(packed)
        tmp.close()
        return tmp.name
    except Exception:
        return src_path


def play_notification_sound(sound_filename=None, volume=1.0):
    if not sound_filename:
        sound_filename = "notification.wav"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", sound_filename)
    if not os.path.isfile(path):
        return
    try:
        play_path = _apply_volume_to_wav(path, max(0.0, min(1.0, volume)))
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(play_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif sys.platform == "darwin":
            subprocess.Popen(["afplay", play_path])
        else:
            if os.path.isfile("/usr/bin/paplay"):
                subprocess.Popen(["paplay", play_path])
            elif os.path.isfile("/usr/bin/aplay"):
                subprocess.Popen(["aplay", play_path])
    except Exception:
        pass


class NotificationOverlay:
    def __init__(self):
        self.root = None
        self.thread = None
        self.running = False
        self._notify_queue = queue.Queue()
        self._active = []
        self._fixed_height = None
        self._max_width = 0

    def start(self):
        if not HAS_TKINTER:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            self.root.attributes("-topmost", True)
            self._poll()
            self.root.mainloop()
        except Exception:
            pass

    def _poll(self):
        try:
            item = self._notify_queue.get_nowait()
            self._show_window(*item)
        except queue.Empty:
            pass
        if self.running and self.root:
            try:
                self.root.after(100, self._poll)
            except Exception:
                pass

    def _reposition(self):
        try:
            if not self.root:
                return
            gap = 4
            width = self._max_width
            x = self.root.winfo_screenwidth() - width - 20
            y = self.root.winfo_screenheight() - self._fixed_height - 20
            for entry in reversed(self._active):
                try:
                    entry["win"].geometry(f"{width}x{self._fixed_height}+{x}+{y}")
                    y -= self._fixed_height + gap
                except Exception:
                    pass
        except Exception:
            pass

    def _show_window(self, title, line2, line3, title_color, price_color):
        try:
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.92)
            win.configure(bg=BG_DARK)

            frame = tk.Frame(win, bg=BG_LIGHT)
            frame.pack(fill="both", expand=True)

            inner = tk.Frame(frame, bg=BG_DARK)
            inner.pack(fill="both", expand=True, padx=2, pady=2)

            def _close_early(w=win):
                try:
                    self._destroy_window(w)
                except Exception:
                    pass

            close_btn = tk.Button(inner, text="✕", command=_close_early,
                                  bg=BG_DARK, fg="white", bd=0, font=("Segoe UI", 8, "bold"),
                                  activebackground=BG_LIGHT, activeforeground="white",
                                  cursor="hand2", padx=2, pady=0)
            close_btn.place(relx=1.0, rely=1.0, anchor="se", x=-4, y=-4)

            title_label = tk.Label(inner, text=title, fg=title_color, bg=BG_DARK, font=("Segoe UI", 11, "bold"), anchor="center", justify="center")
            title_label.pack(padx=12, pady=(4, 2))

            line2_label = tk.Label(inner, text=line2, fg="white", bg=BG_DARK, font=("Segoe UI", 9, "bold"), anchor="center", justify="center")
            line2_label.pack(padx=12, pady=2)

            line3_label = tk.Label(inner, text=line3, fg=price_color, bg=BG_DARK, font=("Segoe UI", 12, "bold"), anchor="center", justify="center")
            line3_label.pack(padx=12, pady=(2, 0))

            win.update_idletasks()
            title_w = title_label.winfo_reqwidth()
            line2_w = line2_label.winfo_reqwidth()
            line3_w = line3_label.winfo_reqwidth()
            natural_width = max(title_w, line2_w, line3_w) + 24
            natural_height = frame.winfo_reqheight() + 4

            if self._fixed_height is None:
                self._fixed_height = natural_height
            if natural_width > self._max_width:
                self._max_width = natural_width

            width = self._max_width
            height = self._fixed_height
            x = self.root.winfo_screenwidth() - width - 20
            y = self.root.winfo_screenheight() - height - 20
            win.geometry(f"{width}x{height}+{x}+{y}")

            self._active.append({"win": win})
            self._reposition()

            win.after(15000, self._destroy_window, win)
        except Exception:
            pass

    def _destroy_window(self, win):
        try:
            self._active = [w for w in self._active if w["win"] is not win]
            if not self._active:
                self._max_width = 0
                self._fixed_height = None
            else:
                max_w = 0
                for entry in self._active:
                    try:
                        inner = entry["win"].winfo_children()[0]
                        for child in inner.winfo_children():
                            w = child.winfo_reqwidth()
                            if w > max_w:
                                max_w = w
                    except Exception:
                        pass
                self._max_width = max_w
            self._reposition()
        except Exception:
            pass
        try:
            win.destroy()
        except Exception:
            pass

    def notify(self, title, line2, line3, title_color, price_color):
        if self.running:
            self._notify_queue.put((title, line2, line3, title_color, price_color))


_overlay = NotificationOverlay()


def show_overlay_notification(title, line2, line3, title_color="#aaaaaa", price_color="#aaaaaa", settings=None, sound_filename=None, volume=1.0):
    if settings is None:
        settings = {}
    if not settings.get("notifications_enabled", True):
        return
    try:
        if sys.platform == "linux":
            try:
                subprocess.Popen(["notify-send", title, f"{line2}\n{line3}", "-i", "dialog-information", "-t", "15000"])
            except Exception:
                pass
        elif sys.platform == "darwin" and HAS_PLYER:
            try:
                notification.notify(title=title, message=f"{line2}\n{line3}", app_name="Warframe Trade Watch", timeout=15)
            except Exception:
                pass
        elif sys.platform == "win32" and HAS_TKINTER:
            _overlay.notify(title, line2, line3, title_color, price_color)
        try:
            play_notification_sound(sound_filename, volume=volume)
        except Exception:
            pass
    except Exception:
        pass


def main(page: ft.Page):
    page.title = "Warframe Trade Watch"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_DARK
    page.padding = 16
    page.window.width = 1365
    page.window.height = 768
    page.window.min_width = 1365
    page.window.min_height = 768

    def _force_window_size():
        page.window.width = 1365
        page.window.height = 768
        page.window.min_width = 1365
        page.window.min_height = 768
        try:
            page.loop.call_soon_threadsafe(page.update)
        except Exception:
            pass

    threading.Timer(0.5, _force_window_size).start()

    log_output = ft.ListView(expand=True, spacing=4, auto_scroll=True, padding=8)
    log_output_wts = ft.ListView(expand=True, spacing=4, auto_scroll=True, padding=8)
    log_output_wtb = ft.ListView(expand=True, spacing=4, auto_scroll=True, padding=8)
    log_queue = queue.Queue()

    def append_log(msg):
        try:
            with open("wftw_alerts.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
        except Exception:
            pass
        log_queue.put(msg)

    def _color_for(msg):
        return None

    def _format_name(name):
        if "|" in name:
            return name.replace("|", " (", 1) + ")"
        return name

    def _make_match_card(data, on_delete=None):
        mode = data["mode"]
        item_name = data["item_name"]
        display_rank = data["display_rank"]
        price = data["price"]
        max_price = data["max_price"]
        user = data["user"]
        timestamp = data["timestamp"]
        whisper_msg = data["whisper_msg"]

        is_wts = mode == "wts"
        tag_color = WTS_COLOR if is_wts else WTB_COLOR

        def do_copy(e, msg=whisper_msg):
            try:
                pyperclip.copy(msg)
            except Exception:
                pass

        delete_btn = None
        if on_delete is not None:
            delete_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE, size=13, color=ft.Colors.RED_300),
                    ft.Text("Delete Log", size=13, color="#ff9800"),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                ink=True,
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                on_click=on_delete,
            )

        top_row = [
            ft.Text(f"[{timestamp}]", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(user, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
        ]
        if delete_btn is not None:
            top_row += [ft.Container(expand=True), delete_btn]
        else:
            top_row += [ft.Container(expand=True)]

        return ft.Container(
            content=ft.Column([
                ft.Row(top_row, spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Text(f"{item_name}{display_rank}", size=15, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Text(f"{price}p", size=15, color=tag_color, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CONTENT_COPY, size=15, color=ft.Colors.BLUE_400),
                            ft.Text("Copy", size=15, color=ft.Colors.BLUE_400),
                        ], spacing=2),
                        ink=True,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                        on_click=do_copy,
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0, tight=True),
            bgcolor=BG_LIGHT,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            margin=ft.Margin.only(bottom=2),
        )

    match_queue = queue.Queue()

    def _drain_matches():
        while True:
            data = match_queue.get()
            if data is None:
                break

            def _append(data=data):
                mode = data["mode"]
                card = None

                def on_delete(e):
                    nonlocal card
                    if card is None:
                        return
                    try:
                        target = log_output_wtb if mode == "wtb" else log_output_wts
                        if card in target.controls:
                            target.controls.remove(card)
                            page.update()
                    except Exception:
                        pass

                card = _make_match_card(data, on_delete=on_delete)
                try:
                    if mode == "wtb":
                        log_output_wtb.controls.append(card)
                        if len(log_output_wtb.controls) > 100:
                            log_output_wtb.controls.pop(0)
                    else:
                        log_output_wts.controls.append(card)
                        if len(log_output_wts.controls) > 100:
                            log_output_wts.controls.pop(0)
                except Exception:
                    pass
                try:
                    page.update()
                except Exception:
                    pass

            try:
                page.loop.call_soon_threadsafe(_append)
            except Exception:
                pass

    threading.Thread(target=_drain_matches, daemon=True).start()

    def _drain_queue():
        while True:
            msg = log_queue.get()
            if msg is None:
                break
            color = _color_for(msg)
            now = datetime.now().strftime("%H:%M:%S")
            full = f"[{now}] {msg}"

            def _append(msg=msg, color=color, full=full):
                try:
                    text_ctrl = ft.Text(full, selectable=True, font_family="Consolas", size=11, color=color)
                    if color == WTB_COLOR:
                        log_output_wtb.controls.append(text_ctrl)
                        if len(log_output_wtb.controls) > 400:
                            log_output_wtb.controls.pop(0)
                    elif color == WTS_COLOR:
                        log_output_wts.controls.append(text_ctrl)
                        if len(log_output_wts.controls) > 400:
                            log_output_wts.controls.pop(0)
                    else:
                        log_output.controls.append(text_ctrl)
                        if len(log_output.controls) > 400:
                            log_output.controls.pop(0)
                except Exception:
                    pass
                try:
                    page.update()
                except Exception:
                    pass

            try:
                page.loop.call_soon_threadsafe(_append)
            except Exception:
                pass

    threading.Thread(target=_drain_queue, daemon=True).start()

    load_watchlists()
    _overlay.start()
    _settings = load_settings()
    _sounds_config = load_sounds_config()
    current_status_filter = _settings.get("default_status", STATUS_ONLY_INGAME)
    if current_status_filter not in (STATUS_BOTH, STATUS_ONLY_INGAME, STATUS_ONLY_ONLINE):
        current_status_filter = STATUS_ONLY_INGAME
    tracking_status = "Waiting"

    def _on_match(data):
        match_queue.put(data)
        append_log(f"Found {data['item_name']}{data['display_rank']} in {data['mode'].upper()} list")
        color = WTS_COLOR if data["mode"] == "wts" else WTB_COLOR
        title = f"{data['item_name']}{data['display_rank']}"
        line2 = f"[{data['timestamp']}] {data['user'].upper()} ({data['mode'].upper()})"
        line3 = f"{data['price']}p"
        show_overlay_notification(title, line2, line3, title_color=color, price_color=color, settings=_settings, sound_filename=_sounds_config.get("default_sound"), volume=_settings.get("notification_volume", 1.0))

    core_wts = TrackerCore(log_callback=append_log, match_callback=_on_match)
    core_wtb = TrackerCore(log_callback=append_log, match_callback=_on_match)
    running = False
    tracking_status = "Waiting"

    wts_items_list = ft.Column(spacing=3, scroll=ft.ScrollMode.AUTO, expand=True)
    wtb_items_list = ft.Column(spacing=3, scroll=ft.ScrollMode.AUTO, expand=True)

    wts_price_field = ft.TextField(label="Max Plat", width=90, input_filter=ft.NumbersOnlyInputFilter(), dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")
    wtb_price_field = ft.TextField(label="Min Plat", width=90, input_filter=ft.NumbersOnlyInputFilter(), dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")

    wts_rank_field = ft.Dropdown(label="Rank", width=100, options=[], visible=False, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")
    wtb_rank_field = ft.Dropdown(label="Rank", width=100, options=[], visible=False, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")

    wts_subtype_dropdown = ft.Dropdown(label="Subtype", width=160, options=[], visible=False, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")
    wtb_subtype_dropdown = ft.Dropdown(label="Subtype", width=160, options=[], visible=False, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")

    wts_add_btn = ft.IconButton(icon=ft.Icons.ADD_CIRCLE, tooltip="Add item", icon_color=WTS_COLOR)
    wtb_add_btn = ft.IconButton(icon=ft.Icons.ADD_CIRCLE, tooltip="Add item", icon_color=WTB_COLOR)

    wts_rank_hint = ft.Text("", size=9, color=ft.Colors.ON_SURFACE_VARIANT, visible=False)
    wtb_rank_hint = ft.Text("", size=9, color=ft.Colors.ON_SURFACE_VARIANT, visible=False)

    status_text = ft.Text("Loading items...", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    tracking_text = ft.Text("Loading items...", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    status_label = ft.Text("Status: ", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    status_word = ft.Text("Waiting", size=12, color="#ff9800")
    status_detail = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    def _apply_status_color():
        if tracking_status == "Stopped":
            status_word.color = ft.Colors.RED_400
        elif tracking_status.startswith("Active"):
            status_word.color = ft.Colors.GREEN_400
        elif tracking_status == "Waiting":
            status_word.color = "#ff9800"
        else:
            status_word.color = ft.Colors.ON_SURFACE_VARIANT

    def _set_tracking_status():
        tracking_text.value = f"{len(WTS_WATCHLIST)} WTS + {len(WTB_WATCHLIST)} WTB items loaded."
        parts = tracking_status.split(" ", 1)
        status_word.value = parts[0] if parts else ""
        status_detail.value = f" {parts[1]}" if len(parts) > 1 else ""
        _apply_status_color()

    def set_status_error(msg):
        tracking_text.value = msg
        status_word.value = ""
        status_detail.value = ""

    def on_item_selected(item_name, rank_field=None, rank_hint=None, subtype_dropdown=None):
        item = resolve_item(item_name) if item_name else None
        if not item:
            if rank_field: rank_field.visible = False; rank_hint.visible = False
            if subtype_dropdown: subtype_dropdown.visible = False
            page.update()
            return

        if rank_field: rank_field.visible = False; rank_hint.visible = False
        if subtype_dropdown: subtype_dropdown.visible = False

        if item.get("maxRank") is not None:
            max_rank = item["maxRank"]
            if rank_field:
                rank_field.options = [ft.dropdown.Option(str(r), str(r)) for r in range(max_rank + 1)]
                rank_field.visible = True
                rank_field.value = "0"
                rank_hint.value = f"Max: {max_rank}"
                rank_hint.visible = True
        elif item.get("subtypes"):
            subtypes = item["subtypes"]
            if subtype_dropdown:
                subtype_dropdown.options = [ft.dropdown.Option(st, st.replace("_", " ").title()) for st in subtypes]
                subtype_dropdown.visible = True
                subtype_dropdown.value = subtypes[0]
        page.update()

    def filter_dropdown(tf, suggestions_col, rank_field=None, rank_hint=None, subtype_dropdown=None):
        query = tf.value.strip().lower()
        if not query:
            suggestions_col.controls = []
            suggestions_col.visible = False
            suggestions_col.update()
            if rank_field: rank_field.visible = False; rank_hint.visible = False
            if subtype_dropdown: subtype_dropdown.visible = False
            page.update()
            return

        names = sorted({v["name"] for v in ITEM_CACHE.values()})
        matches = [name for name in names if query in name.lower()][:5]
        if not matches:
            suggestions_col.controls = []
            suggestions_col.visible = False
            suggestions_col.update()
            page.update()
            return

        def make_suggestion(name):
            return ft.Container(
                content=ft.Row([ft.Text(name, size=12, expand=True)], expand=True),
                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                on_click=lambda e, n=name: on_suggestion_click(n, tf, suggestions_col, rank_field, rank_hint, subtype_dropdown),
                data=name,
                ink=True,
                bgcolor=BG_LIGHT,
            )

        suggestions_col.controls = [make_suggestion(n) for n in matches]
        suggestions_col.visible = True
        suggestions_col.update()
        page.update()

    def on_suggestion_click(item_name, search_field, suggestions_col, rank_field=None, rank_hint=None, subtype_dropdown=None):
        search_field.value = item_name
        search_field.update()
        suggestions_col.controls = []
        suggestions_col.visible = False
        suggestions_col.update()
        on_item_selected(item_name, rank_field, rank_hint, subtype_dropdown)

    def close_suggestions(suggestions_col):
        if suggestions_col.visible:
            suggestions_col.controls = []
            suggestions_col.visible = False
            suggestions_col.update()

    def on_page_click(e):
        for sf, sug in [(wts_search_tf, wts_suggestions), (wtb_search_tf, wtb_suggestions)]:
            if sug.visible:
                target = e.control
                inside = False
                while target is not None:
                    if target is sf or target is sug:
                        inside = True
                        break
                    target = target.parent
                if not inside:
                    close_suggestions(sug)

    page.on_click = on_page_click

    def populate_dropdowns():
        names = sorted({v["name"] for v in ITEM_CACHE.values()})
        tracking_text.value = f"Items loaded: {len(names)} | API: warframe.market/v2"

    def load_items_bg():
        if fetch_items():
            populate_dropdowns()
            try:
                page.loop.call_soon_threadsafe(page.update)
            except Exception:
                pass

    threading.Thread(target=load_items_bg, daemon=True).start()

    wts_search_tf = ft.TextField(label="Item", hint_text="Search item...", expand=True, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")
    wtb_search_tf = ft.TextField(label="Item", hint_text="Search item...", expand=True, dense=True, border_color=BG_LIGHT, focused_border_color="#9ecaed")

    wts_suggestions = ft.Column(visible=False, spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
    wtb_suggestions = ft.Column(visible=False, spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    wts_search_tf.on_change = lambda e: filter_dropdown(wts_search_tf, wts_suggestions, wts_rank_field, wts_rank_hint, wts_subtype_dropdown)
    wtb_search_tf.on_change = lambda e: filter_dropdown(wtb_search_tf, wtb_suggestions, wtb_rank_field, wtb_rank_hint, wtb_subtype_dropdown)

    def make_item_row(name, value, mode):
        display_name = name.split("|")[0] if "|" in name else name
        if isinstance(value, list):
            price = value[0]
            if len(value) > 1:
                if isinstance(value[1], int):
                    extra = f"Rank: {value[1]}"
                else:
                    extra = f"{value[1]}"
            else:
                extra = ""
        else:
            price = value
            extra = ""
        color = WTS_COLOR if mode == "wts" else WTB_COLOR
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Text(display_name, expand=1, size=13, no_wrap=False),
                    ft.Text(extra, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                ], expand=1, spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    ft.Text(f"{price}p", size=13, color=color),
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT, size=14, color="#ff9800"),
                        padding=3,
                        ink=True,
                        tooltip="Edit Platinum",
                        on_click=lambda e, n=name, m=mode, pv=price: edit_platinum(n, m, pv)
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_FOREVER, size=14, color="#ff0000"),
                        padding=3,
                        ink=True,
                        tooltip="Remove",
                        on_click=lambda e, n=name, m=mode: delete_item(n, m)
                    ),
                ], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=BG_LIGHT,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            margin=ft.Margin.only(bottom=2),
        )

    def render_watchlist(column, watchlist, mode):
        column.controls.clear()
        if not watchlist:
            column.controls.append(ft.Row([ft.Text("No items. Click + to add.", expand=True, italic=True, color=ft.Colors.ON_SURFACE_VARIANT, size=11)], expand=True))
            return
        for name, val in watchlist.items():
            column.controls.append(make_item_row(name, val, mode))

    render_watchlist(wts_items_list, WTS_WATCHLIST, "wts")
    render_watchlist(wtb_items_list, WTB_WATCHLIST, "wtb")

    def delete_item(name, mode):
        if mode == "wts":
            WTS_WATCHLIST.pop(name, None)
            col = wts_items_list
        else:
            WTB_WATCHLIST.pop(name, None)
            col = wtb_items_list
        save_watchlists()
        render_watchlist(col, WTS_WATCHLIST if mode == "wts" else WTB_WATCHLIST, mode)
        append_log(f"Removed {_format_name(name)} from {mode.upper()}")

    def edit_platinum(name, mode, old_price):
        display_name = name.split("|")[0]
        parts = name.split("|")[1:] if "|" in name else []
        rank = None
        subtype = None
        if parts:
            try:
                rank = int(parts[0])
            except ValueError:
                subtype = parts[0]

        if mode == "wts":
            title = "Edit Platinum (WTS Max)"
            current_label = "Current Max:"
            current_value = f"{old_price}p"
            watchlist = WTS_WATCHLIST
        else:
            title = "Edit Platinum (WTB Min)"
            current_label = "Current Min:"
            current_value = f"{old_price}p"
            watchlist = WTB_WATCHLIST

        new_price_field = ft.TextField(label="New Platinum", value=str(old_price), keyboard_type=ft.KeyboardType.NUMBER, dense=True, text_align=ft.TextAlign.CENTER)

        rows = [
            ft.Text(display_name, size=13, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Row([
                ft.Text(current_label, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(current_value, size=13, color=WTS_COLOR if mode == "wts" else WTB_COLOR),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        ]
        if rank is not None:
            rows.insert(1, ft.Text(f"Rank: {rank}", size=11, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER))
        elif subtype is not None:
            rows.insert(1, ft.Text(f"Subtype: {subtype.replace('_', ' ').title()}", size=11, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER))

        def do_save(e):
            raw = new_price_field.value.strip()
            if not raw:
                append_log("Platinum value cannot be empty.")
                page.update()
                return
            try:
                nv = int(raw)
            except ValueError:
                append_log("Enter a valid integer.")
                page.update()
                return
            raw_name = name
            if rank is not None:
                key = f"{name.split('|')[0]}|{rank}"
                watchlist[key] = [nv, rank]
            elif subtype is not None:
                key = f"{name.split('|')[0]}|{subtype}"
                watchlist[key] = [nv, subtype]
            else:
                watchlist[name] = nv
            save_watchlists()
            col = wts_items_list if mode == "wts" else wtb_items_list
            render_watchlist(col, watchlist, mode)
            append_log(f"Updated platinum for {_format_name(name)}: {old_price}p -> {nv}p ({mode.upper()})")
            page.pop_dialog()

        dlg = ft.AlertDialog(
            title=ft.Text(title, text_align=ft.TextAlign.CENTER),
            content=ft.Column([
                *rows,
                new_price_field,
            ], tight=True, spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("Save", on_click=do_save),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dlg)

    def start_tracker(e):
        nonlocal running, tracking_status
        load_watchlists()
        modes = []
        if WTS_WATCHLIST:
            modes.append("Want to Sell")
        if WTB_WATCHLIST:
            modes.append("Want to Buy")
        if not modes:
            set_status_error("No items tracked")
            page.update()
            return
        if not running:
            running = True
            tracking_status = f"Active ({current_status_filter})"
            start_btn.visible = False
            stop_btn.visible = True
            append_log(f"Scan started | {len(WTS_WATCHLIST)} WTS + {len(WTB_WATCHLIST)} WTB items | Mode: {' + '.join(modes)}")
            core_wts.start(mode="wts", status_filter=current_status_filter)
            core_wtb.start(mode="wtb", status_filter=current_status_filter)
            _set_tracking_status()
            _apply_status_color()
            page.update()

    def stop_tracker(e):
        nonlocal running, tracking_status
        if not running:
            return
        running = False
        tracking_status = "Stopped"
        start_btn.disabled = False
        start_btn.visible = True
        stop_btn.visible = False
        append_log("Stopping scan...")
        core_wts.stop()
        core_wtb.stop()
        append_log("Scan stopped")
        _set_tracking_status()
        _apply_status_color()
        page.update()

    def test_notification(e):
        if HAS_PLYER:
            try:
                notification.notify(
                    title="TEST: Attachment Prime Set",
                    message="150p | PLAYER_ONE | Selling to you\nHi! I'm selling Attachment Prime Set for 150 platinum",
                    app_name="Warframe Trade Watch",
                    timeout=15,
                )
                append_log("System notification sent")
            except Exception as ex:
                append_log(f"System notification failed: {ex}")
        show_overlay_notification("Attachment Prime Set", "[23:17:39] PLAYER_ONE (WTS)", "150p", title_color=WTS_COLOR, price_color=WTS_COLOR, settings={"notifications_enabled": True}, sound_filename=_sounds_config.get("default_sound"), volume=_settings.get("notification_volume", 1.0))
        append_log("Overlay notification shown")
        page.update()

    start_btn = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.PLAY_ARROW), ft.Text("Scan")], spacing=8, tight=True),
        on_click=start_tracker,
        bgcolor=ft.Colors.GREEN_400,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    stop_btn = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.STOP), ft.Text("Stop")], spacing=8, tight=True),
        on_click=stop_tracker,
        bgcolor=ft.Colors.RED_400,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        visible=False,
    )
    def _build_settings_dialog():
        def _sync_main_status():
            status_segmented.selected = [current_status_filter]
            status_segmented.update()
            tracking_status = f"Active ({current_status_filter})" if running else "Idle"
            _set_tracking_status()
            _apply_status_color()
            page.update()

        def _on_default_status_changed(e):
            nonlocal current_status_filter, tracking_status
            current_status_filter = e.control.selected[0] if e.control.selected else STATUS_ONLY_INGAME
            _sync_main_status()
            _settings["default_status"] = current_status_filter
            save_settings(_settings)
            append_log(f"Default status filter set to {current_status_filter}")

        default_status_seg = ft.SegmentedButton(
            selected=[current_status_filter],
            segments=[
                ft.Segment(value=STATUS_ONLY_INGAME, label=ft.Text("In Game", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value=STATUS_ONLY_ONLINE, label=ft.Text("On Site", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value=STATUS_BOTH, label=ft.Text("Both", size=13, weight=ft.FontWeight.W_500)),
            ],
            on_change=_on_default_status_changed,
            width=360,
        )

        notifications_enabled = _settings.get("notifications_enabled", True)

        def _on_notifications_changed(e):
            selected = e.control.selected[0] if e.control.selected else "on"
            if selected == "test":
                test_notification(e)
                notifications_seg.selected = ["on" if _settings.get("notifications_enabled", True) else "off"]
                notifications_seg.update()
                return
            _settings["notifications_enabled"] = selected == "on"
            save_settings(_settings)
            append_log(f"Notifications {'enabled' if selected == 'on' else 'disabled'}")
            page.update()

        notifications_seg = ft.SegmentedButton(
            selected=["on" if notifications_enabled else "off"],
            segments=[
                ft.Segment(value="on", label=ft.Text("On", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="off", label=ft.Text("Off", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="test", label=ft.Row([ft.Icon(ft.Icons.NOTIFICATIONS, size=14), ft.Text("Test", size=13, weight=ft.FontWeight.W_500)], spacing=4, tight=True)),
            ],
            on_change=_on_notifications_changed,
            width=360,
        )

        current_sound = _settings.get("notification_sound") or _sounds_config.get("default_sound") or "notification.wav"
        current_volume = _settings.get("notification_volume", 1.0)
        sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        wav_files = sorted([f for f in os.listdir(sound_dir) if f.lower().endswith(".wav")]) if os.path.isdir(sound_dir) else []
        if not wav_files:
            wav_files = [current_sound] if current_sound else ["notification.wav"]

        current_sound = _settings.get("notification_sound") or _sounds_config.get("default_sound") or "notification.wav"
        current_volume = _settings.get("notification_volume", 1.0)
        sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
        wav_files = sorted([f for f in os.listdir(sound_dir) if f.lower().endswith(".wav")]) if os.path.isdir(sound_dir) else []
        if not wav_files:
            wav_files = [current_sound] if current_sound else ["notification.wav"]

        def _on_browse_click(e):
            folder = sound_dir
            try:
                if sys.platform == "win32":
                    os.startfile(folder)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
            except Exception as ex:
                append_log(f"Failed to open sounds folder: {ex}")

        browse_btn = ft.Container(
            content=ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color="white"),
            bgcolor=BG_LIGHT,
            border_radius=6,
            padding=6,
            width=32,
            height=32,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=_on_browse_click,
        )

        def _refresh_sounds():
            new_files = sorted([f for f in os.listdir(sound_dir) if f.lower().endswith(".wav")]) if os.path.isdir(sound_dir) else []
            if not new_files:
                new_files = [current_sound] if current_sound else ["notification.wav"]
            sound_dropdown.options = [ft.dropdown.Option(f) for f in new_files]
            if sound_dropdown.value not in new_files:
                sound_dropdown.value = new_files[0]
            sound_dropdown.update()

        refresh_btn = ft.Container(
            content=ft.Icon(ft.Icons.REFRESH, size=16, color="white"),
            bgcolor=BG_LIGHT,
            border_radius=6,
            padding=6,
            width=32,
            height=32,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=lambda e: _refresh_sounds(),
        )

        volume_text = ft.Text(f"{int(current_volume * 100)}%", size=11, width=36, text_align=ft.TextAlign.CENTER)

        volume_slider = ft.Slider(
            min=0,
            max=100,
            value=int(current_volume * 100),
            width=120,
        )

        def _on_volume_changed(e):
            val = volume_slider.value
            _settings["notification_volume"] = val / 100.0
            save_settings(_settings)
            volume_text.value = f"{int(val)}%"
            volume_text.update()
            page.update()

        sound_dropdown = ft.Dropdown(
            value=current_sound if current_sound in wav_files else wav_files[0],
            options=[ft.dropdown.Option(f) for f in wav_files],
            dense=True,
            bgcolor=BG_LIGHT,
            border_color=ft.Colors.OUTLINE_VARIANT,
            focused_border_color=ft.Colors.OUTLINE_VARIANT,
        )

        def _on_sound_selected(e):
            selected = sound_dropdown.value
            if selected:
                _settings["notification_sound"] = selected
                _sounds_config["default_sound"] = selected
                save_settings(_settings)
                append_log(f"Sound set to {selected}")

        sound_dropdown.on_change = _on_sound_selected

        sound_seg = ft.Stack([
            ft.SegmentedButton(
                selected=[],
                allow_empty_selection=True,
                disabled=True,
                segments=[
                    ft.Segment(value="open", label=ft.Text("")),
                    ft.Segment(value="refresh", label=ft.Text("")),
                    ft.Segment(value="volume", label=ft.Text("")),
                    ft.Segment(value="indicator", label=ft.Text("")),
                    ft.Segment(value="sound", label=ft.Text("")),
                ],
                width=360,
            ),
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color="white"),
                        bgcolor=BG_LIGHT,
                        width=40,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        ink=True,
                        on_click=_on_browse_click,
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=ft.Icon(ft.Icons.REFRESH, size=16, color="white"),
                        bgcolor=BG_LIGHT,
                        width=40,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        ink=True,
                        on_click=lambda e: _refresh_sounds(),
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=volume_slider,
                        bgcolor=BG_LIGHT,
                        width=140,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=0),
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=volume_text,
                        bgcolor=BG_LIGHT,
                        width=40,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Container(
                        content=sound_dropdown,
                        bgcolor=BG_LIGHT,
                        expand=True,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.symmetric(horizontal=4, vertical=0),
                    ),
                ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                width=360,
                height=40,
            ),
        ], width=360, height=40, clip_behavior=ft.ClipBehavior.HARD_EDGE)

        settings_rows = ft.Column([
            ft.Row([
                ft.Text("Default Status Filter", size=14, weight=ft.FontWeight.BOLD, width=160),
                default_status_seg,
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([
                ft.Text("Notifications", size=14, weight=ft.FontWeight.BOLD, width=160),
                notifications_seg,
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([
                ft.Text("Sound", size=14, weight=ft.FontWeight.BOLD, width=160),
                sound_seg,
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=8, tight=True)

        split_v4 = ft.SegmentedButton(
            selected=[],
            allow_empty_selection=True,
            segments=[
                ft.Segment(value="1", label=ft.Text("1", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="2", label=ft.Text("2", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="3", label=ft.Text("3", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="4", label=ft.Text("4", size=13, weight=ft.FontWeight.W_500)),
                ft.Segment(value="5", label=ft.Text("5", size=13, weight=ft.FontWeight.W_500)),
            ],
            on_change=lambda e: None,
            width=360,
        )

        row5_status_filter = current_status_filter

        def _on_row5_changed(value):
            nonlocal row5_status_filter, current_status_filter, tracking_status
            row5_status_filter = value
            current_status_filter = value
            row5_cell_ingame.bgcolor = "#3b4858" if value == STATUS_ONLY_INGAME else BG_LIGHT
            row5_cell_online.bgcolor = "#3b4858" if value == STATUS_ONLY_ONLINE else BG_LIGHT
            row5_cell_both.bgcolor = "#3b4858" if value == STATUS_BOTH else BG_LIGHT
            row5_cell_ingame.update()
            row5_cell_online.update()
            row5_cell_both.update()
            default_status_seg.selected = [value]
            default_status_seg.update()
            _sync_main_status()
            _settings["default_status"] = current_status_filter
            save_settings(_settings)
            append_log(f"Default status filter set to {current_status_filter}")

        row5_cell_ingame = ft.Container(
            content=ft.Text("In Game", color="#d7e3f7", text_align=ft.TextAlign.CENTER, size=13, weight=ft.FontWeight.W_500),
            bgcolor="#3b4858" if current_status_filter == STATUS_ONLY_INGAME else BG_LIGHT,
            width=120,
            height=40,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=lambda e: _on_row5_changed(STATUS_ONLY_INGAME),
        )

        row5_cell_online = ft.Container(
            content=ft.Text("On Site", color="#d7e3f7", text_align=ft.TextAlign.CENTER, size=13, weight=ft.FontWeight.W_500),
            bgcolor="#3b4858" if current_status_filter == STATUS_ONLY_ONLINE else BG_LIGHT,
            width=120,
            height=40,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=lambda e: _on_row5_changed(STATUS_ONLY_ONLINE),
        )

        row5_cell_both = ft.Container(
            content=ft.Text("Both", color="#d7e3f7", text_align=ft.TextAlign.CENTER, size=13, weight=ft.FontWeight.W_500),
            bgcolor="#3b4858" if current_status_filter == STATUS_BOTH else BG_LIGHT,
            width=120,
            height=40,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=lambda e: _on_row5_changed(STATUS_BOTH),
        )

        split_v5 = ft.Container(
            content=ft.Row([
                row5_cell_ingame,
                row5_cell_online,
                row5_cell_both,
            ], spacing=1, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#8d9199",
            border_radius=20,
            width=360,
            height=40,
            padding=1,
        )

        content = ft.Column([
            ft.Divider(),
            settings_rows,
            ft.Divider(),
            split_v4,
            ft.Divider(),
            split_v5,
        ], spacing=8, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.AlertDialog(
            title=ft.Text("Settings", size=19, weight=ft.FontWeight.BOLD),
            content=content,
            actions=[ft.TextButton("Close", on_click=lambda e: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
            title_padding=ft.Padding(left=24, top=16, right=24, bottom=0),
            content_padding=ft.Padding(left=24, top=0, right=24, bottom=16),
        )

    settings_dlg = _build_settings_dialog()

    settings_btn = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        icon_size=24,
        tooltip="Settings",
        icon_color="white",
        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=8),
        width=40,
        height=40,
        on_click=lambda e: page.show_dialog(settings_dlg),
    )

    def on_status_changed(e):
        nonlocal current_status_filter, tracking_status
        current_status_filter = e.control.selected[0] if e.control.selected else STATUS_BOTH
        tracking_status = f"Active ({current_status_filter})" if running else "Idle"
        _set_tracking_status()
        _apply_status_color()
        page.update()

    status_segmented = ft.SegmentedButton(
        selected=[current_status_filter],
        segments=[
            ft.Segment(value=STATUS_ONLY_INGAME, label=ft.Text("In Game")),
            ft.Segment(value=STATUS_ONLY_ONLINE, label=ft.Text("On Site")),
            ft.Segment(value=STATUS_BOTH, label=ft.Text("Both")),
        ],
        on_change=on_status_changed,
        width=360,
    )

    def add_item_inline(mode):
        is_wts = mode == "wts"
        search_tf = wts_search_tf if is_wts else wtb_search_tf
        suggestions = wts_suggestions if is_wts else wtb_suggestions
        current_price = wts_price_field if is_wts else wtb_price_field
        current_rank = wts_rank_field if is_wts else wtb_rank_field
        current_rank_hint = wts_rank_hint if is_wts else wtb_rank_hint
        current_subtype = wts_subtype_dropdown if is_wts else wtb_subtype_dropdown

        name = search_tf.value.strip()
        price = current_price.value.strip()
        rank = current_rank.value.strip() if current_rank.visible else ""
        subtype = current_subtype.value.strip() if current_subtype.visible else ""
        if not name or not price:
            append_log("Item and price are required.")
            page.update()
            return
        try:
            price_int = int(price)
        except ValueError:
            append_log("Price must be a number.")
            page.update()
            return
        if rank:
            try:
                rank_int = int(rank)
            except ValueError:
                append_log("Rank must be a number.")
                page.update()
                return
            key = f"{name}|{rank_int}"
            (WTS_WATCHLIST if is_wts else WTB_WATCHLIST)[key] = [price_int, rank_int]
        elif subtype:
            key = f"{name}|{subtype}"
            (WTS_WATCHLIST if is_wts else WTB_WATCHLIST)[key] = [price_int, subtype]
        else:
            key = name
            (WTS_WATCHLIST if is_wts else WTB_WATCHLIST)[key] = price_int
        save_watchlists()
        append_log(f"Added {_format_name(key)} to {mode.upper()}")
        with open("add_log.txt", "a") as f:
            f.write(f"add_item_inline({mode}): name={name}, price={price_int}, rank={rank}, subtype={subtype}\n")
            f.write(f"  WTS={WTS_WATCHLIST}\n")
            f.write(f"  WTB={WTB_WATCHLIST}\n")
        column = wts_items_list if is_wts else wtb_items_list
        render_watchlist(column, WTS_WATCHLIST if is_wts else WTB_WATCHLIST, mode)
        search_tf.value = ""
        suggestions.controls = []
        suggestions.visible = False
        suggestions.update()
        current_price.value = ""
        current_rank.value = ""
        current_rank.visible = False
        current_rank_hint.visible = False
        current_subtype.value = ""
        current_subtype.visible = False
        _set_tracking_status()
        _apply_status_color()
        page.update()

    def build_add_form(mode):
        is_wts = mode == "wts"
        search_tf = wts_search_tf if is_wts else wtb_search_tf
        suggestions = wts_suggestions if is_wts else wtb_suggestions
        price = wts_price_field if is_wts else wtb_price_field
        rank = wts_rank_field if is_wts else wtb_rank_field
        rank_hint = wts_rank_hint if is_wts else wtb_rank_hint
        subtype = wts_subtype_dropdown if is_wts else wtb_subtype_dropdown
        add_btn = wts_add_btn if is_wts else wtb_add_btn

        add_btn.on_click = lambda e: add_item_inline(mode)

        return ft.Container(
            content=ft.Column([
                ft.Row([search_tf, rank, subtype, price, add_btn], spacing=4, tight=True),
                suggestions,
                ft.Row([rank_hint], spacing=2, tight=True),
            ], spacing=2, tight=True),
            padding=ft.Padding.symmetric(horizontal=6, vertical=4),
        )

    wts_add_form = build_add_form("wts")
    wtb_add_form = build_add_form("wtb")

    instructions = ft.Container(
        content=ft.Column([
            ft.Text("How to use:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("1. Use form at top of each column to add items.", size=10),
            ft.Text("2. Type in search box to filter the dropdown, then select an item.", size=10),
            ft.Text("4. Rank/Subtype shown automatically if item supports it.", size=10),
            ft.Text("5. Click Start Tracker. Both lists run simultaneously.", size=10),
        ], spacing=2, tight=True, expand=True, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=BG_LIGHT,
        border_radius=10,
        padding=10,
        border=ft.Border.all(1, BG_LIGHT),
        height=122,
        expand=1,
    )

    page.add(
        ft.Column([
            ft.Row([
                ft.Text("Warframe Trade Watch (WFTW)", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                settings_btn,
                status_segmented,
                start_btn,
                stop_btn,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=4),
            ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text("Want to Sell", size=15, weight=ft.FontWeight.BOLD, color=WTS_COLOR),
                            ft.Container(expand=True),
                        ]),
                        wts_add_form,
                        ft.Container(
                            content=wts_items_list,
                            bgcolor=BG_DARK,
                            border_radius=10,
                            padding=8,
                            expand=True,
                            border=ft.Border.all(1, BG_LIGHT),
                        ),
                    ], expand=True),
                    ft.VerticalDivider(width=8),
                    ft.Column([
                        ft.Row([
                            ft.Text("Want to Buy", size=15, weight=ft.FontWeight.BOLD, color=WTB_COLOR),
                            ft.Container(expand=True),
                        ]),
                        wtb_add_form,
                        ft.Container(
                            content=wtb_items_list,
                            bgcolor=BG_DARK,
                            border_radius=10,
                            padding=8,
                            expand=True,
                            border=ft.Border.all(1, BG_LIGHT),
                        ),
                    ], expand=True),
                ], expand=True),
            ], expand=True),
            ft.Divider(height=4),
            ft.Row([
                instructions,
                ft.Container(
                    content=log_output,
                    bgcolor=BG_DARK,
                    border_radius=10,
                    padding=8,
                    border=ft.Border.all(1, BG_LIGHT),
                    height=122,
                    expand=2,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([tracking_text], alignment=ft.MainAxisAlignment.END),
                        ft.Row([status_label, status_word, status_detail], alignment=ft.MainAxisAlignment.END),
                        ft.Container(expand=True),
                        ft.Text("API: api.warframe.market/v2", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("This is a fan project and is not affiliated with Digital Extremes", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=2, tight=True, horizontal_alignment=ft.CrossAxisAlignment.END),
                    bgcolor=BG_LIGHT,
                    border_radius=10,
                    padding=10,
                    border=ft.Border.all(1, BG_LIGHT),
                    height=122,
                    expand=1,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=4),
            ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text("WTS Log", size=14, weight=ft.FontWeight.BOLD, color=WTS_COLOR),
                            ft.Container(expand=True),
                        ]),
                        ft.Container(
                            content=log_output_wts,
                            bgcolor=BG_DARK,
                            border_radius=10,
                            padding=8,
                            expand=True,
                            border=ft.Border.all(1, BG_LIGHT),
                        ),
                    ], expand=True),
                    ft.VerticalDivider(width=8),
                    ft.Column([
                        ft.Row([
                            ft.Text("WTB Log", size=14, weight=ft.FontWeight.BOLD, color=WTB_COLOR),
                            ft.Container(expand=True),
                        ]),
                        ft.Container(
                            content=log_output_wtb,
                            bgcolor=BG_DARK,
                            border_radius=10,
                            padding=8,
                            expand=True,
                            border=ft.Border.all(1, BG_LIGHT),
                        ),
                    ], expand=True),
                ], expand=True),
            ], expand=True),
        ], expand=True)
    )
    def _clamp_window(e=None):
        if page.window.width < 1365 or page.window.height < 768:
            page.window.width = 1365
            page.window.height = 768
            page.update()

    page.on_resize = _clamp_window
    page.on_close = lambda e: (core_wts.stop(), core_wtb.stop())


if __name__ == "__main__":
    ft.run(main)


import tkinter as tk
import subprocess
import sys
import math
from pathlib import Path


# ============================================================
# AFTERGLOW — NEON ARCADE
# Pure Tkinter, no pygame
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
GAMES_DIR = BASE_DIR / "games"

BG = "#0b0812"
PANEL = "#15101f"
CARD = "#191323"
CARD_HOVER = "#281633"

PINK = "#ff3cac"
PINK_DARK = "#c72a88"
PURPLE = "#8b5cf6"
CYAN = "#00e5d4"

WHITE = "#fff7ff"
MUTED = "#a99ab8"
BORDER = "#382343"
ENTRY_BG = "#100c18"

FONT = "Segoe UI"

root = tk.Tk()
root.title("AFTERGLOW | Neon Arcade")
root.geometry("1100x740")
root.minsize(850, 620)
root.configure(bg=BG)

current_user = None
animation_jobs = set()


# ============================================================
# COLORS AND ANIMATION
# ============================================================

def rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def hex_color(values):
    values = [max(0, min(255, int(v))) for v in values]
    return "#{:02x}{:02x}{:02x}".format(*values)


def mix_colors(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return hex_color([
        ca[i] + (cb[i] - ca[i]) * t
        for i in range(3)
    ])


def animate_widget_color(widget, target, duration=150):
    """Animate a widget background using Tkinter's after()."""
    try:
        start = widget.cget("bg")
    except (tk.TclError, TypeError):
        return

    if start == target:
        return

    steps = 8
    delay = max(1, duration // steps)
    count = 0
    job = {"id": None}

    def tick():
        nonlocal count

        if not widget.winfo_exists():
            animation_jobs.discard(job)
            return

        count += 1
        color = mix_colors(start, target, count / steps)

        try:
            widget.configure(bg=color)
        except tk.TclError:
            animation_jobs.discard(job)
            return

        if count < steps:
            job["id"] = widget.after(delay, tick)
        else:
            animation_jobs.discard(job)

    animation_jobs.add(job)
    tick()


def animate_button(button, normal_bg=PANEL, hover_bg=PINK,
                   normal_fg=WHITE, hover_fg=WHITE):
    button.configure(
        bg=normal_bg,
        fg=normal_fg,
        activebackground=hover_bg,
        activeforeground=hover_fg,
        relief="flat",
        bd=0,
        cursor="hand2",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=PINK,
        font=(FONT, 11, "bold"),
        padx=18,
        pady=11,
    )

    def enter(_event):
        animate_widget_color(button, hover_bg)
        button.configure(
            fg=hover_fg,
            highlightbackground=hover_bg,
        )

    def leave(_event):
        animate_widget_color(button, normal_bg)
        button.configure(
            fg=normal_fg,
            highlightbackground=BORDER,
        )

    def press(_event):
        button.configure(relief="sunken")

    def release(_event):
        button.configure(relief="flat")

    button.bind("<Enter>", enter, add="+")
    button.bind("<Leave>", leave, add="+")
    button.bind("<ButtonPress-1>", press, add="+")
    button.bind("<ButtonRelease-1>", release, add="+")


def animate_entry(entry):
    entry.configure(
        bg=ENTRY_BG,
        fg=WHITE,
        insertbackground=PINK,
        relief="flat",
        bd=0,
        font=(FONT, 12),
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=PINK,
    )

    entry.bind(
        "<FocusIn>",
        lambda _e: entry.configure(highlightbackground=PINK),
        add="+",
    )
    entry.bind(
        "<FocusOut>",
        lambda _e: entry.configure(highlightbackground=BORDER),
        add="+",
    )


# ============================================================
# GENERAL UI HELPERS
# ============================================================

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def make_label(parent, text, size=12, color=WHITE,
               weight="normal", **kwargs):
    return tk.Label(
        parent,
        text=text,
        font=(FONT, size, weight),
        fg=color,
        bg=kwargs.pop("bg", parent.cget("bg")),
        **kwargs,
    )


def make_button(parent, text, command, style="pink",
                width=None):
    styles = {
        "pink": (PANEL, PINK, WHITE, WHITE),
        "cyan": ("#11252a", CYAN, WHITE, "#081417"),
        "purple": ("#211735", PURPLE, WHITE, WHITE),
        "dark": (PANEL, CARD_HOVER, WHITE, WHITE),
        "danger": ("#2b1522", "#ff5277", WHITE, WHITE),
    }

    normal, hover, normal_fg, hover_fg = styles[style]

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
    )

    animate_button(
        button,
        normal_bg=normal,
        hover_bg=hover,
        normal_fg=normal_fg,
        hover_fg=hover_fg,
    )

    return button


def make_entry(parent, show=None):
    entry = tk.Entry(parent, show=show)
    animate_entry(entry)
    return entry


def add_header(parent, subtitle="YOUR PERSONAL ARCADE"):
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", padx=38, pady=(24, 16))

    logo = tk.Label(
        header,
        text="AFTERGLOW",
        font=(FONT, 30, "bold"),
        fg=PINK,
        bg=BG,
    )
    logo.pack(anchor="w")

    make_label(
        header,
        subtitle,
        size=9,
        color=CYAN,
        weight="bold",
    ).pack(anchor="w", pady=(2, 0))

    return header


def make_card(parent, title, description, accent, emoji, command):
    outer = tk.Frame(
        parent,
        bg=CARD,
        highlightthickness=1,
        highlightbackground=BORDER,
    )

    inner = tk.Frame(outer, bg=CARD, padx=20, pady=18)
    inner.pack(fill="both", expand=True)

    icon = tk.Label(
        inner,
        text=emoji,
        font=(FONT, 28),
        fg=accent,
        bg=CARD,
    )
    icon.pack(anchor="w")

    tk.Label(
        inner,
        text=title,
        font=(FONT, 17, "bold"),
        fg=WHITE,
        bg=CARD,
    ).pack(anchor="w", pady=(12, 5))

    tk.Label(
        inner,
        text=description,
        font=(FONT, 10),
        fg=MUTED,
        bg=CARD,
        justify="left",
        wraplength=235,
    ).pack(anchor="w")

    play = make_button(
        inner,
        "PLAY  ↗",
        command,
        style="dark",
    )
    play.pack(anchor="w", pady=(18, 0))

    def enter(_event):
        animate_widget_color(outer, CARD_HOVER)
        outer.configure(highlightbackground=accent)

        for widget in (inner, icon):
            widget.configure(bg=CARD_HOVER)

        for widget in inner.winfo_children():
            try:
                if widget.cget("bg") == CARD:
                    widget.configure(bg=CARD_HOVER)
            except tk.TclError:
                pass

    def leave(_event):
        animate_widget_color(outer, CARD)
        outer.configure(highlightbackground=BORDER)

        for widget in (inner, icon):
            widget.configure(bg=CARD)

        for widget in inner.winfo_children():
            try:
                if widget.cget("bg") == CARD_HOVER:
                    widget.configure(bg=CARD)
            except tk.TclError:
                pass

    outer.bind("<Enter>", enter)
    outer.bind("<Leave>", leave)

    for widget in inner.winfo_children():
        widget.bind("<Enter>", enter, add="+")
        widget.bind("<Leave>", leave, add="+")

    return outer


# ============================================================
# DATABASE CONNECTION
# ============================================================

def database_module():
    try:
        import database
        return database
    except Exception as exc:
        show_error(
            "DATABASE ERROR",
            "Не удалось загрузить database.py.\n\n"
            f"{exc}\n\n"
            "Проверь, что database.py лежит рядом с main.py.",
        )
        return None


def show_error(title, message):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.configure(bg=PANEL)
    popup.resizable(False, False)
    popup.transient(root)

    frame = tk.Frame(popup, bg=PANEL, padx=28, pady=24)
    frame.pack(fill="both", expand=True)

    make_label(
        frame, title, size=15, color=PINK, weight="bold"
    ).pack(anchor="w", pady=(0, 12))

    make_label(
        frame, message, size=10, color=WHITE, justify="left"
    ).pack(anchor="w")

    make_button(
        frame, "OK", popup.destroy, "pink"
    ).pack(anchor="e", pady=(18, 0))

    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - popup.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - popup.winfo_height()) // 2
    popup.geometry(f"+{max(0, x)}+{max(0, y)}")


# ============================================================
# AUTHENTICATION SCREEN
# ============================================================

def show_auth():
    clear_screen()

    wrapper = tk.Frame(root, bg=BG)
    wrapper.pack(fill="both", expand=True)

    # Decorative side panel
    left = tk.Frame(wrapper, bg=BG)
    left.pack(side="left", fill="both", expand=True, padx=(55, 20))

    make_label(
        left, "WELCOME TO", 11, CYAN, "bold"
    ).pack(anchor="w", pady=(110, 4))

    make_label(
        left, "AFTERGLOW", 36, PINK, "bold"
    ).pack(anchor="w")

    make_label(
        left,
        "YOUR NIGHT.\nYOUR GAMES.\nYOUR RULES.",
        19,
        WHITE,
        "bold",
        justify="left",
    ).pack(anchor="w", pady=(20, 12))

    make_label(
        left,
        "A tiny arcade with a big neon energy.",
        10,
        MUTED,
    ).pack(anchor="w")

    tk.Frame(left, bg=PINK, height=2, width=120).pack(
        anchor="w", pady=26
    )

    make_label(
        left,
        "SNAKE  /  PONG  /  BREAKOUT",
        9,
        CYAN,
        "bold",
    ).pack(anchor="w")

    # Authentication panel
    panel = tk.Frame(
        wrapper,
        bg=PANEL,
        padx=30,
        pady=28,
        highlightthickness=1,
        highlightbackground=BORDER,
    )
    panel.pack(
        side="right",
        fill="y",
        padx=(15, 55),
        pady=65,
    )

    make_label(
        panel, "PLAYER ACCESS", 19, WHITE, "bold"
    ).pack(anchor="w")

    make_label(
        panel,
        "Sign in or create your account",
        9,
        MUTED,
    ).pack(anchor="w", pady=(5, 24))

    make_label(
        panel, "USERNAME", 9, CYAN, "bold"
    ).pack(anchor="w", pady=(0, 7))

    username = make_entry(panel)
    username.pack(fill="x", ipady=9, pady=(0, 17))

    make_label(
        panel, "PASSWORD", 9, CYAN, "bold"
    ).pack(anchor="w", pady=(0, 7))

    password = make_entry(panel, show="●")
    password.pack(fill="x", ipady=9, pady=(0, 20))

    status = tk.Label(
        panel,
        text="",
        font=(FONT, 9),
        fg="#ff719d",
        bg=PANEL,
        wraplength=250,
        justify="left",
    )
    status.pack(anchor="w", pady=(0, 10))

    def authenticate(register=False):
        nonlocal username, password

        user = username.get().strip()
        secret = password.get()

        if not user or not secret:
            status.configure(text="Enter your username and password.")
            return

        db = database_module()
        if db is None:
            return

        try:
            if hasattr(db, "init_db"):
                db.init_db()

            if register:
                result = db.register_user(user, secret)
            else:
                result = db.login_user(user, secret)

            # Supports database functions that return True/False
            # or a truthy user/result object.
            if result:
                global current_user
                current_user = user
                show_lobby()
            else:
                status.configure(
                    text=(
                        "Account created successfully? Try signing in."
                        if register
                        else "Incorrect username or password."
                    )
                    if not register
                    else "Could not create account. Username may already exist."
                )
        except Exception as exc:
            status.configure(text=str(exc))

    make_button(
        panel,
        "SIGN IN  →",
        lambda: authenticate(False),
        "pink",
    ).pack(fill="x", pady=(0, 10))

    make_button(
        panel,
        "CREATE ACCOUNT  +",
        lambda: authenticate(True),
        "cyan",
    ).pack(fill="x")

    make_label(
        panel,
        "LOCAL ARCADE  •  SQLITE",
        8,
        MUTED,
    ).pack(anchor="center", pady=(24, 0))

    password.bind(
        "<Return>", lambda _event: authenticate(False)
    )
    username.bind(
        "<Return>", lambda _event: password.focus_set()
    )

    username.focus_set()


# ============================================================
# GAME LAUNCHER
# ============================================================

def launch_game(filename):
    game_path = GAMES_DIR / filename

    if not game_path.is_file():
        show_error(
            "GAME NOT FOUND",
            f"Не найден файл:\n{game_path}\n\n"
            "Проверь имя файла и папку games.",
        )
        return

    try:
        subprocess.Popen(
            [sys.executable, str(game_path)],
            cwd=str(BASE_DIR),
        )
    except Exception as exc:
        show_error("LAUNCH ERROR", str(exc))


def logout():
    global current_user
    current_user = None
    show_auth()


def show_lobby():
    clear_screen()

    page = tk.Frame(root, bg=BG)
    page.pack(fill="both", expand=True)

    # Top navigation
    nav = tk.Frame(page, bg=BG)
    nav.pack(fill="x", padx=38, pady=(22, 8))

    brand = tk.Frame(nav, bg=BG)
    brand.pack(side="left")

    make_label(
        brand, "AFTERGLOW", 22, PINK, "bold"
    ).pack(anchor="w")

    make_label(
        brand, "NEON ARCADE", 8, CYAN, "bold"
    ).pack(anchor="w")

    right = tk.Frame(nav, bg=BG)
    right.pack(side="right")

    make_label(
        right,
        f"PLAYER  /  {current_user or 'GUEST'}",
        9,
        MUTED,
        "bold",
    ).pack(side="left", padx=(0, 14))

    make_button(
        right, "LOG OUT", logout, "dark"
    ).pack(side="left")

    tk.Frame(page, bg=BORDER, height=1).pack(
        fill="x", padx=38, pady=(12, 0)
    )

    # Hero area
    hero = tk.Frame(page, bg=BG)
    hero.pack(fill="x", padx=38, pady=(28, 20))

    make_label(
        hero, "CHOOSE YOUR", 10, CYAN, "bold"
    ).pack(anchor="w")

    make_label(
        hero, "NEXT OBSESSION.", 29, WHITE, "bold"
    ).pack(anchor="w", pady=(3, 5))

    make_label(
        hero,
        "Three classics. One neon universe.",
        11,
        MUTED,
    ).pack(anchor="w")

    # Game cards
    cards = tk.Frame(page, bg=BG)
    cards.pack(fill="both", expand=True, padx=38, pady=(5, 25))

    cards.grid_columnconfigure(0, weight=1, uniform="games")
    cards.grid_columnconfigure(1, weight=1, uniform="games")
    cards.grid_columnconfigure(2, weight=1, uniform="games")
    cards.grid_rowconfigure(0, weight=1)

    games = [
        {
            "title": "SNAKE",
            "desc": "Eat, grow, survive.\nOne wrong turn and it's over.",
            "accent": CYAN,
            "emoji": "蛇",
            "file": "snake.py",
        },
        {
            "title": "PONG",
            "desc": "Old-school reflexes.\nKeep the ball in play.",
            "accent": PINK,
            "emoji": "◉",
            "file": "pong.py",
        },
        {
            "title": "BREAKOUT",
            "desc": "Break every brick.\nDon't let the ball drop.",
            "accent": PURPLE,
            "emoji": "▤",
            "file": "breakout.py",
        },
    ]

    for index, game in enumerate(games):
        card = make_card(
            cards,
            game["title"],
            game["desc"],
            game["accent"],
            game["emoji"],
            lambda filename=game["file"]: launch_game(filename),
        )

        card.grid(
            row=0,
            column=index,
            sticky="nsew",
            padx=(0 if index == 0 else 8, 0 if index == 2 else 8),
            pady=5,
        )

    # Bottom strip
    footer = tk.Frame(page, bg=BG)
    footer.pack(fill="x", padx=38, pady=(0, 20))

    tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", pady=(0, 12))

    make_label(
        footer,
        "● SYSTEM ONLINE",
        8,
        CYAN,
        "bold",
    ).pack(side="left")

    make_label(
        footer,
        "MADE FOR NIGHT OWLS",
        8,
        MUTED,
        "bold",
    ).pack(side="right")


# ============================================================
# OPTIONAL SUBTLE ANIMATED ACCENT
# ============================================================

def start_accent_animation():
    """Subtle pulse on the window title; no busy loop."""
    colors = [PINK, "#df45cf", PURPLE, "#df45cf"]
    index = 0

    def pulse():
        nonlocal index

        if not root.winfo_exists():
            return

        # The title remains readable; the color pulse is shown
        # in the app title text for compatibility with Tkinter.
        root.title(
            f"✦ AFTERGLOW | Neon Arcade ✦"
            if index % 2 == 0
            else "AFTERGLOW | Neon Arcade"
        )

        index = (index + 1) % len(colors)
        root.after(1100, pulse)

    pulse()


# ============================================================
# START
# ============================================================

start_accent_animation()
show_auth()
root.mainloop()

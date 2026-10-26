
import sqlite3
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "users.db"


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()


def register_user(username, password):
    username = username.strip()

    if len(username) < 3 or len(username) > 24:
        return False, "Логин должен содержать от 3 до 24 символов."

    if not username.replace("_", "").isalnum():
        return False, "Используй только буквы, цифры и знак _."

    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов."

    salt = secrets.token_bytes(16).hex()
    password_hash = hash_password(password, salt)

    try:
        with connect() as db:
            db.execute(
                """INSERT INTO users (username, salt, password_hash)
                   VALUES (?, ?, ?)""",
                (username, salt, password_hash)
            )
        return True, "Аккаунт успешно создан!"
    except sqlite3.IntegrityError:
        return False, "Этот логин уже занят."


def login_user(username, password):
    with connect() as db:
        user = db.execute(
            """SELECT id, username, salt, password_hash
               FROM users WHERE username = ? COLLATE NOCASE""",
            (username.strip(),)
        ).fetchone()

    if user is None:
        return None

    password_hash = hash_password(password, user[2])

    if secrets.compare_digest(password_hash, user[3]):
        return {"id": user[0], "username": user[1]}

    return None


def save_score(user_id, game, score):
    with connect() as db:
        db.execute(
            "INSERT INTO scores (user_id, game, score) VALUES (?, ?, ?)",
            (user_id, game, max(0, int(score)))
        )

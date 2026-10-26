# RETRO ARCADE

Небольшая ретро-аркада на Python: меню написано на Tkinter, игры — на Pygame.

## Игры
1. **Змейка** — стрелки или WASD.
2. **Понг** — игрок 1: W/S, игрок 2: стрелки вверх/вниз.
3. **Арканоид** — ←/→ или A/D.

Во всех играх `ESC` закрывает окно. В Арканоиде и Змейке после проигрыша можно перезапустить раунд.

## Запуск в VS Code

1. Открой папку `game` в VS Code.
2. Убедись, что установлен Python 3.10 или новее.
3. Открой терминал VS Code (**Terminal → New Terminal**).
4. Создай виртуальное окружение (рекомендуется):

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\\Scripts\\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Установи зависимости:
   ```bash
   python -m pip install -r requirements.txt
   ```

6. Запусти меню:
   ```bash
   python main.py
   ```

Tkinter обычно входит в стандартную поставку Python. На некоторых Linux-дистрибутивах его нужно установить отдельно (например, пакет `python3-tk`).

## Структура проекта

```text
game/
├── main.py
├── requirements.txt
├── README.md
└── games/
    ├── snake.py
    ├── pong.py
    └── breakout.py
```

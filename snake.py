
import tkinter as tk
import random

CELL = 20
COLS, ROWS = 30, 22
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

BG = "#111018"
GRID = "#29243a"
GREEN = "#b8ff5c"
PINK = "#ff5ca8"
WHITE = "#f4f0ff"


class SnakeGame:
    def __init__(self, root):
        self.root = root
        root.title("NEON DECK // SNAKE")
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        root.bind("<KeyPress>", self.on_key)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        self.timer = None
        self.reset()

    def reset(self):
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

        self.snake = [
            (COLS // 2, ROWS // 2),
            (COLS // 2 - 1, ROWS // 2),
            (COLS // 2 - 2, ROWS // 2)
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.dead = False
        self.food = self.new_food()
        self.draw()
        self.tick()

    def new_food(self):
        free = [
            (x, y)
            for x in range(COLS)
            for y in range(ROWS)
            if (x, y) not in self.snake
        ]
        return random.choice(free) if free else None

    def on_key(self, event):
        key = event.keysym.lower()

        if key == "escape":
            self.root.destroy()
            return

        if self.dead:
            if key == "space":
                self.reset()
            return

        directions = {
            "up": (0, -1), "w": (0, -1),
            "down": (0, 1), "s": (0, 1),
            "left": (-1, 0), "a": (-1, 0),
            "right": (1, 0), "d": (1, 0)
        }

        new_direction = directions.get(key)
        if new_direction is None:
            return

        # Нельзя развернуться прямо в собственное тело.
        if new_direction != (-self.direction[0], -self.direction[1]):
            self.next_direction = new_direction

    def tick(self):
        self.timer = None
        if self.dead:
            return

        self.direction = self.next_direction
        hx, hy = self.snake[0]
        head = (hx + self.direction[0], hy + self.direction[1])
        eating = head == self.food
        body = self.snake if eating else self.snake[:-1]

        if (
            not 0 <= head[0] < COLS
            or not 0 <= head[1] < ROWS
            or head in body
        ):
            self.dead = True
            self.draw()
            return

        self.snake.insert(0, head)

        if eating:
            self.score += 10
            self.food = self.new_food()
            if self.food is None:
                self.dead = True
        else:
            self.snake.pop()

        self.draw()

        if not self.dead:
            self.timer = self.root.after(110, self.tick)

    def draw(self):
        c = self.canvas
        c.delete("all")

        for x in range(0, WIDTH, CELL):
            c.create_line(x, 0, x, HEIGHT, fill=GRID)
        for y in range(0, HEIGHT, CELL):
            c.create_line(0, y, WIDTH, y, fill=GRID)

        if self.food is not None:
            x, y = self.food
            c.create_oval(
                x * CELL + 4, y * CELL + 4,
                (x + 1) * CELL - 4, (y + 1) * CELL - 4,
                fill=PINK, outline=""
            )

        for i, (x, y) in enumerate(self.snake):
            pad = 2
            c.create_rectangle(
                x * CELL + pad, y * CELL + pad,
                (x + 1) * CELL - pad, (y + 1) * CELL - pad,
                fill=GREEN if i == 0 else "#6eaa39",
                outline=""
            )

        c.create_rectangle(0, 0, WIDTH, 42, fill="#1c1a29", outline="")
        c.create_text(
            14, 21, anchor="w",
            text=f"SNAKE  //  SCORE {self.score:04d}",
            fill=WHITE, font=("Consolas", 15, "bold")
        )

        if self.dead:
            c.create_rectangle(
                100, 175, WIDTH - 100, 285,
                fill="#1c1a29", outline=PINK, width=2
            )
            c.create_text(
                WIDTH // 2, 210, text="GAME OVER",
                fill=PINK, font=("Consolas", 24, "bold")
            )
            c.create_text(
                WIDTH // 2, 250,
                text="SPACE — RESTART   |   ESC — EXIT",
                fill=WHITE, font=("Consolas", 11)
            )


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()

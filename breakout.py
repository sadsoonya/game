
import tkinter as tk
import random

WIDTH, HEIGHT = 800, 600

BG = "#111018"
CYAN = "#62e7ff"
ORANGE = "#ffb454"
PINK = "#ff5ca8"
WHITE = "#f4f0ff"
MUTED = "#9b95b7"


class BreakoutGame:
    def __init__(self, root):
        self.root = root
        root.title("NEON DECK // BREAKOUT")
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self.colors = [
            PINK, ORANGE, CYAN, "#b8ff5c", "#ae7eff"
        ]
        self.keys = set()
        self.closed = False

        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.protocol("<Escape>", self.close) if False else None
        root.bind("<Escape>", lambda e: self.close())
        root.bind("<space>", lambda e: self.reset()
                  if self.state != "playing" else None)

        self.reset()
        self.loop()

    def close(self):
        self.closed = True
        self.root.destroy()

    def key_down(self, event):
        self.keys.add(event.keysym.lower())

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def reset(self):
        self.paddle_x = WIDTH // 2
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT - 80

        self.vx = random.choice([-4, 4])
        self.vy = -5

        self.score = 0
        self.lives = 3
        self.state = "playing"

        self.bricks = []

        for row in range(5):
            for col in range(10):
                x1 = 42 + col * 72
                y1 = 76 + row * 29

                self.bricks.append({
                    "x1": x1,
                    "y1": y1,
                    "x2": x1 + 64,
                    "y2": y1 + 20,
                    "color": self.colors[row % len(self.colors)]
                })

        self.draw()

    def loop(self):
        if self.closed:
            return

        if "left" in self.keys or "a" in self.keys:
            self.paddle_x -= 7
        if "right" in self.keys or "d" in self.keys:
            self.paddle_x += 7

        self.paddle_x = max(
            55, min(WIDTH - 55, self.paddle_x)
        )

        if self.state == "playing":
            old_x = self.ball_x
            old_y = self.ball_y

            self.ball_x += self.vx
            self.ball_y += self.vy

            # Отскок от боковых стен.
            if self.ball_x <= 8:
                self.ball_x = 8
                self.vx = abs(self.vx)
            elif self.ball_x >= WIDTH - 8:
                self.ball_x = WIDTH - 8
                self.vx = -abs(self.vx)

            # Отскок от верхней стены.
            if self.ball_y <= 8:
                self.ball_y = 8
                self.vy = abs(self.vy)

            # Столкновение с платформой.
            if (
                self.vy > 0
                and HEIGHT - 65 <= self.ball_y <= HEIGHT - 40
                and abs(self.ball_x - self.paddle_x) <= 64
            ):
                self.ball_y = HEIGHT - 66
                self.vy = -abs(self.vy)

                offset = self.ball_x - self.paddle_x
                self.vx = max(
                    -7, min(7, self.vx + offset // 18)
                )

            # Столкновение с кирпичами.
            hit_index = None

            for i, brick in enumerate(self.bricks):
                if (
                    brick["x1"] - 8 <= self.ball_x <= brick["x2"] + 8
                    and brick["y1"] - 8 <= self.ball_y <= brick["y2"] + 8
                ):
                    hit_index = i
                    break

            if hit_index is not None:
                brick = self.bricks.pop(hit_index)

                if old_y < brick["y1"] or old_y > brick["y2"]:
                    self.vy *= -1
                else:
                    self.vx *= -1

                self.score += 10

            # Потеря мяча.
            if self.ball_y > HEIGHT:
                self.lives -= 1

                if self.lives <= 0:
                    self.state = "gameover"
                else:
                    self.ball_x = WIDTH // 2
                    self.ball_y = HEIGHT - 80
                    self.vx = random.choice([-4, 4])
                    self.vy = -5

            if not self.bricks:
                self.state = "win"

        self.draw()
        self.root.after(16, self.loop)

    def draw(self):
        c = self.canvas
        c.delete("all")

        for brick in self.bricks:
            c.create_rectangle(
                brick["x1"], brick["y1"],
                brick["x2"], brick["y2"],
                fill=brick["color"], outline=""
            )

        # Платформа.
        c.create_rectangle(
            self.paddle_x - 55, HEIGHT - 55,
            self.paddle_x + 55, HEIGHT - 41,
            fill=CYAN, outline=""
        )

        # Мяч.
        c.create_oval(
            self.ball_x - 8, self.ball_y - 8,
            self.ball_x + 8, self.ball_y + 8,
            fill=WHITE, outline=""
        )

        c.create_text(
            18, 25, anchor="w",
            text=f"SCORE {self.score:04d}     LIVES {self.lives}",
            fill=WHITE, font=("Consolas", 17, "bold")
        )

        c.create_text(
            WIDTH // 2, HEIGHT - 17,
            text="A/D OR ARROWS — MOVE     SPACE — RESTART     ESC — EXIT",
            fill=MUTED, font=("Consolas", 10)
        )

        if self.state != "playing":
            c.create_rectangle(
                170, 220, WIDTH - 170, 345,
                fill="#1c1a29",
                outline=CYAN if self.state == "win" else PINK,
                width=2
            )

            c.create_text(
                WIDTH // 2, 260,
                text="LEVEL CLEAR!" if self.state == "win" else "GAME OVER",
                fill=CYAN if self.state == "win" else PINK,
                font=("Consolas", 24, "bold")
            )

            c.create_text(
                WIDTH // 2, 305,
                text="SPACE — PLAY AGAIN   |   ESC — EXIT",
                fill=WHITE, font=("Consolas", 11)
            )


if __name__ == "__main__":
    root = tk.Tk()
    BreakoutGame(root)
    root.mainloop()

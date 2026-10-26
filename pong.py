
import tkinter as tk

WIDTH, HEIGHT = 800, 500

BG = "#111018"
CYAN = "#62e7ff"
ORANGE = "#ffb454"
WHITE = "#f4f0ff"
MUTED = "#9b95b7"


class PongGame:
    def __init__(self, root):
        self.root = root
        root.title("NEON DECK // PONG")
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self.p1_y = HEIGHT // 2
        self.p2_y = HEIGHT // 2
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2

        self.vx = 5
        self.vy = 3
        self.score1 = 0
        self.score2 = 0
        self.keys = set()
        self.closed = False

        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.loop()

    def close(self):
        self.closed = True
        self.root.destroy()

    def key_down(self, event):
        self.keys.add(event.keysym.lower())

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def reset_ball(self, direction):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.vx = 5 * direction
        self.vy = 3

    def loop(self):
        if self.closed:
            return

        # Управление игроками.
        if "w" in self.keys:
            self.p1_y -= 7
        if "s" in self.keys:
            self.p1_y += 7
        if "up" in self.keys:
            self.p2_y -= 7
        if "down" in self.keys:
            self.p2_y += 7

        self.p1_y = max(48, min(HEIGHT - 48, self.p1_y))
        self.p2_y = max(48, min(HEIGHT - 48, self.p2_y))

        old_x = self.ball_x
        old_y = self.ball_y

        self.ball_x += self.vx
        self.ball_y += self.vy

        # Отскок от верхней и нижней стен.
        if self.ball_y <= 9 or self.ball_y >= HEIGHT - 9:
            self.vy *= -1

        # Левая платформа.
        if (
            self.vx < 0
            and old_x >= 39
            and self.ball_x <= 39
            and abs(self.ball_y - self.p1_y) <= 57
        ):
            self.ball_x = 40
            self.vx = abs(self.vx)
            self.vy += max(
                -2, min(2, (self.ball_y - self.p1_y) // 15)
            )

        # Правая платформа.
        if (
            self.vx > 0
            and old_x <= WIDTH - 39
            and self.ball_x >= WIDTH - 39
            and abs(self.ball_y - self.p2_y) <= 57
        ):
            self.ball_x = WIDTH - 40
            self.vx = -abs(self.vx)
            self.vy += max(
                -2, min(2, (self.ball_y - self.p2_y) // 15)
            )

        self.vy = max(-7, min(7, self.vy))

        # Гол.
        if self.ball_x < 0:
            self.score2 += 1
            self.reset_ball(-1)
        elif self.ball_x > WIDTH:
            self.score1 += 1
            self.reset_ball(1)

        self.draw()
        self.root.after(16, self.loop)

    def draw(self):
        c = self.canvas
        c.delete("all")

        for y in range(8, HEIGHT, 28):
            c.create_rectangle(
                WIDTH // 2 - 2, y,
                WIDTH // 2 + 2, y + 14,
                fill="#39334f", outline=""
            )

        c.create_rectangle(
            25, self.p1_y - 48, 39, self.p1_y + 48,
            fill=CYAN, outline=""
        )
        c.create_rectangle(
            WIDTH - 39, self.p2_y - 48,
            WIDTH - 25, self.p2_y + 48,
            fill=ORANGE, outline=""
        )

        c.create_oval(
            self.ball_x - 9, self.ball_y - 9,
            self.ball_x + 9, self.ball_y + 9,
            fill=WHITE, outline=""
        )

        c.create_text(
            WIDTH // 4, 25,
            text=f"PLAYER 1   {self.score1}",
            fill=CYAN, font=("Consolas", 19, "bold")
        )
        c.create_text(
            WIDTH * 3 // 4, 25,
            text=f"PLAYER 2   {self.score2}",
            fill=ORANGE, font=("Consolas", 19, "bold")
        )
        c.create_text(
            WIDTH // 2, HEIGHT - 16,
            text="W/S  VS  UP/DOWN     ESC — EXIT",
            fill=MUTED, font=("Consolas", 10)
        )


if __name__ == "__main__":
    root = tk.Tk()
    PongGame(root)
    root.mainloop()

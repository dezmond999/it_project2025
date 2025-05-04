import tkinter as tk
import random

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SNAKE = 3
BASE_SPEED = 150

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Змейка")

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg="black")
        self.canvas.pack()

        self.status = tk.Label(root, text="", font=("Arial", 12), anchor="w")
        self.status.pack(fill=tk.X)

        self.snake = [(GRID_WIDTH // 2 - i, GRID_HEIGHT // 2) for i in range(INITIAL_SNAKE)]
        self.direction = "Right"
        self.new_direction = "Right"
        self.running = True
        self.paused = False
        self.ctrl_pressed = False
        self.score = 0
        self.food = None
        self.food_bonus = False
        self.food_value = 1

        self.spawn_food()
        self.bind_keys()
        self.update_status()
        self.draw()
        self.game_loop()

    def bind_keys(self):
        self.root.bind("<Up>", lambda e: self.set_direction("Up"))
        self.root.bind("<Down>", lambda e: self.set_direction("Down"))
        self.root.bind("<Left>", lambda e: self.set_direction("Left"))
        self.root.bind("<Right>", lambda e: self.set_direction("Right"))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Control_L>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))

    def set_ctrl(self, value):
        self.ctrl_pressed = value

    def set_direction(self, dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if dir != opposites.get(self.direction):
            self.new_direction = dir

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.canvas.create_text(
                GRID_WIDTH * CELL_SIZE // 2,
                GRID_HEIGHT * CELL_SIZE // 2,
                text="Пауза", font=("Arial", 30), fill="white"
            )
        else:
            self.game_loop()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                self.food = pos
                break
        # 10% шанс на бонусное яблоко
        self.food_bonus = random.random() < 0.1
        self.food_value = 5 if self.food_bonus else 1

    def update_status(self):
        self.status.config(text=f"Счёт: {self.score}")

    def game_loop(self):
        if not self.running or self.paused:
            return

        self.direction = self.new_direction
        head_x, head_y = self.snake[0]

        if self.direction == "Up":
            head_y -= 1
        elif self.direction == "Down":
            head_y += 1
        elif self.direction == "Left":
            head_x -= 1
        elif self.direction == "Right":
            head_x += 1

        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            self.running = False
            self.canvas.create_text(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2,
                                    text="Игра окончена!", font=("Arial", 24), fill="white")
            return

        if (head_x, head_y) in self.snake:
            self.running = False
            self.canvas.create_text(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2,
                                    text="Игра окончена!", font=("Arial", 24), fill="white")
            return

        new_head = (head_x, head_y)
        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.food_value
            # Удлинение на extra сегментов, т.к. один уже добавили
            for _ in range(self.food_value - 1):
                self.snake.append(self.snake[-1])
            self.spawn_food()
            self.update_status()
        else:
            self.snake.pop()

        self.draw()
        delay = BASE_SPEED if not self.ctrl_pressed else max(10, BASE_SPEED // 2)
        self.root.after(delay, self.game_loop)

    def draw(self):
        self.canvas.delete("all")

        # Еда
        color = "orange" if self.food_bonus else "red"
        if self.food:
            self.canvas.create_rectangle(
                self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE,
                (self.food[0] + 1) * CELL_SIZE, (self.food[1] + 1) * CELL_SIZE,
                fill=color, outline="darkred"
            )

        # Змейка
        for i, (x, y) in enumerate(self.snake):
            fill = "lime" if i == 0 else "green"
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill=fill, outline="darkgreen"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

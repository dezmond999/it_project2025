import tkinter as tk
from tkinter.colorchooser import askcolor
import random

CELL_SIZE = 20
BASE_SPEED = {"Лёгкий": 200, "Средний": 100, "Сложный": 50}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Змейка")

        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack()

        self.status = tk.Label(root, text="", font=("Arial", 12), anchor="w")
        self.status.pack(fill=tk.X)

        self.snake = []
        self.direction = "Right"
        self.new_direction = "Right"
        self.running = False
        self.ctrl_pressed = False
        self.score = 0

        self.food = None
        self.food_bonus = False
        self.food_value = 1

        self.walls = []
        self.use_walls = False

        self.snake_color = "green"
        self.player_name = "Игрок"
        self.level = "Средний"
        self.grid_width = 30
        self.grid_height = 20
        self.speed = BASE_SPEED[self.level]

        self.bind_keys()
        self.show_settings_window()

    def show_settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("Настройки игрока")
        win.geometry("300x400")
        win.grab_set()

        tk.Label(win, text="Имя игрока:").pack(pady=5)
        name_entry = tk.Entry(win)
        name_entry.insert(0, self.player_name)
        name_entry.pack()

        tk.Label(win, text="Цвет змейки:").pack(pady=5)
        color_btn = tk.Button(win, text="Выбрать цвет", bg=self.snake_color)

        def choose_color():
            color = askcolor()[1]
            if color:
                self.snake_color = color
                color_btn.config(bg=color)
        color_btn.config(command=choose_color)
        color_btn.pack(pady=5)

        tk.Label(win, text="Сложность:").pack(pady=5)
        level_var = tk.StringVar(value=self.level)
        tk.OptionMenu(win, level_var, *BASE_SPEED.keys()).pack()

        tk.Label(win, text="Ширина поля:").pack(pady=5)
        width_entry = tk.Entry(win)
        width_entry.insert(0, str(self.grid_width))
        width_entry.pack()

        tk.Label(win, text="Высота поля:").pack(pady=5)
        height_entry = tk.Entry(win)
        height_entry.insert(0, str(self.grid_height))
        height_entry.pack()

        wall_var = tk.BooleanVar(value=self.use_walls)
        tk.Checkbutton(win, text="Препятствия", variable=wall_var).pack(pady=5)

        def confirm():
            self.player_name = name_entry.get() or "Игрок"
            self.level = level_var.get()
            self.speed = BASE_SPEED[self.level]
            self.grid_width = max(10, min(50, int(width_entry.get())))
            self.grid_height = max(10, min(50, int(height_entry.get())))
            self.use_walls = wall_var.get()
            win.destroy()
            self.start_game()

        tk.Button(win, text="Играть", command=confirm).pack(pady=20)

    def start_game(self):
        self.canvas.config(width=self.grid_width * CELL_SIZE, height=self.grid_height * CELL_SIZE)
        self.snake = [(self.grid_width // 2 - i, self.grid_height // 2) for i in range(3)]
        self.score = 0
        self.direction = "Right"
        self.new_direction = "Right"
        self.running = True
        self.food = None
        self.food_bonus = False

        self.spawn_food()
        if self.use_walls:
            self.generate_walls()
        self.update_status()
        self.draw()
        self.game_loop()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
            if pos not in self.snake and pos not in self.walls:
                self.food = pos
                break
        self.food_bonus = random.random() < 0.1
        self.food_value = 5 if self.food_bonus else 1

    def generate_walls(self):
        self.walls = []
        while len(self.walls) < random.randint(10, 20):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.food:
                self.walls.append((x, y))

    def update_status(self):
        self.status.config(text=f"{self.player_name} | Счёт: {self.score}")

    def bind_keys(self):
        self.root.bind("<Up>", lambda e: self.set_direction("Up"))
        self.root.bind("<Down>", lambda e: self.set_direction("Down"))
        self.root.bind("<Left>", lambda e: self.set_direction("Left"))
        self.root.bind("<Right>", lambda e: self.set_direction("Right"))
        self.root.bind("<Control_L>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))

    def set_ctrl(self, value):
        self.ctrl_pressed = value

    def set_direction(self, dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if dir != opposites.get(self.direction):
            self.new_direction = dir

    def game_loop(self):
        if not self.running:
            return

        self.direction = self.new_direction
        head_x, head_y = self.snake[0]
        if self.direction == "Up": head_y -= 1
        elif self.direction == "Down": head_y += 1
        elif self.direction == "Left": head_x -= 1
        elif self.direction == "Right": head_x += 1

        new_head = (head_x, head_y)

        if (head_x < 0 or head_x >= self.grid_width or
            head_y < 0 or head_y >= self.grid_height or
            new_head in self.snake or
            new_head in self.walls):
            self.running = False
            self.canvas.create_text(self.grid_width * CELL_SIZE // 2,
                                    self.grid_height * CELL_SIZE // 2,
                                    text="Игра окончена!", font=("Arial", 24), fill="white")
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += self.food_value
            for _ in range(self.food_value - 1):
                self.snake.append(self.snake[-1])
            self.spawn_food()
            self.update_status()
        else:
            self.snake.pop()

        self.draw()
        delay = self.speed if not self.ctrl_pressed else max(10, self.speed // 2)
        self.root.after(delay, self.game_loop)

    def draw(self):
        self.canvas.delete("all")

        for x, y in self.walls:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill="blue", outline="blue"
            )

        if self.food:
            color = "orange" if self.food_bonus else "red"
            self.canvas.create_rectangle(
                self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE,
                (self.food[0] + 1) * CELL_SIZE, (self.food[1] + 1) * CELL_SIZE,
                fill=color, outline="darkred"
            )

        for i, (x, y) in enumerate(self.snake):
            fill = "red" if i == 0 else self.snake_color
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill=fill, outline="darkgreen"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()


import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
import tkinter.messagebox as msgbox
import random
import time
import os

CELL_SIZE = 20
DEFAULT_WIDTH = 30
DEFAULT_HEIGHT = 20
GAME_SPEED = {"Лёгкий": 150, "Средний": 100, "Сложный": 50}
SCORE_FILE = "scores.txt"

COLORS = {
    "bg": "#2e3440",
    "snake": "#a3be8c",
    "food": "#ebcb8b",
    "food_bonus": "#ff8c00",
    "food_green": "#00ff00",  
    "wall": "#5e81ac",
    "text": "#eceff4",
    "border": "#4c566a",
    "snake_head": "#ff0000"
}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Змейка")

        self.notebook = ttk.Notebook(self.root)
        self.game_frame = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.records_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.game_frame, text="Игра")
        self.notebook.add(self.records_frame, text="Рекорды")
        self.notebook.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.game_frame, bg=COLORS["bg"])
        self.canvas.pack()

        self.status_bar = tk.Label(self.game_frame, font=("Arial", 12), bg=COLORS["bg"], fg=COLORS["text"])
        self.status_bar.pack(fill=tk.X)

        self.tree = None
        self.setup_records_table()

        self.running = False
        self.paused = False
        self.ctrl_pressed = False
        self.direction = 'Right'
        self.new_direction = 'Right'
        self.score = 0
        self.level = "Средний"
        self.speed = GAME_SPEED[self.level]
        self.snake = []
        self.food = None
        self.food_bonus = None
        self.food_green = None
        self.food_green_active = False
        self.player_name = "Игрок"
        self.snake_color = COLORS["snake"]
        self.start_time = None
        self.elapsed_time = 0
        self.grid_width = DEFAULT_WIDTH
        self.grid_height = DEFAULT_HEIGHT
        self.use_walls = False
        self.walls = []
        self.extra_life = False
        self.last_gift_score = 0
        self.processed_milestones = set()
        self.extra_life = False

        self.records = []
        self.load_scores()
        self.bind_keys()
        self.show_player_setup()
        self.reset_button = tk.Button(self.records_frame, text="Сбросить рекорды", command=self.reset_scores)
        self.reset_button.pack(pady=10)
        self.reset_button.pack(pady=10)
        self.show_legend()
        self.is_3d = False

        self.pro = None
        self.can_shoot = True
        self.last_shot_score = 0

        self.last_teleport_time = 0
        self.teleport_cooldown = 10 



    def reset_scores(self):
        result = msgbox.askyesno("Подтверждение", "Вы точно уверены, что хотите сбросить рекорды?")
        if result:
            self.records.clear()
            if os.path.exists(SCORE_FILE):
                os.remove(SCORE_FILE)
            self.update_records_table()

    def setup_records_table(self):
        columns = ("Игрок", "Счёт", "Время", "Сложность")
        self.tree = ttk.Treeview(self.records_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill='both', expand=True)

    def update_records_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        sorted_scores = sorted(self.records, key=lambda x: x[1], reverse=True)
        for row in sorted_scores:
            self.tree.insert("", "end", values=row)

    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(" | ")
                    if len(parts) == 4:
                        name, score, time_str, level = parts
                        self.records.append((name, int(score), time_str, level))
        self.update_records_table()

    def save_score(self):
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        record = (self.player_name, self.score, time_str, self.level)
        self.records.append(record)
        with open(SCORE_FILE, "a", encoding="utf-8") as f:
            f.write(" | ".join(map(str, record)) + "\n")
        self.update_records_table()

    def bind_keys(self):
        self.root.bind("<Up>", lambda e: self.set_direction("Up"))
        self.root.bind("<Down>", lambda e: self.set_direction("Down"))
        self.root.bind("<Left>", lambda e: self.set_direction("Left"))
        self.root.bind("<Right>", lambda e: self.set_direction("Right"))
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Return>", lambda e: self.new_game() if not self.running else None)
        self.root.bind("<Control_L>", lambda e: self.set_ctrl(True))
        self.root.bind("<KeyRelease-Control_L>", lambda e: self.set_ctrl(False))
        self.root.bind("r", lambda e: self.randomize_theme())
        self.root.bind("q", lambda e: self.toggle_3d_mode())
        self.root.bind("w", lambda e: self.shoot_pro())
        self.root.bind("e", lambda e: self.teleport())





    def set_ctrl(self, pressed):
        self.ctrl_pressed = pressed

    def set_direction(self, dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if self.running and dir != opposites.get(self.direction):
            self.new_direction = dir

    def show_player_setup(self):
        setup = tk.Toplevel(self.root)
        setup.title("Настройки игрока")
        setup.geometry("300x400")
        setup.configure(bg=COLORS["bg"])
        setup.grab_set()

        tk.Label(setup, text="Имя игрока:", bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=5)
        name_entry = tk.Entry(setup)
        name_entry.insert(0, self.player_name)
        name_entry.pack()

        tk.Label(setup, text="Цвет змейки:", bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=5)
        def choose_color():
            color = askcolor()[1]
            if color:
                self.snake_color = color
                color_button.config(bg=color)
        color_button = tk.Button(setup, text="Выбрать цвет", command=choose_color)
        color_button.pack(pady=5)

        tk.Label(setup, text="Сложность:", bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=5)
        level_var = tk.StringVar(value=self.level)
        level_menu = tk.OptionMenu(setup, level_var, *GAME_SPEED.keys())
        level_menu.pack()

        tk.Label(setup, text="Ширина поля:", bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=5)
        width_entry = tk.Entry(setup)
        width_entry.insert(0, str(self.grid_width))
        width_entry.pack()

        tk.Label(setup, text="Высота поля:", bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=5)
        height_entry = tk.Entry(setup)
        height_entry.insert(0, str(self.grid_height))
        height_entry.pack()

        wall_var = tk.BooleanVar(value=self.use_walls)
        tk.Checkbutton(setup, text="Добавить препятствия", variable=wall_var,
                       bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["bg"]).pack(pady=5)

        def confirm():
            self.player_name = name_entry.get() or "Игрок"
            self.level = level_var.get()
            self.speed = GAME_SPEED[self.level]
            self.grid_width = max(10, min(50, int(width_entry.get())))
            self.grid_height = max(10, min(50, int(height_entry.get())))
            self.use_walls = wall_var.get()
            setup.destroy()
            self.new_game()

        tk.Button(setup, text="Играть", command=confirm).pack(pady=20)

    def new_game(self):
        self.canvas.config(width=self.grid_width * CELL_SIZE, height=self.grid_height * CELL_SIZE)
        self.canvas.delete("all")
        self.running = True
        self.paused = False
        self.score = 0
        self.direction = "Right"
        self.new_direction = "Right"
        self.snake = [(self.grid_width // 2 - i, self.grid_height // 2) for i in range(3)]
        self.start_time = time.time()
        self.elapsed_time = 0
        self.spawn_food()
        if self.use_walls:
            self.generate_walls()
        self.draw()
        self.update_status()
        self.update_timer()
        self.game_loop()

    def get_free_cell(self, exclude=None):
        exclude = exclude or []
        while True:
            cell = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
            if cell not in self.snake and cell not in self.walls and cell not in exclude:
                return cell

    def spawn_food(self):
        self.food_bonus = random.random() < 0.2
        self.food_value = 5 if self.food_bonus else 1
        self.food = self.get_free_cell()

        
        if random.random() < 0.4:
            self.food_green = self.get_free_cell(exclude=[self.food])
            self.food_green_active = True
        else:
            self.food_green = None
            self.food_green_active = False

    def generate_walls(self):
        self.walls = []
        total_walls = random.randint(10, 20)
        for _ in range(total_walls):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.food:
                self.walls.append((x, y))

    def draw(self):
        self.canvas.delete("all")
        for i in range(self.grid_width):
            self.canvas.create_line(i * CELL_SIZE, 0, i * CELL_SIZE, self.grid_height * CELL_SIZE, fill=COLORS["border"])
        for j in range(self.grid_height):
            self.canvas.create_line(0, j * CELL_SIZE, self.grid_width * CELL_SIZE, j * CELL_SIZE, fill=COLORS["border"])

        for wall in self.walls:
            x1 = wall[0] * CELL_SIZE
            y1 = wall[1] * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            if self.is_3d:
                self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 + 2, y2 + 2, fill="#111111", outline="")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["wall"], outline="#aaaaaa")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["wall"], outline=COLORS["wall"])

        for i, segment in enumerate(self.snake):
            color = COLORS["snake_head"] if i == 0 else self.snake_color
            x1 = segment[0] * CELL_SIZE
            y1 = segment[1] * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            if self.is_3d:
                self.canvas.create_oval(x1 + 2, y1 + 2, x2 + 2, y2 + 2, fill="#222222", outline="")
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="#999999" if i == 0 else "#555555")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        food_color = COLORS["food_bonus"] if self.food_bonus else COLORS["food"]
        x1 = self.food[0] * CELL_SIZE
        y1 = self.food[1] * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        if self.is_3d:
            self.canvas.create_oval(x1 + 2, y1 + 2, x2 + 2, y2 + 2, fill="#111111", outline="")
            self.canvas.create_oval(x1, y1, x2, y2, fill=food_color, outline="gray")
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=food_color, outline=food_color)
        
        if self.food:
            x1 = self.food[0] * CELL_SIZE
            y1 = self.food[1] * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            food_color = COLORS["food_bonus"] if self.food_bonus else COLORS["food"]

            if self.is_3d:
                self.canvas.create_oval(x1 + 3, y1 + 3, x2 + 3, y2 + 3, fill="#222222", outline="")
                self.canvas.create_oval(x1 - 2, y1 - 2, x2 + 2, y2 + 2, fill=food_color, outline="#ffffff")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=food_color, outline=food_color)

        if self.food_green_active and self.food_green:
            x1 = self.food_green[0] * CELL_SIZE
            y1 = self.food_green[1] * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            if self.is_3d:
                self.canvas.create_oval(x1 + 3, y1 + 3, x2 + 3, y2 + 3, fill="#111111", outline="")
                self.canvas.create_oval(x1 - 2, y1 - 2, x2 + 2, y2 + 2, fill=COLORS["food_green"], outline="#33ff33")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["food_green"], outline=COLORS["food_green"])
        if self.pro:
            x = self.pro["x"] * CELL_SIZE
            y = self.pro["y"] * CELL_SIZE
            self.canvas.create_oval(x + 5, y + 5, x + 15, y + 15, fill="#ffcc00", outline="#ffaa00")

    def update_status(self):
        self.status_bar.config(
            text=f"Игрок: {self.player_name} | Счёт: {self.score} | Время: {self.elapsed_time} сек | Сложность: {self.level}"
        )

    def update_timer(self):
        if self.running and not self.paused:
            self.elapsed_time = int(time.time() - self.start_time)
            self.update_status()
            self.root.after(1000, self.update_timer)
        
    def pause_and_show_boxes(self):
        self.paused = True
        popup = tk.Toplevel(self.root)
        popup.title("Выбор шкатулки")
        popup.geometry("300x220")
        popup.configure(bg=COLORS["bg"])
        popup.grab_set()

        label = tk.Label(popup, text="Выберите одну из шкатулок", font=("Arial", 12), bg=COLORS["bg"], fg=COLORS["text"])
        label.pack(pady=10)

        result_label = tk.Label(popup, text="", font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["text"])
        result_label.pack(pady=5)

        def choose_box(option):
            if option == 1:
                self.score += 10
                tail = self.snake[-1]
                self.snake.extend([tail] * 10)
                result_text = "Вы выбрали Шкатулку 1: +10 очков и +10 длины"
            elif option == 2:
                self.extra_life = True
                result_text = "Вы выбрали Шкатулку 2: вторая жизнь"
            elif option == 3:
                result_text = "Вы выбрали Шкатулку 3: смерть"
                result_label.config(text=result_text)
                popup.after(1500, lambda: [popup.destroy(), self.resume_or_die()])
                return

            result_label.config(text=result_text)
            popup.after(1500, lambda: [popup.destroy(), self.resume_or_die()])

        for i in range(1, 4):
            btn = tk.Button(popup, text=f"Шкатулка {i}", command=lambda opt=i: choose_box(opt))
            btn.pack(pady=5)

    def resume_or_die(self):
        if not self.running:
            return
        self.paused = False
        self.update_status()
        self.update_timer()
        self.game_loop()

    def game_loop(self):
        if self.paused or not self.running:
            return

        self.direction = self.new_direction
        head_x, head_y = self.snake[0]

        if self.direction == "Up": head_y -= 1
        elif self.direction == "Down": head_y += 1
        elif self.direction == "Left": head_x -= 1
        elif self.direction == "Right": head_x += 1

        if head_x < 0 or head_x >= self.grid_width or head_y < 0 or head_y >= self.grid_height:
            self.game_over()
            return


        if (head_x, head_y) in self.snake or (head_x, head_y) in self.walls:
            self.game_over()
            return

        ate = False

        if (head_x, head_y) == self.food:
            self.score += self.food_value
            if self.food_bonus:
                self.snake.extend([(self.snake[-1][0], self.snake[-1][1])] * (self.food_value - 1))
            self.spawn_food()
            ate = True

        elif self.food_green_active and (head_x, head_y) == self.food_green:
            self.score += 3
            self.food_green_active = False
            ate = True

        milestone = (self.score // 30) * 30
        if milestone >= 30 and milestone not in self.processed_milestones:
            self.processed_milestones.add(milestone)
            self.pause_and_show_boxes()
            return

        if not ate:
            self.snake.pop()

        self.snake = [(head_x, head_y)] + self.snake
        self.draw()

        delay = self.speed if not self.ctrl_pressed else max(10, self.speed // 2)
        self.root.after(delay, self.game_loop)

    def game_over(self):
        if self.extra_life:
            self.extra_life = False
            self.respawn_after_life()
        else:
            self.running = False
            self.save_score()
            self.canvas.create_text(
                self.grid_width * CELL_SIZE // 2,
                self.grid_height * CELL_SIZE // 2,
                text=f"Игра окончена!\nСчёт: {self.score}",
                font=("Arial", 24), fill=COLORS["text"]
            )
    def respawn_after_life(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.grid_width * CELL_SIZE // 2,
            self.grid_height * CELL_SIZE // 2,
            text="⚡ Вы воскресли! ⚡",
            font=("Arial", 28, "bold"),
            fill="#00ffcc"
        )

        self.root.after(100, self._continue_after_effect)
        
    def _continue_after_effect(self):
        self.snake = [(self.grid_width // 2 - i, self.grid_height // 2) for i in range(3)]
        self.direction = "Right"
        self.new_direction = "Right"
        self.food = None
        self.food_green = None
        self.food_green_active = False
        if self.use_walls:
            self.generate_walls()
        self.spawn_food()
        self.draw()
        self.update_status()
        self.update_timer()
        self.game_loop()

    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.canvas.create_text(
                    self.grid_width * CELL_SIZE // 2, self.grid_height * CELL_SIZE // 2,
                    text="Пауза", font=("Arial", 30), fill=COLORS["text"]
                )
            else:
                self.update_timer()
                self.game_loop()
    def show_legend(self):
        legend_text = (
            "Управление: ← ↑ ↓ → - движение | "
            "Пробел - пауза | Enter - новая игра | Ctrl - ускорение | R - смена фона | W - выстрел | Q - изменение формы змейки | E - телепорт (кд 45с)"
        )
        self.legend_label = tk.Label(
            self.game_frame, text=legend_text,
            font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["text"]
        )
        self.legend_label.pack(fill=tk.X, side=tk.BOTTOM)
    def randomize_theme(self):
        def random_color():
            return "#%06x" % random.randint(0, 0xFFFFFF)

        COLORS["bg"] = random_color()
        COLORS["text"] = random_color()
        COLORS["snake"] = random_color()
        COLORS["snake_head"] = random_color()
        COLORS["food"] = random_color()
        COLORS["food_bonus"] = random_color()
        COLORS["food_green"] = random_color()
        COLORS["wall"] = random_color()
        COLORS["border"] = random_color()

        self.snake_color = COLORS["snake"] 

        self.game_frame.config(bg=COLORS["bg"])
        self.canvas.config(bg=COLORS["bg"])
        self.status_bar.config(bg=COLORS["bg"], fg=COLORS["text"])
        if hasattr(self, 'legend_label'):
            self.legend_label.config(bg=COLORS["bg"], fg=COLORS["text"])

        self.draw()
        self.update_status()

    def toggle_3d_mode(self):
        self.is_3d = not self.is_3d
        self.draw()
    
    def shoot_pro(self):
        if not self.running or self.paused:
            return
        if self.score - self.last_shot_score < 30:
            return 
        head_x, head_y = self.snake[0]
        dx, dy = 0, 0
        if self.direction == "Up":
            dy = -1
        elif self.direction == "Down":
            dy = 1
        elif self.direction == "Left":
            dx = -1
        elif self.direction == "Right":
            dx = 1
        self.pro = {"x": head_x, "y": head_y, "dx": dx, "dy": dy}

        self.last_shot_score = self.score
        self.animate_pro()
    
    def animate_pro(self):
        if not self.pro:
            return

        x = self.pro["x"] + self.pro["dx"]
        y = self.pro["y"] + self.pro["dy"]

        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            self.pro = None
            return

        if (x, y) in self.walls:
            self.walls.remove((x, y))
            self.pro = None
            self.draw()
            return

        self.pro["x"] = x
        self.pro["y"] = y
        self.draw()
        self.root.after(50, self.animate_pro)
    def teleport(self):
        if not self.running or self.paused:
            return

        now = time.time()
        if now - self.last_teleport_time < self.teleport_cooldown:
            return  

        new_pos = self.get_free_cell()
        old_head = self.snake[0]
        dx = new_pos[0] - old_head[0]
        dy = new_pos[1] - old_head[1]

        self.snake = [(x + dx, y + dy) for x, y in self.snake]
        self.snake = [seg for seg in self.snake if 0 <= seg[0] < self.grid_width and 0 <= seg[1] < self.grid_height]
        self.last_teleport_time = now
        self.canvas.create_text(
            self.grid_width * CELL_SIZE // 2,
            self.grid_height * CELL_SIZE // 2,
            text="⚡",
            font=("Arial", 20, "bold"),
            fill="#00ffcc"
        )
        self.draw()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

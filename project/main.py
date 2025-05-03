import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SNAKE = 3
SPEED = 150

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Змейка")

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg="black")
        self.canvas.pack()

        self.snake = [(GRID_WIDTH // 2 - i, GRID_HEIGHT // 2) for i in range(INITIAL_SNAKE)]
        self.direction = "Right"
        self.new_direction = "Right"
        self.running = True

        self.bind_keys()
        self.draw()
        self.game_loop()

    def bind_keys(self):
        self.root.bind("<Up>", lambda e: self.set_direction("Up"))
        self.root.bind("<Down>", lambda e: self.set_direction("Down"))
        self.root.bind("<Left>", lambda e: self.set_direction("Left"))
        self.root.bind("<Right>", lambda e: self.set_direction("Right"))

    def set_direction(self, dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if dir != opposites.get(self.direction):
            self.new_direction = dir

    def game_loop(self):
        if not self.running:
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

        self.snake = [(head_x, head_y)] + self.snake[:-1]
        self.draw()
        self.root.after(SPEED, self.game_loop)

    def draw(self):
        self.canvas.delete("all")
        for x, y in self.snake:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill="green", outline="darkgreen"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

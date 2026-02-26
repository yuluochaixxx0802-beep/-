import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
UPDATE_MS = 120


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simple Snake")

        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black")
        self.canvas.pack()

        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 14))
        self.score_label.pack(pady=8)

        self.root.bind("<KeyPress>", self.on_key_press)

        self.after_id = None
        self.reset_game()

    def reset_game(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.score = 0
        self.game_over = False
        self.place_food()
        self.draw()
        self.schedule_next_tick()

    def place_food(self) -> None:
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake
        ]
        self.food = random.choice(available) if available else None

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if self.game_over and key == "r":
            self.reset_game()
            return

        direction_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }

        if key in direction_map and not self.game_over:
            new_direction = direction_map[key]
            current_dx, current_dy = self.direction
            new_dx, new_dy = new_direction
            if (new_dx, new_dy) != (-current_dx, -current_dy):
                self.pending_direction = new_direction

    def schedule_next_tick(self) -> None:
        if not self.game_over:
            self.after_id = self.root.after(UPDATE_MS, self.tick)

    def tick(self) -> None:
        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        hit_wall = not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT)
        hit_self = new_head in self.snake

        if hit_wall or hit_self:
            self.game_over = True
            self.draw()
            return

        self.snake.insert(0, new_head)

        if self.food is not None and new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.place_food()
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def draw(self) -> None:
        self.canvas.delete("all")

        for x, y in self.snake:
            self.draw_cell(x, y, "lime")

        if self.food is not None:
            self.draw_cell(self.food[0], self.food[1], "red")

        if self.game_over:
            self.canvas.create_text(
                GRID_WIDTH * CELL_SIZE // 2,
                GRID_HEIGHT * CELL_SIZE // 2,
                text="Game Over\nPress R to restart",
                fill="white",
                font=("Arial", 18, "bold"),
                justify="center",
            )

    def draw_cell(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray20")


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()

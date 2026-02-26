import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 24
GRID_HEIGHT = 24
BASE_UPDATE_MS = 120
MIN_UPDATE_MS = 65
SPECIAL_FOOD_LIFETIME = 80
RAINBOW_FOOD_LIFETIME = 55


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Colorful Snake Ultra")

        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#0b0c1a")
        self.canvas.pack()

        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 14, "bold"), fg="#0f0f1a")
        self.score_label.pack(pady=8)

        self.hint_label = tk.Label(
            root,
            text="方向鍵移動 | Space 開始 | R 重新開始",
            font=("Arial", 10),
            fg="#404040",
        )
        self.hint_label.pack(pady=(0, 8))

        self.root.bind("<KeyPress>", self.on_key_press)

        self.after_id = None
        self.reset_game(started=False)

    def reset_game(self, started: bool = False) -> None:
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
        self.started = started
        self.speed_ms = BASE_UPDATE_MS
        self.special_food = None
        self.special_food_timer = 0
        self.rainbow_food = None
        self.rainbow_food_timer = 0

        self.place_regular_food()
        self.maybe_spawn_special_food(force=True)
        self.maybe_spawn_rainbow_food(force=True)
        self.update_score_label()
        self.draw()
        if self.started:
            self.schedule_next_tick()

    def update_score_label(self) -> None:
        self.score_label.config(text=f"Score: {self.score} | Speed: {1000 // self.speed_ms} 格/秒")

    def occupied_cells(self) -> set[tuple[int, int]]:
        occupied = set(self.snake)
        if self.regular_food is not None:
            occupied.add(self.regular_food)
        if self.special_food is not None:
            occupied.add(self.special_food)
        if self.rainbow_food is not None:
            occupied.add(self.rainbow_food)
        return occupied

    def random_empty_cell(self, exclude_foods: bool = True) -> tuple[int, int] | None:
        occupied = set(self.snake)
        if exclude_foods:
            if self.regular_food is not None:
                occupied.add(self.regular_food)
            if self.special_food is not None:
                occupied.add(self.special_food)
            if self.rainbow_food is not None:
                occupied.add(self.rainbow_food)

        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        return random.choice(available) if available else None

    def place_regular_food(self) -> None:
        self.regular_food = self.random_empty_cell(exclude_foods=True)

    def maybe_spawn_special_food(self, force: bool = False) -> None:
        if self.special_food is not None:
            return
        if not force and random.random() >= 0.25:
            return

        self.special_food = self.random_empty_cell(exclude_foods=True)
        if self.special_food is not None:
            self.special_food_timer = SPECIAL_FOOD_LIFETIME

    def maybe_spawn_rainbow_food(self, force: bool = False) -> None:
        if self.rainbow_food is not None:
            return
        if not force and random.random() >= 0.15:
            return

        self.rainbow_food = self.random_empty_cell(exclude_foods=True)
        if self.rainbow_food is not None:
            self.rainbow_food_timer = RAINBOW_FOOD_LIFETIME

    def on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()

        if not self.started and key in {"space", "return"}:
            self.started = True
            self.draw()
            self.schedule_next_tick()
            return

        if self.game_over and key == "r":
            self.reset_game(started=False)
            return

        direction_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }

        if key in direction_map and self.started and not self.game_over:
            new_direction = direction_map[key]
            current_dx, current_dy = self.direction
            new_dx, new_dy = new_direction
            if (new_dx, new_dy) != (-current_dx, -current_dy):
                self.pending_direction = new_direction

    def schedule_next_tick(self) -> None:
        if not self.game_over and self.started:
            self.after_id = self.root.after(self.speed_ms, self.tick)

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

        ate_regular = self.regular_food is not None and new_head == self.regular_food
        ate_special = self.special_food is not None and new_head == self.special_food
        ate_rainbow = self.rainbow_food is not None and new_head == self.rainbow_food

        if ate_regular:
            self.score += 1
            self.place_regular_food()
            self.maybe_spawn_special_food()
            self.maybe_spawn_rainbow_food()
        elif ate_special:
            self.score += 3
            self.special_food = None
            self.special_food_timer = 0
            self.speed_ms = max(MIN_UPDATE_MS, self.speed_ms - 7)
        elif ate_rainbow:
            self.score += 5
            self.rainbow_food = None
            self.rainbow_food_timer = 0
            self.speed_ms = max(MIN_UPDATE_MS, self.speed_ms - 3)
        else:
            self.snake.pop()

        if self.special_food is not None:
            self.special_food_timer -= 1
            if self.special_food_timer <= 0:
                self.special_food = None

        if self.rainbow_food is not None:
            self.rainbow_food_timer -= 1
            if self.rainbow_food_timer <= 0:
                self.rainbow_food = None

        if self.score > 0 and self.score % 6 == 0:
            self.speed_ms = max(MIN_UPDATE_MS, self.speed_ms - 1)

        self.update_score_label()
        self.draw()
        self.schedule_next_tick()

    def draw(self) -> None:
        self.canvas.delete("all")
        self.draw_board_background()

        for index, (x, y) in enumerate(self.snake):
            self.draw_snake_segment(x, y, index)

        if self.regular_food is not None:
            self.draw_round_food(self.regular_food[0], self.regular_food[1], "#ff5a5f")

        if self.special_food is not None:
            flashing = self.special_food_timer % 8 < 4
            color = "#ffd166" if flashing else "#f7b538"
            self.draw_diamond_food(self.special_food[0], self.special_food[1], color)

        if self.rainbow_food is not None:
            self.draw_star_food(self.rainbow_food[0], self.rainbow_food[1], "#7c4dff")

        if not self.started:
            self.draw_start_screen()
        elif self.game_over:
            self.draw_game_over_panel()

    def draw_board_background(self) -> None:
        palette = ("#101427", "#141b33", "#1a2140")
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                color = palette[(x + y) % len(palette)]
                self.draw_cell(x, y, color, outline="#0d1122")

    def get_snake_color(self, index: int) -> str:
        if index == 0:
            return "#86f7c2"
        ratio = min(1.0, index / max(1, len(self.snake) - 1))
        red = int(90 + ratio * 100)
        green = int(235 - ratio * 90)
        blue = int(205 - ratio * 140)
        return f"#{red:02x}{green:02x}{blue:02x}"

    def draw_snake_segment(self, x: int, y: int, index: int) -> None:
        color = self.get_snake_color(index)
        self.draw_cell(x, y, color, outline="#202840")
        if index == 0:
            self.draw_snake_face(x, y)

    def draw_snake_face(self, x: int, y: int) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        cx = x1 + CELL_SIZE / 2
        cy = y1 + CELL_SIZE / 2

        eye_offsets = {
            (1, 0): [(4, 5), (4, 14)],
            (-1, 0): [(16, 5), (16, 14)],
            (0, 1): [(5, 4), (14, 4)],
            (0, -1): [(5, 16), (14, 16)],
        }
        pupil_offset = {
            (1, 0): (1.5, 0),
            (-1, 0): (-1.5, 0),
            (0, 1): (0, 1.5),
            (0, -1): (0, -1.5),
        }

        for ex, ey in eye_offsets.get(self.direction, eye_offsets[(1, 0)]):
            self.canvas.create_oval(x1 + ex - 2, y1 + ey - 2, x1 + ex + 2, y1 + ey + 2, fill="white", outline="")
            px, py = pupil_offset.get(self.direction, (1.5, 0))
            self.canvas.create_oval(
                x1 + ex + px - 1,
                y1 + ey + py - 1,
                x1 + ex + px + 1,
                y1 + ey + py + 1,
                fill="#1b1b1b",
                outline="",
            )

        tongue_length = 6
        dx, dy = self.direction
        self.canvas.create_line(
            cx,
            cy,
            cx + dx * tongue_length,
            cy + dy * tongue_length,
            fill="#ff8fab",
            width=2,
        )

    def draw_round_food(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        margin = 3
        self.canvas.create_oval(
            x1 + margin,
            y1 + margin,
            x1 + CELL_SIZE - margin,
            y1 + CELL_SIZE - margin,
            fill=color,
            outline="#3d1620",
            width=2,
        )

    def draw_diamond_food(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        c = CELL_SIZE / 2
        points = [
            (x1 + c, y1 + 2),
            (x1 + CELL_SIZE - 2, y1 + c),
            (x1 + c, y1 + CELL_SIZE - 2),
            (x1 + 2, y1 + c),
        ]
        self.canvas.create_polygon(points, fill=color, outline="#664200", width=2)

    def draw_star_food(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        points = [
            (x1 + 10, y1 + 2),
            (x1 + 13, y1 + 8),
            (x1 + 19, y1 + 8),
            (x1 + 14, y1 + 12),
            (x1 + 16, y1 + 18),
            (x1 + 10, y1 + 14),
            (x1 + 4, y1 + 18),
            (x1 + 6, y1 + 12),
            (x1 + 1, y1 + 8),
            (x1 + 7, y1 + 8),
        ]
        self.canvas.create_polygon(points, fill=color, outline="#2c1461", width=2)
        self.canvas.create_oval(x1 + 8, y1 + 8, x1 + 12, y1 + 12, fill="#c7a8ff", outline="")

    def draw_start_screen(self) -> None:
        width = GRID_WIDTH * CELL_SIZE
        height = GRID_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(30, 80, width - 30, height - 80, fill="#090b16", outline="#7c4dff", width=3)
        self.canvas.create_text(width // 2, 145, text="Colorful Snake Ultra", fill="#c8b6ff", font=("Arial", 28, "bold"))
        self.canvas.create_text(width // 2, 200, text="紅圓 +1 | 金菱形 +3 | 紫星星 +5", fill="#9bf6ff", font=("Arial", 14, "bold"))
        self.canvas.create_text(width // 2, 235, text="吃星星和金色食物都會加速！", fill="#ffd6a5", font=("Arial", 13))
        self.canvas.create_text(width // 2, 300, text="Press SPACE to Start", fill="#ffffff", font=("Arial", 22, "bold"))
        self.canvas.create_text(width // 2, 335, text="使用方向鍵控制蛇蛇前進", fill="#bde0fe", font=("Arial", 13))

    def draw_game_over_panel(self) -> None:
        width = GRID_WIDTH * CELL_SIZE
        height = GRID_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(55, height // 2 - 70, width - 55, height // 2 + 70, fill="#000000", outline="#ff5a5f", width=2)
        self.canvas.create_text(width // 2, height // 2 - 15, text="Game Over", fill="#ffffff", font=("Arial", 26, "bold"))
        self.canvas.create_text(width // 2, height // 2 + 18, text="Press R to restart", fill="#ffd166", font=("Arial", 14, "bold"))

    def draw_cell(self, x: int, y: int, color: str, outline: str = "#202030") -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()

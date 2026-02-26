import random
from typing import Optional, Tuple

try:
    import tkinter as tk
    TK_IMPORT_ERROR = None
except Exception as error:
    tk = None
    TK_IMPORT_ERROR = error


CELL_SIZE = 20
GRID_WIDTH = 24
GRID_HEIGHT = 24
BASE_UPDATE_MS = 120
MIN_UPDATE_MS = 68
STAR_FOOD_LIFETIME = 70

FONT_CN = ("KaiTi", 16)
FONT_CN_BOLD = ("KaiTi", 20, "bold")
FONT_EN_SCRIPT = ("Segoe Script", 28, "bold")
FONT_EN_SCRIPT_SMALL = ("Segoe Script", 18, "bold")


class SnakeGame:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title("Snake Bloom")

        self.canvas_width = GRID_WIDTH * CELL_SIZE
        self.canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="#101419", highlightthickness=0)
        self.canvas.pack()

        self.score_label = tk.Label(root, text="", font=FONT_CN, fg="#1f2a37", bg="#f8f8f8")
        self.score_label.pack(fill="x", pady=(6, 0))

        self.root.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.after_id = None
        self.menu_buttons = {}
        self.state = "menu"
        self.star_speed_enabled = True
        self.reset_game()
        self.draw()

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
        self.speed_ms = BASE_UPDATE_MS
        self.game_over = False
        self.regular_food = None
        self.star_food = None
        self.star_food_timer = 0
        self.spawn_regular_food()
        self.maybe_spawn_star_food(force=True)
        self.update_score_label()

    def update_score_label(self) -> None:
        toggle = "ON" if self.star_speed_enabled else "OFF"
        self.score_label.config(
            text=f"分數 {self.score}   速度 {1000 // self.speed_ms} 格/秒   星星加速(K): {toggle}"
        )

    def available_cells(self) -> list[Tuple[int, int]]:
        occupied = set(self.snake)
        if self.regular_food is not None:
            occupied.add(self.regular_food)
        if self.star_food is not None:
            occupied.add(self.star_food)
        return [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]

    def spawn_regular_food(self) -> None:
        available = self.available_cells()
        self.regular_food = random.choice(available) if available else None

    def maybe_spawn_star_food(self, force: bool = False) -> None:
        if self.star_food is not None:
            return
        if not force and random.random() >= 0.18:
            return
        available = self.available_cells()
        self.star_food = random.choice(available) if available else None
        if self.star_food is not None:
            self.star_food_timer = STAR_FOOD_LIFETIME

    def start_game(self) -> None:
        self.reset_game()
        self.state = "playing"
        self.draw()
        self.schedule_next_tick()

    def open_help(self) -> None:
        self.state = "help"
        self.draw()

    def exit_game(self) -> None:
        self.root.destroy()

    def on_canvas_click(self, event) -> None:
        if self.state != "menu":
            return
        x, y = event.x, event.y
        for name, (x1, y1, x2, y2) in self.menu_buttons.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                if name == "start":
                    self.start_game()
                elif name == "help":
                    self.open_help()
                elif name == "exit":
                    self.exit_game()
                return

    def on_key_press(self, event) -> None:
        key = event.keysym.lower()

        if key == "k":
            self.star_speed_enabled = not self.star_speed_enabled
            self.update_score_label()
            self.draw()
            return

        if self.state == "menu":
            if key in {"1", "s", "return"}:
                self.start_game()
            elif key in {"2", "h"}:
                self.open_help()
            elif key in {"3", "e", "escape"}:
                self.exit_game()
            return

        if self.state == "help":
            if key in {"escape", "backspace", "return"}:
                self.state = "menu"
                self.draw()
            return

        if self.game_over:
            if key == "r":
                self.state = "menu"
                self.draw()
            return

        direction_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }

        if key in direction_map and self.state == "playing":
            new_direction = direction_map[key]
            current_dx, current_dy = self.direction
            new_dx, new_dy = new_direction
            if (new_dx, new_dy) != (-current_dx, -current_dy):
                self.pending_direction = new_direction

    def schedule_next_tick(self) -> None:
        if self.state == "playing" and not self.game_over:
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
            self.state = "game_over"
            self.draw()
            return

        self.snake.insert(0, new_head)

        ate_regular = self.regular_food is not None and new_head == self.regular_food
        ate_star = self.star_food is not None and new_head == self.star_food

        if ate_regular:
            self.score += 1
            self.spawn_regular_food()
            self.maybe_spawn_star_food()
        elif ate_star:
            self.score += 4
            self.star_food = None
            self.star_food_timer = 0
            if self.star_speed_enabled:
                self.speed_ms = max(MIN_UPDATE_MS, self.speed_ms - 8)
        else:
            self.snake.pop()

        if self.star_food is not None:
            self.star_food_timer -= 1
            if self.star_food_timer <= 0:
                self.star_food = None

        if self.score > 0 and self.score % 6 == 0:
            self.speed_ms = max(MIN_UPDATE_MS, self.speed_ms - 1)

        self.update_score_label()
        self.draw()
        self.schedule_next_tick()

    def draw(self) -> None:
        self.canvas.delete("all")
        if self.state == "menu":
            self.draw_menu()
            return
        if self.state == "help":
            self.draw_help()
            return

        self.draw_board()
        for idx, (x, y) in enumerate(self.snake):
            self.draw_snake_segment(x, y, idx)

        if self.regular_food is not None:
            self.draw_round_food(self.regular_food[0], self.regular_food[1], "#ff6b6b")
        if self.star_food is not None:
            color = "#ffd166" if self.star_food_timer % 6 < 3 else "#ffb703"
            self.draw_star_food(self.star_food[0], self.star_food[1], color)

        if self.state == "game_over":
            self.draw_game_over()

    def draw_board(self) -> None:
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                shade = "#171d24" if (x + y) % 2 == 0 else "#1f2730"
                self.draw_cell(x, y, shade, outline="#11161d")

    def draw_menu_button(self, key: str, label: str, y: int) -> Tuple[int, int, int, int]:
        x1, x2 = 120, self.canvas_width - 120
        y1, y2 = y, y + 56
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1b2632", outline="#8ecae6", width=2)
        self.canvas.create_text(self.canvas_width // 2, y + 28, text=f"{key}. {label}", fill="#ffffff", font=FONT_CN_BOLD)
        return (x1, y1, x2, y2)

    def draw_menu(self) -> None:
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill="#0f1720", outline="")
        self.canvas.create_text(self.canvas_width // 2, 120, text="Snake Bloom", fill="#e0fbfc", font=FONT_EN_SCRIPT)
        self.menu_buttons = {
            "start": self.draw_menu_button("1", "Start", 190),
            "help": self.draw_menu_button("2", "How to Play", 265),
            "exit": self.draw_menu_button("3", "Exit", 340),
        }

    def draw_help(self) -> None:
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill="#0f1720", outline="")
        self.canvas.create_text(self.canvas_width // 2, 110, text="How to Play", fill="#e0fbfc", font=FONT_EN_SCRIPT_SMALL)
        lines = [
            "方向鍵控制方向",
            "紅色圓形食物 +1",
            "金色星星 +4（可加速）",
            "按 K 可切換星星加速 ON/OFF",
            "撞牆或撞到自己會結束",
            "Esc / Enter 返回主選單",
        ]
        for i, text in enumerate(lines):
            self.canvas.create_text(self.canvas_width // 2, 180 + i * 40, text=text, fill="#f1f5f9", font=FONT_CN)

    def draw_game_over(self) -> None:
        self.canvas.create_rectangle(100, 190, self.canvas_width - 100, 300, fill="#0b0f14", outline="#ef476f", width=2)
        self.canvas.create_text(self.canvas_width // 2, 225, text="Game Over", fill="#ffffff", font=FONT_EN_SCRIPT_SMALL)
        self.canvas.create_text(self.canvas_width // 2, 268, text="按 R 回到主選單", fill="#ffd6a5", font=FONT_CN)

    def draw_snake_segment(self, x: int, y: int, index: int) -> None:
        color = "#80ed99" if index == 0 else "#57cc99"
        self.draw_cell(x, y, color, outline="#1b4332")
        if index == 0:
            self.draw_snake_face(x, y)

    def draw_snake_face(self, x: int, y: int) -> None:
        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        eye_points = {
            (1, 0): [(5, 5), (5, 14)],
            (-1, 0): [(15, 5), (15, 14)],
            (0, 1): [(5, 5), (14, 5)],
            (0, -1): [(5, 15), (14, 15)],
        }
        for ex, ey in eye_points.get(self.direction, eye_points[(1, 0)]):
            self.canvas.create_oval(x1 + ex - 2, y1 + ey - 2, x1 + ex + 2, y1 + ey + 2, fill="white", outline="")
            self.canvas.create_oval(x1 + ex - 1, y1 + ey - 1, x1 + ex + 1, y1 + ey + 1, fill="#111", outline="")

    def draw_round_food(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        self.canvas.create_oval(x1 + 3, y1 + 3, x1 + CELL_SIZE - 3, y1 + CELL_SIZE - 3, fill=color, outline="#651a1a", width=2)

    def draw_star_food(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        points = [
            (x1 + 10, y1 + 2), (x1 + 13, y1 + 8), (x1 + 19, y1 + 8), (x1 + 14, y1 + 12),
            (x1 + 16, y1 + 18), (x1 + 10, y1 + 14), (x1 + 4, y1 + 18), (x1 + 6, y1 + 12),
            (x1 + 1, y1 + 8), (x1 + 7, y1 + 8),
        ]
        self.canvas.create_polygon(points, fill=color, outline="#5e4800", width=2)

    def draw_cell(self, x: int, y: int, color: str, outline: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, fill=color, outline=outline)


def run() -> int:
    if tk is None:
        print("無法匯入 tkinter，請確認 Python 已安裝 Tk 支援。")
        print("Windows: 重新安裝官方 Python，勾選 tcl/tk and IDLE。")
        print("Ubuntu/Debian: sudo apt install python3-tk")
        print(f"詳細錯誤：{TK_IMPORT_ERROR}")
        return 1

    try:
        root = tk.Tk()
    except tk.TclError as error:
        print("無法啟動圖形介面（Tk）。")
        print("如果你在遠端/WSL/無桌面環境，請在本機桌面環境執行，或設定可用的 DISPLAY。")
        print(f"詳細錯誤：{error}")
        return 1

    SnakeGame(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

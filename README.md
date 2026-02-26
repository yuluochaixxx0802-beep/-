# Colorful Snake Ultra (Python)

更華麗、更有挑戰性的貪吃蛇，使用 Python 內建 `tkinter`，不需要額外安裝套件。

## 正確執行方式（很重要）

請在**終端機（Terminal）**執行，不要先進入 Python 互動模式（不要看到 `>>>` 再貼指令）。

```bash
cd /workspace/-
python3 snake.py
```

如果你現在畫面是 `>>>`，先輸入：

```python
exit()
```

再回到終端機執行上面的 `python3 snake.py`。

## 常見問題

- `IndentationError` 或 `SyntaxError` 出現在 `File "<python-input-...>"`：
  - 代表你把 shell 指令貼進了 Python 互動模式。
  - 請退出 `>>>` 後，在終端機重新執行。

## 新玩法

- 🎬 開場 Start 畫面（按 `Space` 開始）
- 🐍 蛇頭有表情（眼睛 + 吐舌頭）
- 🎨 多彩棋盤與漸層蛇身
- 🍎 圓形紅色食物：+1 分
- 💎 菱形金色食物（限時）：+3 分，並明顯加速
- ⭐ 星形紫色食物（限時）：+5 分，並加速
- 分數提升時，遊戲會逐步加快

## 操作

- `Space`：開始遊戲
- 方向鍵：移動蛇
- 撞牆或撞到自己：遊戲結束
- `R`：重新回到開始畫面

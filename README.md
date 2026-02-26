# Snake Bloom (Python)

簡潔風格的貪吃蛇介面：主畫面只有 `Start`、`How to Play`、`Exit` 三個選項。

## 執行

```bash
python3 snake.py
```

## 主要設定

- 中文字體：楷體（`KaiTi`）
- 英文字體：花體（`Segoe Script`）
- `K`：切換「吃星星是否加速」(ON/OFF)

## 操作

- 主選單：
  - `1` / `Enter`：Start
  - `2`：How to Play
  - `3` / `Esc`：Exit
  - 也可以直接用滑鼠點按選單
- 遊戲中：
  - 方向鍵：控制蛇移動
  - 紅色圓形食物：+1
  - 金色星星食物：+4（若 K 開啟加速）
  - `R`：遊戲結束後回主選單
- 說明頁：`Esc` / `Enter` 返回主選單

## 常見問題

- `ModuleNotFoundError: No module named 'tkinter'`：
  - Windows：重裝官方 Python，勾選 `tcl/tk and IDLE`
  - Ubuntu/Debian：`sudo apt install python3-tk`
- `_tkinter.TclError: no display name and no $DISPLAY environment variable`：
  - 代表沒有圖形桌面環境，請在有桌面的系統執行

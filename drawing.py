import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageOps, ImageEnhance
import time as teim
import pyautogui
import sys as sus

GRID_WIDTH = 100
GRID_HEIGHT = 80
TILE_SIZE = 10
YLEVEL = 920

class MapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Doom Map Editor")
        self.canvas = tk.Canvas(root, width=GRID_WIDTH * TILE_SIZE, height=GRID_HEIGHT * TILE_SIZE, bg="white")
        self.canvas.pack()

        self.tiles = {}  # dict: (x,y) -> opacity level (1–10)
        self.dragged_tiles = set()
        self.drawing = True

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_tile)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.running = True


        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Send to Whiteboard", command=self.send_to_whiteboard).pack(side=tk.LEFT)

        self.opacity_slider = tk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL, label="Opacity (1–10)")
        self.opacity_slider.set(10)
        self.opacity_slider.pack(side=tk.LEFT)

        self.contrast_slider = tk.Scale(control_frame, from_=50, to=200, orient=tk.HORIZONTAL, label="Contrast %")
        self.contrast_slider.set(100)
        self.contrast_slider.pack(side=tk.LEFT)

        self.draw_grid()

    def draw_grid(self):
        for x in range(0, GRID_WIDTH * TILE_SIZE, TILE_SIZE):
            for y in range(0, GRID_HEIGHT * TILE_SIZE, TILE_SIZE):
                self.canvas.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE, outline="gray")

    def get_tile_pos(self, event):
        return (event.x // TILE_SIZE, event.y // TILE_SIZE)

    def opacity_to_color(self, level):
        shade = 255 - int((level / 10) * 255)
        return f"#{shade:02x}{shade:02x}{shade:02x}"

    def draw_tile(self, pos):
        if pos in self.dragged_tiles:
            return
        self.dragged_tiles.add(pos)

        x1, y1 = pos[0] * TILE_SIZE, pos[1] * TILE_SIZE
        x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE

        if self.drawing:
            level = self.opacity_slider.get()
            self.tiles[pos] = level
            color = self.opacity_to_color(level)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        else:
            if pos in self.tiles:
                del self.tiles[pos]
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

    def start_drag(self, event):
        pos = self.get_tile_pos(event)
        self.drawing = pos not in self.tiles
        self.dragged_tiles = set()
        self.draw_tile(pos)

    def drag_tile(self, event):
        self.draw_tile(self.get_tile_pos(event))

    def end_drag(self, event):
        self.dragged_tiles.clear()

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        img = Image.open(path)
        img = ImageOps.grayscale(img)

        # Enhance contrast
        contrast_factor = self.contrast_slider.get() / 100.0  # from 0.5 to 2.0
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)

        img = img.resize((GRID_WIDTH, GRID_HEIGHT))

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                brightness = img.getpixel((x, y))
                if brightness > 230:
                    level = 0
                elif brightness > 180:
                    level = 1
                elif brightness > 130:
                    level = 2
                elif brightness > 80:
                    level = 3
                elif brightness > 30:
                    level = 4
                else:
                    level = 5

                mapped_level = level * 2  # gives 0, 2, 4, 6, 8, 10
                if mapped_level > 0:
                    self.tiles[(x, y)] = mapped_level
                    color = self.opacity_to_color(mapped_level)
                    x1, y1 = x * TILE_SIZE, y * TILE_SIZE
                    x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def send_to_whiteboard(self):
        grid = [
            [self.tiles.get((x, y), 0) for x in range(GRID_WIDTH)]
            for y in range(GRID_HEIGHT)
        ]

        teim.sleep(3)

        screen_width, screen_height = pyautogui.size()
        canvas_width = GRID_WIDTH * TILE_SIZE
        canvas_height = GRID_HEIGHT * TILE_SIZE
        start_x = (screen_width - canvas_width) // 2
        start_y = (screen_height - canvas_height) // 2

        pyautogui.PAUSE = 0
        short_delay = 0.005

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.running == False:
                    return

                clicks = grid[y][x]
                if clicks > 0 and  self.running:
                    px = start_x + x * TILE_SIZE + TILE_SIZE // 2
                    py = start_y + y * TILE_SIZE + TILE_SIZE // 2

                    op_lvl = {
                        'd': (30, YLEVEL),
                        1: (111, YLEVEL),
                        2: (141, YLEVEL),
                        3: (170, YLEVEL),
                        4: (194, YLEVEL),
                        5: (214, YLEVEL),
                        6: (230, YLEVEL),
                        7: (239, YLEVEL),
                        8: (250, YLEVEL),
                        9: (275, YLEVEL),
                        10: (275, YLEVEL)
                    }

                    pyautogui.moveTo(op_lvl['d'])
                    pyautogui.click()
                    teim.sleep(0.05)
                    pyautogui.moveTo(op_lvl[clicks])
                    pyautogui.click()

                    pyautogui.moveTo(px, py)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(px + 3, py + 3)
                    pyautogui.mouseUp()
                    teim.sleep(short_delay)


if __name__ == "__main__":
    root = tk.Tk()
    app = MapEditor(root)
    root.mainloop()

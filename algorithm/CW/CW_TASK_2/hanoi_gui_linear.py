
import tkinter as tk
PEG_ORDER = ('A', 'B', 'C')

def are_adjacent(a, b):
    return (a == 'A' and b == 'B') or (a == 'B' and b == 'A') or (a == 'B' and b == 'C') or (a == 'C' and b == 'B')

def hanoi_linear(n, src, dst, aux, moves):
    if n == 0:
        return
    if are_adjacent(src, dst):
        hanoi_linear(n - 1, src, aux, dst, moves)
        moves.append((src, dst))
        hanoi_linear(n - 1, aux, dst, src, moves)
    else:
        hanoi_linear(n - 1, src, dst, aux, moves)
        moves.append((src, aux))
        hanoi_linear(n - 1, dst, src, aux, moves)
        moves.append((aux, dst))
        hanoi_linear(n - 1, src, dst, aux, moves)

class HanoiGUI:
    def __init__(self, root):
        self.root = root
        root.title("Tower of Hanoi (Adjacent Moves Only)")
        self.canvas = tk.Canvas(root, width=900, height=420, bg="#111")
        self.canvas.pack(fill="both", expand=True)

        controls = tk.Frame(root, bg="#181818")
        controls.pack(fill="x")
        tk.Label(controls, text="Disks:", fg="#eee", bg="#181818").pack(side="left", padx=(10,4))
        self.n_var = tk.IntVar(value=4)
        tk.Spinbox(controls, from_=1, to=10, width=4, textvariable=self.n_var).pack(side="left", padx=(0,10))
        tk.Button(controls, text="Reset", command=self.reset).pack(side="left", padx=5)
        tk.Button(controls, text="Step", command=self.step).pack(side="left", padx=5)
        tk.Button(controls, text="Auto Play", command=self.auto_play).pack(side="left", padx=5)
        tk.Button(controls, text="Pause", command=self.pause).pack(side="left", padx=5)
        tk.Label(controls, text="Speed (ms):", fg="#eee", bg="#181818").pack(side="left", padx=(20,4))
        self.speed_var = tk.IntVar(value=300)
        tk.Scale(controls, from_=50, to=1500, orient="horizontal", variable=self.speed_var, showvalue=True, length=200).pack(side="left")
        self.status = tk.Label(controls, text="", fg="#ccc", bg="#181818")
        self.status.pack(side="right", padx=10)

        self.peg_x = {}
        self.disk_items = {}
        self.stacks = {'A': [], 'B': [], 'C': []}
        self.moves = []
        self.move_index = 0
        self.after_id = None

        self.draw_board()
        self.reset()

    def draw_board(self):
        self.canvas.delete("all")
        w = int(self.canvas['width'])
        h = int(self.canvas['height'])
        margin = 80
        peg_spacing = (w - 2 * margin) // 2
        xs = [margin + i * peg_spacing for i in range(3)]
        for i, peg in enumerate(PEG_ORDER):
            x = xs[i]
            self.peg_x[peg] = x
            self.canvas.create_rectangle(x - 6, 100, x + 6, h - 40, fill="#444", outline="")
            self.canvas.create_text(x, 30, text=f"Peg {peg}", fill="#ddd", font=("Segoe UI", 14))
        self.canvas.create_rectangle(40, h - 40, w - 40, h - 30, fill="#555", outline="")

    def reset(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.draw_board()
        self.disk_items.clear()
        self.stacks = {'A': [], 'B': [], 'C': []}
        n = self.n_var.get()
        base_width = 220
        min_width = 80
        w_step = (base_width - min_width) / max(1, n - 1) if n > 1 else 0
        for size in range(n, 0, -1):
            width = int(min_width + (size - 1) * w_step)
            rect = self.create_disk('A', size, width)
            self.disk_items[size] = rect
            self.stacks['A'].append(size)
        self.moves = []
        hanoi_linear(n, 'A', 'C', 'B', self.moves)
        self.move_index = 0
        self.update_status()

    def create_disk(self, peg, size, width):
        x = self.peg_x[peg]
        stack = self.stacks[peg]
        h = int(self.canvas['height'])
        height = 18
        y = (h - 40) - height * len(stack) - 2
        rect = self.canvas.create_rectangle(x - width // 2, y - height, x + width // 2, y, fill="#29a", outline="#9cf")
        self.canvas.tag_raise(rect)
        return rect

    def place_disk(self, peg, size):
        x = self.peg_x[peg]
        h = int(self.canvas['height'])
        height = 18
        level = len(self.stacks[peg]) + 1
        y = (h - 40) - height * level - 2
        rect = self.disk_items[size]
        x0, y0, x1, y1 = self.canvas.coords(rect)
        w = x1 - x0
        self.canvas.coords(rect, x - w/2, y - height, x + w/2, y)

    def legal(self, src, dst):
        if not self.stacks[src]:
            return False
        if not are_adjacent(src, dst):
            return False
        moving = self.stacks[src][-1]
        if not self.stacks[dst]:
            return True
        return moving < self.stacks[dst][-1]

    def step(self):
        if self.move_index >= len(self.moves):
            return
        src, dst = self.moves[self.move_index]
        if self.legal(src, dst):
            size = self.stacks[src].pop()
            self.stacks[dst].append(size)
            self.place_disk(dst, size)
            self.move_index += 1
            self.update_status()
        else:
            self.move_index += 1
            self.update_status()
            self.step()

    def auto_play(self):
        if self.after_id is not None:
            return
        def tick():
            if self.move_index >= len(self.moves):
                self.after_id = None
                return
            self.step()
            self.after_id = self.root.after(self.speed_var.get(), tick)
        tick()

    def pause(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def update_status(self):
        self.status.config(text=f"Move {self.move_index}/{len(self.moves)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HanoiGUI(root)
    root.mainloop()

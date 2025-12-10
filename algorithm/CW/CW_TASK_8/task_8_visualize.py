import tkinter as tk
from tkinter import messagebox, filedialog

# -------------- Colors and config --------------

COLOR_MAP = {
    1: "#ff4b4b",  # red
    2: "#4b7bff",  # blue
    3: "#4bff6a",  # green
    4: "#ffd84b",  # yellow
    5: "#ff4bd2",  # pink
    6: "#4bfff2",  # cyan
    7: "#b44bff",  # purple
    8: "#ff924b",  # orange
    9: "#8cff4b",  # lime
    10: "#ffffff", # white
}

BACKGROUND_COLOR = "#202020"
STACK_COLOR = "#404040"
OUTLINE_COLOR = "#101010"

DEFAULT_FILE = "game.txt"


# -------------- File loading --------------

def load_game_file(path):
    """
    File format:

    Line 1:
        <num_stacks> <capacity>

    Next num_stacks lines:
        k c1 c2 ... ck
        (k = number of balls in this stack,
         c1..ck = colors from bottom to top)

    Remaining lines:
        from to   (1-based indices)
    """
    with open(path, "r") as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    if not raw_lines:
        raise ValueError("File is empty")

    # First line: num_stacks capacity
    parts = raw_lines[0].split()
    if len(parts) != 2:
        raise ValueError("First line must be: <num_stacks> <capacity>")

    try:
        num_stacks = int(parts[0])
        capacity = int(parts[1])
    except ValueError:
        raise ValueError("First line must contain two integers")

    if num_stacks <= 0 or capacity <= 0:
        raise ValueError("num_stacks and capacity must be positive")

    if len(raw_lines) < 1 + num_stacks:
        raise ValueError("Not enough lines for stack descriptions")

    stacks = []
    # Next num_stacks lines: k c1 c2 ... ck
    for i in range(num_stacks):
        line = raw_lines[1 + i]
        parts = line.split()
        if not parts:
            raise ValueError(f"Empty line for stack {i+1}")

        try:
            k = int(parts[0])
        except ValueError:
            raise ValueError(f"Invalid k in line for stack {i+1}: '{line}'")

        colors = []
        if k > 0:
            if len(parts) != k + 1:
                raise ValueError(
                    f"Stack {i+1} line '{line}' does not have k={k} colors"
                )
            for p in parts[1:]:
                try:
                    colors.append(int(p))
                except ValueError:
                    raise ValueError(
                        f"Invalid color '{p}' in stack {i+1}"
                    )

        if k > capacity:
            raise ValueError(
                f"Stack {i+1} has {k} balls which exceeds capacity {capacity}"
            )

        stacks.append(colors)  # bottom to top

    # Remaining lines: moves "from to"
    moves = []
    for line in raw_lines[1 + num_stacks:]:
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(
                f"Move line '{line}' must have two integers: from to"
            )
        try:
            fr = int(parts[0])
            to = int(parts[1])
        except ValueError:
            raise ValueError(f"Move line '{line}' has non-integer indices")

        fr_idx = fr - 1
        to_idx = to - 1
        if fr_idx < 0 or fr_idx >= num_stacks or to_idx < 0 or to_idx >= num_stacks:
            raise ValueError(
                f"Move '{line}' has indices out of range for {num_stacks} stacks"
            )

        moves.append((fr_idx, to_idx))

    return stacks, capacity, moves


# -------------- Simulation --------------

def apply_move(state, move, capacity):
    """
    Apply one move (from_idx, to_idx) to state in place.
    state: list of stacks, each stack is a list [bottom..top].
    """
    fr, to = move
    if not state[fr]:
        raise ValueError(f"Invalid move: source stack {fr+1} is empty")

    if len(state[to]) >= capacity:
        raise ValueError(f"Invalid move: destination stack {to+1} is full")

    ball = state[fr][-1]

    # Optional rule: either empty dest or same color on top
    if state[to] and state[to][-1] != ball:
        raise ValueError(
            f"Invalid move: cannot place color {ball} on top of {state[to][-1]} "
            f"in stack {to+1}"
        )

    state[fr].pop()
    state[to].append(ball)


def generate_state_history(initial_state, moves, capacity):
    """
    Build list of states: history[step] is state after 'step' moves.
    step 0 is the initial configuration.
    """
    import copy
    history = [copy.deepcopy(initial_state)]
    current = copy.deepcopy(initial_state)
    for mv in moves:
        apply_move(current, mv, capacity)
        history.append(copy.deepcopy(current))
    return history


# -------------- GUI --------------

class BallSortViewer(tk.Frame):
    def __init__(self, master, initial_state, capacity, moves, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.initial_state = initial_state
        self.capacity = capacity
        self.moves = moves

        self.num_stacks = len(initial_state)
        self.state_history = generate_state_history(initial_state, moves, capacity)
        self.current_step = 0

        # Canvas
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=500,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control panel
        controls = tk.Frame(self)
        controls.pack(side=tk.BOTTOM, fill=tk.X)

        self.info_label = tk.Label(
            controls,
            text=f"Step 0 / {len(self.state_history) - 1}"
        )
        self.info_label.pack(side=tk.LEFT, padx=10)

        btn_open = tk.Button(controls, text="Open File", command=self.open_file)
        btn_open.pack(side=tk.RIGHT, padx=5)

        btn_last = tk.Button(controls, text=">>", command=self.go_last)
        btn_last.pack(side=tk.RIGHT, padx=5)

        btn_next = tk.Button(controls, text="Next", command=self.step_forward)
        btn_next.pack(side=tk.RIGHT, padx=5)

        btn_prev = tk.Button(controls, text="Prev", command=self.step_back)
        btn_prev.pack(side=tk.RIGHT, padx=5)

        btn_first = tk.Button(controls, text="<<", command=self.go_first)
        btn_first.pack(side=tk.RIGHT, padx=5)

        self.bind_events()
        self.draw_current_state()

    def bind_events(self):
        # Optional: keyboard shortcuts
        self.master.bind("<Left>", lambda e: self.step_back())
        self.master.bind("<Right>", lambda e: self.step_forward())
        self.master.bind("<Home>", lambda e: self.go_first())
        self.master.bind("<End>", lambda e: self.go_last())

    # -------- file reload --------

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open game file",
            filetypes=[("Text files", "*.txt *.dat *.log *.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            stacks, capacity, moves = load_game_file(path)
            self.initial_state = stacks
            self.capacity = capacity
            self.moves = moves
            self.num_stacks = len(stacks)
            self.state_history = generate_state_history(stacks, moves, capacity)
            self.current_step = 0
            self.draw_current_state()
            self.update_info()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    # -------- navigation --------

    def go_first(self):
        self.current_step = 0
        self.draw_current_state()
        self.update_info()

    def go_last(self):
        self.current_step = len(self.state_history) - 1
        self.draw_current_state()
        self.update_info()

    def step_forward(self):
        if self.current_step < len(self.state_history) - 1:
            self.current_step += 1
            self.draw_current_state()
            self.update_info()

    def step_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.draw_current_state()
            self.update_info()

    def update_info(self):
        self.info_label.config(
            text=f"Step {self.current_step} / {len(self.state_history) - 1}"
        )

    # -------- drawing --------

    def draw_current_state(self):
        self.canvas.delete("all")
        state = self.state_history[self.current_step]

        width = int(self.canvas.winfo_width() or 800)
        height = int(self.canvas.winfo_height() or 500)

        top_margin = 40
        bottom_margin = 60
        stack_height_px = height - top_margin - bottom_margin

        stack_width = max(40, width // max(1, (2 * self.num_stacks)))
        spacing = stack_width
        total_width = (
            self.num_stacks * stack_width + (self.num_stacks - 1) * spacing
        )
        start_x = (width - total_width) // 2

        for i, stack in enumerate(state):
            x0 = start_x + i * (stack_width + spacing)
            x1 = x0 + stack_width
            y0 = top_margin
            y1 = top_margin + stack_height_px

            # Tube
            self.canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                outline=OUTLINE_COLOR,
                width=2,
                fill=STACK_COLOR,
            )

            if not stack:
                # Label stack index under the tube
                self.canvas.create_text(
                    (x0 + x1) / 2,
                    y1 + 15,
                    text=str(i + 1),
                    fill="white",
                )
                continue

            max_balls = self.capacity
            cell_height = stack_height_px / max_balls

            # Balls: stack is [bottom..top]
            for j, color_id in enumerate(stack):
                bottom_y = y1 - j * cell_height
                top_y = bottom_y - cell_height

                cx = (x0 + x1) / 2
                cy = (top_y + bottom_y) / 2
                radius = min(stack_width, cell_height) * 0.4

                fill_color = COLOR_MAP.get(color_id, "#cccccc")

                self.canvas.create_oval(
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                    fill=fill_color,
                    outline="black",
                    width=1,
                )

            self.canvas.create_text(
                (x0 + x1) / 2,
                y1 + 15,
                text=str(i + 1),
                fill="white",
            )


# -------------- Main --------------

def main():
    try:
        stacks, capacity, moves = load_game_file(DEFAULT_FILE)
    except Exception as e:
        print(f"Could not load default file '{DEFAULT_FILE}': {e}")
        print("Using a dummy config; open your real file from the GUI.")
        stacks = [[1, 2, 1], [2], [], []]
        capacity = 4
        moves = []

    root = tk.Tk()
    root.title("Ball Sorting Game Viewer")

    viewer = BallSortViewer(root, stacks, capacity, moves)
    viewer.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()

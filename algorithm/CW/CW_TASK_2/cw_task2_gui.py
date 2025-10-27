
import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

LINE_RE = re.compile(r"Move\s+no\.\s*\d+\s*:\s*Move\s+disk\s+(\d+)\s+from\s+rod\s+([ABC])\s+to\s+rod\s+([ABC])", re.I)

class SimpleHanoiGUI:
    def __init__(self, root):
        self.root = root
        root.title("Hanoi Moves (Simple GUI using your C++ exe)")

        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=8)

        self.exe_path = tk.StringVar(value="")
        tk.Button(top, text="Select EXE", command=self.pick_exe).pack(side="left")
        self.exe_label = tk.Label(top, text="No executable selected", anchor="w")
        self.exe_label.pack(side="left", padx=8)

        mid = tk.Frame(root)
        mid.pack(fill="x", padx=8)
        tk.Label(mid, text="Disks (N):").pack(side="left")
        self.n_var = tk.IntVar(value=4)
        tk.Spinbox(mid, from_=1, to=14, textvariable=self.n_var, width=5).pack(side="left", padx=6)
        tk.Button(mid, text="Run", command=self.run_cpp).pack(side="left", padx=6)
        tk.Button(mid, text="Clear", command=self.clear).pack(side="left", padx=6)

        self.info = tk.Label(root, text="", anchor="w")
        self.info.pack(fill="x", padx=8, pady=(0,6))

        self.listbox = tk.Listbox(root, width=80, height=20)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def pick_exe(self):
        path = filedialog.askopenfilename(title="Select your compiled C++ executable",
                                          filetypes=[("Executables", "*.exe *.out *.bin *"), ("All files", "*.*")])
        if path:
            self.exe_path.set(path)
            self.exe_label.config(text=os.path.basename(path))

    def run_cpp(self):
        exe = self.exe_path.get().strip()
        if not exe or not os.path.exists(exe):
            messagebox.showwarning("Select EXE", "Please select your compiled C++ program first.")
            return
        n = int(self.n_var.get())

        # Your C++ reads N from stdin, so we just pipe it.
        try:
            res = subprocess.run([exe], input=str(n) + "\n",
                                 capture_output=True, text=True, timeout=30)
        except Exception as e:
            messagebox.showerror("Error running program", str(e))
            return

        out = res.stdout.strip()
        if not out:
            messagebox.showerror("No output", "Your program did not print any moves.")
            return

        self.listbox.delete(0, tk.END)
        parsed_lines = 0
        for line in out.splitlines():
            line = line.strip()
            if LINE_RE.search(line):
                self.listbox.insert(tk.END, line)
                parsed_lines += 1

        self.info.config(text=f"Parsed {parsed_lines} moves. Exit code: {res.returncode}")

    def clear(self):
        self.listbox.delete(0, tk.END)
        self.info.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleHanoiGUI(root)
    root.mainloop()

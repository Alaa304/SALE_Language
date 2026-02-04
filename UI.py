import tkinter as tk
from tkinter import scrolledtext
from compiler import run_compiler

# ===============================
# COLORS & THEME
# ===============================

BG = "#0f172a"        # Dark Blue
PANEL = "#020617"     # Editor Background
BTN = "#2563eb"       # Blue Button
BTN_HOVER = "#1d4ed8"
TEXT = "#e5e7eb"      # Light Text
ACCENT = "#22c55e"    # Green

# ===============================
# MAIN WINDOW
# ===============================

root = tk.Tk()
root.title("ESAL Compiler IDE")
root.geometry("1300x720")
root.configure(bg=BG)

# ===============================
# TOP BAR
# ===============================

top_frame = tk.Frame(root, bg=BG, height=50)
top_frame.pack(fill=tk.X)

title = tk.Label(
    top_frame,
    text="ESAL COMPILER IDE",
    fg=ACCENT,
    bg=BG,
    font=("Segoe UI", 16, "bold")
)
title.pack(side=tk.LEFT, padx=20)

# ===============================
# BUTTONS
# ===============================

def on_hover(e):
    e.widget["background"] = BTN_HOVER

def on_leave(e):
    e.widget["background"] = BTN


btn_compile = tk.Button(
    top_frame,
    text="▶ Compile",
    bg=BTN,
    fg="white",
    font=("Segoe UI", 11, "bold"),
    relief=tk.FLAT,
    padx=20,
    pady=6
)

btn_compile.pack(side=tk.RIGHT, padx=10)
btn_compile.bind("<Enter>", on_hover)
btn_compile.bind("<Leave>", on_leave)


btn_clear = tk.Button(
    top_frame,
    text="🧹 Clear",
    bg="#334155",
    fg="white",
    font=("Segoe UI", 11),
    relief=tk.FLAT,
    padx=20,
    pady=6,
    command=lambda: output_area.delete("1.0", tk.END)
)

btn_clear.pack(side=tk.RIGHT)

# ===============================
# MAIN PANELS
# ===============================

main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ---------------- LEFT (EDITOR) ----------------

left_panel = tk.Frame(main_frame, bg=BG)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

lbl_editor = tk.Label(
    left_panel,
    text="SOURCE CODE",
    fg=TEXT,
    bg=BG,
    font=("Segoe UI", 11, "bold")
)
lbl_editor.pack(anchor="w")

code_area = scrolledtext.ScrolledText(
    left_panel,
    bg=PANEL,
    fg="#38bdf8",
    insertbackground="white",
    font=("Consolas", 12),
    padx=10,
    pady=10
)

code_area.pack(fill=tk.BOTH, expand=True, pady=5)


# ---------------- RIGHT (OUTPUT) ----------------

right_panel = tk.Frame(main_frame, bg=BG)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

lbl_output = tk.Label(
    right_panel,
    text="COMPILER OUTPUT",
    fg=TEXT,
    bg=BG,
    font=("Segoe UI", 11, "bold")
)
lbl_output.pack(anchor="w")

output_area = scrolledtext.ScrolledText(
    right_panel,
    bg=PANEL,
    fg="#f8fafc",
    insertbackground="white",
    font=("Consolas", 11),
    padx=10,
    pady=10
)

output_area.pack(fill=tk.BOTH, expand=True, pady=5)


# ===============================
# STATUS BAR
# ===============================

status_bar = tk.Label(
    root,
    text="Ready",
    bg="#020617",
    fg="#94a3b8",
    anchor="w",
    padx=15,
    font=("Segoe UI", 10)
)

status_bar.pack(fill=tk.X)


# ===============================
# COMPILER ACTION
# ===============================

def compile_code():

    status_bar.config(text="Compiling...")

    code = code_area.get("1.0", tk.END)
    result = run_compiler(code)

    output_area.delete("1.0", tk.END)

    if result["errors"]:
        output_area.insert(tk.END, "❌ ERRORS\n\n")
        for e in result["errors"]:
            output_area.insert(tk.END, e + "\n")

    if result["warnings"]:
        output_area.insert(tk.END, "\n⚠ WARNINGS\n\n")
        for w in result["warnings"]:
            output_area.insert(tk.END, w + "\n")

    output_area.insert(tk.END, "\n📦 SYMBOL TABLE\n\n")
    output_area.insert(tk.END, result["symbol_table"])

    status_bar.config(text="Compilation Finished ✔")


btn_compile.config(command=compile_code)


# ===============================
# START UI
# ===============================

def start_ui():
    root.mainloop()

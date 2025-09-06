import tkinter as tk


class ScreenInfo:
    root = tk.Tk()
    root.withdraw()
    horizontal = root.winfo_screenwidth()
    vertical = root.winfo_screenheight()
    root.destroy()

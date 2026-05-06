import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from gui import MazeApp

if __name__ == '__main__':
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
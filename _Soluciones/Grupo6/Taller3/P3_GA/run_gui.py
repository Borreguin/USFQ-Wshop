import os
import sys

print("Python:", sys.executable)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Taller3.P3_GA.GUI.app import main

main()

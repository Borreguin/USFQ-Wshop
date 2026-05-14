import os, sys
script_path = os.path.dirname(os.path.abspath(__file__))
p1_uml_path = os.path.dirname(script_path)
data_path = os.path.join(script_path, 'data')
print(f"Adding {p1_uml_path} to sys.path")
sys.path.append(script_path)
import os
import sys
import time
import matplotlib.pyplot as plt
from collections import deque
import heapq

# Ajustar el path para importar utilidades
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from Taller2.P1.P1_util import define_color

def load_maze(filename):
	maze = []
	with open(filename, 'r') as f:
		for line in f:
			maze.append(list(line.strip('\n')))
	return maze

def find_pos(maze, symbol):
	for y, row in enumerate(maze):
		for x, cell in enumerate(row):
			if cell == symbol:
				return (y, x)
	return None

def neighbors(maze, pos):
	y, x = pos
	for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
		ny, nx = y+dy, x+dx
		if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
			if maze[ny][nx] != '#':
				yield (ny, nx)

# BFS
def bfs(maze, start, goal):
	queue = deque([start])
	visited = {start: None}
	nodes_explored = 0
	while queue:
		current = queue.popleft()
		nodes_explored += 1
		if current == goal:
			break
		for n in neighbors(maze, current):
			if n not in visited:
				visited[n] = current
				queue.append(n)
	# Reconstruir camino
	path = []
	node = goal
	while node and node in visited:
		path.append(node)
		node = visited[node]
	path.reverse()
	return path, nodes_explored

# A* (Manhattan)
def heuristic(a, b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(maze, start, goal):
	heap = [(0 + heuristic(start, goal), 0, start, None)]
	visited = {}
	nodes_explored = 0
	while heap:
		f, g, current, parent = heapq.heappop(heap)
		if current in visited:
			continue
		visited[current] = parent
		nodes_explored += 1
		if current == goal:
			break
		for n in neighbors(maze, current):
			if n not in visited:
				heapq.heappush(heap, (g+1+heuristic(n, goal), g+1, n, current))
	# Reconstruir camino
	path = []
	node = goal
	while node and node in visited:
		path.append(node)
		node = visited[node]
	path.reverse()
	return path, nodes_explored

def plot_solution(maze, path, title, savefile=None):
	height = len(maze)
	width = len(maze[0])
	fig = plt.figure(figsize=(width/8, height/8))
	for y in range(height):
		for x in range(width):
			cell = maze[y][x]
			color = define_color(cell)
			plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')
	# Dibujar camino
	if path:
		py, px = zip(*path)
		plt.plot(px, py, color='blue', linewidth=2, label='Solución')
	plt.title(title)
	plt.xlim(0, width)
	plt.ylim(0, height)
	plt.gca().invert_yaxis()
	plt.xticks([])
	plt.yticks([])
	fig.tight_layout()
	if savefile:
		plt.savefig(savefile)
	plt.show()

def solve_and_compare(maze_file, name):
	maze = load_maze(maze_file)
	start = find_pos(maze, 'E')
	goal = find_pos(maze, 'S')
	print(f"Resolviendo {name}...")
	# BFS
	t0 = time.time()
	path_bfs, explored_bfs = bfs(maze, start, goal)
	t1 = time.time()
	print(f"BFS: longitud={len(path_bfs)}, nodos explorados={explored_bfs}, tiempo={t1-t0:.4f}s")
	plot_solution(maze, path_bfs, f"{name} - BFS", savefile=f"{name}_BFS.png")
	# A*
	t0 = time.time()
	path_astar, explored_astar = astar(maze, start, goal)
	t1 = time.time()
	print(f"A*: longitud={len(path_astar)}, nodos explorados={explored_astar}, tiempo={t1-t0:.4f}s")
	plot_solution(maze, path_astar, f"{name} - A*", savefile=f"{name}_Astar.png")

if __name__ == "__main__":
	base = os.path.join(project_path, '../../../Taller2/P1')
	solve_and_compare(os.path.join(base, 'laberinto2.txt'), 'laberinto2')
	solve_and_compare(os.path.join(base, 'laberinto4.txt'), 'laberinto4')

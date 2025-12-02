import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from P1_Search import find_start_goal, dfs, bfs, dijkstra, astar
import json



def study_case_1():
    print("This is study case 1")
    maze_file = 'laberinto1.txt'
    loader = MazeLoader(maze_file).load_Maze()

    graph = loader.get_graph()
    start, goal = find_start_goal(loader.maze)

    results = [
        dfs(graph, start, goal),
        bfs(graph, start, goal),
        dijkstra(graph, start, goal),
        astar(graph, start, goal),
    ]

    for r in results:
        print(
            f"{r['algo']:8} | found={r['found']} | visited={r['visited']}"
            f" | path_len={r['path_len']} | cost={r['cost']} | time_ms={r['time_ms']:.3f}"
        )

    for r in results:
        algo = r["algo"].lower().replace("*", "astar")
        loader.plot_solution(
            path=r["path"],
            visited=r.get("visited_nodes", None),
            save_as=f"sol_{algo}_{maze_file.replace('.txt','')}.png",
            show=False,
            title=f"{r['algo']} | visited={r['visited']} | len={r['path_len']}"
        )



def study_case_2():
    print("This is study case 2")
    maze_file = 'laberinto2.txt'
    loader = MazeLoader(maze_file).load_Maze()

    graph = loader.get_graph()
    start, goal = find_start_goal(loader.maze)

    results = [
        dfs(graph, start, goal),
        bfs(graph, start, goal),
        dijkstra(graph, start, goal),
        astar(graph, start, goal),
    ]

    for r in results:
        print(
            f"{r['algo']:8} | found={r['found']} | visited={r['visited']}"
            f" | path_len={r['path_len']} | cost={r['cost']} | time_ms={r['time_ms']:.3f}"
        )

    for r in results:
        algo = r["algo"].lower().replace("*", "astar")
        loader.plot_solution(
            path=r["path"],
            visited=r.get("visited_nodes", None),
            save_as=f"sol_{algo}_{maze_file.replace('.txt','')}.png",
            show=False,
            title=f"{r['algo']} | visited={r['visited']} | len={r['path_len']}"
        )

def study_case_3():
    print("This is study case 2")
    maze_file = 'laberinto3.txt'
    loader = MazeLoader(maze_file).load_Maze()

    graph = loader.get_graph()
    start, goal = find_start_goal(loader.maze)

    results = [
        dfs(graph, start, goal),
        bfs(graph, start, goal),
        dijkstra(graph, start, goal),
        astar(graph, start, goal),
    ]

    for r in results:
        print(
            f"{r['algo']:8} | found={r['found']} | visited={r['visited']}"
            f" | path_len={r['path_len']} | cost={r['cost']} | time_ms={r['time_ms']:.3f}"
        )

    for r in results:
        algo = r["algo"].lower().replace("*", "astar")
        loader.plot_solution(
            path=r["path"],
            visited=r.get("visited_nodes", None),
            save_as=f"sol_{algo}_{maze_file.replace('.txt','')}.png",
            show=False,
            title=f"{r['algo']} | visited={r['visited']} | len={r['path_len']}"
        )


if __name__ == '__main__':
    study_case_1()
    study_case_2()
    study_case_3()

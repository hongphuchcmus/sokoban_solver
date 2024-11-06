from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban, Record
from runner import Runner
import os
import psutil

INPUT_DIR = "input"
OUTPUT_DIR = "output"

solver_records = {}
for file in os.listdir(INPUT_DIR):
    if file.startswith("input-") and file.endswith(".txt"):
        g = Sokoban(f"{INPUT_DIR}/{file}")
        for algo in ["BFS", "DFS", "UCS", "AStar"]:
            if algo == "BFS":
                solver = BFSSolver(g)
            elif algo == "DFS":
                solver = DFSSolver(g)
            elif algo == "UCS":
                solver = UCSSolver(g)
            elif algo == "AStar":
                solver = AStarSolver(g)
            
            solver.solve()
            if algo not in solver_records:
                solver_records[algo] = []
            solver_records[algo].append(solver.record)

# Write a csv
# Algo| Map | Time | Memory | Steps | Nodes
# BFS | 1 |
# BFS | 2 | 
# BFS | 3 |
# ... |...|
# BFS| 10|
# DFS | 1 |
# DFS | 2 |
# DFS | 3 |
# ...|...|
# DFS|10|
# ...|...

with open("results.csv", "w") as f:
    f.write("Algo, Map,Time,Memory,Steps,Nodes\n")
    for algo in solver_records:
        for i in range(len(solver_records[algo])):
            record = solver_records[algo][i]
            f.write(f"{algo},{i+1}, {record.time_ms},{record.memory_mb},{record.steps},{record.node}\n")
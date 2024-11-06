from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban, Record
from runner import Runner
import os
import psutil
import pandas as pd

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
# and then, for each algo,I want you to draw 4 line graphs with x-axis as map number and y-axis relatively as time taken to solve the map, memory used to solve the map, steps taken to solve the map, and nodes expanded to solve the map.
# You can use matplotlib for this.


with open("results.csv", "w") as f:
    f.write("Algo, Map,Time,Memory,Steps,Nodes\n")
    for algo in solver_records:
        for i in range(len(solver_records[algo])):
            record = solver_records[algo][i]
            f.write(f"{algo},{i+1}, {record.time_ms},{record.memory_mb},{record.steps},{record.node}\n")
            

# import pandas as pd
# import matplotlib.pyplot as plt

# # Read data from the CSV file
# data = pd.read_csv("results.csv")
# data.columns = data.columns.str.strip()
# print(data.columns)
# # Define the criteria to plot
# criteria = ['Time', 'Memory', 'Steps', 'Nodes']

# # Define algorithms to compare
# algorithms = ['BFS', 'DFS', 'UCS', 'AStar']

# # Generate plots for each criterion
# for criterion in criteria:
#     plt.figure(figsize=(10, 6))
    
#     # Plot each algorithm's data for the current criterion
#     for algo in algorithms:
#         algo_data = data[data['Algo'] == algo]
#         plt.plot(algo_data['Map'], algo_data[criterion], marker='o', label=algo)
    
#     # Labeling the plot
#     plt.title(f"Comparison of {criterion} across Maps for Different Algorithms")
#     plt.xlabel("Map")
#     plt.ylabel(criterion)
#     plt.xticks(data['Map'].unique())  # Set x-ticks to map numbers
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()

#     plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# Read data from the CSV file and strip any extra whitespace from column names
data = pd.read_csv("results.csv")
data.columns = data.columns.str.strip()  # Ensure no whitespace in column names

# Define the criteria to plot
criteria = ['Time', 'Memory', 'Steps', 'Nodes']
# Define algorithms to compare
algorithms = ['BFS', 'DFS', 'UCS', 'AStar']

# Create a 2x2 subplot layout
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Comparison of Algorithms Across Maps by Different Criteria", fontsize=16)

# Iterate over each criterion and axis to plot each graph
for i, criterion in enumerate(criteria):
    ax = axs[i // 2, i % 2]  # Get the correct subplot in 2x2 grid
    
    # Plot each algorithm's data for the current criterion
    for algo in algorithms:
        algo_data = data[data['Algo'] == algo]
        ax.plot(algo_data['Map'], algo_data[criterion], marker='o', label=algo)
    
    # Labeling for each subplot
    ax.set_title(f"{criterion} Comparison")
    ax.set_xlabel("Map")
    ax.set_ylabel(criterion)
    ax.legend()
    ax.grid(True)

# Adjust layout for better spacing
plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Leave space for the main title
plt.show()

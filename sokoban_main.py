import sokoban_console_refactored as skb
from bfs import BFSSolver
from dfs import DFSSolver
import time as time

g = skb.Sokoban("input.txt")
g.draw_input_matrix()

dfs = DFSSolver(g)
path = dfs.solve()
print("Path found: ", path)

g.draw_input_matrix()

ares_last_position = g.ares_initial_position
stone_positions = g.stones_initial_positions

for i in range(len(path)):
    time.sleep(.1)

    ares_movement = path[i].lower()
    
    ares_direction = (0, 0)
    if ares_movement == "l":
        ares_direction = (0, -1)
    elif ares_movement == "r":
        ares_direction = (0, 1)
    elif ares_movement == "u":
        ares_direction = (-1, 0)
    elif ares_movement == "d":
        ares_direction = (1, 0)
    
    ares_new_position = (ares_last_position[skb.Y] + ares_direction[skb.Y], ares_last_position[skb.X] + ares_direction[skb.X])
    if ares_movement.upper() == path[i]:
        # Push the stone
        for i in range(len(stone_positions)):
            if stone_positions[i] == ares_new_position:
                stone_positions[i] = (ares_new_position[skb.Y] + ares_direction[skb.Y], ares_new_position[skb.X] + ares_direction[skb.X])
                break
    ares_last_position = ares_new_position
    
    visual_state = skb.State(ares_last_position, stone_positions)
    print(g.draw_state(visual_state, [], False))
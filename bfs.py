import sokoban_console_refactored as skb
from collections import deque

class BFSSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g

    def branch(self, g : skb.Sokoban, state: skb.State) -> list[skb.State]:
        child_states = []
        reachables = g.reachable_squares(state.ares_normalized_position, state.stone_positions)
        for stone_id in range(len(state.stone_positions)):
            stone_pos = state.stone_positions[stone_id]
            for pushable in g.pushable_squares(reachables, stone_pos):
                if g.can_push(pushable, stone_pos, state):
                    new_stones = state.stone_positions.copy()
                    new_stones[stone_id] = g.push(pushable, stone_pos, state)

                    new_reachables = g.reachable_squares(pushable, new_stones)
                    min_reachable = g.minreachable_square(new_reachables)
                    child_state = skb.State(min_reachable, new_stones)
                    g.draw_state(child_state, new_reachables)
                    child_states.append(child_state)

                    deadlock = g.get_deadlock(child_state, new_stones[stone_id])
                    if len(deadlock) > 0:
                        g.draw_state(child_state, deadlock)
                        print("Deadlock!")
                        continue
        return child_states

    def solve(self) -> str:
        initial_state = self.g.initial_state()
        initial_state_hash = self.g.get_hash(initial_state)
        
        frontier = [initial_state_hash]
        transposition_table = {initial_state_hash : initial_state}
        explored = []
        parents = {}

        found = False 
        processed_count = 0
        goal_state_hash = ""

        g = self.g
        while len(frontier) > 0:
            print("processed_count = ", processed_count)
            current_hash = frontier.pop(0)
            current = transposition_table[current_hash]
            explored.append(current_hash)

            for child in self.branch(g, current):
                child_hash = g.get_hash(child)
                if (child_hash not in explored) and (child_hash not in transposition_table):
                    transposition_table[child_hash] = child
                    parents[child_hash] = current_hash
                    
                    if g.is_solved(child):
                        found = True
                        goal_state_hash = child_hash
                        print("Done!")
                        break
                    frontier.append(child_hash)
            processed_count += 1
            if found:
                break
        if found:
            g.draw_state(transposition_table[goal_state_hash])
        return goal_state_hash
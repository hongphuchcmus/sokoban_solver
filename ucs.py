import sokoban_console_refactored as skb
import time as time
from heapq import heappush, heappop

class UCSSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.transposition_table = {}

    def branch(self, g : skb.Sokoban, state: skb.State) -> tuple[int, list[skb.State]]:
        child_states = []
        for direction in skb.DIRECTIONS:
            ares_new_position = (state.ares_position[skb.Y] + direction[skb.Y], state.ares_position[skb.X] + direction[skb.X])
            if g.matrix_at(ares_new_position) == skb.WALL:
                continue
            new_stones = state.stone_positions.copy()
            cost = 1
            encounter_stone = False
            pushed = False
            # Check if ares can push any stones
            for stone_id in range(len(state.stone_positions)):
                stone_pos = state.stone_positions[stone_id]
                if stone_pos == ares_new_position:
                    encounter_stone = True
                    if g.can_push(state.ares_position, stone_pos, state):
                        new_stones[stone_id] = (stone_pos[skb.Y] + direction[skb.Y], stone_pos[skb.X] + direction[skb.X])
                        cost = g.get_stone_weight(stone_id)
                        pushed = True
                    break
            if encounter_stone and not pushed:
                continue
            child_state = skb.State(ares_new_position, new_stones)
            child_states.append((cost, child_state))
        return child_states

    def trace(self, g : skb.Sokoban, state_path : list[skb.State]) -> str:
        path = []
        for i in range(len(state_path)-1):
            ares_current_position = state_path[i].ares_position
            ares_next_position = state_path[i+1].ares_position
            move_direction = (ares_next_position[skb.Y] - ares_current_position[skb.Y], ares_next_position[skb.X] - ares_current_position[skb.X])
            
            is_pushing = False
            for stone_pos in state_path[i].stone_positions:
                if stone_pos == ares_next_position:
                    path.append(g.map_move_direction(move_direction).upper())
                    is_pushing = True
                    break
            if not is_pushing:
                path.append(g.map_move_direction(move_direction))
        return path


    def solve(self) -> str:
        initial_state = skb.State(self.g.ares_initial_position, self.g.stones_initial_positions)
        initial_state_hash = self.g.get_hash(initial_state)
        
        frontier = [initial_state_hash]
        costs = {initial_state_hash : 0}
        transposition_table = {initial_state_hash : initial_state}
        explored = []
        parents = {initial_state_hash : None }

        found = False 
        processed_count = 0
        goal_state_hash = ""

        g = self.g
        while len(frontier) > 0:
            #print("processed_count = ", processed_count)
            frontier.sort(key=lambda x: costs[x])
            current_hash = frontier.pop(0)
            #print("Exploring state: ", current_hash, " cost: ", costs[current_hash])
            current = transposition_table[current_hash]
            explored.append(current_hash)
            for child_cost_and_state in self.branch(g, current):
                cost, child = child_cost_and_state
                child_hash = g.get_hash(child)

                if (child_hash not in frontier) and (child_hash not in explored):
                    transposition_table[child_hash] = child
                    parents[child_hash] = current_hash
                    costs[child_hash] = costs[current_hash] + cost
                    if g.is_solved(child):
                        found = True
                        goal_state_hash = child_hash
                        print("Done!")
                        break
                    frontier.append(child_hash)
                elif (child_hash in frontier) and (costs[child_hash] > costs[current_hash] + cost):
                    parents[child_hash] = current_hash
                    costs[child_hash] = costs[current_hash] + cost

            processed_count += 1
            if found:
                break
        if not found:
            return ""
        
        # Tracing time!
        state_path = []
        backtracer = goal_state_hash
        while backtracer:
            state_path.append(transposition_table[backtracer])
            backtracer = parents[backtracer]
        state_path.reverse()
        path = self.trace(g, state_path)
        
        return "".join(path)

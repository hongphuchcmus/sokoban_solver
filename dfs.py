import sokoban_console_refactored as skb
import time as time

class DFSSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.transposition_table = {}

    # Since we are not saving ares exact position at each state
    # We have to use some kind of pathfinding to interpolate area path
    # moving between two states
    def bfs_transition_path(self, g : skb.Sokoban, from_position, to_position, stone_positions):
        frontier = [from_position]
        explored = []
        parents = {from_position : None}
        found = False
        while frontier:
            current = frontier.pop(0)
            explored.append(current)
            for neighbor in g.neighbors(current):
                if g.matrix_at(neighbor) != skb.WALL \
                    and (neighbor not in stone_positions) \
                        and (neighbor not in explored) \
                            and (neighbor not in frontier):
                    frontier.append(neighbor)
                    parents[neighbor] = current
                    if neighbor == to_position:
                        found = True
                        break
            if found:
                break
        path = []
        backtracer = to_position
        while backtracer:
            path.append(backtracer)
            backtracer = parents[backtracer]
        path.reverse()

        return path
    
    def trace(self, g : skb.Sokoban, state_path):
        navigation_path = []

        ares_last_position = g.ares_initial_position
        for i in range(len(state_path)-1):
            #print("Interpolating state ", i)
            current_state = state_path[i]
            next_state = state_path[i+1]
            
            interpolated = False
            # We must find the difference in stone postions
            # to determine where is ares's next position
            for j in range(len(current_state.stone_positions)):
                if current_state.stone_positions[j] != next_state.stone_positions[j]:
                    current_position = current_state.stone_positions[j]
                    new_position = next_state.stone_positions[j]
                    push_direction = (new_position[skb.Y] - current_position[skb.Y], new_position[skb.X] - current_position[skb.X])
                    # Where Ares should be to push the stone
                    push_position = (current_position[skb.Y] - push_direction[skb.Y], current_position[skb.X] - push_direction[skb.X])

                    # Move Ares to the push position
                    path = self.bfs_transition_path(g, ares_last_position, push_position, current_state.stone_positions)
                    for k in range(len(path)-1):
                        direction = (path[k+1][skb.Y] - path[k][skb.Y], path[k+1][skb.X] - path[k][skb.X])
                        navigation_path.append(g.map_move_direction(direction))
                    # Push the stone
                    navigation_path.append(g.map_move_direction(push_direction).upper())
                    # Ares is now at the stone old position
                    ares_last_position = current_position

                    interpolated = True
                    break
            if not interpolated:
                print("Some thing went wrong. We should always have a stone position change")
                return []
        return navigation_path

    def branch(self, g : skb.Sokoban, state: skb.State) -> list[skb.State]:
        child_states = []
        reachables = g.reachable_squares(state.ares_position, state.stone_positions)
        print("All stone positions = ", state.stone_positions)
        for stone_id in range(len(state.stone_positions)):
            stone_pos = state.stone_positions[stone_id]
            print("Stone pos = ", stone_pos)
            for pushable in g.pushable_squares(reachables, stone_pos, state):
                new_stones = state.stone_positions.copy()
                new_stones[stone_id] = g.push(pushable, stone_pos, state)

                new_reachables = g.reachable_squares(pushable, new_stones)
                min_reachable = g.minreachable_square(new_reachables)
                child_state = skb.State(min_reachable, new_stones)
                #g.draw_state(child_state, new_reachables)
                child_states.append(child_state)

                deadlock = g.get_deadlock(child_state, new_stones[stone_id])
                if len(deadlock) > 0:
                    #g.draw_state(child_state, deadlock)
                    #print("Deadlock!")
                    continue
        return child_states

    def solve(self) -> str:
        initial_state = self.g.initial_state()
        self.g.draw_input_matrix()
        initial_state_hash = self.g.get_hash(initial_state)
        
        frontier = [initial_state_hash]
        transposition_table = {initial_state_hash : initial_state}
        explored = []
        parents = {initial_state_hash : None }

        found = False 
        processed_count = 0
        goal_state_hash = ""

        g = self.g
        while len(frontier) > 0:
            print("processed_count = ", processed_count)
            current_hash = frontier.pop()
            current = transposition_table[current_hash]
            explored.append(current_hash)

            for child in self.branch(g, current):
                child_hash = g.get_hash(child)
                if (child_hash not in explored) and (child_hash not in explored):
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

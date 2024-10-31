import sokoban_console_refactored as skb
import time as time

class BFSSolver:

    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.frontier = []
        self.explored = set()
        self.transposition_table = {}
        self.parents = {}
        self.MIN_REACHABLE = 0
        self.REACHABLE_POSITIONS = 1
        self.REACHABLE_STONES_NEIGHBORS = 2
        self.MAX = 1000

    def minreachable_square(self, g : skb.Sokoban, reachable_squares):
        min_square = reachable_squares[0]
        for i in range(1, len(reachable_squares)):
            if min_square[skb.Y] * g.cols + min_square[skb.X] > reachable_squares[i][skb.Y] * g.cols + reachable_squares[i][skb.X]:
                min_square = reachable_squares[i]
        return min_square

    def reachable_squares(self, g : skb.Sokoban, ares_position , stone_positions ):
        # A simple DFS to find reachable squares
        frontier = [ares_position]
        explored = []
        while frontier:
            child = frontier.pop()
            explored.append(child)
            for neighbor in g.neighbors(child):
                if g.matrix_at(neighbor) != skb.WALL \
                    and (neighbor not in stone_positions) \
                        and (neighbor not in explored) \
                            and (neighbor not in frontier):
                    frontier.append(neighbor)
        return explored
    
    def pushable_squares(self, g : skb.Sokoban, reachables, stone_position, state : skb.Sokoban ):
        pushables = []
        for neighbor in g.neighbors(stone_position):
            if neighbor in reachables and g.can_push(neighbor, stone_position, state):
                pushables.append(neighbor)
        return pushables


    # Since we are not saving ares exact position at each state
    # We have to use some kind of pathfinding to interpolate the path
    # between two states
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
        if not found:
            return []
        
        path = []
        backtracer = to_position
        while backtracer:
            path.append(backtracer)
            backtracer = parents[backtracer]
        path.reverse()

        return path
    
    def trace(self, g : skb.Sokoban, state_hash_path):
        navigation_path = []

        ares_last_position = g.initial_ares_position
        for i in range(len(state_hash_path)-1):
            #print("Interpolating state ", i)
            current_state = self.transposition_table[state_hash_path[i]]
            next_state = self.transposition_table[state_hash_path[i+1]]
            
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
        
        reachables = self.reachable_squares(g, state.ares_position, state.stone_positions)
        # Loop through all the reachable squares, find push positions (positions where Ares can push a stone)
        # Each push action create a child state
        for stone_id in range(len(state.stone_positions)):
            stone_current_position = state.stone_positions[stone_id]
            for push_position in self.pushable_squares(g, reachables, stone_current_position, state):
                if not g.is_neighbor(push_position, stone_current_position) \
                    or not g.can_push(push_position, stone_current_position, state):
                    continue
                
                stone_new_position = g.push(push_position, stone_current_position, state)
                
                # Create a new state
                new_stone_positions = state.stone_positions.copy()
                new_stone_positions[stone_id] = stone_new_position

                new_reachables = self.reachable_squares(g, stone_current_position, new_stone_positions)
                new_min_reachable = self.minreachable_square(g, new_reachables)

                child_state = skb.State(new_min_reachable, new_stone_positions)
                #g.draw_state(child_state)

                deadlock = g.get_deadlock(child_state, stone_new_position)
                if len(deadlock) > 0:
                    #g.draw_state(child_state, deadlock)
                    #print("Deadlock!")
                    continue
                #child_hash_test = child_state.get_hash()
                # if child_hash_test == "-1063920407664356272":
                #     g.draw_state(child_state, new_reachables)
                #     input(f"Pausing at {child_hash_test}")
                #g.draw_state(child_state)
                #input("-")
                #print(child_hash_test)
                child_states.append(child_state)

        return child_states

    def initial_state(self, g : skb.Sokoban) -> skb.State:
        reachables = self.reachable_squares(g, g.initial_ares_position, g.initial_stone_positions)
        min_reachable = self.minreachable_square(g, reachables)
        return skb.State(min_reachable, g.initial_stone_positions)
    
    def solve(self) -> str:
        g = self.g

        initial_state = self.initial_state(g)
        initial_state_hash = initial_state.get_hash()
        
        self.frontier = [initial_state_hash]
        self.transposition_table = {initial_state_hash : initial_state}
        self.explored.clear()
        self.parents = {initial_state_hash : None }

        found = False 
        goal_state_hash = ""

        # processed_count = 0

        while len(self.frontier) > 0:
            # print("processed_count = ", processed_count)
            current_hash = self.frontier.pop(0)
            current = self.transposition_table[current_hash]
            self.explored.add(current_hash)

            for child in self.branch(g, current):
                child_hash = g.get_hash(child)
                if (child_hash not in self.frontier) and (child_hash not in self.explored):
                    self.transposition_table[child_hash] = child
                    self.parents[child_hash] = current_hash
                    if g.is_solved(child):
                        found = True
                        goal_state_hash = child_hash
                        print("Done!")
                        break
                    self.frontier.append(child_hash)
            # processed_count += 1
            if found:
                break
        if not found:
            ""
        
        # Backtracking to contruct the path
        state_path = []
        backtracer = goal_state_hash
        while backtracer:
            state_path.append(backtracer)
            g.draw_state(self.transposition_table[backtracer])
            backtracer = self.parents[backtracer]
        state_path.reverse()
        # Call trace() to return every movement of  
        path = self.trace(g, state_path)
        return "".join(path)

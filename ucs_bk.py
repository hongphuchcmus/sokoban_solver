import sokoban_console_refactored as skb
import time as time

class UCSSolver:
    def __init__(self, g: skb.Sokoban, use_ares_steps = False):
        self.g = g
        self.frontier = []
        self.costs = {}
        self.parents = {}
        self.explored = set()
        self.transposition_table = {}
        self.use_ares_steps = use_ares_steps

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

    def minreachable_square(self, g : skb.Sokoban, reachable_squares):
        min_square = reachable_squares[0]
        for i in range(1, len(reachable_squares)):
            if min_square[skb.Y] * g.cols + min_square[skb.X] > reachable_squares[i][skb.Y] * g.cols + reachable_squares[i][skb.X]:
                min_square = reachable_squares[i]
        return min_square

    # This can be used to get all the reachable squares from a given position as well,
    # via costs.keys(). Sorry for the fact that this function is multi-purpose
    # (it's to avoid code duplication)
    def costs_to_reachable_square(self, g : skb.Sokoban, ares_position, stone_positions):
        # Use a quick UCS to find the smalledt costs to all reachables squares
        frontier = [ares_position]
        explored = []
        costs = { ares_position : 0 }
        while frontier:
            child = frontier.pop(0)
            explored.append(child)
            for neighbor in g.neighbors(child):
                if g.matrix_at(neighbor) == skb.WALL \
                    or neighbor in stone_positions:
                    continue
                if (neighbor not in explored) \
                            and (neighbor not in frontier):
                    frontier.append(neighbor)
                    costs[neighbor] = costs[child] + 1
        return costs

    def branch(self, g : skb.Sokoban, state_hash) -> tuple[int, list[skb.State]]:
        child_states = []
        state = self.transposition_table[state_hash]
        
        # Use ares normalized position
        if not self.use_ares_steps:
            
            ares_exact_position = (0, 0)
            # It's required that we know the exact position of ares for the 
            # costs_to_reachable_square() to work as expected
            if self.parents[state_hash] is not None:
                parent_state = self.transposition_table[self.parents[state_hash]]
                # We can guess where
                # ares is by looking at the movent of the stones
                # Aside from some bugs or errors, ares_exact_position should always be determined after this loop
                for stone_id in range(len(state.stone_positions)):
                    if parent_state.stone_positions[stone_id] != state.stone_positions[stone_id]:
                        ares_exact_position = parent_state.stone_positions[stone_id]
                        break
            else:
                ares_exact_position = g.initial_ares_position

            costs_to_reachables = self.costs_to_reachable_square(g, ares_exact_position, state.stone_positions)
            for push_position in costs_to_reachables:
                for stone_id in range(len(state.stone_positions)):
                    stone_current_position = state.stone_positions[stone_id]
                    if not g.is_neighbor(push_position, stone_current_position) \
                        or not g.can_push(push_position, stone_current_position, state):
                        continue

                    stone_new_position = g.push(push_position, stone_current_position, state)
                    
                    # Create a new state
                    new_stone_positions = state.stone_positions.copy()
                    new_stone_positions[stone_id] = stone_new_position

                    new_reachables = list(self.costs_to_reachable_square(g, stone_current_position, new_stone_positions).keys())
                    new_min_reachable = self.minreachable_square(g, new_reachables)

                    child_state = skb.State(new_min_reachable, new_stone_positions)
                    #g.draw_state(child_state)

                    deadlock = g.get_deadlock(child_state, stone_new_position)
                    if len(deadlock) > 0:
                        #g.draw_state(child_state, deadlock)
                        #print("Deadlock!")
                        continue

                    # Calculate the weight of transition
                    # First, identify the weight of the stone
                    stone_weight = g.get_stone_weight(stone_id)
                    # Second, the smallest cost to reach the push position
                    moving_cost = costs_to_reachables[push_position]
                    # Combine the two to get the total weight
                    weight = stone_weight + moving_cost

                    child_states.append((weight, child_state))
                    
                    if child_state.get_hash() == "-6523971831761971067":
                        print("parent = ", state_hash)
                        input("Found the defect!")
                        # if child_state.get_hash() == "7774435512059431117":
        else: # Step by step
            for direction in skb.DIRECTIONS:
                
                ares_new_position = (state.ares_position[skb.Y] + direction[skb.Y], state.ares_position[skb.X] + direction[skb.X])
                if g.matrix_at(ares_new_position) == skb.WALL:
                    continue
                
                new_stones = state.stone_positions.copy()
                weight = 1
                encountered_stone = False
                pushed = False

                # Check if ares can push any stones
                for stone_id in range(len(state.stone_positions)):
                    stone_pos = state.stone_positions[stone_id]
                    if stone_pos == ares_new_position:
                        encountered_stone = True
                        if g.can_push(state.ares_position, stone_pos, state):
                            new_stones[stone_id] = (stone_pos[skb.Y] + direction[skb.Y], stone_pos[skb.X] + direction[skb.X])
                            weight = g.get_stone_weight(stone_id)
                            pushed = True
                        break
                if encountered_stone and not pushed:
                    continue

                child_state = skb.State(ares_new_position, new_stones)
                child_states.append((weight, child_state))
                

        return child_states

    def trace_steps(self, g : skb.Sokoban, state_hash_path : list[skb.State]) -> str:
        path = []
        for i in range(len(state_hash_path)-1):
            current_state = self.transposition_table[state_hash_path[i]]
            next_state = self.transposition_table[state_hash_path[i+1]]

            ares_current_position = current_state.ares_position
            ares_next_position = next_state.ares_position

            move_direction = (ares_next_position[skb.Y] - ares_current_position[skb.Y], ares_next_position[skb.X] - ares_current_position[skb.X])
            
            is_pushing = False
            for stone_pos in current_state.stone_positions:
                if stone_pos == ares_next_position:
                    path.append(g.map_move_direction(move_direction).upper())
                    is_pushing = True
                    break
            if not is_pushing:
                path.append(g.map_move_direction(move_direction))
        return path
    
    def initial_state(self, g : skb.Sokoban) -> skb.State:
        if self.use_ares_steps:
            return skb.State(g.initial_ares_position, g.initial_stone_positions)
        else:
            reachables = list(self.costs_to_reachable_square(g, g.initial_ares_position, g.initial_stone_positions).keys())
            min_reachable = self.minreachable_square(g, reachables)
            return skb.State(min_reachable, g.initial_stone_positions)

    def solve(self) -> str:
        g = self.g

        initial_state = self.initial_state(g)
        initial_state_hash = initial_state.get_hash()
        
        self.frontier = [initial_state_hash]
        self.costs = {initial_state_hash : 0}
        self.transposition_table = {initial_state_hash : initial_state}
        self.explored.clear()
        self.parents = {initial_state_hash : None }

        found = False 
        processed_count = 0
        goal_state_hash = ""

        while len(self.frontier) > 0:
            print("processed_count = ", processed_count)
            # Priority queue base on path costs
            #self.frontier.sort(key=lambda x: self.costs[x])
            
            self.frontier.sort(key=lambda x: self.costs[x])
            current_hash = self.frontier.pop(0)
            current = self.transposition_table[current_hash]
            print("Exploring state: ", current_hash)
            if current_hash == "7774435512059431117":
                # print("cost of this: ", self.costs[current_hash])
                # self.frontier.sort(key=lambda x: self.costs[x])
                # print("frontier: ")
                # for f in self.frontier:
                #     print("hash = ", f, " c = ", self.costs[f], "; ")
                #     g.draw_state(self.transposition_table[f])
                print("Debugging ... ")
                g.draw_state(current)
                backtracker = self.frontier[0]
                while backtracker:
                    print(f"d- hash = {backtracker}, c = {self.costs[backtracker]}")
                    g.draw_state(self.transposition_table[backtracker])
                    backtracker = self.parents[backtracker]
                input("Paused")

            
            if g.is_solved(current):
                found = True
                goal_state_hash = current_hash
                print("Done!")
                break

            self.explored.add(current_hash)
            
            print("branching", "-"*40)
            branching = []
            for weight, child in self.branch(g, current_hash):
                child_hash = child.get_hash()
                

                if (child_hash not in self.frontier) and (child_hash not in self.transposition_table):
                    
                    self.transposition_table[child_hash] = child
                    self.parents[child_hash] = current_hash
                    self.costs[child_hash] = self.costs[current_hash] + weight

                    self.frontier.append(child_hash)
                    branching.append(child_hash)

                # elif (child_hash in self.frontier) and (self.costs[child_hash] > self.costs[current_hash] + weight):
                #     self.parents[child_hash] = current_hash
                #     self.costs[child_hash] = self.costs[current_hash] + weight
            
            for child_hash in branching:
                print("hash = ", child_hash)
                print("cost = ", self.costs[child_hash])
                g.draw_state(self.transposition_table[child_hash])

            processed_count += 1
        
        if not found:
            return ""
        
        print("Total cost: ", self.costs[goal_state_hash])

        # Tracing time!
        state_hash_path = []
        backtracer = goal_state_hash
        while backtracer is not None:
            print("hash = ", backtracer)
            g.draw_state(self.transposition_table[backtracer])
            state_hash_path.append(backtracer)
            backtracer = self.parents[backtracer]
        state_hash_path.reverse()
        input("---")
        
        if self.use_ares_steps:
            path = self.trace_steps(g, state_hash_path)
        else:
            path = self.trace(g, state_hash_path)
        
        return "".join(path)

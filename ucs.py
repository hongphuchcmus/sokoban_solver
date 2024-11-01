import sokoban_console_refactored as skb
import time as time

class UCSSolver:
    def __init__(self, g: skb.Sokoban):
        self.g = g
        self.frontier = []
        self.costs = {}
        self.parents = {}
        self.explored = set()
        self.transposition_table = {}

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
    
    def trace(self, g : skb.Sokoban, state_hash_path : list[skb.State]) -> str:
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
    
    def initial_state(self, g : skb.Sokoban) -> skb.State:
        return skb.State(g.initial_ares_position, g.initial_stone_positions)
        
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
            
            if g.is_solved(current):
                found = True
                goal_state_hash = current_hash
                print("Done!")
                break

            self.explored.add(current_hash)
            
            branching = []
            for weight, child in self.branch(g, current_hash):
                child_hash = child.get_hash()
                

                if (child_hash not in self.frontier) and (child_hash not in self.transposition_table):
                    
                    self.transposition_table[child_hash] = child
                    self.parents[child_hash] = current_hash
                    self.costs[child_hash] = self.costs[current_hash] + weight

                    self.frontier.append(child_hash)
                    branching.append(child_hash)

                elif (child_hash in self.frontier) and (self.costs[child_hash] > self.costs[current_hash] + weight):
                    self.parents[child_hash] = current_hash
                    self.costs[child_hash] = self.costs[current_hash] + weight
            
            processed_count += 1
        
        if not found:
            return ""
        
        print("Total cost: ", self.costs[goal_state_hash])

        # Tracing time!
        state_hash_path = []
        backtracer = goal_state_hash
        while backtracer is not None:
            state_hash_path.append(backtracer)
            backtracer = self.parents[backtracer]
        state_hash_path.reverse()
        print(state_hash_path)
        
        path = self.trace(g, state_hash_path)
        
        return "".join(path)

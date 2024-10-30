#Using classes to refactor the Sokuban game
import time as time
from colorama import Fore, Back, Style

ARES = "@"
WALL = "#"
SPACE = " "
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

Y = 0
X = 1

class State:
    def __init__(self, ares_position , stone_positions ):
        self.ares_position = ares_position
        self.stone_positions = stone_positions

class Sokoban:
    def __init__(self, input : str) -> None:
        self.input_matrix = []
        with open("input.txt", "r") as file_in:
            lines = file_in.read().splitlines()
            for line in lines:
                self.input_matrix.append(line)
        # Preprocess
        # TODO: Fill in missing spaces to make the input square
        # Righ now, just assume that is the case
        self.ares_initial_position = self.init_ares_position()
        self.stones_initial_positions = self.init_stone_positions()
        # Since stones and player are dynamic, it's better to store them in separate lists
        # The working matrix should only contain static objects
        self.matrix = self.get_static_matrix()
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0]) 

        # Init deadlocks
        self.deadlock_patterns = self.get_deadlock_patterns()
    
    def draw_input_matrix(self, highlights  = [], console_output = True):
        matrix_string = []
        for i, row in enumerate(self.input_matrix):
            for j, col in enumerate(row):
                if console_output and (i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")
                print(col, end="")
                print(Style.RESET_ALL, end="")
                if not console_output:
                    matrix_string.append(col)
            if console_output:
                print()
            else:
                matrix_string.append("\n")
        return "".join(matrix_string)

    def draw_matrix(self, highlights  = [], console_output = True):
        matrix_string = []
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if console_output and (i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")
                print(col, end="")
                print(Style.RESET_ALL, end="")
                if not console_output:
                    matrix_string.append(col)
            if console_output:
                print()
            else:
                matrix_string.append("\n")
        return "".join(matrix_string)

    def draw_state(self, state : State, highlights  = [], console_output = True):
        matrix_string = []
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if console_output and (i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")
                char = ""
                if (i, j) == state.ares_position:
                    if self.matrix_at((i, j)) == SWITCH:
                        char = ARES_ON_SWITCH
                    else:
                        char = ARES
                elif (i, j) in state.stone_positions:
                    if self.matrix_at((i, j)) == SWITCH:
                        char = STONE_ON_SWITCH
                    else:
                        char = STONE
                else:
                    char = col
                if console_output:
                    print(char, end="")
                    print(Style.RESET_ALL, end="")
                else:
                    matrix_string.append(char)
            if console_output:
                print()
            else:
                matrix_string.append("\n")
        return "".join(matrix_string)

    # Get what static object is at pos
    def matrix_at(self, pos ) -> str:
        return self.matrix[pos[Y]][pos[X]] # Remember y for height/row and x for width/column

    def stone_weight(self, stone_id : int) -> int:
        return 1

    # Check for deadlock patterns around the pushed_stone
    # Return the area that matched the deadlock pattern
    def get_deadlock(self, state : State, pushed_stone ):
        # We extract the area of the puzzle that we are going to check
        # Now assume that we only check for 2x2 deadlock patterns
        # That mean in the puzzle we should check a 3x3 area
        # The stone should be in the middle of the area
        check_square = [\
            (pushed_stone[Y] -1, pushed_stone[X] - 1),
            (pushed_stone[Y] - 1, pushed_stone[X]),
            (pushed_stone[Y] -1, pushed_stone[X] + 1),
            (pushed_stone[Y], pushed_stone[X]-1),
            (pushed_stone[Y], pushed_stone[X]),
            (pushed_stone[Y], pushed_stone[X]+1),
            (pushed_stone[Y]+1, pushed_stone[X]-1),
            (pushed_stone[Y]+1, pushed_stone[X]),
            (pushed_stone[Y]+1, pushed_stone[X]+1)]
        # We should have 4 different area to check for 2x2 patterns 
        check_areas = [\
            [check_square[0], check_square[1], check_square[3], check_square[4]],
            [check_square[1], check_square[2], check_square[4], check_square[5]],
            [check_square[3], check_square[4], check_square[6], check_square[7]],
            [check_square[4], check_square[5], check_square[7], check_square[8]]]

        for pattern in self.deadlock_patterns:
            height = len(pattern)
            width = len(pattern[0])
            # For now, let's just check for 2x2 deadlock patterns
            if height != 2 or width != 2:
                continue
            for check_area in check_areas:
                matched_count = 0
                area_out_of_bound = False
                for i in range(4):
                    check_position = check_area[i]
                    if check_position[Y] < 0 or check_position[Y] >= self.rows or check_position[X] < 0 or check_position[X] >= self.cols:
                        area_out_of_bound = True
                        break
                    what_is_here = ""
                    if check_position in state.stone_positions: # state[1] is stone positions
                        # A stone can be deadlock but if it reached the goal, we shouldn't care
                        if self.matrix_at(check_position) == SWITCH:
                            what_is_here = WALL
                        else:
                            what_is_here = STONE
                    elif self.matrix_at(check_position) == WALL:
                        what_is_here = WALL
                    else:
                        what_is_here = SPACE
                    if what_is_here == pattern[i//2][i%2]:
                        matched_count += 1
                if area_out_of_bound:
                    continue
                if matched_count == 4:
                    return check_area
        return []

    # Init deadlocks
    # Ex: A deadlock: ["#$", "#$"]
    def get_deadlock_patterns(self):
        def flip_pattern(pattern, width, height):
            flipped_pattern = []
            for i in range(height):
                flipped_pattern.append([" "]*width)

            # Flip the pattern vertically
            for i in range(height):
                for j in range(width):
                    flipped_pattern[i][j] = pattern[i][width-j-1]
            for i in range(len(flipped_pattern)):
                flipped_pattern[i] = "".join(flipped_pattern[i])

            flipped_pattern = tuple(flipped_pattern)

            return flipped_pattern
        def rotate_pattern_counter_lockwise(pattern, width, height):
            rotated_pattern = []
            # Rotate 90 degrees counter clockwise
            for j in range(width-1, -1, -1):
                row = []
                for i in range(height):
                    row.append(pattern[i][j])
                row = "".join(row)
                rotated_pattern.append(row)
            
            rotated_pattern = tuple(rotated_pattern)
            
            return rotated_pattern

        patterns = {}
        with open("deadlocks.txt", "r") as file_in:
            for line in file_in:
                if line == "\n":
                    break
                info = line.strip("\n")
                stone_count, height, width = map(int, info.split(" ", 2))

                pattern = []
                for i in range(height):
                    pattern.append(file_in.readline()[0:-1])
                pattern = tuple(pattern)
                pattern_hash = hash(pattern)

                if pattern_hash in patterns:
                    print("Duplicate pattern found!")
                    continue
                patterns[str(hash(pattern))] = pattern
                
                for flip in [True, False]:
                    alt_pattern = pattern
                    if flip:
                        alt_pattern = flip_pattern(alt_pattern, width, height)
                    current_width = width
                    current_height = height
                    for i in range(4):
                        alt_pattern = rotate_pattern_counter_lockwise(alt_pattern, current_width, current_height)
                        current_width, current_height = current_height, current_width
                        alt_pattern_hash = hash(alt_pattern)
                        if alt_pattern_hash in patterns:
                            print("Duplicate pattern found!")
                            continue
                        patterns[str(hash(alt_pattern))] = alt_pattern
            return list(patterns.values())

    # Only run once on init
    def init_ares_position(self):
        for i in range(len(self.input_matrix)):
            for j in range(len(self.input_matrix[i])):
                if self.input_matrix[i][j] in [ARES, ARES_ON_SWITCH]:
                    return (i, j)
        return (0, 0)
    # Only run once on init
    def init_stone_positions(self):
        stone_positions = []
        for i in range(len(self.input_matrix)):
            for j in range(len(self.input_matrix[i])):
                if self.input_matrix[i][j] in [STONE, STONE_ON_SWITCH]:
                    stone_positions.append((i, j))
        return stone_positions

    # Simpliy working matrix with static objects, i.g walls, switches
    def get_static_matrix(self):
        static_matrix = []
        for i in range(len(self.input_matrix)):
            row = []
            for j in range(len(self.input_matrix[i])):
                if self.input_matrix[i][j] in [ARES, STONE]:
                    row.append(SPACE)
                elif self.input_matrix[i][j] in [ARES_ON_SWITCH, STONE_ON_SWITCH]:
                    row.append(SWITCH)
                else:
                    row.append(self.input_matrix[i][j])
            static_matrix.append("".join(row))
        return static_matrix

    def initial_state(self):
        reachables =  self.reachable_squares(self.ares_initial_position, self.stones_initial_positions)
        min_reachable = self.minreachable_square(reachables)
        return State(min_reachable, self.stones_initial_positions)

    def is_solved(self, state : State):
        for stone_position in state.stone_positions:
            if self.matrix_at(stone_position) != SWITCH:
                return False
        return True
    
    def pushable_squares(self, reachable_squares , stone_position, state : State):
        pushables = []
        for neighbor in self.neighbors(stone_position):
            if neighbor in reachable_squares and self.can_push(neighbor, stone_position, state):
                pushables.append(neighbor)
        return pushables

    def neighbors(self, position ):
        y = position[Y]
        x = position[X]
        return [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]

    def minreachable_square(self, reachable_squares):
        min_square = reachable_squares[0]
        for i in range(1, len(reachable_squares)):
            if min_square[Y] * self.cols + min_square[X] > reachable_squares[i][Y] * self.cols + reachable_squares[i][X]:
                min_square = reachable_squares[i]
        return min_square

    def reachable_squares(self, ares_postion , stone_positions ):
        # A simple DFS to find reachable squares
        frontier = [ares_postion]
        explored = []
        while frontier:
            child = frontier.pop()
            explored.append(child)
            for neighbor in self.neighbors(child):
                if self.matrix_at(neighbor) != WALL \
                    and (neighbor not in stone_positions) \
                        and (neighbor not in explored) \
                            and (neighbor not in frontier):
                    frontier.append(neighbor)
        return explored

    def can_push(self, ares_position , stone_position , state:State):
        y_translation = stone_position[Y] - ares_position[Y]
        x_translation = stone_position[X] - ares_position[X]
        new_position = (stone_position[Y] + y_translation, stone_position[X] + x_translation)
        if self.matrix_at(new_position) != WALL and (new_position not in state.stone_positions):
            return True
        return False

    def push(self, ares_position, stone_position, state:State):
        y_translation = stone_position[Y] - ares_position[Y]
        x_translation = stone_position[X] - ares_position[X]
        new_position = (stone_position[Y] + y_translation, stone_position[X] + x_translation)
        return new_position

    def get_hash(self, state : State) -> str:
        ares_y = state.ares_position[Y]
        ares_x = state.ares_position[X]
        to_hash = [(ares_y, ares_x)]
        stone_positions = []
        for sp in state.stone_positions:
            stone_y = sp[Y]
            stone_x = sp[X]
            stone_positions.append((stone_y, stone_x))
        stone_positions = tuple(stone_positions)
        to_hash.append(stone_positions)
        to_hash = tuple(to_hash)
        return str(hash(to_hash))

    def map_move_direction(self, direction):
        if direction[1] == 1 and direction[0] == 0:
            return "r"
        elif direction[1] == -1 and direction[0] == 0:
            return "l"
        elif direction[1] == 0 and direction[0] == 1:
            return "d"
        elif direction[1] == 0 and direction[0] == -1:
            return "u"
        return "?"
    
    # Since we are not saving ares exact position at each state
    # We have to use some kind of pathfinding to interpolate area path
    # moving between two states
    def bfs_transition_path(self, from_position, to_position, stone_positions):
        frontier = [from_position]
        explored = []
        parents = {from_position : None}
        found = False
        while frontier:
            current = frontier.pop(0)
            explored.append(current)
            for neighbor in self.neighbors(current):
                if self.matrix_at(neighbor) != WALL \
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
    
    # Let's make the game traces the path for us
    def trace(self, state_path):
        navigation_path = []

        ares_last_position = self.ares_initial_position
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
                    push_direction = (new_position[Y] - current_position[Y], new_position[X] - current_position[X])
                    # Where Ares should be to push the stone
                    push_position = (current_position[Y] - push_direction[Y], current_position[X] - push_direction[X])

                    # Move Ares to the push position
                    path = self.bfs_transition_path(ares_last_position, push_position, current_state.stone_positions)
                    for k in range(len(path)-1):
                        direction = (path[k+1][Y] - path[k][Y], path[k+1][X] - path[k][X])
                        navigation_path.append(self.map_move_direction(direction))
                    # Push the stone
                    navigation_path.append(self.map_move_direction(push_direction).upper())
                    # Ares is now at the stone old position
                    ares_last_position = current_position

                    interpolated = True
                    break
            if not interpolated:
                print("Some thing went wrong. We should always have a stone position change")
                return []
        return navigation_path        
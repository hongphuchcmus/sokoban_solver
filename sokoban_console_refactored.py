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

DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

class State:
    def __init__(self, ares_position , stone_positions ):
        self.ares_position = ares_position
        self.stone_positions = stone_positions
    
    def get_hash(self) -> str:
        ares_y = self.ares_position[Y]
        ares_x = self.ares_position[X]
        to_hash = [(ares_y, ares_x)]
        stone_positions = []
        for sp in self.stone_positions:
            stone_y = sp[Y]
            stone_x = sp[X]
            stone_positions.append((stone_y, stone_x))
        stone_positions = tuple(stone_positions)
        to_hash.append(stone_positions)
        to_hash = tuple(to_hash)
        return str(hash(to_hash))

class Sokoban:
    def __init__(self, input : str) -> None:
        self.input_matrix = []
        self.stone_weights = []
        with open("input.txt", "r") as file_in:
            # The first line holds the weights of our stones
            lines = file_in.read().splitlines()
            self.stone_weights = list(map(int, lines[0].strip().split(" ")))
            for i in range(1, len(lines)):
                self.input_matrix.append(lines[i])

        # Preprocess
        # TODO: Fill in missing spaces to make the input square
        # Righ now, just assume that is the case
        self.initial_ares_position = self.init_ares_position()
        self.initial_stone_positions = self.init_stone_positions()
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
    def matrix_at(self, pos) -> str:
        return self.matrix[pos[Y]][pos[X]] # Remember y for height/row and x for width/column

    def get_stone_weight(self, stone_id : int) -> int:
        return self.stone_weights[stone_id]

    def get_switches(self):
        switches = []
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if self.matrix[i][j] == SWITCH:
                    switches.append((i, j))
        return switches
    
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
    # This used to be a more advance system,
    # allowing the check for predefined deadlock pattern 
    # from all directions
    # The deadlocks used in the get_deadlock()
    # now only checks for 2x2 pattern
    # for performance reasons
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

    # Simplify the working matrix with static objects, i.g walls, switches and spaces
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

    # Deprecated: It's upto the solver to init the first state
    def initial_state(self):
        reachables =  self.reachable_squares(self.initial_ares_position, self.initial_stone_positions)
        min_reachable = self.minreachable_square(reachables)
        return State(min_reachable, self.initial_stone_positions)
    
    # Are all stones at the switches?
    def is_solved(self, state : State):
        for stone_position in state.stone_positions:
            if self.matrix_at(stone_position) != SWITCH:
                return False
        return True
    
    # Deprecated. Return the squares at which ares can go there and push a stone
    def pushable_squares(self, reachable_squares , stone_position, state : State):
        pushables = []
        for neighbor in self.neighbors(stone_position):
            if neighbor in reachable_squares and self.can_push(neighbor, stone_position, state):
                pushables.append(neighbor)
        return pushables

    # Return the neighbors of "position" in 4 directions
    def neighbors(self, position ):
        y = position[Y]
        x = position[X]
        return [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]

    def is_neighbor(self, neighbor, position):
        if abs(neighbor[Y] - position[Y]) > 1 or abs(neighbor[X] - position[X] > 1):
            return False

        for d in DIRECTIONS:
            if position[Y] + d[Y] == neighbor[Y] and position[X] + d[X] == neighbor[X]:
                return True
        return False

    # Deprecated. Return the reachable square with the smallest index 
    def minreachable_square(self, reachable_squares):
        min_square = reachable_squares[0]
        for i in range(1, len(reachable_squares)):
            if min_square[Y] * self.cols + min_square[X] > reachable_squares[i][Y] * self.cols + reachable_squares[i][X]:
                min_square = reachable_squares[i]
        return min_square

    # Deprecated. Return all the reachable square from "ares_position"
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

    # Can ares push a stone at "stone_position" from "ares_position"
    def can_push(self, ares_position , stone_position , state:State):
        y_translation = stone_position[Y] - ares_position[Y]
        x_translation = stone_position[X] - ares_position[X]
        new_position = (stone_position[Y] + y_translation, stone_position[X] + x_translation)
       
        if self.matrix_at(new_position) != WALL and (new_position not in state.stone_positions):
            return True
        return False
    
    # Deprecated. Can ares move in the particular direction
    def can_move(self, ares_position, direction, state : State):
        new_position = (ares_position[Y] + direction[Y], ares_position[X] + direction[X])
        if self.matrix_at(new_position) != WALL and (new_position not in state.stone_positions):
            return True
        return False

    # Return the stone position after pushing from "ares_position"
    def push(self, ares_position, stone_position, state:State):
        y_translation = stone_position[Y] - ares_position[Y]
        x_translation = stone_position[X] - ares_position[X]
        new_position = (stone_position[Y] + y_translation, stone_position[X] + x_translation)
        return new_position

    # Deprecated: The State class should handle the hash itself.
    # Return the hash for a state, using this to check if a state 
    # was already discovered
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

    # Return a corresponding letter for a direction
    def map_move_direction(self, direction):
        if direction == (0, 1):
            return "r"
        elif direction == (0, -1):
            return "l"
        elif direction == (1, 0):
            return "d"
        elif direction == (-1, 0):
            return "u"
        return "?"
    
    # Return a corresponding direction for a letter
    # This is the inversed version of map_move_direction()
    def map_move_letter(self, letter):
        letter = letter.lower()
        if letter == "r":
            return (0, 1)
        elif letter == "l":
            return (0, -1)
        elif letter == "d":
            return (1, 0)
        elif letter == "u":
            return (-1, 0)
    
    # With the specified path, run and print (or return) the result
    # of the matrix for each action  
    def run(self, path, console_output = True) -> list[str]:
        result = []
        ares_last_position = self.initial_ares_position
        stone_positions = self.initial_stone_positions.copy()
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
            ares_new_position = (ares_last_position[Y] + ares_direction[Y], ares_last_position[X] + ares_direction[X])
            if ares_movement.upper() == path[i]:
                # Push the stone
                for i in range(len(stone_positions)):
                    if stone_positions[i] == ares_new_position:
                        stone_positions[i] = (ares_new_position[Y] + ares_direction[Y], ares_new_position[X] + ares_direction[X])
                        break
            ares_last_position = ares_new_position
            visual_state = State(ares_last_position, stone_positions)
            result.append(self.draw_state(visual_state, [], console_output))
        return result
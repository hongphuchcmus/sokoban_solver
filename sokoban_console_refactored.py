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


class Position:
    def __init__(self, y, x) -> None:
        self._y = y
        self._x = x
    # y, x are readonly
    @property
    def y(self):
        return self._y
    @property
    def x(self):
        return self._x
    def __repr__(self) -> str:
        return f"({self._y}, {self._x})"
    def __str__(self) -> str:
        return f"({self._y}, {self._x})"

    # Needed for quick "position in positions" check
    def __eq__(self, value: object) -> bool:
        return self._y == value.y and self._x == value.x

class State:
    def __init__(self, ares_normalized_position : Position, stone_positions : list[Position]):
        self.ares_normalized_position = ares_normalized_position
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
        self.stone_positions = self.init_stone_positions()
        # Since stones and player are dynamic, it's better to store them in separate lists
        # The working matrix should only contain static objects
        self.matrix = self.get_static_matrix()
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0]) 

        # Init deadlocks
        self.deadlock_patterns = self.get_deadlock_patterns()
    
    def draw_input_matrix(self, highlights : list[Position] = []):
        for i, row in enumerate(self.input_matrix):
            for j, col in enumerate(row):
                if Position(i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")
                print(col, end="")
                print(Style.RESET_ALL, end="")
            print()

    def draw_matrix(self, highlights : list[Position] = []):
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if Position(i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")
                print(col, end="")
                print(Style.RESET_ALL, end="")
            print()

    def draw_state(self, state : State, highlights : list[Position] = []):
        for i, row in enumerate(self.matrix):
            for j, col in enumerate(row):
                if Position(i, j) in highlights:
                    print(Fore.CYAN + Back.WHITE, end="")

                if Position(i, j) == state.ares_normalized_position:
                    if self.matrix_at(Position(i, j)) == SWITCH:
                        print(ARES_ON_SWITCH, end="")
                    else:
                        print(ARES, end="")
                elif Position(i, j) in state.stone_positions:
                    if self.matrix_at(Position(i, j)) == SWITCH:
                        print(STONE_ON_SWITCH, end="")
                    else:
                        print(STONE, end="")
                else:
                    print(col, end="")
                print(Style.RESET_ALL, end="")
            print()

    # Get what static object is at pos
    def matrix_at(self, pos : Position) -> str:
        return self.matrix[pos.y][pos.x] # Remember y for height/row and x for width/column

    def stone_weight(self, stone_id : int) -> int:
        return 1

    # Check for deadlock patterns around the pushed_stone
    # Return the area that matched the deadlock pattern
    def get_deadlock(self, state : State, pushed_stone : Position):
        # We extract the area of the puzzle that we are going to check
        # Now assume that we only check for 2x2 deadlock patterns
        # That mean in the puzzle we should check a 3x3 area
        # The stone should be in the middle of the area
        check_square = [\
            Position(pushed_stone.y -1, pushed_stone.x - 1),
            Position(pushed_stone.y - 1, pushed_stone.x),
            Position(pushed_stone.y -1, pushed_stone.x + 1),
            Position(pushed_stone.y, pushed_stone.x-1),
            Position(pushed_stone.y, pushed_stone.x),
            Position(pushed_stone.y, pushed_stone.x+1),
            Position(pushed_stone.y+1, pushed_stone.x-1),
            Position(pushed_stone.y+1, pushed_stone.x),
            Position(pushed_stone.y+1, pushed_stone.x+1)]
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
                    if check_position.y < 0 or check_position.y >= self.rows or check_position.x < 0 or check_position.x >= self.cols:
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
                    return Position(i, j)
        return Position(0, 0)
    # Only run once on init
    def init_stone_positions(self):
        stone_positions = []
        for i in range(len(self.input_matrix)):
            for j in range(len(self.input_matrix[i])):
                if self.input_matrix[i][j] in [STONE, STONE_ON_SWITCH]:
                    stone_positions.append(Position(i, j))
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
        reachables =  self.reachable_squares(self.ares_initial_position, self.stone_positions)
        min_reachable = self.minreachable_square(reachables)
        return State(min_reachable, self.stone_positions)

    def is_solved(self, state : State):
        for stone_position in state.stone_positions:
            if self.matrix_at(stone_position) != SWITCH:
                return False
        return True
    
    def pushable_squares(self, reachable_squares : list[Position], stone_position : Position):
        pushables = []
        for neighbor in self.neighbors(stone_position):
            if neighbor in reachable_squares:
                pushables.append(neighbor)
        return pushables

    def neighbors(self, position : Position):
        y = position.y
        x = position.x
        return [Position(y+1, x), Position(y-1, x), Position(y, x+1), Position(y, x-1)]

    def minreachable_square(self, reachable_squares : list[Position]):
        min_square = reachable_squares[0]
        for i in range(1, len(reachable_squares)):
            if min_square.y * self.cols + min_square.x > reachable_squares[i].y * self.cols + reachable_squares[i].x:
                min_square = reachable_squares[i]
        return min_square

    def reachable_squares(self, ares_postion : Position, stone_positions : list[Position]):
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

    def can_push(self, ares_position : Position, stone_position : Position, state:State):
        y_translation = stone_position.y - ares_position.y
        x_translation = stone_position.x - ares_position.x
        new_position = Position(stone_position.y + y_translation, stone_position.x + x_translation)
        if self.matrix_at(new_position) != WALL and (new_position not in state.stone_positions):
            return True
        return False

    def push(self, ares_position, stone_position, state:State):
        y_translation = stone_position.y - ares_position.y
        x_translation = stone_position.x - ares_position.x
        new_position = Position(stone_position.y + y_translation, stone_position.x + x_translation)
        return new_position

    def get_hash(self, state : State) -> str:
        ares_y = state.ares_normalized_position.y
        ares_x = state.ares_normalized_position.x
        to_hash = [(ares_y, ares_x)]
        stone_positions = []
        for sp in state.stone_positions:
            stone_y = sp.y
            stone_x = sp.x
            stone_positions.append((stone_y, stone_x))
        stone_positions = tuple(stone_positions)
        to_hash.append(stone_positions)
        to_hash = tuple(to_hash)
        return str(hash(to_hash))
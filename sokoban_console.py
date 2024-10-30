# Prototype for sokoban solver
import time as time
from colorama import Fore, Back, Style

ARES = "@"
WALL = "#"
SPACE = " "
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

# Only use the fist time running the solver
def ares_position(puzzle_matrix):
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [ARES, ARES_ON_SWITCH]:
                return (i, j)
    return (0, 0)
# Only use the fist time running the solver
def stone_positions(puzzle_matrix):
    stone_positions = []
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [STONE, STONE_ON_SWITCH]:
                stone_positions.append((i, j))
    return stone_positions

def pushable_squares(puzzle_matrix, reachable_squares, stone_position, stone_positions):
    pushables = []
    for neighbor in neighbors(stone_position):
        if neighbor in reachable_squares and can_push(puzzle_matrix, stone_position, neighbor, stone_positions):
            pushables.append(neighbor)
    return pushables

def neighbors(position):
    x = position[0]
    y = position[1]
    return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

def minreachable_square(puzzle_matrix, reachable_squares):
    min_square = reachable_squares[0]
    cols = len(puzzle_matrix[0])
    for i in range(1, len(reachable_squares)):
        if min_square[0] * cols + min_square[1] > reachable_squares[i][0] * cols + reachable_squares[i][1]:
            min_square = reachable_squares[i]
    return min_square

def reachable_squares(puzzle_matrix, ares_position, stone_positions):
    x = ares_position[0]
    y = ares_position[1]
    # A simple DFS to find reachable squares
    frontier = [(x, y)]
    explored = []
    while frontier:
        child = frontier.pop()
        explored.append(child)
        for neighbor in neighbors(child):
            x = neighbor[0]
            y = neighbor[1]
            if puzzle_matrix[x][y] != WALL \
                and (neighbor not in stone_positions) \
                    and (neighbor not in explored) \
                        and (neighbor not in frontier):
                frontier.append(neighbor)
    return explored

def branch(puzzle_matrix, state, deadlock_patterns, transposition_table):
    child_states = []
    reachables = reachable_squares(puzzle_matrix, state[0], state[1])
    for i in range(len(state[1])):
        for pushable in pushable_squares(puzzle_matrix, reachables, state[1][i], state[1]):
            new_stones = list(state[1])
            new_stone_position = push(puzzle_matrix, state[1][i], pushable)
            new_stones[i] = new_stone_position

            new_reachables = reachable_squares(puzzle_matrix, state[0], new_stones)
            child_state = get_state(new_reachables, new_stones)

            deadlock = is_deadlock(puzzle_matrix, child_state, deadlock_patterns, new_stone_position)
            if len(deadlock) > 0:
                transposition_table[str(hash(child_state))] = child_state
                draw_on_static_puzzle(puzzle_matrix, child_state, deadlock)
                print("Deadlock found!")
                continue

            child_states.append(child_state)
    return child_states

def can_push(puzzle_matrix, stone_position, ares_position, stone_positions):
    x_translation = stone_position[0] - ares_position[0]
    y_translation = stone_position[1] - ares_position[1]
    new_position = (stone_position[0] + x_translation, stone_position[1] + y_translation)
    if puzzle_matrix[new_position[0]][new_position[1]] != WALL and (new_position not in stone_positions):
        return True
    return False

def push(puzzle_matrix, stone_position, ares_position):
    x_translation = stone_position[0] - ares_position[0]
    y_translation = stone_position[1] - ares_position[1]
    return (stone_position[0] + x_translation, stone_position[1] + y_translation)

def is_solved(puzzle_matrix, state):
    for stone_position in state[1]:
        if puzzle_matrix[stone_position[0]][stone_position[1]] not in SWITCH:
            return False
    return True

# Draw multiple states on one line
def draw_many_on_static_puzzle(static_puzzle_matrix, states):
    if len(states) == 0:
        return
    static_puzzle_matrix_clones = []
    for state in states:
        static_puzzle_matrix_clone = []
        for i in range(len(static_puzzle_matrix)):
            row = []
            for j in range(len(static_puzzle_matrix[i])):
                row.append(static_puzzle_matrix[i][j])
            static_puzzle_matrix_clone.append(row)
        if static_puzzle_matrix_clone[state[0][0]][state[0][1]] == SWITCH:
            static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES_ON_SWITCH
        else:
            static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES
        if state[1]:
            for stone in state[1]:
                if static_puzzle_matrix_clone[stone[0]][stone[1]] == SWITCH:
                    static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE_ON_SWITCH
                else:
                    static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE
        static_puzzle_matrix_clones.append(static_puzzle_matrix_clone)
    
    for i in range(len(static_puzzle_matrix_clones[0])):
        for j in range(len(states)):
            for k in range(len(static_puzzle_matrix_clones[j][i])):
                print(static_puzzle_matrix_clones[j][i][k], end="")
            print(" "*4, end="")
        print()

def draw_puzzle(puzzle_matrix, highlight_positions = [], hightlighter = "█"):
    for i in range(len(puzzle_matrix)):
        for j in range(len(puzzle_matrix[i])):
            if (i, j) in highlight_positions:
                print(Fore.CYAN + Back.WHITE + puzzle_matrix[i][j], end="")
            else:
                print(Style.RESET_ALL + puzzle_matrix[i][j], end="")
        print()

def draw_on_static_puzzle(static_puzzle_matrix, state, highlight_positions = [], hightlighter = "█"):
    static_puzzle_matrix_clone = []
    for i in range(len(static_puzzle_matrix)):
        row = []
        for j in range(len(static_puzzle_matrix[i])):
            row.append(static_puzzle_matrix[i][j])
        static_puzzle_matrix_clone.append(row)

    if static_puzzle_matrix_clone[state[0][0]][state[0][1]] == SWITCH:
        static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES_ON_SWITCH
    else:
        static_puzzle_matrix_clone[state[0][0]][state[0][1]] = ARES
    
    for stone in state[1]:
        if static_puzzle_matrix_clone[stone[0]][stone[1]] == SWITCH:
            static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE_ON_SWITCH
        else:
            static_puzzle_matrix_clone[stone[0]][stone[1]] = STONE

    draw_puzzle(static_puzzle_matrix_clone, highlight_positions, hightlighter)

def get_initial_state(puzzle_matrix):
    ares_pos = ares_position(puzzle_matrix)
    stones = stone_positions(puzzle_matrix)
    reachables = reachable_squares(puzzle_matrix, ares_pos, stones)
    min_reachable = minreachable_square(puzzle_matrix, reachables)
    return (min_reachable, tuple(stones)) 

def get_state(reachables, stone_positions):
    min_reachable = minreachable_square(puzzle_matrix, reachables)
    return (min_reachable, tuple(stone_positions)) 

def bfs(puzzle_matrix):
    initial_state = get_initial_state(puzzle_matrix)
    puzzle_matrix = get_static_puzzle_matrix(puzzle_matrix)
    initial_state_hash = str(hash(initial_state))
    tranposition_table = {initial_state_hash : initial_state}
    deadlock_patterns = get_deadlock_patterns()

    frontier = [initial_state_hash]
    explored = [initial_state_hash]
    parents = {initial_state_hash : None}
    
    found = False 
    processed_count = 0
    goal_state_hash = None

    while frontier:
        print("processed_count = ", processed_count)
        current_hash = frontier.pop(0)
        current = tranposition_table[current_hash]
        explored.append(current_hash)

        branching = []
        for child in branch(puzzle_matrix, current, deadlock_patterns, tranposition_table):
            child_hash = str(hash(child))
            if (child_hash not in explored) and (child_hash not in tranposition_table):
                tranposition_table[child_hash] = child
                parents[child_hash] = current_hash
                if is_solved(puzzle_matrix, child):
                    found = True
                    goal_state_hash = child_hash
                    draw_on_static_puzzle(puzzle_matrix, child)
                    print("Done!")
                    break
                frontier.append(child_hash)
                branching.append(child)
        draw_many_on_static_puzzle(puzzle_matrix, branching)
        processed_count += 1
        if found:
            break
    
    if not found:
        print("No solution found")
        return
    
    path = []
    backtracer = goal_state_hash
    while backtracer:
        path.append(tranposition_table[backtracer])
        backtracer = parents[backtracer]
    path.reverse()
    return path

def get_static_puzzle_matrix(puzzle_matrix):
    static_matrix = []

    for i in range(len(puzzle_matrix)):
        row = []
        for j in range(len(puzzle_matrix[i])):
            if puzzle_matrix[i][j] in [ARES, STONE]:
                row.append(SPACE)
            elif puzzle_matrix[i][j] in [ARES_ON_SWITCH, STONE_ON_SWITCH]:
                row.append(SWITCH)
            else:
                row.append(puzzle_matrix[i][j])
        static_matrix.append(row)
    return static_matrix

# Since we are not saving ares exact position at each state
# We have to use some kind of pathfinding to interpolate area path
# moving between two states
def bfs_transition_path(puzzle_matrix, from_position, to_position, stone_positions):
    frontier = [from_position]
    explored = []
    parents = {from_position : None}
    found = False
    while frontier:
        current = frontier.pop(0)
        explored.append(current)
        for neighbor in neighbors(current):
            if puzzle_matrix[neighbor[0]][neighbor[1]] != WALL \
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

def map_move_direction(direction):
    if direction[1] == 1 and direction[0] == 0:
        return "r"
    elif direction[1] == -1 and direction[0] == 0:
        return "l"
    elif direction[1] == 0 and direction[0] == 1:
        return "d"
    elif direction[1] == 0 and direction[0] == -1:
        return "u"
    return "?"

def trace(puzzle_matrix, state_path, ares_initial_position):
    navigation_path = []

    ares_last_position = ares_initial_position
    for i in range(len(state_path)-1):
        print("Interpolating state ", i)
        current_state = state_path[i]
        next_state = state_path[i+1]
        
        interpolated = False
        # We must find the difference in stone postions
        # to determine where is ares's next position
        for j in range(len(current_state[1])):
            if current_state[1][j] != next_state[1][j]:
                push_direction = (next_state[1][j][0] - current_state[1][j][0], next_state[1][j][1] - current_state[1][j][1])
                push_position = (current_state[1][j][0] - push_direction[0], current_state[1][j][1] - push_direction[1])

                # Move ares to the push position
                path = bfs_transition_path(puzzle_matrix, ares_last_position, push_position, current_state[1])
                for k in range(len(path)-1):
                    direction = (path[k+1][0] - path[k][0], path[k+1][1] - path[k][1])
                    navigation_path.append(map_move_direction(direction))
                # Push the stone
                navigation_path.append(map_move_direction(push_direction).upper())
                # Ares is now at the stone old position
                ares_last_position = current_state[1][j]
                interpolated = True
                break
        if not interpolated:
            print("Some thing went wrong. We should always have a stone position change")
            return []
    return navigation_path

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

def get_deadlock_patterns():
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

def is_deadlock(puzzle_matrix, state, patterns, pushed_stone):
    rows = len(puzzle_matrix)
    cols = len(puzzle_matrix[0])

    # We extract the area of the puzzle that we are going to check
    # Now assume that we only check for 2x2 deadlock patterns
    # That mean in the puzzle we should check a 3x3 area
    # The stone should be in the middle of the area
    deadlock_area = []

    check_square = [\
        (pushed_stone[0] -1, pushed_stone[1] - 1),
        (pushed_stone[0] - 1, pushed_stone[1]),
        (pushed_stone[0] -1, pushed_stone[1] + 1),
        (pushed_stone[0], pushed_stone[1]-1),
        (pushed_stone[0], pushed_stone[1]),
        (pushed_stone[0], pushed_stone[1]+1),
        (pushed_stone[0]+1, pushed_stone[1]-1),
        (pushed_stone[0]+1, pushed_stone[1]),
        (pushed_stone[0]+1, pushed_stone[1]+1)]
    

    # We should have 4 different area to check for 2x2 patterns 
    check_areas = [\
        [check_square[0], check_square[1], check_square[3], check_square[4]],
        [check_square[1], check_square[2], check_square[4], check_square[5]],
        [check_square[3], check_square[4], check_square[6], check_square[7]],
        [check_square[4], check_square[5], check_square[7], check_square[8]]]

    for pattern in patterns:
        height = len(pattern)
        width = len(pattern[0])
        # For now, let's just check for 2x2 deadlock patterns
        if height != 2 or width != 2:
            continue
        for check_area in check_areas:
            matched_count = 0
            area_out_of_bound = False
            for i in range(4):
                if check_area[i][0] < 0 or check_area[i][0] >= rows or check_area[i][1] < 0 or check_area[i][1] >= cols:
                    area_out_of_bound = True
                    break
                check_position = check_area[i]
                what_is_here = ""
                if check_position in state[1]: # state[1] is stone positions
                    # A stone can be deadlock but if it reached the goal, we shouldn't care
                    if puzzle_matrix[check_position[0]][check_position[1]] == SWITCH:
                        what_is_here = WALL
                    else:
                        what_is_here = STONE
                elif puzzle_matrix[check_position[0]][check_position[1]] == WALL:
                    what_is_here = WALL
                else:
                    what_is_here = SPACE

                if what_is_here == pattern[i//2][i%2]:
                    matched_count += 1
            if area_out_of_bound:
                continue
            if matched_count == 4:
                print(pattern)
                return check_area
    return []

if __name__ == "__main__":
    puzzle_matrix = []
    with open("input.txt", "r") as file_in:
        lines = file_in.read().splitlines()
        for line in lines:
            puzzle_row = list(line)
            puzzle_matrix.append(puzzle_row)
    
    ares_initial_position = ares_position(puzzle_matrix)
    
    solved_path = bfs(puzzle_matrix)
    print("Solve states: ")
    draw_many_on_static_puzzle(get_static_puzzle_matrix(puzzle_matrix), solved_path)
    solved_navigation_path = trace(puzzle_matrix, solved_path, ares_initial_position)
    print("Solved path: ", "".join(solved_navigation_path))



ARES = "@"
WALL = "#"
SPACE = " "
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

puzzle_matrix = \
"""
#######
#    .#
#  $$.#
# @$#.#
#######
"""

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

puzzle_matrix = puzzle_matrix.split("\n")[1:-1]

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
        return tuple(patterns.values())

def is_deadlock(puzzle_matrix, pattern):
    rows = len(puzzle_matrix)
    cols = len(puzzle_matrix[0])
    height = len(pattern)
    width = len(pattern[0])
    matched = False
    for i in range(rows):
        for j in range(cols):
            matched_count = 0
            for k in range(height):
                for l in range(width):
                    if (i + k <= rows -1) and (j + l <= cols - 1):
                        what_is_here = puzzle_matrix[i + k][j + l]
                        if what_is_here in (ARES, ARES_ON_SWITCH):
                            what_is_here = SPACE # Ignore Ares
                        if what_is_here in (STONE_ON_SWITCH):
                            what_is_here = STONE # Stones on switches are still stones
                        
                        if puzzle_matrix[i + k][j + l] == pattern[k][l]:
                            matched_count += 1
                            if matched_count == width * height:
                                matched = True
                                return True
            if matched:
                break
    if not matched:
        return False
    
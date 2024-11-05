import pygame
import pygame_widgets
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban, SokobanStateDrawingData
from runner import Runner
from widgets import get_widgets
from widgets_events import *
import argparse
import os

# Directory
INPUT_DIR = "input"
OUTPUT_DIR = "output"

# Screen settings
TILE_SIZE = 30
ROWS, COLS = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE  # Extra space for dropdown and buttons
FPS = 24

# Background image
def draw_background(screen : pygame.surface):
    for i in range(ROWS):
        for j in range(COLS):
            bg = pygame.image.load("textures/background.png").convert()
            bg = pygame.transform.scale(bg, (TILE_SIZE, TILE_SIZE))
            screen.blit(bg, (i * TILE_SIZE, j * TILE_SIZE))

# Draw matrix function
def draw_sokoban_state(screen : pygame.surface, s : SokobanStateDrawingData, text_font):
    center_offset = (ROWS/2-s.rows/2, COLS/2-s.cols/2)
    stone_index = 0
    for i in range(s.rows):
        for j in range(s.cols):
            x, y = (j + center_offset[1]) * TILE_SIZE , (i + center_offset[0]) * TILE_SIZE
            tile = s.state_at((i, j))

            # Draw a different texture for the inner region
            if (i, j) not in s.outer_squares:
                img = pygame.image.load("textures/inner_floor.png").convert()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile == "#":
                img = pygame.image.load("textures/wall.png").convert()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in ".*+":
                img = pygame.image.load("textures/switch.png").convert()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in "@+":
                img = pygame.image.load("textures/link.png").convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))
            if tile in "$*":
                img = pygame.image.load("textures/stone.png").convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                screen.blit(img, (x, y))

                # Draw the weight of the stone
                stone_weight = text_font.render(str(s.stone_weights[stone_index]), True, (0, 0, 0))
                screen.blit(stone_weight, (x + 10, y + 10))
                stone_index += 1

SCREEN_SELECT = 0
SCREEN_DEMO = 1
ANIMATION_STEP = 2 # Frames between each move

def main(mode : str):
	# Initialize Pygame
    pygame.init()    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sokoban Solver Visualization")

    default_font = pygame.font.Font("fonts/FreePixel.ttf", 14)
    widgets = get_widgets(screen, default_font)

    algo = None
    level = None
    sokoban_game = None
    sokoban_solved_states = []
    sokoban_solver = None
    sokoban_solver_record_data = ""

    current_screen = SCREEN_SELECT
    frame_count = 0
    state_index = 0
    is_paused = False

    clock = pygame.time.Clock()

    while True:
        running_solver = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == SELECT_ALGO_EVENT:
                algo = widgets["algo_menu"].getSelected()
            elif event.type == SELECT_MAP_EVENT:
                level = widgets["level_menu"].getSelected()
            elif event.type == RUN_EVENT:
                if level is not None and algo is not None:
                    sokoban_game = Sokoban(f"{INPUT_DIR}/{level}")
                    # Add in the initial state to see the level ayout first
                    sokoban_solved_states = [Runner.initial_state(sokoban_game)]
                    current_screen = SCREEN_DEMO
            elif event.type == START_EVENT:
                state_index = 0
                if len(sokoban_solved_states) == 1 and algo is not None:
                    if algo == "BFS":
                        sokoban_solver = BFSSolver(sokoban_game)
                    elif algo == "DFS":
                        sokoban_solver = DFSSolver(sokoban_game)
                    elif algo == "UCS":
                        sokoban_solver = UCSSolver(sokoban_game)
                    elif algo == "AStar":
                        sokoban_solver = AStarSolver(sokoban_game)
                    running_solver = True
                is_paused = False
            elif event.type == PAUSE_EVENT:
                is_paused = not is_paused
            elif event.type == STOP_EVENT:
                state_index = 0
                sokoban_solved_states = [Runner.initial_state(sokoban_game)]
            elif event.type == BACK_EVENT:
                current_screen = SCREEN_SELECT
                sokoban_game = None
                sokoban_solved_states = []
                sokoban_solver = None
                is_paused = False
            elif mode == "debug" and event.type == pygame.KEYDOWN:
                custom_move = ""
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    custom_move = 'r'
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    custom_move = 'l'
                elif event.key in (pygame.K_w, pygame.K_UP):
                    custom_move = 'u'
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    custom_move = 'd'
                # Altering the input
                if custom_move != "":
                    g = Sokoban("", sokoban_game.matrix, sokoban_game.cols, sokoban_game.rows, sokoban_game.stone_weights)
                    sokoban_solved_states = [Runner.run(g, custom_move)[1]]
                    sokoban_game = Sokoban("", sokoban_solved_states[0].state, sokoban_game.cols, sokoban_game.rows, sokoban_solved_states[0].stone_weights)

        if mode == "debug":
            screen.fill((255, 255, 255))
        else:
            draw_background(screen)

        if current_screen == SCREEN_SELECT:
            # Show the selection widgets
            widgets["algo_menu"].show()
            widgets["level_menu"].show()
            widgets["run_button"].show()
            widgets["start_button"].hide()
            # Hide the demo widgets
            widgets["start_button"].hide()
            widgets["pause_button"].hide()
            widgets["stop_button"].hide()
            widgets["back_button"].hide()
            widgets["message_box"].hide()
            widgets["statistic_box"].hide()

        elif current_screen == SCREEN_DEMO:
            # Hide the selection widgets
            widgets["algo_menu"].hide()
            widgets["level_menu"].hide()
            widgets["run_button"].hide()
            # Show the demo widgets
            widgets["start_button"].show()
            widgets["pause_button"].show()
            widgets["stop_button"].show()
            widgets["back_button"].show()
            widgets["statistic_box"].show()

            widgets["message_box"].hide() # hide this by default

            if len(sokoban_solved_states) > 0:
                # Show the map
                if len(sokoban_solved_states) == 1:
                    draw_sokoban_state(screen, sokoban_solved_states[0], default_font)
                elif state_index < len(sokoban_solved_states):
                    widgets["statistic_box"].setText(f"{algo}: Step {sokoban_solved_states[state_index].steps} - Weight {sokoban_solved_states[state_index].weight}")
                    draw_sokoban_state(screen, sokoban_solved_states[state_index], default_font)
                    
                    if not is_paused and frame_count % ANIMATION_STEP == 0:
                        state_index += 1
                        if state_index == len(sokoban_solved_states):
                            state_index = len(sokoban_solved_states) - 1

        if running_solver:
            widgets["message_box"].show()
            widgets["message_box"].setText("Solving...")
            pygame_widgets.update(events)
            pygame.display.update()

            path = sokoban_solver.solve()
            print(path)

            if path is None:
                widgets["message_box"].setText("No solution!")
                pygame_widgets.update(events)
                pygame.display.update()
                pygame.time.wait(2000)
                clock.tick(FPS)
                frame_count += 1
            else:
                sokoban_solved_states = Runner.run(sokoban_game, path)
                sokoban_solver_record_data = sokoban_solver.record.data()
                # Determine the output file
                output_file = "output.txt"
                if level.startswith("input-") and level.endswith(".txt"):
                    output_file = level.replace("input-", "output-")
                # Check if this algorithm has been run before
                # If so, only change that algorithm's output
                output_lines = []
                run_before = False
                if os.path.exists(f"{OUTPUT_DIR}/{output_file}"):
                    with open(f"{OUTPUT_DIR}/{output_file}", "r") as f:
                        lines = f.read().splitlines()
                        for i in range(len(lines)):
                            if lines[i] == algo and i + 1 <= len(lines) and i + 1 < len(lines):
                                lines[i+1] = sokoban_solver.record.data()
                                lines[i+2] = path
                                run_before = True
                                break
                        output_lines = lines
                # If not, just append the output
                if len(output_lines) == 0 or not run_before:
                    output_lines.append(algo)
                    output_lines.append(sokoban_solver.record.data())
                    output_lines.append(path)
                # Write the output
                with open(f"{OUTPUT_DIR}/{output_file}", "w") as f:
                    for line in output_lines:
                        f.write(line + "\n")
        else:
            pygame_widgets.update(events)
            pygame.display.update()
            clock.tick(FPS)
            frame_count += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run mode')
    parser.add_argument('--mode', type=str, help='debug or normal', default='normal')

    args = parser.parse_args()
    main(args.mode)
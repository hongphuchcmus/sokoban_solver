import pygame
import pygame_widgets
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
from sokoban import Sokoban
from runner import Runner
from widgets import get_widgets
from widgets_events import *


# Screen settings
TILE_SIZE = 30
ROWS, COLS = 20, 20
SCREEN_WIDTH, SCREEN_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE  # Extra space for dropdown and buttons
FPS = 15

# Visual class for Sokoban state
class SokobanState:
    def __init__(self, steps, weight, state, g : Sokoban) -> None:
        self.cols = g.cols
        self.rows = g.rows
        self.outer_squares = g.outer_squares
        self.state = state
        self.steps = steps
        self.weight = weight

# Background image
def draw_background(screen : pygame.surface):
    for i in range(ROWS):
        for j in range(COLS):
            bg = pygame.image.load("textures/background.png").convert()
            bg = pygame.transform.scale(bg, (TILE_SIZE, TILE_SIZE))
            screen.blit(bg, (i * TILE_SIZE, j * TILE_SIZE))

# Draw matrix function
def draw_sokoban_state(screen : pygame.surface, s : SokobanState):
    center_offset = (ROWS/2-s.rows/2, COLS/2-s.cols/2)
    for i in range(s.rows):
        for j in range(s.cols):
            x, y = (j + center_offset[1]) * TILE_SIZE , (i + center_offset[0]) * TILE_SIZE
            tile = s.state[i][j]

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

SCREEN_SELECT = 0
SCREEN_DEMO = 1

ANIMATION_STEP = 3 # Frames between each step

def main():
	# Initialize Pygame
    pygame.init()    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sokoban Solver Visualization")

    widgets = get_widgets(screen, pygame.font.Font("fonts/FreePixel.ttf", 14))
    

    algo = "BFS"
    level = "1"
    sokoban_game = None
    sokoban_solved_states = []
    sokoban_solver = None
    sokoban_initial_state = None

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
                if level is not None:
                    sokoban_game = Sokoban(f"Tests/{level}.txt")
                if level is not None:
                    if algo == "BFS":
                        sokoban_solver = BFSSolver(sokoban_game)
                    elif algo == "DFS":
                        sokoban_solver = DFSSolver(sokoban_game)
                    elif algo == "UCS":
                        sokoban_solver = UCSSolver(sokoban_game)
                    elif algo == "AStar":
                        sokoban_solver = AStarSolver(sokoban_game)
                    else:
                        algo = None
                # print(algo, level)
                if algo is not None and level is not None:
                    # Add in the initial state as placeholder
                    sokoban_initial_state = Runner.state_string_to_string_list(sokoban_game, sokoban_game.matrix)
                    sokoban_solved_states = [SokobanState(0, 0, sokoban_initial_state, sokoban_game)]
                    current_screen = SCREEN_DEMO
                    
            elif event.type == START_EVENT:
                state_index = 0
                running_solver = True
            elif event.type == PAUSE_EVENT:
                is_paused = not is_paused
            elif event.type == STOP_EVENT:
                state_index = 0
                sokoban_solved_states = [SokobanState(0, 0, sokoban_initial_state, sokoban_game)]
            elif event.type == BACK_EVENT:
                current_screen = SCREEN_SELECT
                sokoban_game = None
                sokoban_solved_states = []
                sokoban_solver = None
                sokoban_initial_state = None
                is_paused = False

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
                    draw_sokoban_state(screen, sokoban_solved_states[0])
                elif state_index < len(sokoban_solved_states):
                    widgets["statistic_box"].setText(f"{algo}: Step {sokoban_solved_states[state_index].steps} - Weight {sokoban_solved_states[state_index].weight}")
                    draw_sokoban_state(screen, sokoban_solved_states[state_index])
                    if frame_count * bool(is_paused) % ANIMATION_STEP == 0:
                        state_index += 1
                    if state_index == len(sokoban_solved_states):
                        state_index = len(sokoban_solved_states) - 1

        if running_solver:
            widgets["message_box"].show()
            widgets["message_box"].setText("Solving...")
            pygame_widgets.update(events)
            pygame.display.update()

            path = sokoban_solver.solve(False)

            if path is None:
                widgets["message_box"].setText("No solution!")
                pygame_widgets.update(events)
                pygame.display.update()
                pygame.time.wait(2000)
                clock.tick(FPS)
                frame_count += 1
            else:
                weights_and_states = Runner.run(sokoban_game, path)
                for i in range(len(weights_and_states)):
                    state = SokobanState(i, weights_and_states[i][0], weights_and_states[i][1], sokoban_game)
                    sokoban_solved_states.append(state)
        else:
            pygame_widgets.update(events)
            pygame.display.update()
            clock.tick(FPS)
            frame_count += 1


if __name__ == '__main__':
	main()
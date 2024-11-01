import pygame
import time
from bfs import BFSSolver
from dfs import DFSSolver
from ucs import UCSSolver
from astar import AStarSolver
import sokoban_console_refactored as skb

# Initialize Pygame
pygame.init()

# Screen settings
TILE_SIZE = 50
ROWS, COLS = 10, 10
SCREEN_WIDTH, SCREEN_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 100  # Extra space for buttons
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban Solver Visualization")

# Colors
COLOR_WALL = (100, 100, 100)
COLOR_SPACE = (255, 255, 255)
COLOR_PLAYER = (0, 0, 255)
COLOR_STONE = (139, 69, 19)
COLOR_SWITCH = (255, 215, 0)
COLOR_STONE_ON_SWITCH = (255, 140, 0)
COLOR_PLAYER_ON_SWITCH = (30, 144, 255)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_TEXT = (255, 255, 255)

# Button settings
BUTTON_WIDTH, BUTTON_HEIGHT = 100, 40
button_font = pygame.font.Font(None, 30)

# Animation states
START, PAUSE, STOP = 0, 1, 2
animation_state = STOP
frame_index = 0

# Draw buttons
def draw_button(x, y, text):
    button_rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, COLOR_BUTTON, button_rect)
    text_surface = button_font.render(text, True, COLOR_BUTTON_TEXT)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect

# Draw matrix function
def draw_matrix(matrix):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            tile = matrix[row][col]
            if tile == "#":
                pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == " ":
                pygame.draw.rect(screen, COLOR_SPACE, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == "@":
                pygame.draw.rect(screen, COLOR_PLAYER, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == "$":
                pygame.draw.rect(screen, COLOR_STONE, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == ".":
                pygame.draw.rect(screen, COLOR_SWITCH, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == "*":
                pygame.draw.rect(screen, COLOR_STONE_ON_SWITCH, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == "+":
                pygame.draw.rect(screen, COLOR_PLAYER_ON_SWITCH, (x, y, TILE_SIZE, TILE_SIZE))

# Button click handling
def handle_button_click(mouse_pos):
    global animation_state
    if start_button.collidepoint(mouse_pos):
        animation_state = START
    elif pause_button.collidepoint(mouse_pos):
        animation_state = PAUSE
    elif stop_button.collidepoint(mouse_pos):
        animation_state = STOP

# Main game loop
running = True
solver_instance = BFSSolver(skb.Sokoban("input.txt"))
path = solver_instance.solve()
sokoban_instance = skb.Sokoban("input.txt")
matrices = sokoban_instance.run(path)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_button_click(pygame.mouse.get_pos())

    # Draw the current puzzle matrix
    screen.fill(COLOR_SPACE)
    if animation_state == START and frame_index < len(matrices):
        draw_matrix(matrices[frame_index])
        frame_index += 1
        time.sleep(0.1)  # Control speed of animation
    elif animation_state == STOP:
        frame_index = 0  # Reset to the start
    elif animation_state == PAUSE:
        # Draw the current frame but don't increment
        if frame_index < len(matrices):
            draw_matrix(matrices[frame_index])

    # Draw buttons on top of the puzzle
    start_button = draw_button(50, SCREEN_HEIGHT - 80, "Start")
    pause_button = draw_button(200, SCREEN_HEIGHT - 80, "Pause")
    stop_button = draw_button(350, SCREEN_HEIGHT - 80, "Stop")

    pygame.display.flip()

pygame.quit()

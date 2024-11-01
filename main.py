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
COLOR_BUTTON_HOVER = (100, 160, 210)
COLOR_BUTTON_PRESSED = (50, 110, 150)
COLOR_BUTTON_TEXT = (255, 255, 255)

# Button settings
BUTTON_WIDTH, BUTTON_HEIGHT = 100, 40
button_font = pygame.font.Font(None, 30)

# Animation states
START, PAUSE, STOP = 0, 1, 2
animation_state = STOP
frame_index = 0

# Button Class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, pressed_color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        # Determine color based on state
        if self.is_pressed:
            current_color = self.pressed_color
        elif self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color
        pygame.draw.rect(surface, current_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos, mouse_pressed):
        # Update hover and press states
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_pressed = self.is_hovered and mouse_pressed

    def is_clicked(self, mouse_pos, mouse_pressed):
        # Check if clicked (hovered and pressed released)
        return self.is_hovered and not mouse_pressed

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
def handle_button_click(mouse_pos, mouse_pressed, buttons):
    global animation_state
    if buttons['start'].is_clicked(mouse_pos, mouse_pressed):
        animation_state = START
    elif buttons['pause'].is_clicked(mouse_pos, mouse_pressed):
        animation_state = PAUSE
    elif buttons['stop'].is_clicked(mouse_pos, mouse_pressed):
        animation_state = STOP

# Main game loop
running = True
solver_instance = BFSSolver(skb.Sokoban("input.txt"))
path = solver_instance.solve()
sokoban_instance = skb.Sokoban("input.txt")
matrices = sokoban_instance.run(path)

# Initialize buttons
buttons = {
    'start': Button(50, SCREEN_HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT, "Start", COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_PRESSED, COLOR_BUTTON_TEXT, button_font),
    'pause': Button(200, SCREEN_HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT, "Pause", COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_PRESSED, COLOR_BUTTON_TEXT, button_font),
    'stop': Button(350, SCREEN_HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT, "Stop", COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_PRESSED, COLOR_BUTTON_TEXT, button_font)
}

# Draw initial matrix before starting animation
screen.fill(COLOR_SPACE)
draw_matrix(matrices[0])  # Display the initial puzzle state
pygame.display.flip()  # Update the screen with the initial matrix

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_button_click(mouse_pos, mouse_pressed, buttons)
    
    # Update each button
    for button in buttons.values():
        button.update(mouse_pos, mouse_pressed)

    # Draw the current puzzle matrix based on animation state
    if animation_state == START and frame_index < len(matrices):
        screen.fill(COLOR_SPACE)
        draw_matrix(matrices[frame_index])
        frame_index += 1
        time.sleep(0.1)  # Control speed of animation
    elif animation_state == STOP:
        frame_index = 0  # Reset to the start
    elif animation_state == PAUSE and frame_index < len(matrices):
        screen.fill(COLOR_SPACE)
        draw_matrix(matrices[frame_index])

    # Draw buttons on top
    for button in buttons.values():
        button.draw(screen)
    
    pygame.display.flip()

pygame.quit()

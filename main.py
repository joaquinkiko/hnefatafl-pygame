# Main game runner
import pygame
from pygame import Surface
from pygame.locals import *
import sys
from board import Board, Position

# Window initialization constants
WINDOW_SIZE: tuple = (640, 480)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE
WINDOW_FLAGS: int = pygame.RESIZABLE | pygame.SCALED
# Simulation rate
FRAMES_PER_SECOND: int = 30
# Window clear color
CLEAR_COLOR: tuple = (0, 0, 0)
# Game directories
BASE_DIR: str = __file__.removesuffix(__file__.split("/")[-1])
ASSET_DIR: str = f"{BASE_DIR}assets/"
# Asset paths
ASSET_GRID: str = f"{ASSET_DIR}grid.png"

def main():
    # Initialize GUI
    pygame.init()
    window: Surface = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
    clock = pygame.time.Clock()

    # Setup variables
    board: Board = Board()
    is_attacker_turn: bool = True # Attacker always starts

    # Load assets
    grid_texture: Surface = pygame.image.load(ASSET_GRID)
    grid_texture_size: tuple[int, int] = grid_texture.get_size()

    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_F11:
                            pygame.display.toggle_fullscreen()
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        # Simulate

        # Clear the window
        window.fill(CLEAR_COLOR)

        # Draw window elements
        
        # Draw board
        draw_board(window, board, grid_texture, grid_texture_size)

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)

def draw_board(window: Surface,
               board: Board,
               texture: Surface,
               texture_size: tuple[int, int]
               ) -> None:
    # Get offset so that board is centered
    offset: tuple[int, int] = (
         (window.get_width() - (board.width * texture_size[0])) / 2,
         (window.get_height() - (board.height * texture_size[1])) / 2
        )
    # Draw grid
    for x in range(board.width):
            for y in range(board.height):
                window.blit(
                    texture,
                    (
                        x * texture_size[0] + offset[0],
                        y * texture_size[1] + offset[1]
                    )
                    )

if __name__ == "__main__": main()
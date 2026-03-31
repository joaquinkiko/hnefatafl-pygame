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
ASSET_ATTACKER: str = f"{ASSET_DIR}p_attacker.png"
ASSET_DEFENDER: str = f"{ASSET_DIR}p_defender.png"
ASSET_KING: str = f"{ASSET_DIR}p_king.png"
ASSET_ESCAPE: str = f"{ASSET_DIR}s_escape.png"
ASSET_THRONE: str = f"{ASSET_DIR}s_throne.png"

def main():
    # Initialize GUI
    pygame.init()
    window: Surface = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
    clock = pygame.time.Clock()

    # Setup variables
    board: Board = Board()
    is_attacker_turn: bool = True # Attacker always starts

    # Load assets
    textures: dict[str, Surface] = {
        "grid": pygame.image.load(ASSET_GRID),
        "p_king": pygame.image.load(ASSET_KING),
        "p_defender": pygame.image.load(ASSET_DEFENDER),
        "p_attacker": pygame.image.load(ASSET_ATTACKER),
        "s_escape": pygame.image.load(ASSET_ESCAPE),
        "s_throne": pygame.image.load(ASSET_THRONE),
    }
    texture_sizes: dict[str, tuple[int, int]] = {}
    for key in textures.keys():
        texture_sizes[key] = textures[key].get_size()
    

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
        draw_board(window, board, textures, texture_sizes)
        draw_pieces(window, board, textures, texture_sizes)

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)

def draw_board(window: Surface,
               board: Board,
               textures: dict[str, Surface],
               texture_sizes: dict[str, tuple[int, int]]
               ) -> None:
    # Get offset so that board is centered
    offset: tuple[int, int] = (
         (window.get_width() - (board.width * texture_sizes["grid"][0])) / 2,
         (window.get_height() - (board.height * texture_sizes["grid"][1])) / 2
        )
    # Draw grid
    for x in range(board.width):
            for y in range(board.height):
                window.blit(
                    textures["grid"],
                    (
                        x * texture_sizes["grid"][0] + offset[0],
                        y * texture_sizes["grid"][1] + offset[1]
                    )
                    )

def draw_pieces(window: Surface,
               board: Board,
               textures: dict[str, Surface],
               texture_sizes: dict[str, tuple[int, int]]
               ) -> None:
    # Get offset so that board is centered
    offset: tuple[int, int] = (
         (window.get_width() - (board.width * texture_sizes["grid"][0])) / 2,
         (window.get_height() - (board.height * texture_sizes["grid"][1])) / 2
        )
    # Draw grid
    for x in range(board.width):
            for y in range(board.height):
                # Get draw position based off of grid size
                draw_position: tuple[int, int] = (
                        x * texture_sizes["grid"][0] + offset[0],
                        y * texture_sizes["grid"][1] + offset[1]
                    )
                match board.get_piece_at(Position(x, y)):
                    case "attacker":
                        window.blit(textures["p_attacker"], draw_position)
                    case "defender":
                        window.blit(textures["p_defender"], draw_position)
                    case "king":
                        window.blit(textures["p_king"], draw_position)

if __name__ == "__main__": main()
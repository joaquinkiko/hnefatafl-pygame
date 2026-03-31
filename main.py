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
    selected_piece: Position = None

    # Load assets
    textures: dict[str, Surface] = {
        "p_king": pygame.image.load(ASSET_KING),
        "p_defender": pygame.image.load(ASSET_DEFENDER),
        "p_attacker": pygame.image.load(ASSET_ATTACKER),
        "s_empty": pygame.image.load(ASSET_GRID),
        "s_escape": pygame.image.load(ASSET_ESCAPE),
        "s_throne": pygame.image.load(ASSET_THRONE),
    }
    texture_sizes: dict[str, tuple[int, int]] = {}
    for key in textures.keys():
        texture_sizes[key] = textures[key].get_size()
    
    gui_positions: list[tuple[pygame.Rect, Position]] = get_space_rects(window, board, texture_sizes)

    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONDOWN:
                    for gui_position in gui_positions:
                        test_rect: pygame.Rect = gui_position[0]
                        if test_rect.collidepoint(event.pos):
                            click_position: Position = gui_position[1]
                            match board.get_piece_at(click_position):
                                case "attacker":
                                    if is_attacker_turn:
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case "defender":
                                    if not is_attacker_turn:
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case "king":
                                    if not is_attacker_turn:
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case _:
                                    # See if move can be made
                                    if not selected_piece == None:
                                        # Move piece if possible
                                        if click_position in board.get_valid_moves(selected_piece):
                                            board.move_piece(selected_piece, click_position)
                                            is_attacker_turn = not is_attacker_turn
                                        selected_piece = None

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
        draw_board(window, board, textures, gui_positions)
        draw_pieces(window, board, textures, gui_positions)

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)

def get_space_rects(window: Surface,
                    board: Board,
                    texture_sizes: dict[str, tuple[int, int]]
                    ) -> list[tuple[pygame.Rect, Position]]:
    output: list[tuple[pygame.Rect, Position]] = []
    # Use "s_empty" texture for base space sizing
    space_size: tuple[int ,int] = texture_sizes["s_empty"]
    # Get offset so that board is centered
    offset: tuple[int, int] = (
         (window.get_width() - (board.width * space_size[0])) / 2,
         (window.get_height() - (board.height * space_size[1])) / 2
        )
    for x in range(board.width):
        for y in range(board.height):
            start: tuple[int, int] = (
                    x * space_size[0] + offset[0],
                    y * space_size[1] + offset[1]
                )
            output.append([
                pygame.Rect(start[0], start[1], space_size[0], space_size[1]),
                Position(x, y)
            ])
    return output

def draw_board(window: Surface,
               board: Board,
               textures: dict[str, Surface],
               gui_positions: list[tuple[pygame.Rect, Position]]
               ) -> None:
    for gui_position in gui_positions:
        draw_position: tuple[int, int] = gui_position[0].topleft
        board_position: Position = gui_position[1]
        if board.is_escape(board_position):
            window.blit(textures["s_escape"], draw_position)
        elif board.is_restricted(board_position):
            window.blit(textures["s_throne"], draw_position)
        else:
            window.blit(textures["s_empty"], draw_position)

def draw_pieces(window: Surface,
               board: Board,
               textures: dict[str, Surface],
               gui_positions: list[tuple[pygame.Rect, Position]]
               ) -> None:
    for gui_position in gui_positions:
        draw_position: tuple[int, int] = gui_position[0].topleft
        board_position: Position = gui_position[1]
        match board.get_piece_at(board_position):
            case "attacker":
                window.blit(textures["p_attacker"], draw_position)
            case "defender":
                window.blit(textures["p_defender"], draw_position)
            case "king":
                window.blit(textures["p_king"], draw_position)

if __name__ == "__main__": main()
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
COLOR_HINT_SELECTON: pygame.Color = pygame.Color(0, 255, 0)
COLOR_HINT_VALID_MOVE: pygame.Color = pygame.Color(255, 255, 0)
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
ASSET_FONT_BOARD: str | None = f"{ASSET_DIR}antiquity-print.ttf"
ASSET_FONT_LOG: str | None = None
ASSET_FONT_STATUS: str | None = f"{ASSET_DIR}antiquity-print.ttf"
# Board font
FONT_BOARD_SIZE: int = 12
FONT_BOARD_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_BOARD_SPACING: int = 4
# Log font
FONT_LOG_SIZE: int = 18
FONT_LOG_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_LOG_SPACING: int = 8
FONT_LOG_TOP_LEFT: tuple[int, int] = (4, 4)
# Status font 
FONT_STATUS_SIZE: int = 16
FONT_STATUS_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_STATUS_SPACING: int = 4
FONT_STATUS_Y_OFFSET: int = 8
# Should we use antialiasing for fonts
USE_FONT_AA: bool = False

def main():
    # Initialize GUI
    pygame.init()
    window: Surface = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
    clock = pygame.time.Clock()

    # Setup variables
    board: Board = Board()
    selected_piece: Position = None

    # Load assets
    pygame.font.init()
    font_board: pygame.font.Font = pygame.font.Font(ASSET_FONT_BOARD, FONT_BOARD_SIZE)
    font_log: pygame.font.Font = pygame.font.Font(ASSET_FONT_LOG, FONT_LOG_SIZE)
    font_status: pygame.font.Font = pygame.font.Font(ASSET_FONT_STATUS, FONT_STATUS_SIZE)
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
                        if board.has_been_won(): continue # Ignore if there's a winner
                        test_rect: pygame.Rect = gui_position[0]
                        if test_rect.collidepoint(event.pos):
                            click_position: Position = gui_position[1]
                            match board.get_piece_at(click_position):
                                case "attacker":
                                    if board.is_attacker_turn():
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case "defender":
                                    if board.is_defender_turn():
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case "king":
                                    if board.is_defender_turn():
                                        selected_piece = click_position
                                    else:
                                        selected_piece = None
                                case _:
                                    # See if move can be made
                                    if not selected_piece == None:
                                        if board.is_valid_move(selected_piece, click_position):
                                            board.play_turn(selected_piece, click_position)
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
        if not selected_piece == None:
            draw_selection_hint(window,
                                board,
                                selected_piece,
                                gui_positions
                                )
        draw_board(window, board, textures, gui_positions)
        draw_board_indice_markers(window, font_board, gui_positions)
        draw_pieces(window, board, textures, gui_positions)
        draw_board_log(window, board, font_log)
        daw_board_status(window, board, font_status)

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)

def draw_board_log(window: Surface, board: Board, font: pygame.font.Font) -> None:
    """Draws text log of board turns."""
    offset: int = 0
    for line in board.get_complete_turn_log().split("\n"):
        text_log = font.render(line, USE_FONT_AA, FONT_LOG_COLOR)
        window.blit(text_log, (FONT_LOG_TOP_LEFT[0], FONT_LOG_TOP_LEFT[1] + offset))
        offset += font.get_height() + FONT_LOG_SPACING

def daw_board_status(window: Surface, board: Board, font: pygame.font.Font) -> None:
    """Draws whose turn it is, or if game has been won, along with turn number."""
    string: str = ""
    if board.has_been_won():
        string = board.winner.capitalize() + " has won!"
    else:
        string = f"Turn {board.get_turn_number()}:\n{board.get_current_player().capitalize()}"
    offset: int = 0
    draw_x: int = window.get_width() / 2
    draw_y: int = window.get_height()\
                - FONT_STATUS_Y_OFFSET\
                - (len(string.split("\n")) * font.get_height())
    for line in string.split("\n"):
        text_log = font.render(line, USE_FONT_AA, FONT_LOG_COLOR)
        window.blit(text_log,
                    (
                        draw_x - (font.size(line)[0] / 2),
                        draw_y + offset
                    )
                    )
        offset += font.get_height() + FONT_STATUS_SPACING

def draw_board_indice_markers(window: Surface,
                              font: pygame.font.Font,
                              gui_positions: list[tuple[pygame.Rect, Position]],
                              ) -> None:
    """Draw letter and number indices along board edges."""
    for gui_position in gui_positions:
        rect: pygame.Rect = gui_position[0]
        position: Position = gui_position[1]
        if position.row == 0:
            # Draw number beside
            string: str = position.get_column_string()
            text_size: tuple[int, int] = font.size(string)
            draw_x: int = rect.left - text_size[0] - FONT_BOARD_SPACING
            draw_y: int = rect.centery - (text_size[1] / 2)
            text = font.render(string, USE_FONT_AA, FONT_LOG_COLOR)
            window.blit(text, (draw_x, draw_y))
        if position.column == 0:
            # Draw letter above
            string: str = position.get_row_string()
            text_size: tuple[int, int] = font.size(string)
            draw_x: int = rect.centerx - (text_size[0] / 2)
            draw_y: int = rect.top - font.get_height() - FONT_BOARD_SPACING
            text = font.render(string, USE_FONT_AA, FONT_LOG_COLOR)
            window.blit(text, (draw_x, draw_y))

def get_space_rects(window: Surface,
                    board: Board,
                    texture_sizes: dict[str, tuple[int, int]]
                    ) -> list[tuple[pygame.Rect, Position]]:
    """
    Get a list containing Rects and Positions for board spaces.
    This can be useful for drawing the board and for handling mouse events.
    """
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

def draw_selection_hint(window: Surface,
                     board: Board,
                     selection: Position,
                     gui_positions: list[tuple[pygame.Rect, Position]],
                     ) -> None:
    """Draw color hints for selected piece and valid moves"""
    valid_moves: list[Position] = board.get_valid_moves(selection)
    for gui_position in gui_positions:
        draw_rect: pygame.Rect = gui_position[0]
        board_position: Position = gui_position[1]
        
        if board_position in valid_moves:
            pygame.draw.rect(window, COLOR_HINT_VALID_MOVE, draw_rect)
        elif board_position == selection:
            pygame.draw.rect(window, COLOR_HINT_SELECTON, draw_rect)

def draw_board(window: Surface,
               board: Board,
               textures: dict[str, Surface],
               gui_positions: list[tuple[pygame.Rect, Position]]
               ) -> None:
    """Draw board spaces"""
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
    """Draw board pieces"""
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
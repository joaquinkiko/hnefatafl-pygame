# Main game runner
import pygame
from pygame import Surface
from pygame.locals import *
import sys
from hnefatafl import Board, Position, Piece

# Window initialization constants
WINDOW_SIZE: tuple = (640, 480)
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE
WINDOW_FLAGS: int = pygame.RESIZABLE | pygame.SCALED
# Simulation rate
FRAMES_PER_SECOND: int = 30
# Window clear color
CLEAR_COLOR: tuple = (60, 19, 33)
COLOR_HINT_SELECTON: pygame.Color = pygame.Color(169, 64, 7)
COLOR_HINT_VALID_MOVE: pygame.Color = pygame.Color(210, 176, 76)
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
ASSET_ARROW_UP: str = f"{ASSET_DIR}arrow_up.png"
ASSET_ARROW_DOWN: str = f"{ASSET_DIR}arrow_down.png"
ASSET_RESET: str = f"{ASSET_DIR}reset.png"
ASSET_FONT_BOARD: str | None = f"{ASSET_DIR}antiquity-print.ttf"
ASSET_FONT_LOG: str | None =  f"{ASSET_DIR}textmachine_handwriting.ttf"
ASSET_FONT_STATUS: str | None = f"{ASSET_DIR}antiquity-print.ttf"
ASSET_MUSIC: str = f"{ASSET_DIR}Ancient Library.wav"
ASSET_SFX_SELECT: str = f"{ASSET_DIR}select.ogg"
ASSET_SFX_INVALID: str = f"{ASSET_DIR}invalid.ogg"
ASSET_SFX_MOVE: str = f"{ASSET_DIR}move.ogg"
ASSET_SFX_CAPTURE: str = f"{ASSET_DIR}capture.ogg"
ASSET_SFX_WIN: str = f"{ASSET_DIR}win.wav"
# Board font
FONT_BOARD_SIZE: int = 12
FONT_BOARD_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_BOARD_SPACING: int = 4
# Log font
FONT_LOG_SIZE: int = 8
FONT_LOG_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_LOG_SPACING: int = 8
FONT_LOG_TOP_LEFT: tuple[int, int] = (4, 4)
# Status font 
FONT_STATUS_SIZE: int = 16
FONT_STATUS_COLOR: pygame.Color = pygame.Color(255, 255, 255)
FONT_STATUS_SPACING: int = 4
FONT_STATUS_Y_OFFSET: int = 8
# Log scroll speed
LOG_SCROLL_SPEED: int = 5
# Arrow Spacing
ARROW_SPACING: int = 8
# Should we use antialiasing for fonts
USE_FONT_AA: bool = True

def main():
    # Initialize GUI
    pygame.init()
    window: Surface = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
    clock = pygame.time.Clock()

    # Setup variables
    board: Board = Board()
    selected_piece: Position = None
    log_scroll_offset: int = 0

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
    arrow_up_img: Surface = pygame.image.load(ASSET_ARROW_UP)
    arrow_down_img: Surface = pygame.image.load(ASSET_ARROW_DOWN)
    reset_img: Surface = pygame.image.load(ASSET_RESET)
    texture_sizes: dict[str, tuple[int, int]] = {}
    for key in textures.keys():
        texture_sizes[key] = textures[key].get_size()
    
    gui_positions: list[tuple[pygame.Rect, Position]] = get_space_rects(window, board, texture_sizes)

    arrow_buttons_height: int = max(arrow_up_img.get_size()[1], arrow_down_img.get_size()[1]) + ARROW_SPACING
    # Bottom left corner
    arrow_up_rect: pygame.Rect = pygame.Rect(
        arrow_down_img.get_size()[0] + ARROW_SPACING * 2,
        WINDOW_HEIGHT - arrow_up_img.get_size()[1] - ARROW_SPACING,
        arrow_up_img.get_size()[0],
        arrow_up_img.get_size()[1]
        )
    arrow_down_rect: pygame.Rect = pygame.Rect(
        ARROW_SPACING,
        WINDOW_HEIGHT - arrow_up_img.get_size()[1] - ARROW_SPACING,
        arrow_down_img.get_size()[0],
        arrow_down_img.get_size()[1]
        )
    # Top right corner
    reset_rect: pygame.Rect = pygame.Rect(
        WINDOW_WIDTH - reset_img.get_size()[0],
        0,
        reset_img.get_size()[0],
        reset_img.get_size()[1]
        )
    # This is how much area we have to display text
    log_area_height: int = WINDOW_HEIGHT - arrow_buttons_height - FONT_LOG_TOP_LEFT[1] - font_log.get_height()

    # Load audio
    pygame.mixer.music.load(ASSET_MUSIC)
    pygame.mixer.music.play(-1, 0, 0)
    pygame.mixer.music.set_volume(0.5)
    sfx_select = pygame.mixer.Sound(ASSET_SFX_SELECT)
    sfx_invalid = pygame.mixer.Sound(ASSET_SFX_INVALID)
    sfx_move = pygame.mixer.Sound(ASSET_SFX_MOVE)
    sfx_capture = pygame.mixer.Sound(ASSET_SFX_CAPTURE)
    sfx_win = pygame.mixer.Sound(ASSET_SFX_WIN)


    # Main game loop
    while True:
        # Calculate scrolling area for log
        log_lines: list[str] = board.get_complete_turn_log().split("\n")
        visible_lines: int = max(1, int(log_area_height / (font_log.get_height() + FONT_LOG_SPACING)))
        max_scroll: int = max(0, (len(log_lines) - visible_lines) * (font_log.get_height() + FONT_LOG_SPACING))

        # Handle events
        for event in pygame.event.get():
            match event.type:
                case pygame.MOUSEBUTTONDOWN:
                    # Log scroll buttons
                    if arrow_up_rect.collidepoint(event.pos):
                        log_scroll_offset = log_scroll_offset - LOG_SCROLL_SPEED
                        continue
                    if arrow_down_rect.collidepoint(event.pos):
                        log_scroll_offset = log_scroll_offset + LOG_SCROLL_SPEED
                        continue
                    if reset_rect.collidepoint(event.pos):
                        # Reset board
                        selected_piece = None
                        pygame.mixer.music.play(-1, 0, 0)
                        board = Board()
                        continue
                    # Board click
                    for gui_position in gui_positions:
                        if board.has_been_won(): continue # Ignore if there's a winner
                        test_rect: pygame.Rect = gui_position[0]
                        if test_rect.collidepoint(event.pos):
                            click_position: Position = gui_position[1]
                            match board.get_piece_at(click_position):
                                case Piece.Attacker:
                                    if board.is_attacker_turn():
                                        selected_piece = click_position
                                        sfx_select.play()
                                    else:
                                        selected_piece = None
                                        sfx_invalid.play()
                                case Piece.Defender:
                                    if board.is_defender_turn():
                                        selected_piece = click_position
                                        sfx_select.play()
                                    else:
                                        selected_piece = None
                                        sfx_invalid.play()
                                case Piece.King:
                                    if board.is_defender_turn():
                                        selected_piece = click_position
                                        sfx_select.play()
                                    else:
                                        selected_piece = None
                                        sfx_invalid.play()
                                case _:
                                    # See if move can be made
                                    if not selected_piece == None:
                                        if board.is_valid_move(selected_piece, click_position):
                                            piece_count: int = len(board.get_all_pieces())
                                            board.play_turn(selected_piece, click_position)
                                            selected_piece = None
                                            log_scroll_offset = max_scroll
                                            if board.has_been_won():
                                                sfx_win.play()
                                            elif piece_count != len(board.get_all_pieces()): # A piece has been captured
                                                sfx_capture.play()
                                            else:
                                                sfx_move.play()
                                        else:
                                            sfx_invalid.play()
                                    else:
                                        sfx_invalid.play()
                case pygame.MOUSEWHEEL:
                    if event.y > 0:
                        log_scroll_offset = log_scroll_offset - LOG_SCROLL_SPEED
                    elif event.y < 0:
                        log_scroll_offset = log_scroll_offset + LOG_SCROLL_SPEED
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_F11:
                            pygame.display.toggle_fullscreen()
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        # Clamp scroll changes made during event collection
        log_scroll_offset = max(0, min(log_scroll_offset, max_scroll))

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
        draw_board_log(window, board, font_log, log_scroll_offset, log_area_height)
        window.blit(arrow_up_img, arrow_up_rect.topleft)
        window.blit(arrow_down_img, arrow_down_rect.topleft)
        window.blit(reset_img, reset_rect.topleft)
        daw_board_status(window, board, font_status)

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)

def draw_board_log(window: Surface,
                   board: Board,
                   font: pygame.font.Font,
                   scroll_offset: int,
                   area_height: int) -> None:
    """Draws text log of board turns."""
    offset: int = 0
    for line in ("Turn Log:\n" + board.get_complete_turn_log()).split("\n"):
        if FONT_LOG_TOP_LEFT[1] + offset - scroll_offset > area_height:
            break # Don't overflow
        text_log = font.render(line, USE_FONT_AA, FONT_LOG_COLOR)
        window.blit(text_log, (FONT_LOG_TOP_LEFT[0], FONT_LOG_TOP_LEFT[1] + offset - scroll_offset))
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
        # Don't draw if space is occupied
        if board.get_piece_at(board_position) != None: continue
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
            case Piece.Attacker:
                window.blit(textures["p_attacker"], draw_position)
            case Piece.Defender:
                window.blit(textures["p_defender"], draw_position)
            case Piece.King:
                window.blit(textures["p_king"], draw_position)

if __name__ == "__main__": main()
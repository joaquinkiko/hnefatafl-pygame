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

def main():
    # Initialize GUI
    pygame.init()
    window: Surface = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
    clock = pygame.time.Clock()

    # Setup variables

    # Load assets

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

        # Update the window
        pygame.display.update()

        # Slow down simulation
        clock.tick(FRAMES_PER_SECOND)



if __name__ == "__main__": main()